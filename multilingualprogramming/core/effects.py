#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 capability and effect model scaffolding."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Effect:
    """Named capability used by a semantic construct."""

    name: str


@dataclass(frozen=True)
class EffectSet:
    """Collection of capabilities attached to a node or declaration."""

    effects: tuple[Effect, ...] = field(default_factory=tuple)

    def names(self) -> tuple[str, ...]:
        """Return effect names in declaration order."""
        return tuple(effect.name for effect in self.effects)
