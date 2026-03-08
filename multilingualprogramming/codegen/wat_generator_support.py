#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Shared support helpers for the WAT generator."""

import json
from pathlib import Path

from multilingualprogramming.parser.ast_nodes import (
    AttributeAccess,
    CallExpr,
    FunctionDef,
    Identifier,
    StringLiteral,
)


_BUILTINS_ALIASES_PATH = (
    Path(__file__).parent.parent / "resources" / "usm" / "builtins_aliases.json"
)
with _BUILTINS_ALIASES_PATH.open(encoding="utf-8") as _f:
    _BUILTINS_ALIASES: dict = json.load(_f)["aliases"]


def _aliases_for(canonical: str) -> frozenset:
    """Return {canonical} plus every localized alias from builtins_aliases.json."""
    names = {canonical}
    for lang_aliases in _BUILTINS_ALIASES.get(canonical, {}).values():
        names.update(lang_aliases)
    return frozenset(names)


_PRINT_NAMES = _aliases_for("print")
_RANGE_NAMES = _aliases_for("range")
_ABS_NAMES = _aliases_for("abs")
_MIN_NAMES = _aliases_for("min")
_MAX_NAMES = _aliases_for("max")
_LEN_NAMES = _aliases_for("len")


def _name(node) -> str:
    """Extract a readable name from an AST name-like node."""
    if isinstance(node, str):
        return node
    if isinstance(node, Identifier):
        return node.name
    if isinstance(node, AttributeAccess):
        return f"{_name(node.obj)}.{node.attr}"
    if hasattr(node, "name"):
        return node.name
    return str(node)


_PARAM_SEPARATORS = frozenset(("/", "*"))

_RENDER_MODE_DECORATOR_NAMES = frozenset({"render_mode", "mode_rendu"})
_SUPPORTED_RENDER_MODES = frozenset({"scalar_field", "point_stream", "polyline"})
_STREAM_RENDER_MODES = frozenset({"point_stream", "polyline"})
_BUFFER_OUTPUT_DECORATOR_NAMES = frozenset({"buffer_output", "sortie_tampon"})

_WAT_HOST_IMPORT_SIGNATURES = [
    {
        "module": "env",
        "name": "print_str",
        "param_types": ["i32", "i32"],
        "return_type": "void",
    },
    {
        "module": "env",
        "name": "print_f64",
        "param_types": ["f64"],
        "return_type": "void",
    },
    {
        "module": "env",
        "name": "print_bool",
        "param_types": ["i32"],
        "return_type": "void",
    },
    {
        "module": "env",
        "name": "print_sep",
        "param_types": [],
        "return_type": "void",
    },
    {
        "module": "env",
        "name": "print_newline",
        "param_types": [],
        "return_type": "void",
    },
    {
        "module": "env",
        "name": "pow_f64",
        "param_types": ["f64", "f64"],
        "return_type": "f64",
    },
]


def _real_params(func_def: FunctionDef) -> list:
    """Return the real WAT parameter names for *func_def*."""
    result = []
    for p in (func_def.params or []):
        pname = _name(p.name)
        if pname in _PARAM_SEPARATORS:
            continue
        if getattr(p, "is_vararg", False) or getattr(p, "is_kwarg", False):
            continue
        result.append(pname)
    return result


def _extract_render_mode(func_def: FunctionDef) -> str:
    """Extract @render_mode("...") metadata from function decorators."""
    for decorator in (func_def.decorators or []):
        if not isinstance(decorator, CallExpr):
            continue
        if _name(decorator.func) not in _RENDER_MODE_DECORATOR_NAMES:
            continue
        if not decorator.args:
            continue
        first_arg = decorator.args[0]
        if not isinstance(first_arg, StringLiteral):
            continue
        mode = first_arg.value.strip()
        if mode in _SUPPORTED_RENDER_MODES:
            return mode
    return "scalar_field"


def _extract_buffer_output(func_def: FunctionDef) -> str:
    """Extract @buffer_output("...") metadata; defaults to 'points'."""
    for decorator in (func_def.decorators or []):
        if not isinstance(decorator, CallExpr):
            continue
        if _name(decorator.func) not in _BUFFER_OUTPUT_DECORATOR_NAMES:
            continue
        if not decorator.args:
            continue
        first_arg = decorator.args[0]
        if not isinstance(first_arg, StringLiteral):
            continue
        output_kind = first_arg.value.strip()
        if output_kind:
            return output_kind
    return "points"
