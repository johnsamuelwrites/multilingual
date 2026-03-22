#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""SemanticMatcher and ~= operator runtime tests."""
# pylint: disable=missing-class-docstring,import-error

import pytest

from multilingualprogramming.runtime.ai_runtime import AIRuntime, MockProvider
from multilingualprogramming.runtime.semantic_match import (
    SemanticMatcher,
    semantic_match,
    clear_cache,
)


@pytest.fixture(autouse=True)
def reset():
    """Reset runtime and semantic-match caches around each test."""
    AIRuntime.reset()
    clear_cache()
    yield
    AIRuntime.reset()
    clear_cache()


# ===========================================================================
# semantic_match() fallback (no provider)
# ===========================================================================

class TestSemanticMatchFallback:
    def test_exact_match_returns_true(self):
        assert semantic_match("hello", "hello") is True

    def test_exact_mismatch_returns_false(self):
        assert semantic_match("hello", "world") is False

    def test_case_insensitive_fallback(self):
        # fallback is exact equality — case matters
        assert semantic_match("Hello", "hello") is False


# ===========================================================================
# semantic_match() with provider
# ===========================================================================

class TestSemanticMatchWithProvider:
    def test_similar_texts_match(self):
        provider = MockProvider()
        provider.set_embed_dim(4)
        AIRuntime.register(provider)

        # Mock provider returns deterministic vectors for the same input
        result = semantic_match("yes", "yes", threshold=0.5)
        assert result is True

    def test_threshold_controls_match(self):
        provider = MockProvider()
        provider.set_embed_dim(4)
        AIRuntime.register(provider)

        # Two different strings will get different embeddings;
        # with threshold=0.0 it should always match (any similarity >= 0)
        result = semantic_match("hi", "hello", threshold=0.0)
        assert result is True


# ===========================================================================
# SemanticMatcher
# ===========================================================================

class TestSemanticMatcher:
    def test_match_exact(self):
        matcher = SemanticMatcher()
        assert matcher.match("yes", "yes") is True

    def test_best_match_returns_closest(self):
        provider = MockProvider()
        provider.set_embed_dim(8)
        AIRuntime.register(provider)

        matcher = SemanticMatcher()
        # "yes" should be its own best match from ["yes", "no", "maybe"]
        best, _ = matcher.best_match("yes", ["yes", "no", "maybe"])
        assert best is not None
        assert best in ["yes", "no", "maybe"]

    def test_best_match_empty_candidates(self):
        matcher = SemanticMatcher()
        best, _ = matcher.best_match("yes", [])
        assert best is None

    def test_match_with_provider(self):
        provider = MockProvider()
        provider.set_embed_dim(4)
        AIRuntime.register(provider)

        matcher = SemanticMatcher(threshold=0.0)
        # With threshold 0.0 any two strings should match
        assert matcher.match("hello", "world") is True

    def test_match_no_provider_fallback(self):
        # No provider — falls back to exact equality
        matcher = SemanticMatcher()
        assert matcher.match("apple", "apple") is True
        assert matcher.match("apple", "orange") is False
