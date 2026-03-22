#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""VectorIndex and nearest() retrieval runtime tests."""
# pylint: disable=missing-class-docstring

from multilingualprogramming.runtime.retrieval_runtime import (
    RetrievalResult,
    VectorIndex,
    format_context,
    nearest,
)


# ===========================================================================
# VectorIndex
# ===========================================================================

class TestVectorIndex:
    def test_empty_index(self):
        idx = VectorIndex()
        assert len(idx) == 0

    def test_add_entry(self):
        idx = VectorIndex()
        idx.add("hello", [1.0, 0.0])
        assert len(idx) == 1

    def test_repr(self):
        idx = VectorIndex()
        idx.add("x", [1.0])
        assert "1" in repr(idx)


# ===========================================================================
# nearest()
# ===========================================================================

class TestNearest:
    def _make_index(self):
        idx = VectorIndex()
        idx.add("Paris", [1.0, 0.0, 0.0])
        idx.add("Berlin", [0.0, 1.0, 0.0])
        idx.add("Tokyo", [0.0, 0.0, 1.0])
        return idx

    def test_nearest_returns_top_k(self):
        idx = self._make_index()
        results = nearest([1.0, 0.0, 0.0], idx, top_k=2)
        assert len(results) == 2

    def test_nearest_top_1_is_closest(self):
        idx = self._make_index()
        results = nearest([1.0, 0.0, 0.0], idx, top_k=1)
        assert results[0].text == "Paris"

    def test_results_sorted_by_score(self):
        idx = self._make_index()
        results = nearest([1.0, 0.0, 0.0], idx, top_k=3)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_min_score_filters_results(self):
        idx = self._make_index()
        # Query is orthogonal to Berlin and Tokyo: their scores will be 0.0
        results = nearest([1.0, 0.0, 0.0], idx, top_k=3, min_score=0.5)
        assert all(r.score >= 0.5 for r in results)
        assert len(results) == 1
        assert results[0].text == "Paris"

    def test_empty_index_returns_empty(self):
        idx = VectorIndex()
        results = nearest([1.0, 0.0], idx, top_k=5)
        assert results == []

    def test_retrieval_result_repr(self):
        r = RetrievalResult(text="hello", score=0.95)
        assert "0.9500" in repr(r)

    def test_top_k_limits_results(self):
        idx = VectorIndex()
        for i in range(10):
            idx.add(f"doc{i}", [float(i), 0.0])
        results = nearest([9.0, 0.0], idx, top_k=3)
        assert len(results) == 3

    def test_metadata_preserved(self):
        idx = VectorIndex()
        idx.add("doc", [1.0, 0.0], metadata={"source": "wiki"})
        results = nearest([1.0, 0.0], idx, top_k=1)
        assert results[0].metadata["source"] == "wiki"


# ===========================================================================
# format_context()
# ===========================================================================

class TestFormatContext:
    def test_single_result(self):
        results = [RetrievalResult(text="Paris is nice.", score=1.0)]
        ctx = format_context(results)
        assert ctx == "Paris is nice."

    def test_multiple_results_joined(self):
        results = [
            RetrievalResult(text="A", score=1.0),
            RetrievalResult(text="B", score=0.8),
        ]
        ctx = format_context(results)
        assert "A" in ctx
        assert "B" in ctx

    def test_custom_separator(self):
        results = [
            RetrievalResult(text="X", score=1.0),
            RetrievalResult(text="Y", score=0.9),
        ]
        ctx = format_context(results, separator=" | ")
        assert ctx == "X | Y"

    def test_empty_results(self):
        assert format_context([]) == ""
