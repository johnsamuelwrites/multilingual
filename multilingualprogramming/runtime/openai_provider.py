#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""OpenAI provider for the Core 1.0 AI runtime.

Connects Multilingual's AI-native language constructs to the OpenAI Chat
Completions and Embeddings APIs via the official ``openai`` Python SDK.

Installation
------------
    pip install openai

Usage
-----
    from multilingualprogramming.runtime.openai_provider import OpenAIProvider
    from multilingualprogramming.runtime.ai_runtime import AIRuntime

    AIRuntime.register(OpenAIProvider())               # uses OPENAI_API_KEY env var
    # or
    AIRuntime.register(OpenAIProvider(api_key="sk-..."))

Model name mapping
------------------
Model reference literals in Multilingual (@gpt-4o, @gpt-4-turbo, …) are
resolved by the _resolve_model() method.  Any name not in the alias table is
passed through as-is, so @gpt-4o-mini works without any configuration.
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
    StreamChunk,
)


# Short name → full OpenAI model ID
_MODEL_ALIASES: dict[str, str] = {
    "gpt4o":       "gpt-4o",
    "gpt-4o":      "gpt-4o",
    "gpt4":        "gpt-4-turbo",
    "gpt-4":       "gpt-4-turbo",
    "gpt4-turbo":  "gpt-4-turbo",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt4o-mini":  "gpt-4o-mini",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt3":        "gpt-3.5-turbo",
    "gpt-3.5":     "gpt-3.5-turbo",
    "o1":          "o1",
    "o1-mini":     "o1-mini",
    "o3-mini":     "o3-mini",
}

_DEFAULT_MAX_TOKENS = 4096
_DEFAULT_EMBED_MODEL = "text-embedding-3-small"


class OpenAIProvider(AIProvider):
    """AIProvider implementation backed by the OpenAI Chat Completions API.

    Parameters
    ----------
    api_key:
        OpenAI API key.  Defaults to the ``OPENAI_API_KEY`` environment
        variable when omitted.
    default_model:
        Model used when the program does not specify one explicitly.
        Defaults to ``"gpt-4o"``.
    embed_model:
        Model used for embedding requests.
        Defaults to ``"text-embedding-3-small"``.
    max_tokens:
        Maximum tokens to generate.  Defaults to 4096.
    base_url:
        Override the API base URL.  Useful for OpenAI-compatible local
        endpoints (e.g. LM Studio, vLLM).  Defaults to None (OpenAI's URL).
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "gpt-4o",
        embed_model: str = _DEFAULT_EMBED_MODEL,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        base_url: str | None = None,
    ) -> None:
        try:
            import openai as _openai  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required to use OpenAIProvider.\n"
                "Install it with:  pip install openai"
            ) from exc

        resolved_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        client_kwargs: dict = {"api_key": resolved_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = _openai.OpenAI(**client_kwargs)
        self._async_client = _openai.AsyncOpenAI(**client_kwargs)
        self._default_model = default_model
        self._embed_model = embed_model
        self._max_tokens = max_tokens

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_model(self, model: ModelRef) -> str:
        """Resolve a ModelRef to a full OpenAI model ID."""
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
        response = self._client.chat.completions.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            **kwargs,
        )
        content = ""
        if response.choices:
            content = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        return PromptResult(content=content, model=model_id, usage=usage)

    def embed(self, model: ModelRef, text: str, **kwargs) -> EmbeddingVector:
        """Return a dense embedding vector using the OpenAI Embeddings API."""
        embed_model = kwargs.pop("embed_model", self._embed_model)
        response = self._client.embeddings.create(
            model=embed_model,
            input=text,
            **kwargs,
        )
        values = response.data[0].embedding
        return EmbeddingVector(
            values=values, model=embed_model, dimensions=len(values)
        )

    # ------------------------------------------------------------------
    # Override: native streaming
    # ------------------------------------------------------------------

    def stream(self, model: ModelRef, template: str, **kwargs) -> Iterator[StreamChunk]:
        """Stream tokens using the OpenAI streaming Chat Completions API."""
        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        with self._client.chat.completions.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            stream=True,
            **kwargs,
        ) as stream_ctx:
            for chunk in stream_ctx:
                delta = chunk.choices[0].delta if chunk.choices else None
                content = (delta.content or "") if delta else ""
                is_final = (
                    chunk.choices[0].finish_reason is not None
                    if chunk.choices
                    else False
                )
                yield StreamChunk(content=content, is_final=is_final)

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

        Uses OpenAI's ``response_format={"type": "json_object"}`` when a
        non-string target type is declared, then attempts to parse the
        response.
        """
        if target_type is None or target_type is str:
            return self.prompt(model, template, **kwargs).content

        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        json_prompt = (
            f"{template}\n\n"
            "Respond with valid JSON only matching the schema for "
            f"{getattr(target_type, '__name__', str(target_type))}. "
            "Do not include any text outside the JSON object."
        )
        response = self._client.chat.completions.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": json_prompt}],
            response_format={"type": "json_object"},
            **kwargs,
        )
        raw = ""
        if response.choices:
            raw = (response.choices[0].message.content or "").strip()
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
        """Async prompt using the OpenAI async client."""
        model_id = self._resolve_model(model)
        max_tokens = self._max_tokens_for(kwargs)
        response = await self._async_client.chat.completions.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": template}],
            **kwargs,
        )
        content = ""
        if response.choices:
            content = response.choices[0].message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        return PromptResult(content=content, model=model_id, usage=usage)
