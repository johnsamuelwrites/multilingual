#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 type model scaffolding."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CoreType:
    """Base type for Core 1.0 semantic types."""

    name: str


@dataclass(frozen=True)
class NamedType(CoreType):
    """Named primitive or declared type."""


@dataclass(frozen=True)
class GenericType(CoreType):
    """Generic type such as list<T> or result<T, E>."""

    parameters: tuple[CoreType, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RecordField:
    """Named field in a record type."""

    name: str
    field_type: CoreType


@dataclass(frozen=True)
class RecordType(CoreType):
    """Structured record type."""

    fields: tuple[RecordField, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UnionVariant:
    """Single tagged-union variant."""

    name: str
    payload: RecordType | None = None


@dataclass(frozen=True)
class UnionType(CoreType):
    """Tagged union type."""

    variants: tuple[UnionVariant, ...] = field(default_factory=tuple)
