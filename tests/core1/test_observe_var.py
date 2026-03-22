#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Observe-var runtime tests.

Tests for the reactive Signal / ReactiveEngine plumbing that backs
``observe var`` bindings at runtime.
"""
# pylint: disable=missing-class-docstring,import-error

import pytest

from multilingualprogramming.runtime.reactive import (
    CanvasNode,
    ReactiveEngine,
    Signal,
    stream_to_view,
)
from multilingualprogramming.runtime.ai_types import StreamChunk


# ===========================================================================
# Signal
# ===========================================================================

class TestSignal:
    def test_initial_value(self):
        sig = Signal("count", 0)
        assert sig.get() == 0

    def test_set_updates_value(self):
        sig = Signal("x", 1)
        sig.set(42)
        assert sig.get() == 42

    def test_on_change_fires(self):
        sig = Signal("s", "hello")
        captured = []
        sig.on_change(captured.append)
        sig.set("world")
        assert captured == ["world"]

    def test_multiple_handlers(self):
        sig = Signal("n", 0)
        log: list[int] = []
        sig.on_change(log.append)
        sig.on_change(log.append)
        sig.set(7)
        assert log == [7, 7]

    def test_remove_handler(self):
        sig = Signal("r", 0)
        log: list[int] = []
        handler = log.append
        sig.on_change(handler)
        sig.set(1)
        sig.remove_handler(handler)
        sig.set(2)
        assert log == [1]

    def test_repr(self):
        sig = Signal("x", 3)
        assert "x" in repr(sig)
        assert "3" in repr(sig)


# ===========================================================================
# ReactiveEngine
# ===========================================================================

class TestReactiveEngine:
    def test_declare_and_get(self):
        eng = ReactiveEngine()
        sig = eng.declare("score", 0)
        assert eng.get("score") is sig

    def test_declare_idempotent(self):
        eng = ReactiveEngine()
        s1 = eng.declare("x", 1)
        s2 = eng.declare("x", 99)   # second call should return existing
        assert s1 is s2
        assert s1.get() == 1

    def test_get_missing_raises(self):
        eng = ReactiveEngine()
        with pytest.raises(KeyError):
            eng.get("nonexistent")

    def test_names(self):
        eng = ReactiveEngine()
        eng.declare("a", 0)
        eng.declare("b", 0)
        assert set(eng.names()) == {"a", "b"}

    def test_on_change_decorator(self):
        eng = ReactiveEngine()
        eng.declare("val", 0)
        log: list[int] = []

        @eng.on_change("val")
        def handle(v: int) -> None:
            log.append(v)

        eng.get("val").set(5)
        assert log == [5]

    def test_snapshot(self):
        eng = ReactiveEngine()
        eng.declare("a", 1)
        eng.declare("b", 2)
        snap = eng.snapshot()
        assert snap == {"a": 1, "b": 2}

    def test_snapshot_reflects_updates(self):
        eng = ReactiveEngine()
        eng.declare("x", 10)
        eng.get("x").set(20)
        assert eng.snapshot()["x"] == 20


# ===========================================================================
# stream_to_view
# ===========================================================================

class TestStreamToView:
    def test_plain_string_chunks(self):
        sig = Signal("out", "")
        stream_to_view(iter(["hello", " ", "world"]), sig)
        assert sig.get() == "hello world"

    def test_stream_chunk_objects(self):
        sig = Signal("response", "")
        # StreamChunk uses 'content' field
        chunks = [StreamChunk(content="Hi"), StreamChunk(content="!")]
        stream_to_view(iter(chunks), sig)
        assert sig.get() == "Hi!"

    def test_replace_mode(self):
        sig = Signal("out", "old")
        stream_to_view(iter(["new"]), sig, append=False)
        assert sig.get() == "new"

    def test_transform(self):
        sig = Signal("out", "")
        stream_to_view(iter([1, 2, 3]), sig, transform=lambda x: str(x * 2))
        assert sig.get() == "246"

    def test_handlers_fire_per_chunk(self):
        sig = Signal("out", "")
        updates: list[str] = []
        sig.on_change(updates.append)

        stream_to_view(iter(["a", "b", "c"]), sig)

        assert updates == ["a", "ab", "abc"]


# ===========================================================================
# CanvasNode
# ===========================================================================

class TestCanvasNode:
    def test_bind_slot(self):
        canvas = CanvasNode(name="main")
        sig = Signal("text", "hello")
        canvas.bind("content", sig)
        assert canvas.to_dict()["bindings"]["content"] == "hello"

    def test_binding_updates_slot(self):
        canvas = CanvasNode(name="chat")
        sig = Signal("msg", "")
        canvas.bind("message", sig)
        sig.set("world")
        assert canvas.to_dict()["bindings"]["message"] == "world"

    def test_nested_children(self):
        parent = CanvasNode(name="root")
        child = CanvasNode(name="inner")
        parent.children.append(child)
        d = parent.to_dict()
        assert len(d["children"]) == 1
        assert d["children"][0]["name"] == "inner"

    def test_repr(self):
        canvas = CanvasNode(name="box")
        assert "box" in repr(canvas)
