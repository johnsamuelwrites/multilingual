#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tool registry and agent execution loop for Core 1.0.

@tool-decorated functions are registered here.  The AgentLoop drives
the plan-call-observe-respond cycle for @agent-decorated functions.
"""

from __future__ import annotations

import functools
import inspect
from typing import Callable

from multilingualprogramming.runtime.ai_runtime import AIRuntime
from multilingualprogramming.runtime.ai_types import (
    ModelRef,
    PromptResult,
    ToolCall,
    ToolResult,
)


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registry of callable tools available to agents.

    Tools are registered with their name, description, and parameter schema.
    The schema is inferred from the Python function signature when not provided.
    """

    def __init__(self) -> None:
        self._tools: dict[str, dict] = {}

    def register(
        self,
        fn: Callable,
        description: str = "",
        name: str | None = None,
    ) -> None:
        """Register a callable as a named tool."""
        tool_name = name or fn.__name__
        sig = inspect.signature(fn)
        params = {}
        for pname, param in sig.parameters.items():
            ann = param.annotation
            params[pname] = {
                "type": ann.__name__ if ann is not inspect.Parameter.empty else "any",
                "required": param.default is inspect.Parameter.empty,
            }
        self._tools[tool_name] = {
            "fn": fn,
            "description": description or (fn.__doc__ or "").strip(),
            "parameters": params,
        }

    def call(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call and return its result."""
        entry = self._tools.get(tool_call.name)
        if entry is None:
            return ToolResult(
                name=tool_call.name,
                error=f"Unknown tool: {tool_call.name!r}",
                call_id=tool_call.call_id,
            )
        try:
            output = entry["fn"](**tool_call.arguments)
            return ToolResult(
                name=tool_call.name,
                output=output,
                call_id=tool_call.call_id,
            )
        except Exception as exc:
            return ToolResult(
                name=tool_call.name,
                error=str(exc),
                call_id=tool_call.call_id,
            )

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def descriptions(self) -> str:
        """Return a compact textual summary of all registered tools."""
        lines = []
        for name, entry in self._tools.items():
            params = ", ".join(
                f"{k}: {v['type']}" for k, v in entry["parameters"].items()
            )
            lines.append(f"  {name}({params}) — {entry['description']}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Module-level default registry
# ---------------------------------------------------------------------------

_default_registry = ToolRegistry()


def tool(description: str = "", name: str | None = None):
    """Decorator that registers a function as a @tool.

    Usage::

        @tool(description="Search the web for current information")
        def web_search(query: str) -> list:
            ...
    """
    def decorator(fn: Callable) -> Callable:
        _default_registry.register(fn, description=description, name=name)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper.__tool__ = True
        return wrapper

    # Handle bare @tool usage (no parentheses)
    if callable(description):
        fn = description
        description = ""
        return decorator(fn)
    return decorator


def get_registry() -> ToolRegistry:
    """Return the module-level default tool registry."""
    return _default_registry


# ---------------------------------------------------------------------------
# Agent execution loop
# ---------------------------------------------------------------------------

class AgentLoop:
    """Drives a simple plan-call-observe-respond agent cycle.

    The loop:
    1. Sends the user request to the model with a tool description.
    2. If the model response contains a tool call directive (JSON),
       executes the tool and feeds the result back.
    3. Repeats until the model produces a final answer (no tool call)
       or the max_steps limit is reached.

    This is a minimal reference implementation.  Real agent loops should
    override ``_extract_tool_call`` and ``_format_tool_result`` to match
    the provider's specific tool-calling protocol.
    """

    def __init__(
        self,
        model: ModelRef,
        registry: ToolRegistry | None = None,
        max_steps: int = 10,
        system_prompt: str = "",
    ) -> None:
        self.model = model
        self.registry = registry or _default_registry
        self.max_steps = max_steps
        self.system_prompt = system_prompt
        self.history: list[dict] = []

    def run(self, user_request: str) -> str:
        """Run the agent loop and return the final answer."""
        tools_desc = self.registry.descriptions()
        prompt = self._build_prompt(user_request, tools_desc)
        for _ in range(self.max_steps):
            result = AIRuntime.prompt(self.model, prompt)
            tool_call = self._extract_tool_call(result.content)
            if tool_call is None:
                return result.content
            tool_result = self.registry.call(tool_call)
            self.history.append({"tool": tool_call.name, "result": tool_result.output})
            prompt = self._format_tool_result(prompt, result.content, tool_result)
        return result.content

    def _build_prompt(self, request: str, tools_desc: str) -> str:
        parts = []
        if self.system_prompt:
            parts.append(self.system_prompt)
        if tools_desc:
            parts.append(f"Available tools:\n{tools_desc}")
        parts.append(f"Request: {request}")
        if self.history:
            obs = "\n".join(
                f"  {h['tool']}: {h['result']}" for h in self.history
            )
            parts.append(f"Previous observations:\n{obs}")
        return "\n\n".join(parts)

    def _extract_tool_call(self, response: str) -> ToolCall | None:
        """Extract a tool call from the model response.

        Default: look for a JSON object containing a "tool" key.
        Scans for '{' characters and attempts to parse a complete JSON object
        at each position, handling nested objects.
        Override to support provider-specific formats.
        """
        import json
        for start in range(len(response)):
            if response[start] != "{":
                continue
            # Walk forward to find the matching closing brace
            depth = 0
            in_string = False
            escape_next = False
            for end in range(start, len(response)):
                ch = response[end]
                if escape_next:
                    escape_next = False
                    continue
                if ch == "\\" and in_string:
                    escape_next = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = response[start:end + 1]
                        try:
                            data = json.loads(candidate)
                            if not isinstance(data, dict):
                                break
                            name = data.get("tool") or data.get("name")
                            args = data.get("arguments") or data.get("args") or {}
                            if name:
                                return ToolCall(name=name, arguments=args)
                        except Exception:
                            pass
                        break
        return None

    def _format_tool_result(
        self,
        original_prompt: str,
        model_response: str,
        result: ToolResult,
    ) -> str:
        if result.success:
            observation = f"Tool '{result.name}' returned: {result.output}"
        else:
            observation = f"Tool '{result.name}' failed: {result.error}"
        return (
            f"{original_prompt}\n\n"
            f"Model called: {model_response}\n\n"
            f"Observation: {observation}\n\n"
            "Continue with the original request."
        )
