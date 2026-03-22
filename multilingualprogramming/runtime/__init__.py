#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual Core 1.0 runtime package.

Public re-exports
-----------------
AI execution
    AIRuntime, AIProvider       — abstract provider protocol
    AnthropicProvider           — Anthropic Messages API backend

Reactive / UI
    ReactiveEngine, Signal      — observable state and reactive bindings
    CanvasNode, stream_to_view  — UI canvas and stream binding helpers

Structured concurrency
    Channel                     — typed async FIFO channel (channel<T>)

Observability
    ml_trace, ml_cost           — trace and cost wrappers
    ml_explain                  — explanation wrapper
    TraceEvent, CostInfo        — result types

Placement
    local, edge, cloud          — @local / @edge / @cloud decorators
    get_placement               — inspect placement annotation

Agent memory and coordination
    ml_memory, MemoryStore      — named persistent memory stores
    Swarm, ml_delegate          — multi-agent swarm and delegation
    swarm_decorator             — @swarm(...) decorator factory
"""

from multilingualprogramming.runtime.ai_runtime import AIRuntime, AIProvider
from multilingualprogramming.runtime.ai_types import (
    EmbeddingVector,
    ModelRef,
    Plan,
    PromptResult,
    Reasoning,
    StreamChunk,
)
from multilingualprogramming.runtime.channel import Channel
from multilingualprogramming.runtime.memory_store import MemoryStore, ml_memory
from multilingualprogramming.runtime.observability import (
    CostInfo,
    TraceEvent,
    ml_cost,
    ml_explain,
    ml_trace,
)
from multilingualprogramming.runtime.placement import (
    cloud,
    edge,
    get_placement,
    local,
)
from multilingualprogramming.runtime.reactive import (
    CanvasNode,
    ReactiveEngine,
    Signal,
    stream_to_view,
)
from multilingualprogramming.runtime.swarm import (
    Swarm,
    ml_delegate,
    swarm_decorator,
)

__all__ = [
    # AI
    "AIProvider",
    "AIRuntime",
    "EmbeddingVector",
    "ModelRef",
    "Plan",
    "PromptResult",
    "Reasoning",
    "StreamChunk",
    # Reactive
    "CanvasNode",
    "ReactiveEngine",
    "Signal",
    "stream_to_view",
    # Concurrency
    "Channel",
    # Observability
    "CostInfo",
    "TraceEvent",
    "ml_cost",
    "ml_explain",
    "ml_trace",
    # Placement
    "cloud",
    "edge",
    "get_placement",
    "local",
    # Memory and agents
    "MemoryStore",
    "Swarm",
    "ml_delegate",
    "ml_memory",
    "swarm_decorator",
]
