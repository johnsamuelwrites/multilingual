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
_INT_NAMES = _aliases_for("int")
_POW_NAMES = _aliases_for("pow")
_SUM_NAMES = _aliases_for("sum")
_LIST_NAMES = _aliases_for("list")
_TUPLE_NAMES = _aliases_for("tuple")
_SET_NAMES = _aliases_for("set")
_STR_NAMES = _aliases_for("str")
_ZIP_NAMES = _aliases_for("zip")
_INPUT_NAMES = _aliases_for("input")
_ARGC_NAMES = _aliases_for("argc")
_ARGV_NAMES = _aliases_for("argv")

# DOM bridge builtins — map canonical name → WAT host import name
_DOM_BUILTINS: dict[str, str] = {
    "dom_get":     "ml_dom_get",      # (id_ptr, id_len) -> f64 handle
    "dom_text":    "ml_dom_set_text", # (handle, ptr, len)
    "dom_html":    "ml_dom_set_html", # (handle, ptr, len)
    "dom_value":   "ml_dom_get_value",# (handle, buf_ptr, buf_len) -> i32 bytes_written
    "dom_attr":    "ml_dom_set_attr", # (handle, name_ptr, name_len, val_ptr, val_len)
    "dom_create":  "ml_dom_create",   # (tag_ptr, tag_len) -> f64 handle
    "dom_append":  "ml_dom_append",   # (parent_handle, child_handle)
    "dom_style":   "ml_dom_style",    # (handle, prop_ptr, prop_len, val_ptr, val_len)
    "dom_remove":  "ml_dom_remove",   # (handle)
    "dom_class":   "ml_dom_set_class",# (handle, cls_ptr, cls_len)
}

# WAT signatures for each DOM host import (param types, return type)
_DOM_HOST_SIGNATURES: dict[str, tuple[list[str], str]] = {
    "ml_dom_get":       (["i32", "i32"],                    "f64"),
    "ml_dom_set_text":  (["f64", "i32", "i32"],             ""),
    "ml_dom_set_html":  (["f64", "i32", "i32"],             ""),
    "ml_dom_get_value": (["f64", "i32", "i32"],             "i32"),
    "ml_dom_set_attr":  (["f64", "i32", "i32", "i32", "i32"], ""),
    "ml_dom_create":    (["i32", "i32"],                    "f64"),
    "ml_dom_append":    (["f64", "f64"],                    ""),
    "ml_dom_style":     (["f64", "i32", "i32", "i32", "i32"], ""),
    "ml_dom_remove":    (["f64"],                           ""),
    "ml_dom_set_class": (["f64", "i32", "i32"],             ""),
}

_DOM_CANONICAL_NAMES: frozenset = frozenset(_DOM_BUILTINS.keys())

# Caller-facing parameter kinds for each DOM builtin ("str" = ptr+len pair, "f64" = handle).
# "ret_str" = returns string (f64 ptr, length in $__last_str_len).
_DOM_CALLER_PARAMS: dict[str, list[str]] = {
    "dom_get":    ["str"],
    "dom_text":   ["f64", "str"],
    "dom_html":   ["f64", "str"],
    "dom_value":  ["f64"],
    "dom_attr":   ["f64", "str", "str"],
    "dom_create": ["str"],
    "dom_append": ["f64", "f64"],
    "dom_style":  ["f64", "str", "str"],
    "dom_remove": ["f64"],
    "dom_class":  ["f64", "str"],
}
_DOM_CALLER_RETURNS: dict[str, str] = {
    "dom_get":    "f64",
    "dom_text":   "",
    "dom_html":   "",
    "dom_value":  "ret_str",
    "dom_attr":   "",
    "dom_create": "f64",
    "dom_append": "",
    "dom_style":  "",
    "dom_remove": "",
    "dom_class":  "",
}


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

# All I/O and math helpers (print_*, pow_f64) are now implemented as internal
# WAT functions backed by WASI syscalls.  The generated module requires:
#   fd_write — stdout (always)
#   fd_read  — stdin / input() builtin
_WAT_HOST_IMPORT_SIGNATURES = [
    {
        "module": "wasi_snapshot_preview1",
        "name": "fd_write",
        "param_types": ["i32", "i32", "i32", "i32"],
        "return_type": "i32",
    },
    {
        "module": "wasi_snapshot_preview1",
        "name": "fd_read",
        "param_types": ["i32", "i32", "i32", "i32"],
        "return_type": "i32",
    },
    {
        "module": "wasi_snapshot_preview1",
        "name": "args_sizes_get",
        "param_types": ["i32", "i32"],
        "return_type": "i32",
    },
    {
        "module": "wasi_snapshot_preview1",
        "name": "args_get",
        "param_types": ["i32", "i32"],
        "return_type": "i32",
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


def _has_decorator(func_def: FunctionDef, names) -> bool:
    """Return True if *func_def* has any decorator whose name is in *names*."""
    if isinstance(names, str):
        names = (names,)
    names = frozenset(names)
    for decorator in (func_def.decorators or []):
        if _name(decorator) in names:
            return True
    return False


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
