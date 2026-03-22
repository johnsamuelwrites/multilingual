#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multi-agent swarm coordination runtime for Multilingual.

Provides the Python-backend implementations of:

    @swarm(agents=[...])     — declare a coordinator over a pool of agents
    delegate(agent, message) — send a message to an agent and get a future

A Swarm is a coordinator that can fan-out tasks to named sub-agents,
collect results, and synthesise a final response.  On the Python backend
the sub-agents are async callables and delegation uses asyncio.

Usage (from transpiled Python)
-------------------------------
    from multilingualprogramming.runtime.swarm import Swarm, ml_delegate

    # Define sub-agents as async callables
    async def researcher(q): ...
    async def writer(q): ...

    coordinator = Swarm(name="team", agents={"researcher": researcher,
                                              "writer": writer})

    # Inside an async context:
    result = await ml_delegate(coordinator, "researcher", "What is AI?")
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable


class Swarm:
    """A named pool of specialised sub-agents.

    Parameters
    ----------
    name:
        Display name for this swarm.
    agents:
        Mapping of agent name → async callable.
    """

    def __init__(
        self,
        name: str,
        agents: dict[str, Callable] | None = None,
    ) -> None:
        self.name = name
        self._agents: dict[str, Callable] = agents or {}

    def register(self, name: str, agent: Callable) -> None:
        """Register a sub-agent under *name*."""
        self._agents[name] = agent

    async def delegate(self, agent_name: str, message: Any) -> Any:
        """Delegate *message* to the named sub-agent and return its result."""
        agent = self._agents.get(agent_name)
        if agent is None:
            raise KeyError(
                f"Swarm {self.name!r} has no agent named {agent_name!r}. "
                f"Available: {sorted(self._agents)}"
            )
        if asyncio.iscoroutinefunction(agent):
            return await agent(message)
        return agent(message)

    async def broadcast(self, message: Any) -> dict[str, Any]:
        """Broadcast *message* to all sub-agents and collect results."""
        tasks = {
            name: asyncio.create_task(self.delegate(name, message))
            for name in self._agents
        }
        results = {}
        for name, task in tasks.items():
            results[name] = await task
        return results

    def __repr__(self) -> str:
        return f"Swarm({self.name!r}, agents={sorted(self._agents)!r})"


async def ml_delegate(swarm_or_agent: Any, *args: Any) -> Any:
    """Delegate a task.

    Supports two call patterns:

    * ``ml_delegate(swarm, agent_name, message)`` — route through a Swarm
    * ``ml_delegate(agent_callable, message)``     — call directly
    """
    if isinstance(swarm_or_agent, Swarm):
        if len(args) < 2:
            raise TypeError("ml_delegate(swarm, agent_name, message) requires 3 arguments")
        agent_name, message = args[0], args[1]
        return await swarm_or_agent.delegate(agent_name, message)

    # Direct callable delegation
    agent = swarm_or_agent
    message = args[0] if args else None
    if asyncio.iscoroutinefunction(agent):
        return await agent(message)
    return agent(message)


def swarm_decorator(agents: list | None = None, **kwargs) -> Callable:
    """``@swarm(agents=[...])`` decorator factory.

    Wraps a coordinator function and attaches a Swarm instance that maps
    agent names to their callables.  The agents list may contain callables
    directly (their ``__name__`` is used as the key).
    """
    def decorator(fn: Callable) -> Callable:
        agent_map: dict[str, Callable] = {}
        for agent in (agents or []):
            if callable(agent):
                agent_map[agent.__name__] = agent
            elif isinstance(agent, tuple) and len(agent) == 2:
                agent_map[agent[0]] = agent[1]
        sw = Swarm(name=fn.__name__, agents=agent_map)
        fn.__ml_swarm__ = sw  # type: ignore[attr-defined]
        return fn

    return decorator
