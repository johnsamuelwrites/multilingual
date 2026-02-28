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
    AttributeAccess,
)
from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.core.ir import CoreIRProgram


# ---------------------------------------------------------------------------
# Localised builtin name sets
# ---------------------------------------------------------------------------

_PRINT_NAMES = frozenset({
    # English
    "print",
    # Romance / Germanic / Slavic
    "afficher", "imprimir", "ausgeben", "stampa", "imprima",
    "drukuj", "afdrukken", "skriv", "tulosta",
    # Indic / Semitic / East Asian
    "छापो", "اطبع", "ছাপাও", "அச்சிடு", "打印", "表示",
})

_RANGE_NAMES = frozenset({
    "range",
    "intervalle", "rango", "bereich", "intervallo", "intervalo",
    "zakres", "bereik", "intervall", "interval", "vali",
    "परास", "مدى", "পরিসর", "வரம்பு", "范围", "範囲",
})

# abs() → WAT f64.abs  (1 argument)
_ABS_NAMES = frozenset({
    "abs",
    # French
    "valeurabsolue", "valeur_absolue",
    # Spanish
    "valorabsoluto", "valor_absoluto",
    # German
    "betrag",
    # Italian
    "valoreassoluto",
    # Portuguese shares the same alias as Spanish (kept once above)
    # Polish
    "wartoscbezwzgledna",
    # Dutch
    "absoluutewaarde",
    # Hindi
    "निरपेक्षमान",
    # Arabic
    "قيمةمطلقة",
    # Chinese / Japanese
    "绝对值", "絶対値",
})

# min() → WAT f64.min  (2 arguments; more args unsupported)
_MIN_NAMES = frozenset({
    "min",
    "minimum", "minimo",
    # localized aliases from builtins_aliases.json
    "न्यूनतम",  # hi
    "الحد_الأدنى", "الحدالأدنى",  # ar
    "最小",  # zh / ja
})

# max() → WAT f64.max  (2 arguments; more args unsupported)
_MAX_NAMES = frozenset({
    "max",
    "maximum", "maximo", "massimo",
    "अधिकतम",  # hi
    "الحد_الأقصى", "الحدالأقصى",  # ar
    "最大",  # zh / ja
})


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
        saved = (self._instrs, self._locals, self._loop_stack, self._var_class_types)
        self._instrs = []
        self._locals = set()
        self._loop_stack = []
        self._var_class_types = {}
        return saved

    @staticmethod
    def _mangle_class_method_name(class_name: str, method_name: str) -> str:
        return f"{class_name}__{method_name}"

    def _collect_class_lowering(self, classes: list[ClassDef]):
        """Pre-collect lowered names for class methods and constructors."""
        for cls in classes:
            class_name = _name(cls.name)
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

    def _restore_func_state(self, saved):
        self._instrs, self._locals, self._loop_stack, self._var_class_types = saved

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
        for member in (class_def.body or []):
            if isinstance(member, FunctionDef):
                method_name = _name(member.name)
                lowered_name = self._mangle_class_method_name(class_name, method_name)
                self._emit_function(member, emitted_name=lowered_name)

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
    # Statement generation
    # -----------------------------------------------------------------------

    def _emit(self, line: str):
        self._instrs.append(line)

    def _gen_stmts(self, stmts: list, indent: str):
        for stmt in stmts:
            self._gen_stmt(stmt, indent)

    def _gen_stmt(self, stmt, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements
        if isinstance(stmt, VariableDeclaration):
            name = _name(stmt.name)
            self._locals.add(name)
            self._emit(f"{indent};; let {name} = ...")
            self._gen_expr(stmt.value, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
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
                    inferred_class = self._infer_class_name(stmt.value)
                    if inferred_class:
                        self._var_class_types[name] = inferred_class
                    elif name in self._var_class_types:
                        del self._var_class_types[name]
                else:
                    # Compound assignment: a += b → a = a op b
                    _compound = {"+=": "f64.add", "-=": "f64.sub",
                                 "*=": "f64.mul", "/=": "f64.div"}
                    wat_op = _compound.get(op, "f64.add")
                    self._emit(f"{indent};; {name} {op} ...")
                    self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
                    self._gen_expr(stmt.value, indent)
                    self._emit(f"{indent}{wat_op}")
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                    if name in self._var_class_types:
                        del self._var_class_types[name]
            else:
                self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")

        elif isinstance(stmt, ExpressionStatement):
            expr = stmt.expression
            if isinstance(expr, CallExpr):
                fname = _name(expr.func)
                if fname in _PRINT_NAMES:
                    self._gen_print(expr, indent)
                elif fname in _ABS_NAMES and len(expr.args) == 1:
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}f64.abs")
                    self._emit(f"{indent}drop")
                elif fname in _MIN_NAMES and len(expr.args) == 2:
                    self._gen_expr(expr.args[0], indent)
                    self._gen_expr(expr.args[1], indent)
                    self._emit(f"{indent}f64.min")
                    self._emit(f"{indent}drop")
                elif fname in _MAX_NAMES and len(expr.args) == 2:
                    self._gen_expr(expr.args[0], indent)
                    self._gen_expr(expr.args[1], indent)
                    self._emit(f"{indent}f64.max")
                    self._emit(f"{indent}drop")
                elif fname in self._defined_func_names:
                    # Known WAT function — emit args then call
                    self._emit(f"{indent};; call {fname}(...)")
                    self._gen_call_args(expr, indent, fname)
                    self._emit(f"{indent}call ${self._wat_symbol(fname)}")
                    self._emit(f"{indent}drop")
                elif fname in self._class_ctor_names:
                    ctor = self._class_ctor_names[fname]
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
                    self._emit(f"{indent};; instance call {fname}(...)")
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

        elif isinstance(stmt, FunctionDef):
            # Nested function def — not directly supported
            self._emit(f"{indent};; nested def {_name(stmt.name)} — skipped in WAT")

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
            fname = _name(node.func)
            if fname in _PRINT_NAMES:
                self._emit(f"{indent}f64.const 0  ;; print() used as expression")
            elif fname in _ABS_NAMES and len(node.args) == 1:
                # abs(x) → f64.abs
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.abs")
            elif fname in _MIN_NAMES and len(node.args) == 2:
                # min(a, b) → f64.min
                self._gen_expr(node.args[0], indent)
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}f64.min")
            elif fname in _MAX_NAMES and len(node.args) == 2:
                # max(a, b) → f64.max
                self._gen_expr(node.args[0], indent)
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}f64.max")
            elif fname in self._defined_func_names:
                # Known WAT function — emit args then call
                self._gen_call_args(node, indent, fname)
                self._emit(f"{indent}call ${self._wat_symbol(fname)}")
            elif fname in self._class_ctor_names:
                ctor = self._class_ctor_names[fname]
                self._emit(f"{indent}f64.const 0  ;; implicit self")
                self._gen_call_args(node, indent, ctor, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
            elif fname in self._class_attr_call_names:
                lowered = self._class_attr_call_names[fname]
                self._gen_call_args(node, indent, lowered)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            elif self._class_method_target_from_call(node):
                lowered = self._class_method_target_from_call(node)
                self._emit(f"{indent}f64.const 0  ;; implicit self")
                self._gen_call_args(node, indent, lowered, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            else:
                # Closure, constructor, builtin, or other non-WAT callable
                self._emit(f"{indent}f64.const 0  ;; unsupported call: {fname}(...)")

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
