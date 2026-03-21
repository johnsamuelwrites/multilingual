#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Semantic IR node scaffolding for Multilingual Core 1.0."""

from dataclasses import dataclass, field

from multilingualprogramming.core.effects import EffectSet
from multilingualprogramming.core.types import CoreType


@dataclass
class IRNode:
    """Base semantic IR node."""

    line: int = 0
    column: int = 0


@dataclass
class IRProgram(IRNode):
    """Semantic root node."""

    body: list[IRNode] = field(default_factory=list)
    source_language: str = "en"
    effects: EffectSet = field(default_factory=EffectSet)


@dataclass
class IRBinding(IRNode):
    """Binding node with explicit mutability."""

    name: str = ""
    value: IRNode | None = None
    is_mutable: bool = False
    annotation: CoreType | None = None


@dataclass
class IRFunction(IRNode):
    """Semantic function declaration."""

    name: str = ""
    parameters: list[str] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    return_type: CoreType | None = None
    effects: EffectSet = field(default_factory=EffectSet)
    is_async: bool = False
    syntax_keyword: str = "fn"


@dataclass
class IRTypeDecl(IRNode):
    """Type declaration node."""

    name: str = ""
    declared_type: CoreType | None = None


@dataclass
class IRExpression(IRNode):
    """Placeholder expression node."""

    inferred_type: CoreType | None = None
