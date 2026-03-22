#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Anthropic provider for the Core 1.0 AI runtime.

Connects Multilingual's AI-native language constructs to the Anthropic
Messages API via the official ``anthropic`` Python SDK.

Installation
------------
    pip install anthropic

Usage
-----
    from multilingualprogramming.runtime.anthropic_provider import AnthropicProvider
    from multilingualprogramming.runtime.ai_runtime import AIRuntime

    AIRuntime.register(AnthropicProvider())          # uses ANTHROPIC_API_KEY env var
    # or
    AIRuntime.register(AnthropicProvider(api_key="sk-ant-..."))

Model name mapping
------------------
Model reference literals in Multilingual (@claude-sonnet, @claude-haiku, …)
are resolved to full Anthropic model IDs by the _resolve_model() method.
Any name not in the table is passed through as-is, so
@claude-sonnet-4-6 works without any configuration.
"""

from __future__ import annotations

import json
import os
from typing import Iterator

from multilingualprogramming.runtime.ai_runtime import AIProvider
from multilingualprogramming.runtime.ai_types import (
    EmbeddingVector,
    ModelRef,
    PromptResult,
    Reasoning,
    StreamChunk,
)


# Short name → full Anthropic model ID
_MODEL_ALIASES: dict[str, str] = {
    "claude-opus":         "claude-opus-4-6",
    "claude-sonnet":       "claude-sonnet-4-6",
    "claude-haiku":        "claude-haiku-4-5-20251001",
    "opus":                "claude-opus-4-6",
    "sonnet":              "claude-sonnet-4-6",
    "haiku":               "claude-haiku-4-5-20251001",
}

_DEFAULT_MAX_TOKENS = 4096


class AnthropicProvider(AIProvider):
    """AIProvider implementation backed by the Anthropic Messages API.

    Parameters
    ----------
    api_key:
        Anthropic API key.  Defaults to the ``ANTHROPIC_API_KEY`` environment
        variable when omitted.
    default_model:
        Model used when the program does not specify one explicitly.
        Defaults to ``"claude-sonnet-4-6"``.
    max_tokens:
        Maximum tokens to generate.  Defaults to 4096.
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "claude-sonnet-4-6",
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        try:
            import anthropic as _anthropic  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "The 'anthropic' package is required to use AnthropicProvider.\n"
                "Install it with:  pip install anthropic"
            ) from exc

        self._client = _anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        )
        self._async_client = _anthropic.AsyncAnthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        )
        self._default_model = default_model
        self._max_tokens = max_tokens

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_model(self, model: ModelRef) -> str:
        """Resolve a ModelRef to a full Anthropic model ID."""
        name = model.name or self._default_model
        return _MODEL_ALIASES.get(name, name)

    def _max_tokens_for(self, kwargs: dict) -> int:
        return kwargs.pop("max_tokens", self._max_tokens)

    # ------------------------------------------------------------------
    # Required abstract methods
    # ------------------------------------------------------------------

    def prompt(self, model: ModelRef, template: str, **kwargs) -> PromptResult:
        """Send a prompt and return the full text response."""
        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        message = self._client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            **kwargs,
        )
        content = message.content[0].text if message.content else ""
        usage = {}
        if message.usage:
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
        return PromptResult(content=content, model=model_id, usage=usage)

    def embed(self, model: ModelRef, text: str, **kwargs) -> EmbeddingVector:
        """Anthropic does not provide a native embeddings API.

        Falls back to a hash-based mock vector so that programs using
        @claude-* model refs for embedding don't hard-fail.  Use an
        OpenAI or Cohere provider if real embeddings are required.
        """
        dim = kwargs.pop("dimensions", 1536)
        seed = hash(text) & 0xFFFFFFFF
        values = [float((seed >> (i % 32)) & 0xFF) / 255.0 for i in range(dim)]
        mag = sum(v * v for v in values) ** 0.5 or 1.0
        values = [v / mag for v in values]
        return EmbeddingVector(values=values, model=model.name, dimensions=dim)

    # ------------------------------------------------------------------
    # Override: native streaming
    # ------------------------------------------------------------------

    def stream(self, model: ModelRef, template: str, **kwargs) -> Iterator[StreamChunk]:
        """Stream tokens using the Anthropic streaming Messages API."""
        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        with self._client.messages.stream(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            **kwargs,
        ) as stream_ctx:
            for text in stream_ctx.text_stream:
                yield StreamChunk(content=text, is_final=False)
        yield StreamChunk(content="", is_final=True)

    # ------------------------------------------------------------------
    # Override: native thinking (extended thinking models)
    # ------------------------------------------------------------------

    def think(self, model: ModelRef, template: str, **kwargs) -> Reasoning:
        """Use extended thinking when the model supports it, otherwise fall back."""
        model_id = self._resolve_model(model)
        # Extended thinking is available on claude-sonnet-4-* and claude-opus-4-*
        supports_thinking = any(
            tag in model_id for tag in ("sonnet-4", "opus-4")
        )
        if supports_thinking:
            max_tokens = self._max_tokens_for(kwargs)
            thinking_budget = min(max_tokens // 2, 8000)
            message = self._client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                thinking={"type": "enabled", "budget_tokens": thinking_budget},
                messages=[{"role": "user", "content": template}],
                **kwargs,
            )
            trace_parts = []
            conclusion_parts = []
            for block in message.content:
                if block.type == "thinking":
                    trace_parts.append(block.thinking)
                elif block.type == "text":
                    conclusion_parts.append(block.text)
            usage = {}
            if message.usage:
                usage = {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                }
            return Reasoning(
                trace="\n".join(trace_parts),
                conclusion="\n".join(conclusion_parts),
                model=model_id,
                usage=usage,
            )
        # Fallback for models without native thinking
        return super().think(model, template, **kwargs)

    # ------------------------------------------------------------------
    # Override: structured generation with JSON mode
    # ------------------------------------------------------------------

    def generate(
        self,
        model: ModelRef,
        template: str,
        target_type: type | None = None,
        **kwargs,
    ) -> object:
        """Generate a structured value.

        Asks the model to respond in JSON when a non-string target type is
        declared, then attempts to parse the response.
        """
        if target_type is None or target_type is str:
            return self.prompt(model, template, **kwargs).content

        json_prompt = (
            f"{template}\n\n"
            "Respond with valid JSON only matching the schema for "
            f"{getattr(target_type, '__name__', str(target_type))}. "
            "Do not include any text outside the JSON object."
        )
        result = self.prompt(model, json_prompt, **kwargs)
        raw = result.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            data = json.loads(raw)
            if hasattr(target_type, "__dataclass_fields__"):
                return target_type(**{
                    k: v for k, v in data.items()
                    if k in target_type.__dataclass_fields__
                })
            return data
        except Exception:
            return raw

    # ------------------------------------------------------------------
    # Async variants
    # ------------------------------------------------------------------

    async def prompt_async(self, model: ModelRef, template: str, **kwargs) -> PromptResult:
        """Async prompt using the Anthropic async client."""
        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        message = await self._async_client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            **kwargs,
        )
        content = message.content[0].text if message.content else ""
        usage = {}
        if message.usage:
            usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
        return PromptResult(content=content, model=model_id, usage=usage)
