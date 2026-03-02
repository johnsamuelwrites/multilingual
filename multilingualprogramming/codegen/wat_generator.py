#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
WebAssembly Text (WAT) code generator for the multilingual programming language.

Generates valid, executable WAT (WebAssembly Text format) from the
arithmetic / loop / conditional subset of the multilingual AST.

The generated WAT can be:
  - Displayed to the user as human-readable WASM source
  - Compiled to binary .wasm via wabt/wat2wasm (browser or CLI)
  - Executed directly in any WASM runtime (browser, wasmtime, wasmer …)

Supported AST constructs:
  - VariableDeclaration / Assignment (all values are f64)
  - NumeralLiteral (decimal, Unicode script digits via MPNumeral)
  - StringLiteral  (stored in WAT linear memory data section)
  - BooleanLiteral / NoneLiteral
  - BinaryOp:  +  -  *  /  %  //  ==  !=  <  <=  >  >=
  - UnaryOp:   -  not
  - BooleanOp: and  or
  - CompareOp  (chained comparisons — first pair used)
  - IfStatement  (if / elif / else)
  - WhileLoop
  - ForLoop over range(stop) or range(start, stop)
  - FunctionDef  (f64 parameters, f64 return)
  - ReturnStatement
  - ExpressionStatement containing a print / display builtin call
  - CallExpr to user-defined functions

Unsupported constructs (classes, imports, closures …) emit WAT comments
so the output remains syntactically valid.

Host imports expected by the generated module:
  (import "env" "print_str"     (func (param i32 i32)))  ;; ptr, len
  (import "env" "print_f64"     (func (param f64)))
  (import "env" "print_bool"    (func (param i32)))
  (import "env" "print_sep"     (func))                  ;; space between args
  (import "env" "print_newline" (func))
"""
# pylint: disable=mixed-line-endings

from copy import deepcopy
import json
from pathlib import Path
import re

from multilingualprogramming.parser.ast_nodes import (
    VariableDeclaration,
    Assignment,
    ExpressionStatement,
    PassStatement,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    GlobalStatement,
    LocalStatement,
    IfStatement,
    WhileLoop,
    ForLoop,
    FunctionDef,
    ClassDef,
    TryStatement,
    WithStatement,
    MatchStatement,
    BinaryOp,
    UnaryOp,
    BooleanOp,
    CompareOp,
    CallExpr,
    Identifier,
    NumeralLiteral,
    StringLiteral,
    BooleanLiteral,
    NoneLiteral,
    ListLiteral,
    TupleLiteral,
    AttributeAccess,
    IndexAccess,
    AwaitExpr,
    LambdaExpr,
    ListComprehension,
    DictComprehension,
    SetComprehension,
    GeneratorExpr,
    Parameter,
)
from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.core.ir import CoreIRProgram


# ---------------------------------------------------------------------------
# Localised builtin name sets — built dynamically from builtins_aliases.json
# ---------------------------------------------------------------------------

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
_ABS_NAMES   = _aliases_for("abs")
_MIN_NAMES   = _aliases_for("min")
_MAX_NAMES   = _aliases_for("max")
_LEN_NAMES   = _aliases_for("len")


# ---------------------------------------------------------------------------
# Helper: extract name string from an AST name node or raw str
# ---------------------------------------------------------------------------

def _name(node) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, Identifier):
        return node.name
    if isinstance(node, AttributeAccess):
        # e.g. module.func → "module.func" for display purposes
        return f"{_name(node.obj)}.{node.attr}"
    if hasattr(node, "name"):
        return node.name
    return str(node)


# Separator pseudo-parameter names used by Python for positional-only (/)
# and keyword-only (*) boundaries — these are not real WAT parameters.
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
]


def _real_params(func_def: FunctionDef) -> list:
    """Return the real WAT parameter names for *func_def*.

    Filters out:
    - positional-only separator ``/`` and keyword-only separator ``*``
    - ``*args`` (vararg) and ``**kwargs`` (kwarg) — not representable in WAT
    """
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


# ---------------------------------------------------------------------------
# WATCodeGenerator
# ---------------------------------------------------------------------------

class WATCodeGenerator:  # pylint: disable=too-many-instance-attributes
    """
    Visitor-based WAT source code generator.

    Usage::

        gen = WATCodeGenerator()
        wat_text = gen.generate(ast_program)   # str
    """

    def __init__(self):
        # Per-generation mutable state (reset on each generate() call)
        self._instrs: list[str] = []      # current instruction lines
        self._locals: set[str] = set()    # local names in current function
        self._label_count: int = 0        # monotone counter for unique labels
        self._loop_stack: list[tuple[str, str]] = []  # (break_lbl, cont_lbl)
        self._data: bytearray = bytearray()
        self._strings: dict[str, tuple[int, int]] = {}
        self._funcs: list[str] = []
        # Names of functions compiled to WAT in this module (populated in generate())
        self._defined_func_names: set[str] = set()
        # Maps function name → ordered list of real WAT param names (separators excluded)
        self._func_real_params: dict[str, list] = {}
        # Maps function name → render mode metadata
        self._func_render_modes: dict[str, str] = {}
        # Maps class names to lowered constructor names (Class(...) -> call ctor)
        self._class_ctor_names: dict[str, str] = {}
        # Maps "Class.method" display names to lowered WAT function names.
        self._class_attr_call_names: dict[str, str] = {}
        # Best-effort local variable -> class-name tracking (for obj.method calls).
        self._var_class_types: dict[str, str] = {}
        # Source identifier -> safe WAT symbol name.
        self._wat_symbols: dict[str, str] = {}
        self._used_wat_symbols: set[str] = set()
        # OOP object model: field layout and sizes per class.
        # _class_direct_fields: own (non-inherited) fields scanned from the class body.
        # _class_field_layouts: effective (merged) layout including inherited fields.
        self._class_direct_fields: dict[str, dict[str, int]] = {}
        self._class_field_layouts: dict[str, dict[str, int]] = {}
        self._class_obj_sizes: dict[str, int] = {}
        # Name of the class currently being emitted (set in _emit_class).
        self._current_class: str | None = None
        # Inheritance: maps class_name -> [base_class_names] (strings).
        self._class_bases: dict[str, list[str]] = {}
        # String length tracking: var_name -> WAT local that holds byte length.
        self._string_len_locals: dict[str, str] = {}
        # Locals known to hold list/tuple pointers (heap-allocated).
        self._list_locals: set[str] = set()
        # True when any heap allocation (list or OOP) is needed.
        self._need_heap_ptr: bool = False

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def generate(self, program) -> str:
        """Generate a complete WAT module string from an AST node."""
        # Reset state
        self._instrs = []
        self._locals = set()
        self._label_count = 0
        self._loop_stack = []
        self._data = bytearray()
        self._strings = {}
        self._funcs = []
        self._defined_func_names = set()
        self._func_real_params = {}
        self._func_render_modes = {}
        self._class_ctor_names = {}
        self._class_attr_call_names = {}
        self._var_class_types = {}
        self._wat_symbols = {}
        self._used_wat_symbols = set()
        self._class_direct_fields = {}
        self._class_field_layouts = {}
        self._class_obj_sizes = {}
        self._current_class = None
        self._class_bases = {}
        self._string_len_locals = {}
        self._list_locals = set()
        self._need_heap_ptr = False

        if isinstance(program, CoreIRProgram):
            program = program.ast

        funcs = [s for s in program.body if isinstance(s, FunctionDef)]
        classes = [s for s in program.body if isinstance(s, ClassDef)]
        top = [s for s in program.body if not isinstance(s, (FunctionDef, ClassDef))]

        # Record which function names will actually be compiled to WAT and build
        # a map of each function's real WAT parameter names (excluding Python
        # separators '/' and bare '*', vararg *args, and **kwargs, which have no
        # direct WAT equivalent and must not appear as call arguments).
        self._defined_func_names = {_name(f.name) for f in funcs}
        for f in funcs:
            fname = _name(f.name)
            self._func_real_params[fname] = _real_params(f)
            self._func_render_modes[fname] = _extract_render_mode(f)
        self._collect_class_lowering(classes)

        for func in funcs:
            self._emit_function(func)
        for cls in classes:
            self._emit_class(cls)

        if top:
            self._emit_main(top)

        return self._build_module()

    def generate_abi_manifest(self, program) -> dict:
        """Generate ABI manifest metadata for frontend/runtime integration."""
        if isinstance(program, CoreIRProgram):
            program = program.ast

        funcs = [s for s in program.body if isinstance(s, FunctionDef)]
        top = [s for s in program.body if not isinstance(s, FunctionDef)]

        exports = []
        for func in funcs:
            params = _real_params(func)
            fname = _name(func.name)
            render_mode = _extract_render_mode(func)
            export_entry = {
                "name": fname,
                "arg_types": ["f64"] * len(params),
                "return_type": "f64",
                "mode": render_mode,
            }
            if render_mode in _STREAM_RENDER_MODES:
                output_kind = _extract_buffer_output(func)
                export_entry["stream_output"] = {
                    "kind": output_kind,
                    "count_export": f"{fname}_point_count",
                    "writer_export": f"{fname}_write_points",
                    "writer_signature": {
                        "arg_types": ["i32", "i32"],
                        "return_type": "i32",
                    },
                    "item_layout": {
                        "kind": "struct",
                        "stride_bytes": 16,
                        "fields": [
                            {"name": "x", "type": "f64", "offset_bytes": 0},
                            {"name": "y", "type": "f64", "offset_bytes": 8},
                        ],
                    },
                }
            exports.append(export_entry)

        if top:
            exports.append({
                "name": "__main",
                "arg_types": [],
                "return_type": "void",
                "mode": "scalar_field",
            })

        return {
            "abi_version": 1,
            "backend": "wat",
            "tuple_lowering": {
                "preferred": "out_params",
                "supported": ["multi_value", "out_params"],
                "out_params_memory_layout": {
                    "length_type": "i32",
                    "element_type": "f64",
                    "header_bytes": 4,
                    "element_size_bytes": 8,
                },
            },
            "exports": exports,
            "required_host_imports": deepcopy(_WAT_HOST_IMPORT_SIGNATURES),
            "memory_layout": {
                "primitive_types": {
                    "f64": {"size_bytes": 8, "alignment_bytes": 8},
                    "i32": {"size_bytes": 4, "alignment_bytes": 4},
                },
                "collections": {
                    "array<f64>": {
                        "element_type": "f64",
                        "element_size_bytes": 8,
                        "offset_formula": "base + index * 8",
                    }
                },
            },
        }

    def generate_js_host_shim(self, manifest: dict) -> str:
        """Generate a JavaScript host-import shim from an ABI manifest."""
        imports = manifest.get("required_host_imports", [])
        lines = [
            "// Auto-generated host shim from multilingual WASM ABI manifest",
            "export function createEnvHost(memoryRef = { current: null }) {",
            "  const textDecoder = new TextDecoder('utf-8');",
            "  function readUtf8(ptr, len) {",
            "    const memory = memoryRef.current;",
            "    if (!memory) return '';",
            "    const bytes = new Uint8Array(memory.buffer, ptr, len);",
            "    return textDecoder.decode(bytes);",
            "  }",
            "",
            "  return {",
            "    env: {",
        ]
        for entry in imports:
            name = entry["name"]
            if name == "print_str":
                lines.append("      print_str: (ptr, len) => { console.log(readUtf8(ptr, len)); },")
            elif name == "print_f64":
                lines.append("      print_f64: (value) => { console.log(value); },")
            elif name == "print_bool":
                lines.append("      print_bool: (value) => { console.log(Boolean(value)); },")
            elif name == "print_sep":
                lines.append("      print_sep: () => { /* spacing hook */ },")
            elif name == "print_newline":
                lines.append("      print_newline: () => { /* newline hook */ },")
            else:
                unhandled = (
                    f"      {name}: (...args) => "
                    f"{{ console.warn('Unhandled import {name}', args); }},"
                )
                lines.append(unhandled)
        lines.extend([
            "    },",
            "  };",
            "}",
        ])
        return "\n".join(lines)

    def generate_renderer_template(self, manifest: dict) -> str:
        """Generate a frontend renderer skeleton from ABI manifest metadata."""
        exports = manifest.get("exports", [])
        export_map_literal = json.dumps(
            {
                entry["name"]: {
                    "mode": entry.get("mode", "scalar_field"),
                    "stream_output": entry.get("stream_output"),
                }
                for entry in exports
            },
            indent=2,
        )
        lines = [
            "// Auto-generated renderer skeleton from multilingual WASM ABI manifest",
            "export const ABI_EXPORTS = " + export_map_literal + ";",
            "",
            "export async function loadWasmModule(url, importsFactory) {",
            "  const memoryRef = { current: null };",
            "  const imports = importsFactory(memoryRef);",
            "  const result = await WebAssembly.instantiateStreaming(fetch(url), imports);",
            "  const exports = result.instance.exports;",
            "  memoryRef.current = exports.memory || null;",
            "  return { instance: result.instance, exports, memoryRef };",
            "}",
            "",
            "export function renderByMode(ctx, abiName, exports, args = []) {",
            "  const abi = ABI_EXPORTS[abiName];",
            "  if (!abi) throw new Error(`Unknown ABI export: ${abiName}`);",
            "  if (abi.mode === 'scalar_field') {",
            "    return exports[abiName](...args);",
            "  }",
            "  if (abi.mode === 'point_stream' || abi.mode === 'polyline') {",
            "    const stream = abi.stream_output;",
            "    if (!stream) throw new Error(`Missing stream metadata for ${abiName}`);",
            "    const count = exports[stream.count_export]();",
            "    return { count, writer: stream.writer_export };",
            "  }",
            "  throw new Error(`Unsupported render mode: ${abi.mode}`);",
            "}",
        ]
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # Module assembly
    # -----------------------------------------------------------------------

    def _build_module(self) -> str:
        lines = ["(module"]
        lines += [
            '  (import "env" "print_str"     (func $print_str     (param i32 i32)))',
            '  (import "env" "print_f64"     (func $print_f64     (param f64)))',
            '  (import "env" "print_bool"    (func $print_bool    (param i32)))',
            '  (import "env" "print_sep"     (func $print_sep))',
            '  (import "env" "print_newline" (func $print_newline))',
            '  (memory (export "memory") 1)',
        ]
        if self._data:
            escaped = "".join(f"\\{b:02x}" for b in self._data)
            lines.append(f'  (data (i32.const 0) "{escaped}")')
        # Emit bump-allocator global when any stateful class or heap allocation exists.
        has_stateful = any(size > 0 for size in self._class_obj_sizes.values())
        if has_stateful or self._need_heap_ptr:
            heap_base = max((len(self._data) + 7) // 8 * 8, 64)
            lines.append(f'  (global $__heap_ptr (mut i32) (i32.const {heap_base}))')
        lines.extend(self._funcs)
        lines.append(")")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # String interning
    # -----------------------------------------------------------------------

    def _intern(self, s: str) -> tuple[int, int]:
        """Return (byte_offset, byte_length) for string in the data section."""
        if s not in self._strings:
            encoded = s.encode("utf-8")
            offset = len(self._data)
            self._data.extend(encoded)
            self._strings[s] = (offset, len(encoded))
        return self._strings[s]

    # -----------------------------------------------------------------------
    # Label generation
    # -----------------------------------------------------------------------

    def _new_label(self) -> int:
        self._label_count += 1
        return self._label_count

    def _wat_symbol(self, name: str) -> str:
        """Return a deterministic, WAT-safe symbol for a source identifier."""
        key = str(name)
        if key in self._wat_symbols:
            return self._wat_symbols[key]

        safe = re.sub(r"[^A-Za-z0-9_.$]", "_", key)
        if not safe:
            safe = "sym"
        if safe[0].isdigit():
            safe = f"n_{safe}"

        candidate = safe
        suffix = 2
        while candidate in self._used_wat_symbols:
            candidate = f"{safe}_{suffix}"
            suffix += 1

        self._used_wat_symbols.add(candidate)
        self._wat_symbols[key] = candidate
        return candidate

    # -----------------------------------------------------------------------
    # Function generation helpers
    # -----------------------------------------------------------------------

    def _gen_call_args(self, call_expr: CallExpr, indent: str, fname: str, skip_params: int = 0):
        """Push argument values for a call to a known WAT function.

        Resolves keyword arguments by matching them against the function's
        real parameter list, so calls like ``f(x, b=y)`` push the correct
        number of f64 values even when some parameters are keyword-only.
        """
        real_params = self._func_real_params.get(fname)
        if real_params:
            # Full-fidelity mapping: match each WAT param slot to its argument.
            kwargs = dict(call_expr.keywords or [])
            effective_params = real_params[skip_params:]
            for i, pname in enumerate(effective_params):
                if i < len(call_expr.args):
                    self._gen_expr(call_expr.args[i], indent)
                elif pname in kwargs:
                    self._gen_expr(kwargs[pname], indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; missing arg: {pname}")
        else:
            # Fallback: just push positional args in order.
            for arg in call_expr.args:
                self._gen_expr(arg, indent)

    def _save_func_state(self):
        saved = (self._instrs, self._locals, self._loop_stack,
                 self._var_class_types, self._current_class,
                 self._string_len_locals, self._list_locals)
        self._instrs = []
        self._locals = set()
        self._loop_stack = []
        self._var_class_types = {}
        self._string_len_locals = {}
        self._list_locals = set()
        # _current_class is NOT reset here: _emit_class sets it before each method
        # and it must persist into the method body.
        return saved

    @staticmethod
    def _mangle_class_method_name(class_name: str, method_name: str) -> str:
        return f"{class_name}__{method_name}"

    def _collect_class_lowering(self, classes: list[ClassDef]):
        """Pre-collect lowered names for class methods and constructors."""
        # Pass 1: register methods, constructors, and own (direct) field layouts.
        for cls in classes:
            class_name = _name(cls.name)
            # Collect base class names (string identifiers only; skip complex exprs).
            self._class_bases[class_name] = [
                _name(b) for b in (cls.bases or [])
                if isinstance(b, Identifier)
            ]
            for member in (cls.body or []):
                if not isinstance(member, FunctionDef):
                    continue
                method_name = _name(member.name)
                lowered = self._mangle_class_method_name(class_name, method_name)
                self._defined_func_names.add(lowered)
                self._func_real_params[lowered] = _real_params(member)
                self._func_render_modes[lowered] = _extract_render_mode(member)
                self._class_attr_call_names[f"{class_name}.{method_name}"] = lowered
                if method_name == "__init__":
                    self._class_ctor_names[class_name] = lowered
            # Store own (non-inherited) field layout for use in pass 2.
            self._class_direct_fields[class_name] = self._collect_class_fields(cls)

        # Pass 2: compute effective (inherited) field layouts and object sizes.
        for class_name in self._class_direct_fields:
            eff = self._effective_field_layout(class_name)
            self._class_field_layouts[class_name] = eff
            self._class_obj_sizes[class_name] = len(eff) * 8

        # Pass 3: inherit method name-table entries and constructors from ancestors.
        for class_name in self._class_bases:
            for ancestor in self._mro(class_name)[1:]:
                # Inherit method entries not already defined on class_name.
                for key, val in list(self._class_attr_call_names.items()):
                    if key.startswith(f"{ancestor}."):
                        method_name = key[len(ancestor) + 1:]
                        own_key = f"{class_name}.{method_name}"
                        if own_key not in self._class_attr_call_names:
                            self._class_attr_call_names[own_key] = val
                # Inherit constructor if class_name defines no __init__.
                if (class_name not in self._class_ctor_names
                        and ancestor in self._class_ctor_names):
                    self._class_ctor_names[class_name] = self._class_ctor_names[ancestor]

    def _collect_class_fields(self, class_def: ClassDef) -> dict[str, int]:
        """Scan all method bodies for self.attr = ... to build field layout.

        Returns an ordered dict {field_name: byte_offset}.  Each f64 field is
        8 bytes.  Fields are ordered by first-seen assignment.
        """
        fields: dict[str, int] = {}

        def _scan(stmts):
            for stmt in (stmts or []):
                if isinstance(stmt, Assignment):
                    t = stmt.target
                    if (isinstance(t, AttributeAccess)
                            and isinstance(t.obj, Identifier)
                            and t.obj.name == "self"
                            and t.attr not in fields):
                        fields[t.attr] = len(fields) * 8
                elif isinstance(stmt, IfStatement):
                    _scan(stmt.body)
                    for _, eb in (stmt.elif_clauses or []):
                        _scan(eb)
                    _scan(stmt.else_body)
                elif isinstance(stmt, (WhileLoop, ForLoop)):
                    _scan(stmt.body)
                elif isinstance(stmt, FunctionDef):
                    _scan(stmt.body)

        for member in (class_def.body or []):
            if isinstance(member, FunctionDef):
                _scan(member.body)
        return fields

    def _mro(self, class_name: str) -> list[str]:
        """Return the C3 linearization (MRO) for class_name (class itself first).

        Implements the C3 superclass linearization algorithm — the same used by
        CPython for all new-style classes.  Handles diamond inheritance and
        arbitrary single/multiple inheritance hierarchies.  Cycle-safe via a
        visited set passed through the recursive helper.
        """
        return self._c3_mro(class_name, frozenset())

    def _c3_mro(self, class_name: str, visiting: frozenset) -> list[str]:
        """Recursive C3 linearization step."""
        if class_name in visiting:
            return [class_name]          # cycle guard
        visiting = visiting | {class_name}
        bases = self._class_bases.get(class_name, [])
        if not bases:
            return [class_name]
        sequences = [list(self._c3_mro(b, visiting)) for b in bases] + [list(bases)]
        return [class_name] + self._c3_merge(sequences)

    @staticmethod
    def _c3_merge(sequences: list[list[str]]) -> list[str]:
        """C3 merge step: picks heads not in any tail, in order."""
        result: list[str] = []
        while True:
            sequences = [s for s in sequences if s]
            if not sequences:
                return result
            for seq in sequences:
                candidate = seq[0]
                if not any(candidate in s[1:] for s in sequences):
                    result.append(candidate)
                    for s in sequences:
                        if s and s[0] == candidate:
                            del s[0]
                    break
            else:
                # Inconsistent hierarchy — append first candidate to make progress.
                candidate = sequences[0][0]
                result.append(candidate)
                for s in sequences:
                    if s and s[0] == candidate:
                        del s[0]

    def _effective_field_layout(self, class_name: str,
                                 _visiting: set[str] | None = None) -> dict[str, int]:
        """Compute the complete field layout for class_name including all inherited fields.

        Parent fields are prepended before own fields so that inherited methods
        that reference ``self.field`` use the correct byte offsets when called on
        subclass instances.
        """
        if _visiting is None:
            _visiting = set()
        if class_name in _visiting:
            return {}
        _visiting.add(class_name)
        layout: dict[str, int] = {}
        for base in self._class_bases.get(class_name, []):
            for field in self._effective_field_layout(base, _visiting):
                if field not in layout:
                    layout[field] = len(layout) * 8
        # Append own fields in scan order (value = original offset, sort key).
        own = self._class_direct_fields.get(class_name) or {}
        for field in sorted(own, key=lambda f: own[f]):
            if field not in layout:
                layout[field] = len(layout) * 8
        return layout

    def _resolve_super_call(self, call_expr) -> str | None:
        """If call_expr is super().method(args) inside a class method, return the
        lowered WAT function name of the first ancestor that defines method.
        Returns None if the pattern does not match or no ancestor is found.
        """
        func = call_expr.func
        if not isinstance(func, AttributeAccess):
            return None
        obj = func.obj
        if not (isinstance(obj, CallExpr)
                and isinstance(obj.func, Identifier)
                and obj.func.name == "super"):
            return None
        if not self._current_class:
            return None
        method_name = _name(func.attr)
        for ancestor in self._mro(self._current_class)[1:]:
            key = f"{ancestor}.{method_name}"
            if key in self._class_attr_call_names:
                return self._class_attr_call_names[key]
        return None

    def _resolve_field(self, class_name: str, field_name: str) -> int | None:
        """Return byte offset of field_name in class_name, or None if unknown."""
        return (self._class_field_layouts.get(class_name) or {}).get(field_name)

    def _is_stateful_class(self, class_name: str) -> bool:
        """Return True if the class has at least one self.attr field."""
        return bool(self._class_obj_sizes.get(class_name, 0))

    def _restore_func_state(self, saved):
        (self._instrs, self._locals, self._loop_stack,
         self._var_class_types, self._current_class,
         self._string_len_locals, self._list_locals) = saved

    def _infer_class_name(self, expr) -> str | None:
        """Infer class name for simple object-like values tracked in WAT lowering."""
        if isinstance(expr, CallExpr):
            called_name = _name(expr.func)
            if called_name in self._class_ctor_names:
                return called_name
        if isinstance(expr, Identifier):
            return self._var_class_types.get(expr.name)
        return None

    def _class_method_target_from_call(self, call_expr: CallExpr) -> str | None:
        """Resolve obj.method(...) to lowered class method using tracked var types."""
        func = call_expr.func
        if not isinstance(func, AttributeAccess):
            return None
        obj = func.obj
        if not isinstance(obj, Identifier):
            return None
        class_name = self._var_class_types.get(obj.name)
        if not class_name:
            return None
        return self._class_attr_call_names.get(f"{class_name}.{func.attr}")

    def _emit_function(self, func_def: FunctionDef, emitted_name: str | None = None):
        """Generate WAT for a user-defined function."""
        saved = self._save_func_state()

        func_name = emitted_name or _name(func_def.name)
        # Use only the real WAT params — excludes '/', '*' separators and *args/**kwargs.
        param_names = _real_params(func_def)
        self._locals = set(param_names)

        # Generate body instructions first (populates self._locals)
        self._gen_stmts(func_def.body, "    ")
        body_instrs = list(self._instrs)
        local_names = sorted(self._locals - set(param_names))

        wat_func_name = self._wat_symbol(func_name)
        lines = [f'  (func ${wat_func_name} (export "{func_name}")']
        for pn in param_names:
            lines.append(f"    (param ${self._wat_symbol(pn)} f64)")
        lines.append("    (result f64)")
        for ln in local_names:
            lines.append(f"    (local ${self._wat_symbol(ln)} f64)")
        lines.extend(body_instrs)
        lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")

        self._funcs.append("\n".join(lines))
        if self._func_render_modes.get(func_name) in _STREAM_RENDER_MODES:
            self._funcs.append(self._build_stream_buffer_helpers(func_name))
        self._restore_func_state(saved)

    def _emit_class(self, class_def: ClassDef):
        """Lower class methods to standalone WAT functions."""
        class_name = _name(class_def.name)
        self._current_class = class_name          # set context for field-access lowering
        for member in (class_def.body or []):
            if isinstance(member, FunctionDef):
                method_name = _name(member.name)
                lowered_name = self._mangle_class_method_name(class_name, method_name)
                self._emit_function(member, emitted_name=lowered_name)
        self._current_class = None                # clear after all methods emitted

    def _emit_stateful_ctor(self, class_name: str, ctor: str,
                             call_expr, indent: str, keep_ref: bool):
        """Emit WAT for allocating a stateful object instance and calling __init__.

        Advances $__heap_ptr by the object size, then calls __init__ with the
        old heap-ptr value as self (encoded as f64).  If keep_ref is True, also
        pushes the object pointer as f64 onto the stack (expression context).
        """
        obj_size = self._class_obj_sizes[class_name]
        self._emit(f"{indent};; alloc {class_name} ({obj_size} bytes)")
        # Advance heap pointer; old value = object base address.
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}i32.const {obj_size}")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}global.set $__heap_ptr")
        # self = heap_ptr - obj_size = original base address.
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}i32.const {obj_size}")
        self._emit(f"{indent}i32.sub")
        self._emit(f"{indent}f64.convert_i32_u  ;; self ptr as f64")
        self._gen_call_args(call_expr, indent, ctor, skip_params=1)
        self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
        self._emit(f"{indent}drop  ;; discard __init__ return value")
        if keep_ref:
            # Expression context: push object reference as f64.
            self._emit(f"{indent}global.get $__heap_ptr")
            self._emit(f"{indent}i32.const {obj_size}")
            self._emit(f"{indent}i32.sub")
            self._emit(f"{indent}f64.convert_i32_u  ;; object ref as f64")

    def _build_stream_buffer_helpers(self, func_name: str) -> str:
        """Emit stream helpers that write point pairs (x, y) into linear memory."""
        lines = [
            (
                f"  (func ${self._wat_symbol(func_name + '_point_count')} "
                f"(export \"{func_name}_point_count\")"
            ),
            "    (result i32)",
            "    i32.const 256",
            "  )",
            (
                f"  (func ${self._wat_symbol(func_name + '_write_points')} "
                f"(export \"{func_name}_write_points\")"
            ),
            "    (param $ptr i32)",
            "    (param $len i32)",
            "    (result i32)",
            "    (local $i i32)",
            "    (local $count i32)",
            "    local.get $len",
            "    i32.const 256",
            "    i32.lt_s",
            "    if (result i32)",
            "      local.get $len",
            "    else",
            "      i32.const 256",
            "    end",
            "    local.set $count",
            "    i32.const 0",
            "    local.set $i",
            "    block $done",
            "      loop $lp",
            "        local.get $i",
            "        local.get $count",
            "        i32.ge_s",
            "        br_if $done",
            "        local.get $ptr",
            "        local.get $i",
            "        i32.const 16",
            "        i32.mul",
            "        i32.add",
            "        local.get $i",
            "        f64.convert_i32_s",
            "        f64.store",
            "        local.get $ptr",
            "        local.get $i",
            "        i32.const 16",
            "        i32.mul",
            "        i32.add",
            "        i32.const 8",
            "        i32.add",
            "        local.get $i",
            "        f64.convert_i32_s",
            "        f64.const 0.5",
            "        f64.mul",
            "        f64.store",
            "        local.get $i",
            "        i32.const 1",
            "        i32.add",
            "        local.set $i",
            "        br $lp",
            "      end",
            "    end",
            "    local.get $count",
            "  )",
        ]
        return "\n".join(lines)

    def _emit_main(self, stmts: list):
        """Generate the exported __main entry-point function."""
        saved = self._save_func_state()

        self._gen_stmts(stmts, "    ")
        body_instrs = list(self._instrs)
        local_names = sorted(self._locals)

        lines = ['  (func $__main (export "__main")']
        for ln in local_names:
            lines.append(f"    (local ${self._wat_symbol(ln)} f64)")
        lines.extend(body_instrs)
        lines.append("  )")

        self._funcs.append("\n".join(lines))
        self._restore_func_state(saved)

    # -----------------------------------------------------------------------
    # Augmented-assignment helper
    # -----------------------------------------------------------------------

    def _gen_augmented_op(self, op: str, rhs_node, indent: str):
        """Emit the compound-assignment arithmetic.

        Precondition : the current (old) value of the LHS is on the f64 stack.
        Postcondition: the new value is on the stack ready for ``local.set`` /
                       ``f64.store``.
        """
        if op in ("+=", "-=", "*=", "/="):
            _arith = {"+=": "f64.add", "-=": "f64.sub",
                      "*=": "f64.mul", "/=": "f64.div"}
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}{_arith[op]}")
        elif op == "//=":
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}f64.div")
            self._emit(f"{indent}f64.floor")
        elif op == "%=":
            # a %= b  →  a - floor(a/b)*b
            n = self._new_label()
            tmp_a = f"__aug_a_{n}"
            tmp_b = f"__aug_b_{n}"
            self._locals.add(tmp_a)
            self._locals.add(tmp_b)
            # old_val is on stack; tee saves it while keeping it on stack.
            self._emit(f"{indent}local.tee ${self._wat_symbol(tmp_a)}")
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}local.tee ${self._wat_symbol(tmp_b)}")
            self._emit(f"{indent}f64.div")
            self._emit(f"{indent}f64.floor")
            self._emit(f"{indent}local.get ${self._wat_symbol(tmp_b)}")
            self._emit(f"{indent}f64.mul")
            # stack: [floor(a/b)*b]  →  negate, then add a
            self._emit(f"{indent}f64.neg")
            self._emit(f"{indent}local.get ${self._wat_symbol(tmp_a)}")
            self._emit(f"{indent}f64.add  ;; a - floor(a/b)*b")
        elif op == "**=":
            self._emit(
                f"{indent};; **= not natively supported in WAT (no f64.pow)"
                f" — old value preserved"
            )
            # Old value stays on stack unchanged; rhs not evaluated.
        elif op in ("&=", "|=", "^="):
            _bitwise = {"&=": "i32.and", "|=": "i32.or", "^=": "i32.xor"}
            self._emit(f"{indent}i32.trunc_f64_s")
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}i32.trunc_f64_s")
            self._emit(f"{indent}{_bitwise[op]}")
            self._emit(f"{indent}f64.convert_i32_s")
        elif op in ("<<=", ">>="):
            _shifts = {"<<=": "i32.shl", ">>=": "i32.shr_s"}
            self._emit(f"{indent}i32.trunc_f64_s")
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}i32.trunc_f64_s")
            self._emit(f"{indent}{_shifts[op]}")
            self._emit(f"{indent}f64.convert_i32_s")
        else:
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}f64.add  ;; unknown augmented op {op!r}")

    # -----------------------------------------------------------------------
    # List / tuple allocation helper
    # -----------------------------------------------------------------------

    def _gen_list_alloc(self, node, indent: str):
        """Allocate a list or tuple literal in linear memory.

        Memory layout: ``[offset 0: length_f64, offset 8: elem0, ...]``
        Total allocation: ``(n + 1) * 8`` bytes.  Pushes the base pointer
        (as f64) onto the stack.
        """
        n = len(node.elements)
        total_bytes = (n + 1) * 8
        lbl = self._new_label()
        ptr_local = f"__list_{lbl}_ptr"
        self._locals.add(ptr_local)
        self._need_heap_ptr = True

        self._emit(f"{indent};; list/tuple literal [{n} elements]")
        # Capture old heap_ptr as f64 base address, then advance.
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.tee ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const {total_bytes}")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}global.set $__heap_ptr")
        # Store length header at base + 0.
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.const {float(n)}")
        self._emit(f"{indent}f64.store")
        # Store each element.
        for i, elem in enumerate(node.elements):
            offset = (i + 1) * 8
            self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}i32.const {offset}")
            self._emit(f"{indent}i32.add")
            self._gen_expr(elem, indent)
            self._emit(f"{indent}f64.store")
        # Push the pointer as f64.
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")

    # -----------------------------------------------------------------------
    # len() helper
    # -----------------------------------------------------------------------

    def _gen_len(self, arg_node, indent: str):
        """Emit WAT that pushes the length of a string or list variable."""
        if isinstance(arg_node, StringLiteral):
            _, byte_len = self._intern(arg_node.value)
            self._emit(f"{indent}f64.const {float(byte_len)}  ;; len of string literal")
        elif isinstance(arg_node, Identifier):
            if arg_node.name in self._string_len_locals:
                len_local = self._string_len_locals[arg_node.name]
                self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
            elif arg_node.name in self._list_locals:
                # Load element count from the list header at offset 0.
                self._emit(f"{indent}local.get ${self._wat_symbol(arg_node.name)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}f64.load  ;; list length from header")
            else:
                self._emit(
                    f"{indent}f64.const 0  "
                    f";; unsupported: len() of {arg_node.name!r} (unknown type)"
                )
        else:
            self._emit(
                f"{indent}f64.const 0  "
                f";; unsupported: len() of {type(arg_node).__name__}"
            )

    # -----------------------------------------------------------------------
    # match/case lowering helper
    # -----------------------------------------------------------------------

    def _gen_match(self, stmt: MatchStatement, indent: str):
        """Lower a match/case statement to a WAT block + nested if instructions."""
        n = self._new_label()
        subj_local = f"__match_subj_{n}"
        blk = f"__match_end_{n}"
        self._locals.add(subj_local)

        self._emit(f"{indent};; match ...")
        self._gen_expr(stmt.subject, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}block ${blk}")

        for case in stmt.cases:
            if getattr(case, "is_default", False) or case.pattern is None:
                self._emit(f"{indent}  ;; case _: (default)")
                self._gen_stmts(case.body, indent + "    ")
                self._emit(f"{indent}  br ${blk}")
            elif isinstance(case.pattern, NumeralLiteral):
                val = self._to_f64(case.pattern.value)
                self._emit(f"{indent}  ;; case {val}:")
                self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
                self._emit(f"{indent}  f64.const {val}")
                self._emit(f"{indent}  f64.eq")
                if getattr(case, "guard", None):
                    self._gen_cond(case.guard, indent + "  ")
                    self._emit(f"{indent}  i32.and")
                self._emit(f"{indent}  if")
                self._gen_stmts(case.body, indent + "    ")
                self._emit(f"{indent}    br ${blk}")
                self._emit(f"{indent}  end")
            elif isinstance(case.pattern, BooleanLiteral):
                val_i = 1 if case.pattern.value else 0
                self._emit(f"{indent}  ;; case {bool(val_i)}:")
                self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
                self._emit(f"{indent}  f64.const {float(val_i)}")
                self._emit(f"{indent}  f64.eq")
                if getattr(case, "guard", None):
                    self._gen_cond(case.guard, indent + "  ")
                    self._emit(f"{indent}  i32.and")
                self._emit(f"{indent}  if")
                self._gen_stmts(case.body, indent + "    ")
                self._emit(f"{indent}    br ${blk}")
                self._emit(f"{indent}  end")
            elif isinstance(case.pattern, StringLiteral):
                self._emit(
                    f"{indent}  ;; case {case.pattern.value!r}: "
                    f"string patterns not comparable as f64 — stub"
                )
                self._emit(
                    f"{indent}  ;; unsupported call: string_pattern_match"
                )
            else:
                self._emit(
                    f"{indent}  ;; case {type(case.pattern).__name__}: "
                    f"complex pattern not lowerable in WAT — stub"
                )

        self._emit(f"{indent}end  ;; match")

    # -----------------------------------------------------------------------
    # Statement generation
    # -----------------------------------------------------------------------

    def _emit(self, line: str):
        self._instrs.append(line)

    def _gen_stmts(self, stmts: list, indent: str):
        for stmt in stmts:
            self._gen_stmt(stmt, indent)

    def _gen_stmt(self, stmt, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        if isinstance(stmt, VariableDeclaration):
            name = _name(stmt.name)
            self._locals.add(name)
            self._emit(f"{indent};; let {name} = ...")
            self._gen_expr(stmt.value, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
            # Track string length and list pointer locals.
            if isinstance(stmt.value, StringLiteral):
                _, byte_len = self._intern(stmt.value.value)
                len_local = f"{name}_strlen"
                self._locals.add(len_local)
                self._emit(f"{indent}f64.const {float(byte_len)}  ;; strlen for {name}")
                self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
                self._string_len_locals[name] = len_local
            elif isinstance(stmt.value, (ListLiteral, TupleLiteral)):
                self._list_locals.add(name)
            inferred_class = self._infer_class_name(stmt.value)
            if inferred_class:
                self._var_class_types[name] = inferred_class
            elif name in self._var_class_types:
                del self._var_class_types[name]

        elif isinstance(stmt, Assignment):
            target = stmt.target
            if isinstance(target, Identifier):
                name = target.name
                self._locals.add(name)
                op = stmt.op
                if op == "=":
                    self._emit(f"{indent};; {name} = ...")
                    self._gen_expr(stmt.value, indent)
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                    # Track string/list types after assignment.
                    if isinstance(stmt.value, StringLiteral):
                        _, byte_len = self._intern(stmt.value.value)
                        len_local = f"{name}_strlen"
                        self._locals.add(len_local)
                        self._emit(
                            f"{indent}f64.const {float(byte_len)}  ;; strlen for {name}"
                        )
                        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
                        self._string_len_locals[name] = len_local
                    elif isinstance(stmt.value, (ListLiteral, TupleLiteral)):
                        self._list_locals.add(name)
                    inferred_class = self._infer_class_name(stmt.value)
                    if inferred_class:
                        self._var_class_types[name] = inferred_class
                    elif name in self._var_class_types:
                        del self._var_class_types[name]
                else:
                    # Compound assignment: a op= b
                    self._emit(f"{indent};; {name} {op} ...")
                    self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
                    self._gen_augmented_op(op, stmt.value, indent)
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                    if name in self._var_class_types:
                        del self._var_class_types[name]
            elif (isinstance(target, AttributeAccess)
                  and isinstance(target.obj, Identifier)):
                # obj.attr = val  (handles self.attr inside methods and
                # c.attr = val for tracked class variables)
                obj_name = target.obj.name
                attr = target.attr
                if obj_name == "self" and self._current_class:
                    cls = self._current_class
                else:
                    cls = self._var_class_types.get(obj_name)
                offset = self._resolve_field(cls, attr) if cls else None
                if offset is not None:
                    op = stmt.op
                    if op == "=":
                        self._emit(f"{indent};; {obj_name}.{attr} = ...")
                        self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                        self._emit(f"{indent}i32.trunc_f64_u")
                        self._emit(f"{indent}i32.const {offset}")
                        self._emit(f"{indent}i32.add")
                        self._gen_expr(stmt.value, indent)
                        self._emit(f"{indent}f64.store")
                    else:
                        # Compound assignment: obj.attr op= val
                        tmp = f"__attr_val_{self._new_label()}"
                        self._locals.add(tmp)
                        self._emit(f"{indent};; {obj_name}.{attr} {op} ...")
                        # Load current field value, apply op, save result.
                        self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                        self._emit(f"{indent}i32.trunc_f64_u")
                        self._emit(f"{indent}i32.const {offset}")
                        self._emit(f"{indent}i32.add")
                        self._emit(f"{indent}f64.load")
                        self._gen_augmented_op(op, stmt.value, indent)
                        self._emit(f"{indent}local.set ${self._wat_symbol(tmp)}")
                        # Store new value (recompute address).
                        self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                        self._emit(f"{indent}i32.trunc_f64_u")
                        self._emit(f"{indent}i32.const {offset}")
                        self._emit(f"{indent}i32.add")
                        self._emit(f"{indent}local.get ${self._wat_symbol(tmp)}")
                        self._emit(f"{indent}f64.store")
                else:
                    self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")
            else:
                self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")

        elif isinstance(stmt, ExpressionStatement):
            expr = stmt.expression
            if isinstance(expr, CallExpr):
                # super().method(args) — lower to direct parent WAT call (statement ctx).
                _super_wat = self._resolve_super_call(expr)
                if _super_wat is not None:
                    super_method = _name(expr.func.attr)
                    self._emit(f"{indent}local.get ${self._wat_symbol('self')}")
                    self._gen_call_args(expr, indent, _super_wat, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(_super_wat)}")
                    self._emit(
                        f"{indent}drop  ;; super().{super_method} return value discarded"
                    )
                    return
                fname = _name(expr.func)
                if fname in _PRINT_NAMES:
                    self._gen_print(expr, indent)
                elif fname in _ABS_NAMES and len(expr.args) == 1:
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}f64.abs")
                    self._emit(f"{indent}drop")
                elif fname in _MIN_NAMES and len(expr.args) >= 1:
                    # min(a, b, c, ...) → chained f64.min instructions
                    self._gen_expr(expr.args[0], indent)
                    for _extra in expr.args[1:]:
                        self._gen_expr(_extra, indent)
                        self._emit(f"{indent}f64.min")
                    self._emit(f"{indent}drop")
                elif fname in _MAX_NAMES and len(expr.args) >= 1:
                    # max(a, b, c, ...) → chained f64.max instructions
                    self._gen_expr(expr.args[0], indent)
                    for _extra in expr.args[1:]:
                        self._gen_expr(_extra, indent)
                        self._emit(f"{indent}f64.max")
                    self._emit(f"{indent}drop")
                elif fname in _LEN_NAMES and len(expr.args) == 1:
                    self._emit(f"{indent};; len(...)")
                    self._gen_len(expr.args[0], indent)
                    self._emit(f"{indent}drop")
                elif fname in self._defined_func_names:
                    # Known WAT function — emit args then call
                    self._emit(f"{indent};; call {fname}(...)")
                    self._gen_call_args(expr, indent, fname)
                    self._emit(f"{indent}call ${self._wat_symbol(fname)}")
                    self._emit(f"{indent}drop")
                elif fname in self._class_ctor_names:
                    ctor = self._class_ctor_names[fname]
                    if self._is_stateful_class(fname):
                        self._emit(f"{indent};; ctor {fname}(...) [stateful]")
                        self._emit_stateful_ctor(fname, ctor, expr, indent, keep_ref=False)
                    else:
                        self._emit(f"{indent};; ctor {fname}(...) -> {ctor}(...)")
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
                        self._gen_call_args(expr, indent, ctor, skip_params=1)
                        self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
                        self._emit(f"{indent}drop")
                elif fname in self._class_attr_call_names:
                    lowered = self._class_attr_call_names[fname]
                    self._emit(f"{indent};; class call {fname}(...)")
                    self._gen_call_args(expr, indent, lowered)
                    self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
                    self._emit(f"{indent}drop")
                elif self._class_method_target_from_call(expr):
                    lowered = self._class_method_target_from_call(expr)
                    obj_expr = expr.func.obj
                    cls = self._var_class_types.get(_name(obj_expr))
                    self._emit(f"{indent};; instance call {fname}(...)")
                    if cls and self._is_stateful_class(cls):
                        self._gen_expr(obj_expr, indent)   # push actual f64 pointer
                    else:
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
                    self._gen_call_args(expr, indent, lowered, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
                    self._emit(f"{indent}drop")
                else:
                    # Closure, constructor, builtin, or other non-WAT callable
                    self._emit(f"{indent};; unsupported call: {fname}(...) — not a WAT function")
            else:
                self._gen_expr(expr, indent)
                self._emit(f"{indent}drop")

        elif isinstance(stmt, IfStatement):
            self._gen_if(stmt, indent)

        elif isinstance(stmt, WhileLoop):
            self._gen_while(stmt, indent)

        elif isinstance(stmt, ForLoop):
            self._gen_for(stmt, indent)

        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self._gen_expr(stmt.value, indent)
            else:
                self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}return")

        elif isinstance(stmt, BreakStatement):
            if self._loop_stack:
                blk = self._loop_stack[-1][0]
                self._emit(f"{indent}br ${blk}")
            else:
                self._emit(f"{indent};; break (no enclosing loop)")

        elif isinstance(stmt, ContinueStatement):
            if self._loop_stack:
                lp = self._loop_stack[-1][1]
                self._emit(f"{indent}br ${lp}")
            else:
                self._emit(f"{indent};; continue (no enclosing loop)")

        elif isinstance(stmt, PassStatement):
            self._emit(f"{indent}nop")

        elif isinstance(stmt, (GlobalStatement, LocalStatement)):
            names = ", ".join(stmt.names)
            self._emit(f"{indent};; {type(stmt).__name__}: {names} (nop in WAT)")

        elif isinstance(stmt, TryStatement):
            # Best-effort: WASM MVP has no native exception handling.
            # Execute the try body unconditionally; skip except handlers.
            # Always execute finally (it runs regardless of exceptions in Python).
            self._emit(f"{indent};; try (best-effort: no WASM exception handling)")
            self._gen_stmts(stmt.body, indent)
            if stmt.handlers:
                self._emit(
                    f"{indent};; except handler(s) omitted "
                    f"(WAT cannot intercept exceptions)"
                )
            if stmt.else_body:
                self._emit(
                    f"{indent};; try-else omitted "
                    f"(no exception state available in WAT)"
                )
            if stmt.finally_body:
                self._emit(f"{indent};; finally")
                self._gen_stmts(stmt.finally_body, indent)

        elif isinstance(stmt, WithStatement):
            # Best-effort: lower the body; __enter__/__exit__ hooks are not
            # callable through the WAT f64 model without a vtable.
            self._emit(
                f"{indent};; with (context-manager hooks not lowerable in WAT)"
            )
            for _, alias in stmt.items:
                if alias:
                    self._locals.add(alias)
                    self._emit(
                        f"{indent}f64.const 0  "
                        f";; placeholder for 'as {alias}' binding"
                    )
                    self._emit(f"{indent}local.set ${self._wat_symbol(alias)}")
            self._gen_stmts(stmt.body, indent)

        elif isinstance(stmt, FunctionDef):
            # Nested function def — not directly supported
            self._emit(f"{indent};; nested def {_name(stmt.name)} — skipped in WAT")

        elif isinstance(stmt, MatchStatement):
            self._gen_match(stmt, indent)

        else:
            self._emit(f"{indent};; (unsupported statement: {type(stmt).__name__})")

    # -----------------------------------------------------------------------
    # Print call
    # -----------------------------------------------------------------------

    def _gen_print(self, call_expr: CallExpr, indent: str):
        self._emit(f"{indent};; print(...)")
        args = call_expr.args
        for i, arg in enumerate(args):
            if i > 0:
                self._emit(f"{indent}call $print_sep")
            if isinstance(arg, StringLiteral):
                offset, length = self._intern(arg.value)
                self._emit(f"{indent}i32.const {offset}   ;; str ptr")
                self._emit(f"{indent}i32.const {length}   ;; str len")
                self._emit(f"{indent}call $print_str")
            elif isinstance(arg, BooleanLiteral):
                self._emit(f"{indent}i32.const {1 if arg.value else 0}")
                self._emit(f"{indent}call $print_bool")
            else:
                self._gen_expr(arg, indent)
                self._emit(f"{indent}call $print_f64")
        self._emit(f"{indent}call $print_newline")

    # -----------------------------------------------------------------------
    # Expression generation  (each call pushes exactly one f64)
    # -----------------------------------------------------------------------

    def _gen_expr(self, node, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements
        if isinstance(node, NumeralLiteral):
            val = self._to_f64(node.value)
            self._emit(f"{indent}f64.const {val}")

        elif isinstance(node, BooleanLiteral):
            self._emit(f"{indent}i32.const {1 if node.value else 0}")
            self._emit(f"{indent}f64.convert_i32_s")

        elif isinstance(node, NoneLiteral):
            self._emit(f"{indent}f64.const 0")

        elif isinstance(node, StringLiteral):
            # Strings are not first-class f64 values — emit 0 as placeholder
            offset, _ = self._intern(node.value)
            self._emit(f"{indent}f64.const {float(offset)}  ;; str offset (not a numeric value)")

        elif isinstance(node, Identifier):
            if node.name in self._locals:
                self._emit(f"{indent}local.get ${self._wat_symbol(node.name)}")
            else:
                # Name not declared as a local — could be a closure, class, or
                # module-level name that WAT cannot represent; emit 0 as placeholder.
                self._emit(f"{indent}f64.const 0  ;; unresolved: {node.name}")

        elif isinstance(node, BinaryOp):
            self._gen_binop(node, indent)

        elif isinstance(node, UnaryOp):
            self._gen_unaryop(node, indent)

        elif isinstance(node, CompareOp):
            self._gen_cmp(node, indent)       # pushes i32
            self._emit(f"{indent}f64.convert_i32_s")

        elif isinstance(node, BooleanOp):
            self._gen_boolop(node, indent)    # pushes i32
            self._emit(f"{indent}f64.convert_i32_s")

        elif isinstance(node, CallExpr):
            # super().method(args) — lower to direct parent WAT call (expression ctx).
            _super_wat = self._resolve_super_call(node)
            if _super_wat is not None:
                self._emit(f"{indent}local.get ${self._wat_symbol('self')}")
                self._gen_call_args(node, indent, _super_wat, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(_super_wat)}")
                return
            fname = _name(node.func)
            if fname in _PRINT_NAMES:
                self._emit(f"{indent}f64.const 0  ;; print() used as expression")
            elif fname in _ABS_NAMES and len(node.args) == 1:
                # abs(x) → f64.abs
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.abs")
            elif fname in _MIN_NAMES and len(node.args) >= 1:
                # min(a, b, c, ...) → chained f64.min instructions
                self._gen_expr(node.args[0], indent)
                for _extra in node.args[1:]:
                    self._gen_expr(_extra, indent)
                    self._emit(f"{indent}f64.min")
            elif fname in _MAX_NAMES and len(node.args) >= 1:
                # max(a, b, c, ...) → chained f64.max instructions
                self._gen_expr(node.args[0], indent)
                for _extra in node.args[1:]:
                    self._gen_expr(_extra, indent)
                    self._emit(f"{indent}f64.max")
            elif fname in _LEN_NAMES and len(node.args) == 1:
                self._gen_len(node.args[0], indent)
            elif fname in self._defined_func_names:
                # Known WAT function — emit args then call
                self._gen_call_args(node, indent, fname)
                self._emit(f"{indent}call ${self._wat_symbol(fname)}")
            elif fname in self._class_ctor_names:
                ctor = self._class_ctor_names[fname]
                if self._is_stateful_class(fname):
                    self._emit_stateful_ctor(fname, ctor, node, indent, keep_ref=True)
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                    self._gen_call_args(node, indent, ctor, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
            elif fname in self._class_attr_call_names:
                lowered = self._class_attr_call_names[fname]
                self._gen_call_args(node, indent, lowered)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            elif self._class_method_target_from_call(node):
                lowered = self._class_method_target_from_call(node)
                obj_expr = node.func.obj
                cls = self._var_class_types.get(_name(obj_expr))
                if cls and self._is_stateful_class(cls):
                    self._gen_expr(obj_expr, indent)   # push actual f64 pointer
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                self._gen_call_args(node, indent, lowered, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            else:
                # Closure, constructor, builtin, or other non-WAT callable
                self._emit(f"{indent}f64.const 0  ;; unsupported call: {fname}(...)")

        elif isinstance(node, LambdaExpr):
            # Lift the lambda to a module-level WAT function named __lambda_N.
            # WAT has no first-class function values representable as f64, so
            # the expression pushes 0.0 as a placeholder.  The emitted WAT
            # function is callable by its mangled name from other WAT code.
            lam_id = self._new_label()
            lam_name = f"__lambda_{lam_id}"
            param_names = []
            for p in (node.params or []):
                if isinstance(p, Parameter):
                    pn = _name(p.name)
                    if pn not in _PARAM_SEPARATORS and not getattr(p, "is_vararg", False) \
                            and not getattr(p, "is_kwarg", False):
                        param_names.append(pn)
                elif isinstance(p, str) and p not in _PARAM_SEPARATORS:
                    param_names.append(p)

            saved = self._save_func_state()
            self._locals = set(param_names)
            self._gen_expr(node.body, "    ")
            body_instrs = list(self._instrs)
            local_names = sorted(self._locals - set(param_names))

            wat_lam = self._wat_symbol(lam_name)
            lines = [f'  (func ${wat_lam} (export "{lam_name}")']
            for pn in param_names:
                lines.append(f"    (param ${self._wat_symbol(pn)} f64)")
            lines.append("    (result f64)")
            for ln in local_names:
                lines.append(f"    (local ${self._wat_symbol(ln)} f64)")
            lines.extend(body_instrs)
            lines.append("  )")
            self._funcs.append("\n".join(lines))
            self._defined_func_names.add(lam_name)
            self._func_real_params[lam_name] = param_names

            self._restore_func_state(saved)
            # No f64 function-pointer representation in WAT; push 0 as placeholder.
            self._emit(
                f"{indent}f64.const 0  "
                f";; lambda lifted to ${wat_lam} (no f64 func-ptr)"
            )

        elif isinstance(node, (ListComprehension, SetComprehension,
                                DictComprehension, GeneratorExpr)):
            # WAT has no native collection types.  For the common pattern
            # [elem for x in range(n)] with a single numeric clause, lower
            # to a WAT loop that accumulates into an f64 sum-accumulator local.
            # For all other forms, push 0 as placeholder.
            clause = node.clauses[0] if node.clauses else None
            is_range_comp = (
                len(node.clauses) == 1
                and isinstance(clause.iterable, CallExpr)
                and _name(clause.iterable.func) in _RANGE_NAMES
                and not clause.conditions
                and isinstance(node, (ListComprehension, GeneratorExpr))
            )
            if is_range_comp:
                # Emit a loop that computes a running sum of the element expression.
                # This is correct for `sum([f(x) for x in range(n)])` patterns
                # when the surrounding call is stripped by Python-side reduction.
                # Without a sum wrapper the result is just the last element value.
                n = self._new_label()
                iter_var_raw = (
                    _name(clause.target)
                    if isinstance(clause.target, Identifier) else f"__ci_{n}"
                )
                iter_var = iter_var_raw
                self._locals.add(iter_var)
                acc_var = f"__cacc_{n}"
                re_var = f"__cre_{n}"
                self._locals.add(acc_var)
                self._locals.add(re_var)
                blk = f"comp_blk_{n}"
                lp = f"comp_lp_{n}"

                itbl = clause.iterable
                if len(itbl.args) == 1:
                    range_start_node = NumeralLiteral("0")
                    range_end_node = itbl.args[0]
                else:
                    range_start_node = itbl.args[0]
                    range_end_node = itbl.args[1]

                self._emit(
                    f"{indent};; listcomp over range — "
                    f"accumulates element values (last value if no sum wrapper)"
                )
                self._gen_expr(range_start_node, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
                self._gen_expr(range_end_node, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(re_var)}")
                self._emit(f"{indent}f64.const 0")
                self._emit(f"{indent}local.set ${self._wat_symbol(acc_var)}")
                self._emit(f"{indent}block ${blk}")
                self._emit(f"{indent}  loop ${lp}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(re_var)}")
                self._emit(f"{indent}    f64.ge")
                self._emit(f"{indent}    br_if ${blk}")
                self._gen_expr(node.element, indent + "    ")
                self._emit(f"{indent}    local.set ${self._wat_symbol(acc_var)}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
                self._emit(f"{indent}    f64.const 1")
                self._emit(f"{indent}    f64.add")
                self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
                self._emit(f"{indent}    br ${lp}")
                self._emit(f"{indent}  end  ;; comp loop")
                self._emit(f"{indent}end  ;; comp block")
                self._emit(f"{indent}local.get ${self._wat_symbol(acc_var)}")
            else:
                self._emit(
                    f"{indent}f64.const 0  "
                    f";; unsupported expr: {type(node).__name__} "
                    f"(collections not representable as f64)"
                )

        elif (isinstance(node, AttributeAccess)
              and isinstance(node.obj, Identifier)):
            # self.attr or known_var.attr — lower to f64.load from object memory.
            obj_name = node.obj.name
            if obj_name == "self" and self._current_class:
                cls = self._current_class
            else:
                cls = self._var_class_types.get(obj_name)
            offset = self._resolve_field(cls, node.attr) if cls else None
            if offset is not None:
                self._emit(f"{indent};; load {obj_name}.{node.attr}")
                self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const {offset}")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}f64.load")
            else:
                self._emit(
                    f"{indent}f64.const 0  ;; unsupported expr: "
                    f"AttributeAccess {obj_name}.{node.attr}"
                )

        elif isinstance(node, (ListLiteral, TupleLiteral)):
            self._gen_list_alloc(node, indent)

        elif isinstance(node, IndexAccess):
            obj = node.obj
            if isinstance(obj, Identifier) and obj.name in self._list_locals:
                # list[i] / tuple[i]  →  load from base + 8 + i*8
                self._emit(f"{indent};; {obj.name}[i]")
                self._emit(f"{indent}local.get ${self._wat_symbol(obj.name)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._gen_expr(node.index, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const 8")
                self._emit(f"{indent}i32.mul")
                self._emit(f"{indent}i32.const 8  ;; skip length header")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}f64.load")
            else:
                self._emit(
                    f"{indent}f64.const 0  ;; unsupported: IndexAccess on non-list"
                )

        elif isinstance(node, AwaitExpr):
            # WAT has no async runtime — evaluate the awaited value synchronously.
            self._gen_expr(node.value, indent)

        else:
            self._emit(f"{indent}f64.const 0  ;; unsupported expr: {type(node).__name__}")

    # -----------------------------------------------------------------------
    # Condition generation (pushes i32: 0 or 1)
    # -----------------------------------------------------------------------

    def _gen_cond(self, node, indent: str):
        if isinstance(node, CompareOp):
            self._gen_cmp(node, indent)
        elif isinstance(node, BooleanOp):
            self._gen_boolop(node, indent)
        elif isinstance(node, UnaryOp) and node.op in ("NOT", "not"):
            self._gen_cond(node.operand, indent)
            self._emit(f"{indent}i32.eqz")
        elif isinstance(node, BooleanLiteral):
            self._emit(f"{indent}i32.const {1 if node.value else 0}")
        elif isinstance(node, BinaryOp) and node.op in (
            "==", "!=", "<", "<=", ">", ">="
        ):
            self._gen_cmp_from_binop(node, indent)
        else:
            # Treat f64 != 0 as truthy
            self._gen_expr(node, indent)
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}f64.ne")

    def _gen_cmp(self, node: CompareOp, indent: str):
        """Push i32 comparison result for a CompareOp node."""
        if not node.comparators:
            self._emit(f"{indent}i32.const 1")
            return
        op, right = node.comparators[0]
        self._gen_expr(node.left, indent)
        self._gen_expr(right, indent)
        _cmp_wat = {
            "==": "f64.eq", "!=": "f64.ne",
            "<":  "f64.lt", "<=": "f64.le",
            ">":  "f64.gt", ">=": "f64.ge",
            "is": "f64.eq", "is not": "f64.ne",
        }
        self._emit(f"{indent}{_cmp_wat.get(op, 'f64.eq')}")

    def _gen_cmp_from_binop(self, node: BinaryOp, indent: str):
        """Push i32 for a BinaryOp that is a comparison operator."""
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        _cmp_wat = {
            "==": "f64.eq", "!=": "f64.ne",
            "<":  "f64.lt", "<=": "f64.le",
            ">":  "f64.gt", ">=": "f64.ge",
        }
        self._emit(f"{indent}{_cmp_wat[node.op]}")

    def _gen_boolop(self, node: BooleanOp, indent: str):
        """Push i32 for AND / OR across all values."""
        for v in node.values:
            self._gen_cond(v, indent)
        op_instr = "i32.and" if node.op in ("AND", "and") else "i32.or"
        for _ in range(len(node.values) - 1):
            self._emit(f"{indent}{op_instr}")

    # -----------------------------------------------------------------------
    # Binary / unary expression helpers
    # -----------------------------------------------------------------------

    def _gen_binop(self, node: BinaryOp, indent: str):  # noqa: C901
        op = node.op

        # Comparison operators -> i32, then convert to f64
        if op in ("==", "!=", "<", "<=", ">", ">="):
            self._gen_cmp_from_binop(node, indent)
            self._emit(f"{indent}f64.convert_i32_s")
            return

        if op == "%":
            # Python-style modulo: a - floor(a/b)*b
            if isinstance(node.left, Identifier):
                # Hot-kernel optimization: avoid evaluating left expression twice.
                tmp_name = f"__mod_left_{self._new_label()}"
                self._locals.add(tmp_name)
                self._gen_expr(node.left, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(tmp_name)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(tmp_name)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(tmp_name)}")
                self._gen_expr(node.right, indent)
                self._emit(f"{indent}f64.div")
                self._emit(f"{indent}f64.floor")
                self._gen_expr(node.right, indent)
                self._emit(f"{indent}f64.mul")
                self._emit(f"{indent}f64.sub")
                return
            self._emit(f"{indent};; f64 modulo")
            self._gen_expr(node.left, indent)   # a
            self._gen_expr(node.left, indent)   # a  (again)
            self._gen_expr(node.right, indent)  # b
            self._emit(f"{indent}f64.div")      # a/b
            self._emit(f"{indent}f64.floor")    # floor(a/b)
            self._gen_expr(node.right, indent)  # b
            self._emit(f"{indent}f64.mul")      # floor(a/b)*b
            self._emit(f"{indent}f64.sub")      # a - floor(a/b)*b
            return

        if op == "//":
            self._gen_expr(node.left, indent)
            self._gen_expr(node.right, indent)
            self._emit(f"{indent}f64.div")
            self._emit(f"{indent}f64.floor")
            return

        if op == "**":
            # No native pow in WASM f64 - emit approximation note
            self._emit(f"{indent};; ** (power) not natively supported in WASM f64")
            self._gen_expr(node.left, indent)
            return

        _arith = {"+": "f64.add", "-": "f64.sub", "*": "f64.mul", "/": "f64.div"}
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}{_arith.get(op, 'f64.add')}  ;; op={op!r}")

    def _gen_unaryop(self, node: UnaryOp, indent: str):
        if node.op == "-":
            self._gen_expr(node.operand, indent)
            self._emit(f"{indent}f64.neg")
        elif node.op in ("NOT", "not"):
            self._gen_cond(node.operand, indent)
            self._emit(f"{indent}i32.eqz")
            self._emit(f"{indent}f64.convert_i32_s")
        elif node.op == "+":
            self._gen_expr(node.operand, indent)
        else:
            self._gen_expr(node.operand, indent)

    # -----------------------------------------------------------------------
    # Compound statement generation
    # -----------------------------------------------------------------------

    def _gen_if(self, stmt: IfStatement, indent: str):
        self._emit(f"{indent};; if ...")
        self._gen_cond(stmt.condition, indent)
        self._emit(f"{indent}if")
        self._gen_stmts(stmt.body, indent + "  ")

        elif_clauses = stmt.elif_clauses
        else_body = stmt.else_body

        if elif_clauses or else_body:
            self._emit(f"{indent}else")
            if elif_clauses:
                # Emit first elif as nested if/else
                elif_cond, elif_body = elif_clauses[0]
                self._emit(f"{indent}  ;; elif ...")
                self._gen_cond(elif_cond, indent + "  ")
                self._emit(f"{indent}  if")
                self._gen_stmts(elif_body, indent + "    ")
                rest = elif_clauses[1:]
                if rest or else_body:
                    self._emit(f"{indent}  else")
                    if rest:
                        # Further elif nesting (one more level)
                        ec2, eb2 = rest[0]
                        self._emit(f"{indent}    ;; elif (inner) ...")
                        self._gen_cond(ec2, indent + "    ")
                        self._emit(f"{indent}    if")
                        self._gen_stmts(eb2, indent + "      ")
                        if else_body:
                            self._emit(f"{indent}    else")
                            self._gen_stmts(else_body, indent + "      ")
                        self._emit(f"{indent}    end")
                    elif else_body:
                        self._gen_stmts(else_body, indent + "    ")
                self._emit(f"{indent}  end")
            elif else_body:
                self._gen_stmts(else_body, indent + "  ")

        self._emit(f"{indent}end  ;; if")

    def _gen_while(self, stmt: WhileLoop, indent: str):
        n = self._new_label()
        blk = f"while_blk_{n}"
        lp = f"while_lp_{n}"
        self._loop_stack.append((blk, lp))

        self._emit(f"{indent};; while ...")
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._gen_cond(stmt.condition, indent + "    ")
        self._emit(f"{indent}    i32.eqz")
        self._emit(f"{indent}    br_if ${blk}")
        self._gen_stmts(stmt.body, indent + "    ")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end  ;; loop")
        self._emit(f"{indent}end  ;; block (while)")

        self._loop_stack.pop()

    def _gen_for(self, stmt: ForLoop, indent: str):
        n = self._new_label()
        blk = f"for_blk_{n}"
        lp = f"for_lp_{n}"
        range_end_local = f"__re{n}"      # holds range end
        self._loop_stack.append((blk, lp))
        self._locals.add(range_end_local)

        # Determine iterator variable name
        target = stmt.target
        if isinstance(target, Identifier):
            iter_var = target.name
        elif isinstance(target, str):
            iter_var = target
        else:
            iter_var = "__for_i"
        self._locals.add(iter_var)

        # Decode range() call
        iterable = stmt.iterable
        range_start = NumeralLiteral("0")
        range_end = None

        if isinstance(iterable, CallExpr):
            fname = _name(iterable.func)
            if fname in _RANGE_NAMES:
                if len(iterable.args) == 1:
                    range_start = NumeralLiteral("0")
                    range_end = iterable.args[0]
                elif len(iterable.args) >= 2:
                    range_start = iterable.args[0]
                    range_end = iterable.args[1]

        if range_end is not None:
            self._emit(f"{indent};; for {iter_var} in range(...)")
            self._gen_expr(range_start, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
            self._gen_expr(range_end, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(range_end_local)}")

            self._emit(f"{indent}block ${blk}")
            self._emit(f"{indent}  loop ${lp}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(range_end_local)}")
            self._emit(f"{indent}    f64.ge")
            self._emit(f"{indent}    br_if ${blk}")
            self._gen_stmts(stmt.body, indent + "    ")
            self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    f64.const 1")
            self._emit(f"{indent}    f64.add")
            self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    br ${lp}")
            self._emit(f"{indent}  end  ;; loop")
            self._emit(f"{indent}end  ;; block (for)")
        else:
            self._emit(f"{indent};; for loop over non-range iterable — not supported in WAT")

        self._loop_stack.pop()

    # -----------------------------------------------------------------------
    # Numeric helpers
    # -----------------------------------------------------------------------

    def _to_f64(self, raw) -> str:
        """Convert a raw numeral value to a WAT f64 literal string."""
        try:
            val = MPNumeral(str(raw)).to_decimal()
            return str(float(val))
        except Exception:
            pass
        try:
            return str(float(raw))
        except (ValueError, TypeError):
            return "0.0"


# ---------------------------------------------------------------------------
# Module-level utility
# ---------------------------------------------------------------------------

_STUB_MARKER = ";; unsupported call:"


def has_stub_calls(wat_text: str) -> bool:
    """Return True if *wat_text* contains any unsupported-call stub lines.

    A WAT module that contains stub lines (emitted for constructs the generator
    cannot lower — closures, constructors, cross-module attribute calls, etc.)
    will produce incorrect numeric results at runtime even if every function is
    properly exported.  Use this check to distinguish a fully-functional export
    from a stub-containing one:

    Example::

        gen = WATCodeGenerator()
        wat = gen.generate(core_program)
        if has_stub_calls(wat):
            print("WARNING: generated WAT contains unsupported-call stubs")
        else:
            print("WAT module is fully functional")
    """
    return _STUB_MARKER in wat_text
