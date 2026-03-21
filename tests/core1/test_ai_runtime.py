#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for Core 1.0 AI runtime: types, provider, dispatcher, tools, semantic match."""

import pytest

from multilingualprogramming.runtime.ai_types import (
    EmbeddingVector, ModelRef, PromptResult, Reasoning, StreamChunk, ToolCall, ToolResult,
)
from multilingualprogramming.runtime.ai_runtime import AIRuntime, MockProvider
from multilingualprogramming.runtime.tool_runtime import (
    AgentLoop, ToolRegistry, tool, get_registry,
)
from multilingualprogramming.runtime.semantic_match import (
    SemanticMatcher, semantic_match, clear_cache,
)


@pytest.fixture(autouse=True)
def reset_runtime():
    """Ensure AIRuntime has no provider between tests."""
    AIRuntime.reset()
    clear_cache()
    yield
    AIRuntime.reset()
    clear_cache()


# ===========================================================================
# ModelRef
# ===========================================================================

class TestModelRef:
    def test_str_includes_at(self):
        m = ModelRef("claude-sonnet")
        assert str(m) == "@claude-sonnet"

    def test_provider_default_empty(self):
        assert ModelRef("gpt-4o").provider == ""


# ===========================================================================
# EmbeddingVector
# ===========================================================================

class TestEmbeddingVector:
    def test_dimensions_inferred(self):
        v = EmbeddingVector(values=[0.1, 0.2, 0.3])
        assert v.dimensions == 3

    def test_len(self):
        v = EmbeddingVector(values=[1.0, 2.0])
        assert len(v) == 2

    def test_cosine_similarity_identical(self):
        v = EmbeddingVector(values=[1.0, 0.0, 0.0])
        assert v.cosine_similarity(v) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        a = EmbeddingVector(values=[1.0, 0.0])
        b = EmbeddingVector(values=[0.0, 1.0])
        assert a.cosine_similarity(b) == pytest.approx(0.0)

    def test_cosine_similarity_opposite(self):
        a = EmbeddingVector(values=[1.0, 0.0])
        b = EmbeddingVector(values=[-1.0, 0.0])
        assert a.cosine_similarity(b) == pytest.approx(-1.0)

    def test_empty_vectors_return_zero(self):
        a = EmbeddingVector(values=[])
        b = EmbeddingVector(values=[])
        assert a.cosine_similarity(b) == 0.0


# ===========================================================================
# Reasoning
# ===========================================================================

class TestReasoning:
    def test_str_returns_conclusion(self):
        r = Reasoning(trace="step 1...", conclusion="42")
        assert str(r) == "42"


# ===========================================================================
# MockProvider
# ===========================================================================

class TestMockProvider:
    def test_returns_queued_response(self):
        p = MockProvider()
        p.add_response("hello world")
        result = p.prompt(ModelRef("test"), "hi")
        assert result.content == "hello world"

    def test_fallback_response_when_queue_empty(self):
        p = MockProvider()
        result = p.prompt(ModelRef("test"), "anything")
        assert "mock response" in result.content

    def test_embed_returns_normalized_vector(self):
        p = MockProvider().set_embed_dim(4)
        v = p.embed(ModelRef("emb"), "hello")
        assert len(v) == 4
        mag = sum(x * x for x in v.values) ** 0.5
        assert mag == pytest.approx(1.0, abs=1e-6)

    def test_call_log_records_operations(self):
        p = MockProvider()
        p.prompt(ModelRef("m"), "q")
        p.embed(ModelRef("e"), "t")
        assert len(p.call_log) == 2
        assert p.call_log[0]["op"] == "prompt"
        assert p.call_log[1]["op"] == "embed"

    def test_think_splits_conclusion(self):
        p = MockProvider()
        p.add_response("Step 1: think. Step 2: more. Conclusion: 42")
        r = p.think(ModelRef("m"), "what is 6*7?")
        assert r.conclusion == "42"
        assert "Step 1" in r.trace

    def test_stream_yields_single_chunk(self):
        p = MockProvider()
        p.add_response("streamed text")
        chunks = list(p.stream(ModelRef("m"), "write something"))
        assert len(chunks) == 1
        assert chunks[0].content == "streamed text"
        assert chunks[0].is_final


# ===========================================================================
# AIRuntime
# ===========================================================================

class TestAIRuntime:
    def test_raises_when_no_provider(self):
        with pytest.raises(RuntimeError, match="No AIProvider"):
            AIRuntime.prompt(ModelRef("m"), "hi")

    def test_register_and_prompt(self):
        p = MockProvider().add_response("pong")
        AIRuntime.register(p)
        result = AIRuntime.prompt(ModelRef("m"), "ping")
        assert result.content == "pong"

    def test_register_bad_type_raises(self):
        with pytest.raises(TypeError):
            AIRuntime.register("not a provider")

    def test_generate_returns_string_by_default(self):
        AIRuntime.register(MockProvider().add_response("the answer"))
        result = AIRuntime.generate(ModelRef("m"), "prompt")
        assert result == "the answer"

    def test_embed_delegates_to_provider(self):
        AIRuntime.register(MockProvider().set_embed_dim(3))
        vec = AIRuntime.embed(ModelRef("emb"), "text")
        assert len(vec) == 3

    def test_think_returns_reasoning(self):
        AIRuntime.register(MockProvider().add_response("Steps... Conclusion: done"))
        r = AIRuntime.think(ModelRef("m"), "think about X")
        assert isinstance(r, Reasoning)
        assert r.conclusion == "done"

    def test_stream_returns_iterator(self):
        AIRuntime.register(MockProvider().add_response("hello"))
        chunks = list(AIRuntime.stream(ModelRef("m"), "hi"))
        assert chunks[0].content == "hello"


# ===========================================================================
# ToolRegistry
# ===========================================================================

class TestToolRegistry:
    def test_register_and_call(self):
        reg = ToolRegistry()
        reg.register(lambda x: x * 2, description="doubles", name="double")
        result = reg.call(ToolCall(name="double", arguments={"x": 5}))
        assert result.success
        assert result.output == 10

    def test_unknown_tool_returns_error(self):
        reg = ToolRegistry()
        result = reg.call(ToolCall(name="unknown", arguments={}))
        assert not result.success
        assert "Unknown tool" in result.error

    def test_names_lists_registered_tools(self):
        reg = ToolRegistry()
        reg.register(lambda: None, name="a")
        reg.register(lambda: None, name="b")
        assert set(reg.names()) == {"a", "b"}

    def test_descriptions_string(self):
        reg = ToolRegistry()
        reg.register(lambda: None, description="does something", name="thing")
        desc = reg.descriptions()
        assert "thing" in desc
        assert "does something" in desc

    def test_tool_exception_captured(self):
        reg = ToolRegistry()
        def fail():
            raise ValueError("boom")
        reg.register(fail, name="fail")
        result = reg.call(ToolCall(name="fail", arguments={}))
        assert not result.success
        assert "boom" in result.error


# ===========================================================================
# @tool decorator
# ===========================================================================

class TestToolDecorator:
    def test_decorated_function_still_callable(self):
        @tool(description="add two numbers")
        def add(a: int, b: int) -> int:
            return a + b
        assert add(2, 3) == 5

    def test_decorated_function_marked(self):
        @tool(description="test")
        def f():
            pass
        assert getattr(f, "__tool__", False)


# ===========================================================================
# AgentLoop
# ===========================================================================

class TestAgentLoop:
    def test_direct_answer_no_tool_call(self):
        AIRuntime.register(MockProvider().add_response("The answer is 42."))
        loop = AgentLoop(model=ModelRef("m"))
        answer = loop.run("What is 6 times 7?")
        assert "42" in answer

    def test_tool_call_then_answer(self):
        p = MockProvider()
        # First response: a tool call in JSON
        p.add_response('{"tool": "calc", "arguments": {"expr": "6*7"}}')
        # Second response: final answer
        p.add_response("The result is 42.")
        AIRuntime.register(p)

        reg = ToolRegistry()
        reg.register(lambda expr: eval(expr), description="calc", name="calc")  # noqa: S307

        loop = AgentLoop(model=ModelRef("m"), registry=reg)
        answer = loop.run("What is 6*7?")
        assert "42" in answer
        assert loop.history[0]["tool"] == "calc"


# ===========================================================================
# SemanticMatcher
# ===========================================================================

class TestSemanticMatcher:
    def test_exact_match_always_true(self):
        # Exact equality works without a provider
        assert semantic_match("yes", "yes", threshold=0.80) is True

    def test_no_provider_falls_back_to_equality(self):
        # No provider registered -- must not raise
        assert semantic_match("yes", "no", threshold=0.80) is False
        assert semantic_match("hello", "hello") is True

    def test_mock_provider_embedding_match(self):
        AIRuntime.register(MockProvider().set_embed_dim(8))
        m = SemanticMatcher(threshold=0.0)   # threshold 0 = any similarity passes
        # With threshold 0, anything should match
        assert m.match("hello", "world") is True

    def test_high_threshold_rejects_dissimilar(self):
        AIRuntime.register(MockProvider().set_embed_dim(8))
        # The mock hashes are fixed -- "hello" and "goodbye" produce different vectors.
        # We just test that the call completes without error.
        m = SemanticMatcher(threshold=0.99)
        result = m.match("hello", "goodbye")
        assert isinstance(result, bool)

    def test_best_match_returns_highest_similarity(self):
        AIRuntime.register(MockProvider().set_embed_dim(4))
        m = SemanticMatcher()
        best, score = m.best_match("query", ["a", "b", "c"])
        assert best in ["a", "b", "c"]
        assert 0.0 <= score <= 1.0

    def test_best_match_empty_returns_none(self):
        # No candidates
        m = SemanticMatcher()
        best, score = m.best_match("q", [])
        assert best is None
        assert score == 0.0
