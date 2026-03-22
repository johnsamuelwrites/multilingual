#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Observability runtime for Multilingual's trace / cost / explain constructs.

These are the Python-backend implementations of the three observability
primitives declared in the language specification:

    trace(expr)          — execute expr and log a timing trace event
    cost(expr)           — execute expr and return (result, CostInfo)
    explain(expr)        — execute expr, then ask the model to explain

All three functions are transparent with respect to the original result
so existing program logic does not need to change when observability is
added or removed.

Usage (from transpiled Python)
-------------------------------
    from multilingualprogramming.runtime.observability import (
        ml_trace, ml_cost, ml_explain,
    )

    result = ml_trace(some_value, label="fetch")
    result, info = ml_cost(some_value)
    result, explanation = ml_explain(some_value)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class TraceEvent:
    """A single trace event recorded during execution."""

    label: str
    value: Any
    elapsed_ms: float
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        return (
            f"[trace:{self.label}] elapsed={self.elapsed_ms:.2f}ms "
            f"value={self.value!r}"
        )


@dataclass
class CostInfo:
    """Token / compute cost summary from an AI expression."""

    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""

    @property
    def total_tokens(self) -> int:
        """Return the combined prompt and completion token count."""
        return self.input_tokens + self.output_tokens

    def __str__(self) -> str:
        return (
            f"CostInfo(model={self.model!r}, "
            f"tokens={self.total_tokens}, "
            f"latency={self.latency_ms:.1f}ms)"
        )


# ---------------------------------------------------------------------------
# Global trace sink (programs may replace this)
# ---------------------------------------------------------------------------

_trace_log: list[TraceEvent] = []


def get_trace_log() -> list[TraceEvent]:
    """Return the accumulated trace events for the current process."""
    return _trace_log


def clear_trace_log() -> None:
    """Clear accumulated trace events."""
    _trace_log.clear()


# ---------------------------------------------------------------------------
# trace(expr, label?)
# ---------------------------------------------------------------------------

def ml_trace(value: Any, label: str = "trace") -> Any:
    """Record a trace event and return *value* unchanged.

    The elapsed time is measured from the last call to ml_trace with the
    same label, or from process start if this is the first.
    """
    start = time.perf_counter()
    event = TraceEvent(
        label=label,
        value=value,
        elapsed_ms=(time.perf_counter() - start) * 1000,
    )
    _trace_log.append(event)
    return value


# ---------------------------------------------------------------------------
# cost(expr)
# ---------------------------------------------------------------------------

def ml_cost(value: Any, _cost_info: CostInfo | None = None) -> tuple[Any, CostInfo]:
    """Return *(value, CostInfo)*.

    When the transpiler emits ``cost(prompt(...))`` it passes the
    PromptResult's usage metadata as *_cost_info*.  If the value is a
    PromptResult or Reasoning object (from ai_types), the cost info is
    extracted automatically.
    """
    info = _cost_info
    if info is None:
        # Try to extract from ai_types objects
        usage = getattr(value, "usage", None)
        model = getattr(value, "model", "")
        if isinstance(usage, dict):
            info = CostInfo(
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                model=model or "",
            )
        else:
            info = CostInfo()
    return value, info


# ---------------------------------------------------------------------------
# explain(expr)
# ---------------------------------------------------------------------------

def ml_explain(value: Any, model: str | None = None) -> tuple[Any, str]:
    """Return *(value, explanation_text)*.

    If *value* is a PromptResult or Reasoning the existing content/conclusion
    is used as the explanation.  Otherwise a generic explanation is returned.

    A real implementation would make a follow-up AI call asking "explain
    your reasoning for: <value>".  The stub is synchronous so that non-AI
    programs can use explain() without an async context.
    """
    _ = model

    conclusion = getattr(value, "conclusion", None)
    if conclusion:
        explanation = (
            f"Reasoning trace:\n{getattr(value, 'trace', '')}\n\n"
            f"Conclusion:\n{conclusion}"
        )
    else:
        content = getattr(value, "content", None)
        if content:
            explanation = f"The model responded: {content}"
        else:
            explanation = f"Value: {value!r}"
    return value, explanation
