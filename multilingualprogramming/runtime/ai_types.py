#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Value types for Core 1.0 AI-native constructs.

These types are the runtime representations of AI operation results.
They are provider-independent: any AIProvider implementation returns these
same types regardless of which LLM API it uses.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import AsyncIterator, Iterator


@dataclass
class ModelRef:
    """Reference to a named language model.  Corresponds to @model-name literals."""
    name: str
    provider: str = ""          # provider hint, e.g. "anthropic", "openai"
    version: str = ""           # optional version pin
    params: dict = field(default_factory=dict)   # extra model parameters

    def __str__(self) -> str:
        return f"@{self.name}"


@dataclass
class PromptResult:
    """Result of a `prompt` expression — a string response."""
    content: str
    model: str = ""
    usage: dict = field(default_factory=dict)


@dataclass
class Reasoning:
    """Structured reasoning trace from a `think` expression."""
    trace: str              # chain-of-thought steps
    conclusion: str         # final answer extracted from the reasoning
    model: str = ""
    usage: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return self.conclusion


@dataclass
class StreamChunk:
    """A single token/chunk from a `stream` expression."""
    content: str
    is_final: bool = False


@dataclass
class EmbeddingVector:
    """Dense float vector from an `embed` expression."""
    values: list[float] = field(default_factory=list)
    model: str = ""
    dimensions: int = 0

    def __post_init__(self):
        if self.dimensions == 0 and self.values:
            self.dimensions = len(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def cosine_similarity(self, other: "EmbeddingVector") -> float:
        """Compute cosine similarity with another embedding vector."""
        if not self.values or not other.values:
            return 0.0
        dot = sum(a * b for a, b in zip(self.values, other.values))
        mag_a = sum(a * a for a in self.values) ** 0.5
        mag_b = sum(b * b for b in other.values) ** 0.5
        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0
        return dot / (mag_a * mag_b)


@dataclass
class ToolCall:
    """A tool invocation request from an agent."""
    name: str
    arguments: dict = field(default_factory=dict)
    call_id: str = ""


@dataclass
class ToolResult:
    """Result of a tool invocation."""
    name: str
    output: object = None
    error: str | None = None
    call_id: str = ""

    @property
    def success(self) -> bool:
        return self.error is None
