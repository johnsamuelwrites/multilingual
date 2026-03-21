#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Runtime implementation of the ~= semantic match operator.

The ~= operator compares two values using embedding cosine similarity
rather than exact string equality.  This module implements that comparison
in a way that integrates with the AIRuntime without coupling the operator
to a specific provider.

Usage in generated code
-----------------------
When the code generator lowers  ``left ~= right``  it will emit a call to
``semantic_match(left, right, threshold=0.80, model=None)``.

Standalone usage
----------------
    from multilingualprogramming.runtime.semantic_match import SemanticMatcher
    matcher = SemanticMatcher(threshold=0.80)
    result = matcher.match("yes", "yeah")   # True
    result = matcher.match("yes", "cancel") # False
"""

from __future__ import annotations

from multilingualprogramming.runtime.ai_runtime import AIRuntime
from multilingualprogramming.runtime.ai_types import EmbeddingVector, ModelRef

# Default embedding model for ~= comparisons.
_DEFAULT_EMBED_MODEL = ModelRef("text-embedding-3-small")

# Cache: text -> EmbeddingVector, to avoid re-embedding repeated values.
_embed_cache: dict[str, EmbeddingVector] = {}


def _get_embedding(text: str, model: ModelRef) -> EmbeddingVector:
    key = f"{model.name}:{text}"
    if key not in _embed_cache:
        _embed_cache[key] = AIRuntime.embed(model, text)
    return _embed_cache[key]


def semantic_match(
    left: object,
    right: object,
    threshold: float = 0.80,
    model: ModelRef | None = None,
) -> bool:
    """Return True if left and right are semantically similar.

    Both values are coerced to strings before embedding.
    threshold: minimum cosine similarity (0.0-1.0).  Default: 0.80.
    model: embedding model to use.  Default: text-embedding-3-small.

    If no AIProvider is registered, falls back to exact string equality
    to allow tests and offline scenarios to run without an API key.
    """
    embed_model = model or _DEFAULT_EMBED_MODEL
    left_str = str(left)
    right_str = str(right)
    if left_str == right_str:
        return True
    try:
        left_vec = _get_embedding(left_str, embed_model)
        right_vec = _get_embedding(right_str, embed_model)
        similarity = left_vec.cosine_similarity(right_vec)
        return similarity >= threshold
    except RuntimeError:
        # No provider registered -- fall back to exact equality.
        return left_str == right_str


def clear_cache() -> None:
    """Clear the embedding cache (useful between tests)."""
    _embed_cache.clear()


class SemanticMatcher:
    """Stateful semantic matcher with configurable threshold and model."""

    def __init__(
        self,
        threshold: float = 0.80,
        model: ModelRef | None = None,
    ) -> None:
        self.threshold = threshold
        self.model = model

    def match(self, left: object, right: object) -> bool:
        """Return True if left and right are semantically similar."""
        return semantic_match(left, right, self.threshold, self.model)

    def best_match(self, query: object, candidates: list) -> tuple[object, float]:
        """Return (best_candidate, similarity_score) from a list."""
        embed_model = self.model or _DEFAULT_EMBED_MODEL
        query_str = str(query)
        try:
            query_vec = _get_embedding(query_str, embed_model)
        except RuntimeError:
            # No provider -- return first exact match or first candidate.
            for c in candidates:
                if str(c) == query_str:
                    return c, 1.0
            return candidates[0] if candidates else (None, 0.0)

        best, best_sim = None, -1.0
        for candidate in candidates:
            c_vec = _get_embedding(str(candidate), embed_model)
            sim = query_vec.cosine_similarity(c_vec)
            if sim > best_sim:
                best, best_sim = candidate, sim
        return best, best_sim
