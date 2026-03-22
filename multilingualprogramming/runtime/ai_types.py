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
        """Infer vector dimensionality from the supplied values when omitted."""
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
        """Return True when the tool invocation completed without error."""
        return self.error is None


# ---------------------------------------------------------------------------
# Plan — structured multi-step reasoning primitive
# ---------------------------------------------------------------------------

@dataclass
class PlanStep:
    """A single step in a plan."""
    index: int
    description: str
    status: str = "pending"   # "pending" | "in_progress" | "done" | "failed"
    result: str = ""


@dataclass
class Plan:
    """Structured multi-step reasoning result produced by the `plan` primitive.

    Agents use Plan to break a goal into discrete steps before executing.

    Usage::

        plan = Plan(goal="Summarise a PDF and email it")
        plan.add_step("Extract text from the PDF")
        plan.add_step("Summarise to 3 bullet points")
        plan.add_step("Compose email body")
        plan.add_step("Send email")

        for step in plan.pending_steps():
            step.status = "done"
    """

    goal: str = ""
    steps: list = field(default_factory=list)   # list[PlanStep]

    def add_step(self, description: str) -> "PlanStep":
        step = PlanStep(index=len(self.steps), description=description)
        self.steps.append(step)
        return step

    def pending_steps(self):
        return [s for s in self.steps if s.status == "pending"]

    def completed_steps(self):
        return [s for s in self.steps if s.status == "done"]

    def is_complete(self) -> bool:
        return all(s.status == "done" for s in self.steps)

    def summary(self) -> str:
        lines = [f"Goal: {self.goal}"]
        for s in self.steps:
            lines.append(f"  [{s.status:10s}] {s.index+1}. {s.description}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# GenerateResult — schema-constrained generation output
# ---------------------------------------------------------------------------

@dataclass
class GenerateResult:
    """Result of a schema-constrained generate expression.

    Carries both the raw text and the parsed structured value.

    Usage::

        result: Invoice = generate @model: context -> Invoice
        # result.value is the Invoice instance (if parsing succeeded)
        # result.raw is the raw text from the model
    """

    raw: str = ""
    value: object = None          # the parsed structured value, or None on failure
    declared_type: str = ""       # name of the declared return type
    parse_error: str = ""         # non-empty if structured parsing failed

    @property
    def ok(self) -> bool:
        return self.value is not None and not self.parse_error
