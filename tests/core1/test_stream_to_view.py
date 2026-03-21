#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Stream-to-view integration tests.

Tests the full pipeline from a (mocked) AI stream through stream_to_view
into a reactive Signal that drives a CanvasNode.
"""
# pylint: disable=missing-class-docstring

import pytest

from multilingualprogramming.runtime.reactive import (
    CanvasNode,
    ReactiveEngine,
    Signal,
    stream_to_view,
)
from multilingualprogramming.runtime.ai_runtime import AIRuntime, MockProvider
from multilingualprogramming.runtime.ai_types import ModelRef, StreamChunk


@pytest.fixture(autouse=True)
def reset_runtime():
    """Reset the shared AI runtime around each test."""
    AIRuntime.reset()
    yield
    AIRuntime.reset()


# ===========================================================================
# Stream to Signal
# ===========================================================================

class TestStreamToSignal:
    def test_empty_stream_leaves_signal_unchanged(self):
        sig = Signal("out", "initial")
        stream_to_view(iter([]), sig)
        assert sig.get() == "initial"

    def test_single_chunk(self):
        sig = Signal("out", "")
        # StreamChunk uses 'content' field
        stream_to_view(iter([StreamChunk(content="hello")]), sig)
        assert sig.get() == "hello"

    def test_multiple_chunks_accumulated(self):
        sig = Signal("out", "")
        chunks = [StreamChunk(content=c) for c in ["The ", "quick ", "fox"]]
        stream_to_view(iter(chunks), sig)
        assert sig.get() == "The quick fox"

    def test_view_reactive_via_signal(self):
        """Signal updates should propagate to a CanvasNode binding."""
        eng = ReactiveEngine()
        sig = eng.declare("response", "")
        canvas = CanvasNode(name="chat")
        canvas.bind("text", sig)

        stream_to_view(
            iter([StreamChunk(content="Hello"), StreamChunk(content=" AI")]),
            sig,
        )

        assert canvas.to_dict()["bindings"]["text"] == "Hello AI"

    def test_intermediate_updates_fire_handlers(self):
        """Each chunk should trigger registered on_change handlers."""
        sig = Signal("out", "")
        snapshots: list[str] = []
        sig.on_change(snapshots.append)

        stream_to_view(iter(["a", "b", "c"]), sig)

        assert snapshots == ["a", "ab", "abc"]


# ===========================================================================
# Full pipeline with MockProvider
# ===========================================================================

class TestStreamToViewWithMockProvider:
    def test_mock_stream_drives_signal(self):
        provider = MockProvider()
        provider.add_response("Paris is the capital of France.")
        AIRuntime.register(provider)

        sig = Signal("answer", "")

        # Simulate what the runtime does when evaluating:
        #   let answer = stream @model: "What is the capital of France?"
        #   bind answer -> chat_view
        raw = AIRuntime.stream(
            ModelRef("default"),
            "What is the capital of France?",
        )
        stream_to_view(raw, sig)

        assert "Paris" in sig.get()

    def test_stream_and_canvas_binding(self):
        provider = MockProvider()
        provider.add_response("Bonjour le monde!")
        AIRuntime.register(provider)

        eng = ReactiveEngine()
        output = eng.declare("output", "")
        canvas = CanvasNode(name="view")
        canvas.bind("content", output)

        raw = AIRuntime.stream(ModelRef("default"), "Say hello in French")
        stream_to_view(raw, output)

        assert canvas.to_dict()["bindings"]["content"] == "Bonjour le monde!"


# ===========================================================================
# ReactiveEngine: observe + on_change pipeline
# ===========================================================================

class TestReactiveEnginePipeline:
    def test_counter_pipeline(self):
        eng = ReactiveEngine()
        count = eng.declare("count", 0)
        doubled: list[int] = []

        @eng.on_change("count")
        def on_count(v: int) -> None:
            doubled.append(v * 2)

        for i in range(1, 4):
            count.set(i)

        assert doubled == [2, 4, 6]

    def test_chain_two_signals(self):
        """Signal A drives Signal B."""
        eng = ReactiveEngine()
        raw = eng.declare("raw_input", "")
        upper = eng.declare("upper_output", "")

        @eng.on_change("raw_input")
        def transform(v: str) -> None:
            upper.set(v.upper())

        raw.set("hello")
        assert upper.get() == "HELLO"

    def test_snapshot_after_stream(self):
        eng = ReactiveEngine()
        eng.declare("text", "")
        stream_to_view(iter(["hi", " there"]), eng.get("text"))
        snap = eng.snapshot()
        assert snap["text"] == "hi there"
