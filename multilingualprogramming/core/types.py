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


@dataclass(frozen=True)
class FunctionType(CoreType):
    """Callable type: (param_types) -> return_type uses effects."""

    param_types: tuple[CoreType, ...] = field(default_factory=tuple)
    return_type: CoreType | None = None
    effects: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VectorType(CoreType):
    """Dense vector type used for embeddings: vector<element_type>.

    dimensions=0 means unspecified (runtime-determined).
    """

    element_type: CoreType | None = None
    dimensions: int = 0


# ---------------------------------------------------------------------------
# Built-in type singletons
#
# These cover all Core 1.0 primitive types plus the most common generics.
# Use these constants everywhere rather than constructing NamedType("int")
# inline, so that type identity comparisons work reliably.
# ---------------------------------------------------------------------------

NONE_TYPE = NamedType("none")
BOOL_TYPE = NamedType("bool")
INT_TYPE = NamedType("int")
FLOAT_TYPE = NamedType("float")
DECIMAL_TYPE = NamedType("decimal")
STRING_TYPE = NamedType("string")
BYTES_TYPE = NamedType("bytes")
RANGE_TYPE = NamedType("range")
MODEL_TYPE = NamedType("model")
SIGNAL_TYPE = NamedType("signal")
IMAGE_TYPE = NamedType("image")
AUDIO_TYPE = NamedType("audio")
VIDEO_TYPE = NamedType("video")
DOCUMENT_TYPE = NamedType("document")
EMBEDDING_TYPE = NamedType("embedding")
PROMPT_TYPE = NamedType("prompt")
TOOL_TYPE = NamedType("tool")
RESOURCE_TYPE = NamedType("resource")

# Generic shorthands
OPTION_INT = GenericType("option", parameters=(INT_TYPE,))
OPTION_STR = GenericType("option", parameters=(STRING_TYPE,))
RESULT_STR_STR = GenericType("result", parameters=(STRING_TYPE, STRING_TYPE))
LIST_STR = GenericType("list", parameters=(STRING_TYPE,))
STREAM_STR = GenericType("stream", parameters=(STRING_TYPE,))
VECTOR_FLOAT = VectorType("vector", element_type=FLOAT_TYPE)
