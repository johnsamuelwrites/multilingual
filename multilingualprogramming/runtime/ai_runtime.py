#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 AI runtime.

This module defines:

  AIProvider   — the protocol every provider implementation must satisfy.
                 Implement this to connect any LLM API.

  AIRuntime    — the singleton-style dispatcher that the language runtime
                 calls when evaluating prompt/generate/think/stream/embed.

  MockProvider — a deterministic test double for unit testing.

Usage
-----
Register a provider before running any AI-native code::

    from multilingualprogramming.runtime.ai_runtime import AIRuntime
    from my_provider import AnthropicProvider

    AIRuntime.register(AnthropicProvider())

    # now prompt(...), generate(...), think(...) etc. all use the provider.
"""

from __future__ import annotations

import abc
from typing import AsyncIterator, Iterator

from multilingualprogramming.runtime.ai_types import (
    EmbeddingVector,
    ModelRef,
    PromptResult,
    Reasoning,
    StreamChunk,
    ToolCall,
    ToolResult,
)


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------

class AIProvider(abc.ABC):
    """Abstract base for AI provider implementations.

    Subclass this to connect Multilingual to any LLM API.
    Only `prompt` and `embed` are required; the rest have default
    implementations built on top of `prompt`.
    """

    @abc.abstractmethod
    def prompt(self, model: ModelRef, template: str, **kwargs) -> PromptResult:
        """Send a prompt to the model and return the full response."""

    @abc.abstractmethod
    def embed(self, model: ModelRef, text: str, **kwargs) -> EmbeddingVector:
        """Return a dense embedding vector for the input text."""

    def generate(self, model: ModelRef, template: str, target_type: type | None = None, **kwargs) -> object:
        """Generate a structured value by constraining model output.

        Default: call prompt and return the string.  Override to add JSON-mode
        or schema-constrained generation.
        """
        result = self.prompt(model, template, **kwargs)
        if target_type is str or target_type is None:
            return result.content
        try:
            import json
            return json.loads(result.content)
        except Exception:
            return result.content

    def think(self, model: ModelRef, template: str, **kwargs) -> Reasoning:
        """Run chain-of-thought reasoning.

        Default: send a modified prompt asking the model to reason step by
        step, then split the response into trace + conclusion.  Override for
        native thinking-model support.
        """
        cot_template = (
            f"{template}\n\n"
            "Think step by step, then state your final answer after 'Conclusion:'."
        )
        result = self.prompt(model, cot_template, **kwargs)
        text = result.content
        if "Conclusion:" in text:
            parts = text.split("Conclusion:", 1)
            trace, conclusion = parts[0].strip(), parts[1].strip()
        else:
            trace, conclusion = text, text
        return Reasoning(
            trace=trace,
            conclusion=conclusion,
            model=model.name,
            usage=result.usage,
        )

    def stream(self, model: ModelRef, template: str, **kwargs) -> Iterator[StreamChunk]:
        """Stream tokens.

        Default: call prompt and yield the full response as a single chunk.
        Override to use native streaming APIs.
        """
        result = self.prompt(model, template, **kwargs)
        yield StreamChunk(content=result.content, is_final=True)

    async def prompt_async(self, model: ModelRef, template: str, **kwargs) -> PromptResult:
        """Async version of prompt.  Default: run sync version."""
        return self.prompt(model, template, **kwargs)

    async def stream_async(self, model: ModelRef, template: str, **kwargs) -> AsyncIterator[StreamChunk]:
        """Async streaming.  Default: yield sync result."""
        result = self.prompt(model, template, **kwargs)
        yield StreamChunk(content=result.content, is_final=True)


# ---------------------------------------------------------------------------
# Mock provider (for testing)
# ---------------------------------------------------------------------------

class MockProvider(AIProvider):
    """Deterministic test double.

    Returns predictable responses without calling any external API.
    Responses can be pre-loaded via `add_response`.
    """

    def __init__(self) -> None:
        self._responses: list[str] = []
        self._embed_dim: int = 4
        self._call_log: list[dict] = []

    def add_response(self, text: str) -> "MockProvider":
        """Queue a response string to be returned by the next prompt call."""
        self._responses.append(text)
        return self

    def set_embed_dim(self, dim: int) -> "MockProvider":
        self._embed_dim = dim
        return self

    @property
    def call_log(self) -> list[dict]:
        return list(self._call_log)

    def prompt(self, model: ModelRef, template: str, **kwargs) -> PromptResult:
        self._call_log.append({"op": "prompt", "model": model.name, "template": template})
        text = self._responses.pop(0) if self._responses else f"mock response to: {template[:40]}"
        return PromptResult(content=text, model=model.name)

    def embed(self, model: ModelRef, text: str, **kwargs) -> EmbeddingVector:
        self._call_log.append({"op": "embed", "model": model.name, "text": text})
        # Deterministic fake embedding based on hash
        seed = hash(text) & 0xFFFFFFFF
        values = [
            float((seed >> i) & 0xFF) / 255.0
            for i in range(0, self._embed_dim * 8, 8)
        ]
        # Normalize
        mag = sum(v * v for v in values) ** 0.5 or 1.0
        values = [v / mag for v in values]
        return EmbeddingVector(values=values, model=model.name, dimensions=self._embed_dim)


# ---------------------------------------------------------------------------
# Runtime dispatcher
# ---------------------------------------------------------------------------

class AIRuntime:
    """Central dispatcher for AI operations in the language runtime.

    Usage::

        AIRuntime.register(my_provider)
        result = AIRuntime.prompt(ModelRef("claude-sonnet"), "Hello!")
    """

    _provider: AIProvider | None = None

    @classmethod
    def register(cls, provider: AIProvider) -> None:
        """Register the provider that will serve all AI operations."""
        if not isinstance(provider, AIProvider):
            raise TypeError(f"Expected AIProvider, got {type(provider).__name__}")
        cls._provider = provider

    @classmethod
    def get_provider(cls) -> AIProvider:
        if cls._provider is None:
            raise RuntimeError(
                "No AIProvider registered.  Call AIRuntime.register(provider) "
                "before using AI-native language constructs."
            )
        return cls._provider

    @classmethod
    def prompt(cls, model: ModelRef, template: str, **kwargs) -> PromptResult:
        return cls.get_provider().prompt(model, template, **kwargs)

    @classmethod
    def generate(cls, model: ModelRef, template: str, target_type=None, **kwargs) -> object:
        return cls.get_provider().generate(model, template, target_type, **kwargs)

    @classmethod
    def think(cls, model: ModelRef, template: str, **kwargs) -> Reasoning:
        return cls.get_provider().think(model, template, **kwargs)

    @classmethod
    def stream(cls, model: ModelRef, template: str, **kwargs) -> Iterator[StreamChunk]:
        return cls.get_provider().stream(model, template, **kwargs)

    @classmethod
    def embed(cls, model: ModelRef, text: str, **kwargs) -> EmbeddingVector:
        return cls.get_provider().embed(model, text, **kwargs)

    @classmethod
    def reset(cls) -> None:
        """Unregister the current provider (useful for testing)."""
        cls._provider = None
