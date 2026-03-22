#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 retrieval runtime.

Provides the ``nearest`` built-in and a simple in-memory vector index for
building RAG (retrieval-augmented generation) pipelines.

Usage
-----
    from multilingualprogramming.runtime.retrieval_runtime import VectorIndex, nearest

    index = VectorIndex()
    index.add("Paris is the capital of France.", embedding=[0.1, 0.9, 0.3])
    index.add("Berlin is the capital of Germany.", embedding=[0.2, 0.8, 0.4])

    results = nearest([0.15, 0.85, 0.35], index, top_k=1)
    # results[0].text == "Paris is the capital of France."
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------

@dataclass
class IndexEntry:
    """A single entry stored in a VectorIndex."""

    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """A nearest-neighbour result."""

    text: str
    score: float          # cosine similarity in [0, 1]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"RetrievalResult(score={self.score:.4f}, text={self.text!r})"


# ---------------------------------------------------------------------------
# Vector index
# ---------------------------------------------------------------------------

class VectorIndex:
    """Simple in-memory nearest-neighbour index.

    Uses brute-force cosine similarity.  Suitable for demos and tests;
    production code should swap in a real ANN index (e.g. FAISS, Annoy).
    """

    def __init__(self) -> None:
        self._entries: list[IndexEntry] = []

    def add(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a document with its pre-computed embedding."""
        self._entries.append(
            IndexEntry(text=text, embedding=embedding, metadata=metadata or {})
        )

    def entries(self) -> list[IndexEntry]:
        """Return the list of all stored index entries."""
        return self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"VectorIndex(entries={len(self._entries)})"


# ---------------------------------------------------------------------------
# nearest() built-in
# ---------------------------------------------------------------------------

def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors.  Returns 0.0 for zero vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def nearest(
    query: list[float],
    index: VectorIndex,
    *,
    top_k: int = 5,
    min_score: float = 0.0,
) -> list[RetrievalResult]:
    """Return the *top_k* nearest entries in *index* to *query*.

    Parameters
    ----------
    query:      query embedding vector.
    index:      the VectorIndex to search.
    top_k:      maximum number of results to return.
    min_score:  minimum cosine similarity threshold (default 0.0 = no filter).

    Returns a list of RetrievalResult sorted by descending similarity.
    """
    scored = [
        RetrievalResult(
            text=entry.text,
            score=_cosine(query, entry.embedding),
            metadata=entry.metadata,
        )
        for entry in index.entries()
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    filtered = [r for r in scored if r.score >= min_score]
    return filtered[:top_k]


# ---------------------------------------------------------------------------
# RAG helper
# ---------------------------------------------------------------------------

def format_context(results: list[RetrievalResult], separator: str = "\n\n") -> str:
    """Format retrieval results as a context string for a prompt."""
    return separator.join(r.text for r in results)
