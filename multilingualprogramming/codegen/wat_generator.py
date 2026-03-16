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
  (import "wasi_snapshot_preview1" "fd_write" (func (param i32 i32 i32 i32) (result i32)))

All I/O (print_str, print_f64, print_bool, print_sep, print_newline) and the
power function (pow_f64) are implemented as self-contained WAT functions backed
by the single WASI fd_write syscall.  No JavaScript host shim is required for
CLI or wasmtime execution; browser execution needs only a standard WASI polyfill.
"""
# pylint: disable=mixed-line-endings

from types import MappingProxyType

from multilingualprogramming.parser.ast_nodes import (
    VariableDeclaration,
    Assignment,
    AnnAssignment,
    ExpressionStatement,
    PassStatement,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    RaiseStatement,
    DelStatement,
    GlobalStatement,
    LocalStatement,
    YieldStatement,
    ImportStatement,
    FromImportStatement,
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
    BytesLiteral,
    BooleanLiteral,
    NoneLiteral,
    ListLiteral,
    TupleLiteral,
    DictLiteral,
    SetLiteral,
    DictUnpackEntry,
    AttributeAccess,
    IndexAccess,
    AwaitExpr,
    LambdaExpr,
    SliceExpr,
    NamedExpr,
    ConditionalExpr,
    ListComprehension,
    DictComprehension,
    SetComprehension,
    GeneratorExpr,
    Parameter,
    FStringLiteral,
    AssertStatement,
    ChainedAssignment,
    StarredExpr,
)
from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.core.ir import CoreIRProgram

from multilingualprogramming.codegen.wat_generator_core import WATGeneratorCoreMixin
from multilingualprogramming.codegen.wat_generator_expression import WATGeneratorExpressionMixin
from multilingualprogramming.codegen.wat_generator_loop import WATGeneratorLoopMixin
from multilingualprogramming.codegen.wat_generator_manifest import WATGeneratorManifestMixin
from multilingualprogramming.codegen.wat_generator_match import WATGeneratorMatchMixin
from multilingualprogramming.codegen.wat_generator_oop import WATGeneratorOOPMixin
from multilingualprogramming.codegen.wat_generator_support import (
    _ABS_NAMES,
    _INT_NAMES,
    _LEN_NAMES,
    _MAX_NAMES,
    _MIN_NAMES,
    _POW_NAMES,
    _PARAM_SEPARATORS,
    _PRINT_NAMES,
    _RANGE_NAMES,
    _SUM_NAMES,
    _LIST_NAMES,
    _TUPLE_NAMES,
    _SET_NAMES,
    _STR_NAMES,
    _ZIP_NAMES,
    _extract_render_mode,
    _name,
    _real_params,
)

# ---------------------------------------------------------------------------
# WATCodeGenerator
# ---------------------------------------------------------------------------

class WATCodeGenerator(
    WATGeneratorManifestMixin,
    WATGeneratorCoreMixin,
    WATGeneratorMatchMixin,
    WATGeneratorExpressionMixin,
    WATGeneratorOOPMixin,
    WATGeneratorLoopMixin,
):  # pylint: disable=too-many-instance-attributes
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
        self._tuple_locals: set[str] = set()
        # Compiler-known dict locals: var_name -> string-key to element index.
        self._dict_key_maps: dict[str, dict[str, int]] = {}
        # Import alias resolution for recognized builtin/math lowerings.
        self._imported_call_aliases: dict[str, str] = {}
        self._module_aliases: dict[str, str] = {}
        # Best-effort virtual files for simple with-open lowering.
        self._open_aliases: dict[str, tuple[str, str]] = {}
        self._virtual_file_contents: dict[str, str] = {}
        # True when any heap allocation (list or OOP) is needed.
        self._need_heap_ptr: bool = False
        # Lambda table: ordered list of WAT func names registered for call_indirect.
        self._lambda_table: list[str] = []
        # Per-function: maps local var name -> lambda WAT func name (for call_indirect).
        self._lambda_locals: dict[str, str] = {}
        # Whether runtime string helpers have been added to _funcs.
        self._str_concat_helper_emitted: bool = False
        self._str_slice_helper_emitted: bool = False
        # Lowered names of @staticmethod and @classmethod methods (no self/cls pushed).
        self._static_method_names: set[str] = set()
        # Maps "ClassName.attr" -> lowered WAT func name for @property getters.
        self._property_getters: dict[str, str] = {}
        # Dynamic dispatch (vtable):
        # _class_ids: class_name -> integer class ID (assigned in lowering pass)
        self._class_ids: dict[str, int] = {}
        # _dispatch_func_names: method_name -> WAT dispatch func name
        # Populated for methods that are overridden in ≥1 subclass.
        self._dispatch_func_names: dict[str, str] = {}
        # Functions known to return heap-backed sequence pointers.
        self._sequence_func_names: set[str] = set()
        # Functions known to return string-like values with $__last_str_len metadata.
        self._string_return_funcs: set[str] = set()
        # Runtime string formatting helpers.
        self._string_format_helpers_emitted: bool = False
        # Narrow closure-factory support for returned nested functions with one captured cell.
        self._closure_factory_funcs: dict[str, str] = {}
        self._closure_locals: dict[str, str] = {}
        # Best-effort local exception handling stack for explicit raise statements.
        self._try_stack: list[dict[str, str]] = []

    @property
    def property_getters(self):
        """Read-only view of registered property getter functions."""
        return MappingProxyType(self._property_getters)

    @property
    def class_ids(self):
        """Read-only view of assigned runtime class IDs."""
        return MappingProxyType(self._class_ids)

    @property
    def dispatch_func_names(self):
        """Read-only view of generated dispatch function names."""
        return MappingProxyType(self._dispatch_func_names)

    @property
    def class_obj_sizes(self):
        """Read-only view of computed object sizes in bytes."""
        return MappingProxyType(self._class_obj_sizes)

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
        self._tuple_locals = set()
        self._dict_key_maps = {}
        self._imported_call_aliases = {}
        self._module_aliases = {}
        self._open_aliases = {}
        self._virtual_file_contents = {}
        self._need_heap_ptr = False
        self._lambda_table = []
        self._lambda_locals = {}
        self._str_concat_helper_emitted = False
        self._str_slice_helper_emitted = False
        self._sequence_func_names = set()
        self._string_return_funcs = set()
        self._string_format_helpers_emitted = False
        self._closure_factory_funcs = {}
        self._closure_locals = {}
        self._try_stack = []

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
            if self._returns_string_like(f):
                self._string_return_funcs.add(fname)
        self._collect_class_lowering(classes)
        self._collect_import_aliases(top)

        for func in funcs:
            self._emit_function(func)
        for cls in classes:
            self._emit_class(cls)
        self._emit_dispatch_functions()

        if top:
            self._emit_main(top)

        return self._build_module()

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
                 self._string_len_locals, self._list_locals,
                 self._tuple_locals,
                 self._dict_key_maps,
                 self._lambda_locals,
                 self._closure_locals,
                 self._try_stack,
                 self._open_aliases,
                 self._virtual_file_contents)
        self._instrs = []
        self._locals = set()
        self._loop_stack = []
        self._var_class_types = {}
        self._string_len_locals = {}
        self._list_locals = set()
        self._tuple_locals = set()
        self._dict_key_maps = {}
        self._lambda_locals = {}
        self._closure_locals = {}
        self._try_stack = []
        self._open_aliases = {}
        self._virtual_file_contents = {}
        # _current_class is NOT reset here: _emit_class sets it before each method
        # and it must persist into the method body.
        return saved

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
            # old_val is on stack as base; push exponent, call host pow_f64.
            self._gen_expr(rhs_node, indent)
            self._emit(f"{indent}call $pow_f64")
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
        self._emit(f"{indent};; list/tuple literal [{n} elements]")
        self._emit_alloc(total_bytes, ptr_local, indent)
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

    def _gen_static_dict_alloc(self, node: DictLiteral, indent: str) -> bool:
        """Allocate a compile-time-known dict as a values array plus key metadata."""
        mapping = self._flatten_static_dict_entries(node)
        if mapping is None:
            return False
        self._gen_list_alloc(ListLiteral(list(mapping.values())), indent)
        return True

    def _gen_divmod_alloc(self, left, right, indent: str) -> None:
        """Allocate a 2-tuple containing quotient and remainder."""
        tmp_left = f"__divmod_left_{self._new_label()}"
        tmp_right = f"__divmod_right_{self._new_label()}"
        tmp_q = f"__divmod_q_{self._new_label()}"
        self._locals.update({tmp_left, tmp_right, tmp_q})

        self._gen_expr(left, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_left)}")
        self._gen_expr(right, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_right)}")

        self._emit(f"{indent}local.get ${self._wat_symbol(tmp_left)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(tmp_right)}")
        self._emit(f"{indent}f64.div")
        self._emit(f"{indent}f64.floor")
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_q)}")

        self._gen_list_alloc(
            TupleLiteral([
                Identifier(tmp_q),
                BinaryOp(
                    Identifier(tmp_left),
                    "-",
                    BinaryOp(Identifier(tmp_q), "*", Identifier(tmp_right)),
                ),
            ]),
            indent,
        )

    def _gen_sorted_copy(self, seq_expr, indent: str) -> bool:
        """Allocate and sort a numeric copy of a list-like pointer."""
        if not (isinstance(seq_expr, Identifier)
                and (seq_expr.name in self._list_locals or seq_expr.name in self._tuple_locals)):
            return False
        name = seq_expr.name
        lbl = self._new_label()
        src_ptr = f"__sort_src_{lbl}"
        dst_ptr = f"__sort_dst_{lbl}"
        len_local = f"__sort_len_{lbl}"
        i_local = f"__sort_i_{lbl}"
        j_local = f"__sort_j_{lbl}"
        a_local = f"__sort_a_{lbl}"
        b_local = f"__sort_b_{lbl}"
        for local_name in (src_ptr, dst_ptr, len_local, i_local, j_local, a_local, b_local):
            self._locals.add(local_name)
        self._need_heap_ptr = True

        self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")

        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit_alloc_dynamic(dst_ptr, indent)

        self._emit(f"{indent}local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")

        copy_blk = f"sort_copy_blk_{lbl}"
        copy_lp = f"sort_copy_lp_{lbl}"
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}block ${copy_blk}")
        self._emit(f"{indent}  loop ${copy_lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${copy_blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    f64.store")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    br ${copy_lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")

        outer_blk = f"sort_outer_blk_{lbl}"
        outer_lp = f"sort_outer_lp_{lbl}"
        inner_blk = f"sort_inner_blk_{lbl}"
        inner_lp = f"sort_inner_lp_{lbl}"
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}block ${outer_blk}")
        self._emit(f"{indent}  loop ${outer_lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${outer_blk}")
        self._emit(f"{indent}    f64.const 0")
        self._emit(f"{indent}    local.set ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}    block ${inner_blk}")
        self._emit(f"{indent}      loop ${inner_lp}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}        f64.const 1")
        self._emit(f"{indent}        f64.sub")
        self._emit(f"{indent}        f64.ge")
        self._emit(f"{indent}        br_if ${inner_blk}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}        i32.trunc_f64_u")
        self._emit(f"{indent}        local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}        i32.trunc_f64_u")
        self._emit(f"{indent}        i32.const 8")
        self._emit(f"{indent}        i32.mul")
        self._emit(f"{indent}        i32.const 8")
        self._emit(f"{indent}        i32.add")
        self._emit(f"{indent}        i32.add")
        self._emit(f"{indent}        f64.load")
        self._emit(f"{indent}        local.set ${self._wat_symbol(a_local)}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}        i32.trunc_f64_u")
        self._emit(f"{indent}        local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}        i32.trunc_f64_u")
        self._emit(f"{indent}        i32.const 1")
        self._emit(f"{indent}        i32.add")
        self._emit(f"{indent}        i32.const 8")
        self._emit(f"{indent}        i32.mul")
        self._emit(f"{indent}        i32.const 8")
        self._emit(f"{indent}        i32.add")
        self._emit(f"{indent}        i32.add")
        self._emit(f"{indent}        f64.load")
        self._emit(f"{indent}        local.set ${self._wat_symbol(b_local)}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(a_local)}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(b_local)}")
        self._emit(f"{indent}        f64.gt")
        self._emit(f"{indent}        if")
        self._emit(f"{indent}          local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}          i32.trunc_f64_u")
        self._emit(f"{indent}          local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}          i32.trunc_f64_u")
        self._emit(f"{indent}          i32.const 8")
        self._emit(f"{indent}          i32.mul")
        self._emit(f"{indent}          i32.const 8")
        self._emit(f"{indent}          i32.add")
        self._emit(f"{indent}          i32.add")
        self._emit(f"{indent}          local.get ${self._wat_symbol(b_local)}")
        self._emit(f"{indent}          f64.store")
        self._emit(f"{indent}          local.get ${self._wat_symbol(dst_ptr)}")
        self._emit(f"{indent}          i32.trunc_f64_u")
        self._emit(f"{indent}          local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}          i32.trunc_f64_u")
        self._emit(f"{indent}          i32.const 1")
        self._emit(f"{indent}          i32.add")
        self._emit(f"{indent}          i32.const 8")
        self._emit(f"{indent}          i32.mul")
        self._emit(f"{indent}          i32.const 8")
        self._emit(f"{indent}          i32.add")
        self._emit(f"{indent}          i32.add")
        self._emit(f"{indent}          local.get ${self._wat_symbol(a_local)}")
        self._emit(f"{indent}          f64.store")
        self._emit(f"{indent}        end")
        self._emit(f"{indent}        local.get ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}        f64.const 1")
        self._emit(f"{indent}        f64.add")
        self._emit(f"{indent}        local.set ${self._wat_symbol(j_local)}")
        self._emit(f"{indent}        br ${inner_lp}")
        self._emit(f"{indent}      end")
        self._emit(f"{indent}    end")
        self._emit(f"{indent}    local.get ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(i_local)}")
        self._emit(f"{indent}    br ${outer_lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(dst_ptr)}")
        return True

    def _static_length(self, node):
        """Return a compile-time-known sequence length, or None."""
        if isinstance(node, (ListLiteral, TupleLiteral, SetLiteral)):
            return len(node.elements)
        if isinstance(node, DictLiteral):
            mapping = self._flatten_static_dict_entries(node)
            return None if mapping is None else len(mapping)
        if isinstance(node, Identifier):
            if node.name in self._dict_key_maps:
                return len(self._dict_key_maps[node.name])
            if node.name in self._list_locals or node.name in self._tuple_locals:
                return None
        return None

    def _gen_static_zip_list(self, zip_call: CallExpr, indent: str) -> bool:
        """Lower zip(a, b, ...) with static literal lengths to a placeholder list."""
        if len(zip_call.args) < 2:
            return False
        lengths = [self._static_length(arg) for arg in zip_call.args]
        if any(length is None for length in lengths):
            return False
        zipped_len = min(lengths)
        self._gen_list_alloc(
            ListLiteral([NumeralLiteral("0") for _ in range(zipped_len)]),
            indent,
        )
        return True

    def _parse_range_bounds(self, iterable):
        """Return (start_node, end_node) for a supported range(...) call."""
        if not (isinstance(iterable, CallExpr) and _name(iterable.func) in _RANGE_NAMES):
            return None
        if len(iterable.args) == 1:
            return NumeralLiteral("0"), iterable.args[0]
        if len(iterable.args) == 2:
            return iterable.args[0], iterable.args[1]
        return None

    def _static_dict_comp_keys(self, node):
        """Return compile-time keys for a simple dict comprehension, or None."""
        if not isinstance(node, DictComprehension) or len(node.clauses) != 1:
            return None
        clause = node.clauses[0]
        if clause.conditions:
            return None
        bounds = self._parse_range_bounds(clause.iterable)
        if bounds is None:
            return None
        start_node, end_node = bounds
        if not (isinstance(start_node, NumeralLiteral) and isinstance(end_node, NumeralLiteral)):
            return None
        if not (isinstance(clause.target, Identifier)
                and isinstance(node.key, CallExpr)
                and _name(node.key.func) in _STR_NAMES
                and len(node.key.args) == 1
                and isinstance(node.key.args[0], Identifier)
                and node.key.args[0].name == clause.target.name):
            return None
        start = int(float(start_node.value))
        end = int(float(end_node.value))
        return [str(i) for i in range(start, end)]

    def _gen_simple_dict_comprehension(self, node, indent: str) -> bool:
        """Lower a simple {str(i): expr for i in range(...)} dict comprehension."""
        keys = self._static_dict_comp_keys(node)
        if keys is None:
            return False
        clause = node.clauses[0]
        bounds = self._parse_range_bounds(clause.iterable)
        if bounds is None:
            return False
        start_node, end_node = bounds

        label = self._new_label()
        iter_var = (
            _name(clause.target)
            if isinstance(clause.target, Identifier) else f"__dict_item_{label}"
        )
        ptr_local = f"__dict_ptr_{label}"
        idx_local = f"__dict_idx_{label}"
        end_local = f"__dict_end_{label}"
        len_local = f"__dict_len_{label}"
        for local_name in (iter_var, ptr_local, idx_local, end_local, len_local):
            self._locals.add(local_name)

        self._need_heap_ptr = True
        self._gen_expr(start_node, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
        self._gen_expr(end_node, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")

        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit_alloc_dynamic(ptr_local, indent)

        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")

        blk = f"dict_comp_blk_{label}"
        loop = f"dict_comp_lp_{label}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._gen_expr(node.value, indent + "    ")
        self._emit(f"{indent}    f64.store")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _simple_generator_spec(self, func_def: FunctionDef):
        """Return lowering info for a simple yield-based generator function."""
        if len(func_def.body) != 1:
            return None
        stmt = func_def.body[0]
        if isinstance(stmt, YieldStatement) and stmt.is_from:
            bounds = self._parse_range_bounds(stmt.value)
            if bounds is None:
                return None
            iter_name = f"__gen_item_{self._new_label()}"
            return bounds[0], bounds[1], iter_name, Identifier(iter_name)
        if isinstance(stmt, ForLoop):
            bounds = self._parse_range_bounds(stmt.iterable)
            if bounds is None or len(stmt.body) != 1:
                return None
            inner = stmt.body[0]
            if not isinstance(inner, YieldStatement) or inner.is_from:
                return None
            if not isinstance(stmt.target, Identifier):
                return None
            return bounds[0], bounds[1], stmt.target.name, inner.value or stmt.target
        return None

    def _emit_simple_generator_function(self, func_def: FunctionDef, emitted_name: str | None = None) -> bool:
        """Lower a simple generator function to a sequence-returning WAT function."""
        spec = self._simple_generator_spec(func_def)
        if spec is None:
            return False

        saved = self._save_func_state()
        func_name = emitted_name or _name(func_def.name)
        param_names = _real_params(func_def)
        self._locals = set(param_names)
        start_node, end_node, iter_var, element_expr = spec

        ptr_local = f"__gen_ptr_{self._new_label()}"
        idx_local = f"__gen_idx_{self._new_label()}"
        len_local = f"__gen_len_{self._new_label()}"
        end_local = f"__gen_end_{self._new_label()}"
        self._locals.update({iter_var, ptr_local, idx_local, len_local, end_local})
        self._need_heap_ptr = True

        self._gen_expr(start_node, "    ")
        self._emit(f"    local.set ${self._wat_symbol(iter_var)}")
        self._gen_expr(end_node, "    ")
        self._emit(f"    local.set ${self._wat_symbol(end_local)}")
        self._emit(f"    local.get ${self._wat_symbol(end_local)}")
        self._emit(f"    local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"    f64.sub")
        self._emit(f"    local.set ${self._wat_symbol(len_local)}")

        self._emit(f"    local.get ${self._wat_symbol(len_local)}")
        self._emit("    i32.trunc_f64_u")
        self._emit("    i32.const 1")
        self._emit("    i32.add")
        self._emit("    i32.const 8")
        self._emit("    i32.mul")
        self._emit_alloc_dynamic(ptr_local, "    ")

        self._emit(f"    local.get ${self._wat_symbol(ptr_local)}")
        self._emit("    i32.trunc_f64_u")
        self._emit(f"    local.get ${self._wat_symbol(len_local)}")
        self._emit("    f64.store")
        self._emit("    f64.const 0")
        self._emit(f"    local.set ${self._wat_symbol(idx_local)}")

        label = self._new_label()
        blk = f"gen_blk_{label}"
        loop = f"gen_lp_{label}"
        self._emit(f"    block ${blk}")
        self._emit(f"      loop ${loop}")
        self._emit(f"        local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"        local.get ${self._wat_symbol(end_local)}")
        self._emit("        f64.ge")
        self._emit(f"        br_if ${blk}")
        self._emit(f"        local.get ${self._wat_symbol(ptr_local)}")
        self._emit("        i32.trunc_f64_u")
        self._emit(f"        local.get ${self._wat_symbol(idx_local)}")
        self._emit("        i32.trunc_f64_u")
        self._emit("        i32.const 8")
        self._emit("        i32.mul")
        self._emit("        i32.const 8")
        self._emit("        i32.add")
        self._emit("        i32.add")
        self._gen_expr(element_expr, "        ")
        self._emit("        f64.store")
        self._emit(f"        local.get ${self._wat_symbol(iter_var)}")
        self._emit("        f64.const 1")
        self._emit("        f64.add")
        self._emit(f"        local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"        local.get ${self._wat_symbol(idx_local)}")
        self._emit("        f64.const 1")
        self._emit("        f64.add")
        self._emit(f"        local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"        br ${loop}")
        self._emit("      end")
        self._emit("    end")
        self._emit(f"    local.get ${self._wat_symbol(ptr_local)}")
        self._emit("    return")

        body_instrs = list(self._instrs)
        local_names = sorted(self._locals - set(param_names))
        wat_func_name = self._wat_symbol(func_name)
        lines = [f'  (func ${wat_func_name} (export "{func_name}")']
        for param_name in param_names:
            lines.append(f"    (param ${self._wat_symbol(param_name)} f64)")
        lines.append("    (result f64)")
        for local_name in local_names:
            lines.append(f"    (local ${self._wat_symbol(local_name)} f64)")
        lines.extend(body_instrs)
        lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")

        self._funcs.append("\n".join(lines))
        self._sequence_func_names.add(func_name)
        self._restore_func_state(saved)
        return True

    def _gen_filtered_or_nested_comprehension_list(self, node, indent: str) -> bool:
        """Lower selected filtered or nested comprehensions to heap-backed lists."""
        if not isinstance(node, (ListComprehension, SetComprehension, GeneratorExpr)):
            return False

        label = self._new_label()
        ptr_local = f"__comp_ptr_{label}"
        write_idx = f"__comp_write_{label}"
        cap_local = f"__comp_cap_{label}"
        self._locals.update({ptr_local, write_idx, cap_local})
        def alloc_with_capacity():
            self._emit(f"{indent}local.get ${self._wat_symbol(cap_local)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}i32.const 1")
            self._emit(f"{indent}i32.add")
            self._emit(f"{indent}i32.const 8")
            self._emit(f"{indent}i32.mul")
            self._emit_alloc_dynamic(ptr_local, indent)
            self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}f64.store")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}local.set ${self._wat_symbol(write_idx)}")

        def emit_store(value_indent: str):
            self._emit(f"{value_indent}local.get ${self._wat_symbol(ptr_local)}")
            self._emit(f"{value_indent}i32.trunc_f64_u")
            self._emit(f"{value_indent}local.get ${self._wat_symbol(write_idx)}")
            self._emit(f"{value_indent}i32.trunc_f64_u")
            self._emit(f"{value_indent}i32.const 8")
            self._emit(f"{value_indent}i32.mul")
            self._emit(f"{value_indent}i32.const 8")
            self._emit(f"{value_indent}i32.add")
            self._emit(f"{value_indent}i32.add")
            self._gen_expr(node.element, value_indent)
            self._emit(f"{value_indent}f64.store")
            self._emit(f"{value_indent}local.get ${self._wat_symbol(write_idx)}")
            self._emit(f"{value_indent}f64.const 1")
            self._emit(f"{value_indent}f64.add")
            self._emit(f"{value_indent}local.set ${self._wat_symbol(write_idx)}")

        if len(node.clauses) == 1:
            clause = node.clauses[0]
            bounds = self._parse_range_bounds(clause.iterable)
            if bounds is None or not clause.conditions:
                return False
            start_node, end_node = bounds
            iter_var = (
                _name(clause.target)
                if isinstance(clause.target, Identifier) else f"__comp_item_{label}"
            )
            end_local = f"__comp_end_{label}"
            self._locals.update({iter_var, end_local})
            self._gen_expr(start_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
            self._gen_expr(end_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(end_local)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(end_local)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}f64.sub")
            self._emit(f"{indent}local.set ${self._wat_symbol(cap_local)}")
            alloc_with_capacity()

            blk = f"comp_filter_blk_{label}"
            loop = f"comp_filter_lp_{label}"
            self._emit(f"{indent}block ${blk}")
            self._emit(f"{indent}  loop ${loop}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(end_local)}")
            self._emit(f"{indent}    f64.ge")
            self._emit(f"{indent}    br_if ${blk}")
            for cond in clause.conditions:
                self._gen_cond(cond, indent + "    ")
                self._emit(f"{indent}    if")
                emit_store(indent + "      ")
                self._emit(f"{indent}    end")
            self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    f64.const 1")
            self._emit(f"{indent}    f64.add")
            self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    br ${loop}")
            self._emit(f"{indent}  end")
            self._emit(f"{indent}end")
        elif len(node.clauses) == 2:
            outer, inner = node.clauses
            outer_bounds = self._parse_range_bounds(outer.iterable)
            inner_bounds = self._parse_range_bounds(inner.iterable)
            if outer_bounds is None or inner_bounds is None or outer.conditions or inner.conditions:
                return False
            outer_var = (
                _name(outer.target)
                if isinstance(outer.target, Identifier) else f"__comp_outer_{label}"
            )
            inner_var = (
                _name(inner.target)
                if isinstance(inner.target, Identifier) else f"__comp_inner_{label}"
            )
            outer_end = f"__comp_outer_end_{label}"
            inner_start = f"__comp_inner_start_{label}"
            inner_end = f"__comp_inner_end_{label}"
            outer_span = f"__comp_outer_span_{label}"
            inner_span = f"__comp_inner_span_{label}"
            self._locals.update({
                outer_var, inner_var, outer_end, inner_start, inner_end, outer_span, inner_span
            })
            outer_start_node, outer_end_node = outer_bounds
            inner_start_node, inner_end_node = inner_bounds

            self._gen_expr(outer_start_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(outer_var)}")
            self._gen_expr(outer_end_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(outer_end)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(outer_end)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(outer_var)}")
            self._emit(f"{indent}f64.sub")
            self._emit(f"{indent}local.set ${self._wat_symbol(outer_span)}")
            self._gen_expr(inner_start_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(inner_start)}")
            self._gen_expr(inner_end_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(inner_end)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(inner_end)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(inner_start)}")
            self._emit(f"{indent}f64.sub")
            self._emit(f"{indent}local.set ${self._wat_symbol(inner_span)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(outer_span)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(inner_span)}")
            self._emit(f"{indent}f64.mul")
            self._emit(f"{indent}local.set ${self._wat_symbol(cap_local)}")
            alloc_with_capacity()

            outer_blk = f"comp_outer_blk_{label}"
            outer_loop = f"comp_outer_lp_{label}"
            inner_blk = f"comp_inner_blk_{label}"
            inner_loop = f"comp_inner_lp_{label}"
            self._emit(f"{indent}block ${outer_blk}")
            self._emit(f"{indent}  loop ${outer_loop}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(outer_var)}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(outer_end)}")
            self._emit(f"{indent}    f64.ge")
            self._emit(f"{indent}    br_if ${outer_blk}")
            self._emit(f"{indent}    local.get ${self._wat_symbol(inner_start)}")
            self._emit(f"{indent}    local.set ${self._wat_symbol(inner_var)}")
            self._emit(f"{indent}    block ${inner_blk}")
            self._emit(f"{indent}      loop ${inner_loop}")
            self._emit(f"{indent}        local.get ${self._wat_symbol(inner_var)}")
            self._emit(f"{indent}        local.get ${self._wat_symbol(inner_end)}")
            self._emit(f"{indent}        f64.ge")
            self._emit(f"{indent}        br_if ${inner_blk}")
            emit_store(indent + "        ")
            self._emit(f"{indent}        local.get ${self._wat_symbol(inner_var)}")
            self._emit(f"{indent}        f64.const 1")
            self._emit(f"{indent}        f64.add")
            self._emit(f"{indent}        local.set ${self._wat_symbol(inner_var)}")
            self._emit(f"{indent}        br ${inner_loop}")
            self._emit(f"{indent}      end")
            self._emit(f"{indent}    end")
            self._emit(f"{indent}    local.get ${self._wat_symbol(outer_var)}")
            self._emit(f"{indent}    f64.const 1")
            self._emit(f"{indent}    f64.add")
            self._emit(f"{indent}    local.set ${self._wat_symbol(outer_var)}")
            self._emit(f"{indent}    br ${outer_loop}")
            self._emit(f"{indent}  end")
            self._emit(f"{indent}end")
        else:
            return False

        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(write_idx)}")
        self._emit(f"{indent}f64.store")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _emit_sum_over_pointer(self, ptr_expr, indent: str) -> None:
        """Emit a numeric sum over a list-like pointer expression."""
        lbl = self._new_label()
        ptr_local = f"__sum_ptr_{lbl}"
        idx_local = f"__sum_idx_{lbl}"
        len_local = f"__sum_len_{lbl}"
        acc_local = f"__sum_acc_{lbl}"
        blk = f"sum_blk_{lbl}"
        loop = f"sum_lp_{lbl}"
        for local_name in (ptr_local, idx_local, len_local, acc_local):
            self._locals.add(local_name)

        self._gen_expr(ptr_expr, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(acc_local)}")
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(acc_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(acc_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(acc_local)}")

    def _gen_simple_comprehension_list(self, node, indent: str) -> bool:
        """Lower a simple range/list comprehension or generator expression to a list."""
        clause = node.clauses[0] if node.clauses else None
        if clause is None or len(node.clauses) != 1 or clause.conditions:
            return False

        iterable_name = _name(clause.iterable) if isinstance(clause.iterable, Identifier) else None
        is_range = (
            isinstance(clause.iterable, CallExpr)
            and _name(clause.iterable.func) in _RANGE_NAMES
        )
        is_list = iterable_name in self._list_locals
        if not (is_range or is_list):
            return False

        label = self._new_label()
        iter_var = _name(clause.target) if isinstance(clause.target, Identifier) else f"__comp_item_{label}"
        ptr_local = f"__comp_ptr_{label}"
        idx_local = f"__comp_idx_{label}"
        len_local = f"__comp_len_{label}"
        src_len_local = f"__comp_src_len_{label}"
        end_local = f"__comp_end_{label}"
        for local_name in (iter_var, ptr_local, idx_local, len_local, src_len_local, end_local):
            self._locals.add(local_name)

        self._need_heap_ptr = True
        if is_range:
            range_args = clause.iterable.args
            if len(range_args) == 1:
                start_node = NumeralLiteral("0")
                end_node = range_args[0]
            elif len(range_args) == 2:
                start_node, end_node = range_args
            else:
                return False
            self._gen_expr(start_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
            self._gen_expr(end_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(end_local)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(end_local)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}f64.sub")
            self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        else:
            self._emit(f"{indent}local.get ${self._wat_symbol(iterable_name)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}f64.load")
            self._emit(f"{indent}local.set ${self._wat_symbol(src_len_local)}")
            self._emit(f"{indent}local.get ${self._wat_symbol(src_len_local)}")
            self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")

        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit_alloc_dynamic(ptr_local, indent)

        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")

        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")
        blk = f"comp_list_blk_{label}"
        loop = f"comp_list_lp_{label}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        if is_list:
            self._emit(f"{indent}    local.get ${self._wat_symbol(iterable_name)}")
            self._emit(f"{indent}    i32.trunc_f64_u")
            self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
            self._emit(f"{indent}    i32.trunc_f64_u")
            self._emit(f"{indent}    i32.const 8")
            self._emit(f"{indent}    i32.mul")
            self._emit(f"{indent}    i32.const 8")
            self._emit(f"{indent}    i32.add")
            self._emit(f"{indent}    i32.add")
            self._emit(f"{indent}    f64.load")
            self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._gen_expr(node.element, indent + "    ")
        self._emit(f"{indent}    f64.store")
        if is_range:
            self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"{indent}    f64.const 1")
            self._emit(f"{indent}    f64.add")
            self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    # -----------------------------------------------------------------------
    # len() helper
    # -----------------------------------------------------------------------

    def _gen_len(self, arg_node, indent: str):
        """Emit WAT that pushes the length of a string or list variable."""
        if isinstance(arg_node, StringLiteral):
            _, byte_len = self._intern(arg_node.value)
            self._emit(f"{indent}f64.const {float(byte_len)}  ;; len of string literal")
        elif isinstance(arg_node, BytesLiteral):
            _, byte_len = self._intern(arg_node.value)
            self._emit(f"{indent}f64.const {float(byte_len)}  ;; len of bytes literal")
        elif isinstance(arg_node, Identifier):
            if arg_node.name in self._string_len_locals:
                len_local = self._string_len_locals[arg_node.name]
                self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
            elif arg_node.name in self._list_locals or arg_node.name in self._tuple_locals \
                    or arg_node.name in self._dict_key_maps:
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

    def _gen_string_len_expr(self, node, indent: str) -> bool:
        """Emit WAT that pushes a tracked UTF-8 byte length for *node*."""
        if isinstance(node, StringLiteral):
            _, byte_len = self._intern(node.value)
            self._emit(f"{indent}f64.const {float(byte_len)}")
            return True
        if isinstance(node, BytesLiteral):
            _, byte_len = self._intern(node.value)
            self._emit(f"{indent}f64.const {float(byte_len)}")
            return True
        if isinstance(node, Identifier) and node.name in self._string_len_locals:
            len_local = self._string_len_locals[node.name]
            self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
            return True
        virtual_read = self._virtual_file_read_content(node)
        if virtual_read is not None:
            _, byte_len = self._intern(virtual_read)
            self._emit(f"{indent}f64.const {float(byte_len)}")
            return True
        if isinstance(node, BinaryOp) and node.op == "+" and self._is_string_binop(node):
            self._gen_string_len_expr(node.left, indent)
            self._gen_string_len_expr(node.right, indent)
            self._emit(f"{indent}f64.add")
            return True
        return False

    def _update_string_tracking(self, name: str, value, indent: str) -> None:
        """Refresh tracked string-length metadata after storing into *name*."""
        if isinstance(value, FStringLiteral) or (
            isinstance(value, CallExpr) and _name(value.func) in self._string_return_funcs
        ):
            len_local = f"{name}_strlen"
            self._locals.add(len_local)
            self._emit(f"{indent}global.get $__last_str_len")
            self._emit(f"{indent}f64.convert_i32_u")
            self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
            self._string_len_locals[name] = len_local
        elif self._gen_string_len_expr(value, indent):
            len_local = f"{name}_strlen"
            self._locals.add(len_local)
            self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
            self._string_len_locals[name] = len_local
        elif name in self._string_len_locals:
            del self._string_len_locals[name]

    def _update_collection_tracking(self, name: str, value) -> None:
        """Refresh tracked list/tuple metadata after storing into *name*."""
        is_container_builtin = (
            isinstance(value, CallExpr)
            and _name(value.func) in (_LIST_NAMES | _TUPLE_NAMES | _SET_NAMES)
            and len(value.args) == 1
            and isinstance(value.args[0], (ListLiteral, TupleLiteral, SetLiteral, DictLiteral))
        )
        returns_tuple = (
            isinstance(value, CallExpr)
            and _name(value.func) == "divmod"
            and len(value.args) == 2
        )
        materialized_sequence = (
            isinstance(value, (ListComprehension, SetComprehension))
            and len(getattr(value, "clauses", [])) == 1
            and not value.clauses[0].conditions
        )
        if isinstance(value, (TupleLiteral,)) or (
            isinstance(value, CallExpr)
            and _name(value.func) in _TUPLE_NAMES
            and len(value.args) == 1
            and isinstance(value.args[0], (ListLiteral, TupleLiteral))
        ) or returns_tuple:
            self._tuple_locals.add(name)
            self._list_locals.discard(name)
        elif isinstance(value, (ListLiteral, SetLiteral)) or materialized_sequence \
                or is_container_builtin or (
            isinstance(value, CallExpr)
            and _name(value.func) == "sorted"
            and len(value.args) >= 1
        ) or (
            isinstance(value, CallExpr)
            and _name(value.func) in self._sequence_func_names
        ) or (
            isinstance(value, CallExpr)
            and _name(value.func) in _LIST_NAMES
            and len(value.args) == 1
            and isinstance(value.args[0], CallExpr)
            and (
                _name(value.args[0].func) in _ZIP_NAMES
                or _name(value.args[0].func) in self._sequence_func_names
            )
        ):
            self._list_locals.add(name)
            self._tuple_locals.discard(name)
        elif name in self._list_locals:
            self._list_locals.remove(name)
        elif name in self._tuple_locals:
            self._tuple_locals.remove(name)

    def _flatten_static_dict_entries(self, node):
        """Return an ordered mapping for a compile-time-resolvable DictLiteral."""
        if not isinstance(node, DictLiteral):
            return None
        flat: dict[str, object] = {}
        for entry in node.entries:
            if isinstance(entry, DictUnpackEntry):
                nested = self._flatten_static_dict_entries(entry.value)
                if nested is None:
                    return None
                flat.update(nested)
                continue
            if not (isinstance(entry, tuple) and len(entry) == 2):
                return None
            key_node, value_node = entry
            if not isinstance(key_node, StringLiteral):
                return None
            flat[key_node.value] = value_node
        return flat

    def _static_set_elements(self, node):
        """Return compile-time-deduplicated elements for a static set(...) call."""
        seq = None
        if isinstance(node, SetLiteral):
            seq = node.elements
        elif isinstance(node, (ListLiteral, TupleLiteral)):
            seq = node.elements
        if seq is None:
            return None
        result = []
        seen = set()
        for elem in seq:
            if isinstance(elem, NumeralLiteral):
                key = ("num", elem.value)
            elif isinstance(elem, StringLiteral):
                key = ("str", elem.value)
            elif isinstance(elem, BooleanLiteral):
                key = ("bool", elem.value)
            else:
                return None
            if key not in seen:
                seen.add(key)
                result.append(elem)
        return result

    def _update_dict_tracking(self, name: str, value) -> None:
        """Refresh tracked static-dict metadata after storing into *name*."""
        if (isinstance(value, CallExpr)
                and _name(value.func) in _LIST_NAMES
                and len(value.args) == 1):
            value = value.args[0]
        mapping = self._flatten_static_dict_entries(value)
        if mapping is not None:
            self._dict_key_maps[name] = {key: index for index, key in enumerate(mapping)}
            return
        keys = self._static_dict_comp_keys(value)
        if keys is not None:
            self._dict_key_maps[name] = {key: index for index, key in enumerate(keys)}
        elif name in self._dict_key_maps:
            del self._dict_key_maps[name]

    def _update_assignment_tracking(self, name: str, value, indent: str) -> None:
        """Refresh side metadata after assignment-like stores into *name*."""
        self._update_string_tracking(name, value, indent)
        self._update_collection_tracking(name, value)
        self._update_dict_tracking(name, value)
        if isinstance(value, LambdaExpr):
            if self._lambda_table:
                self._lambda_locals[name] = self._lambda_table[-1]
        elif name in self._lambda_locals:
            del self._lambda_locals[name]
        if isinstance(value, CallExpr) and _name(value.func) in self._closure_factory_funcs:
            self._closure_locals[name] = self._closure_factory_funcs[_name(value.func)]
        elif name in self._closure_locals:
            del self._closure_locals[name]
        inferred_class = self._infer_class_name(value)
        if inferred_class:
            self._var_class_types[name] = inferred_class
        elif name in self._var_class_types:
            del self._var_class_types[name]

    def _clear_assignment_tracking(self, name: str) -> None:
        """Drop auxiliary metadata for a local after destructive-style updates."""
        if name in self._string_len_locals:
            del self._string_len_locals[name]
        if name in self._list_locals:
            self._list_locals.remove(name)
        if name in self._tuple_locals:
            self._tuple_locals.remove(name)
        if name in self._dict_key_maps:
            del self._dict_key_maps[name]
        if name in self._lambda_locals:
            del self._lambda_locals[name]
        if name in self._closure_locals:
            del self._closure_locals[name]
        if name in self._var_class_types:
            del self._var_class_types[name]

    def _resolve_virtual_file_op(self, call_expr: CallExpr):
        """Return metadata for a tracked open-handle method call, or None."""
        if not isinstance(call_expr.func, AttributeAccess):
            return None
        obj = call_expr.func.obj
        if not isinstance(obj, Identifier):
            return None
        alias = obj.name
        if alias not in self._open_aliases:
            return None
        path, mode = self._open_aliases[alias]
        return alias, path, mode, call_expr.func.attr

    def _virtual_file_read_content(self, node):
        """Return compile-time string content for a tracked file-handle read call."""
        if not isinstance(node, CallExpr):
            return None
        resolved = self._resolve_virtual_file_op(node)
        if resolved is None:
            return None
        _alias, path, mode, method = resolved
        if method != "read" or "r" not in mode:
            return None
        return self._virtual_file_contents.get(path, "")

    def _emit_last_str_len_from_f64(self, indent: str) -> None:
        """Convert a top-of-stack f64 length into $__last_str_len."""
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}global.set $__last_str_len")

    def _ensure_string_format_helpers(self):
        """Emit scratch-buffer string formatting helpers once per module."""
        if self._string_format_helpers_emitted:
            return
        self._string_format_helpers_emitted = True
        mem_end = self._WASM_PAGES * 65536
        scratch = mem_end - 64
        fmt = scratch + 12
        lines = [
            "  (func $__fmt_default_tmpstr (param $v f64) (result i32 i32)",
            "    (local $neg i32)",
            "    (local $int_part i64)",
            "    local.get $v",
            "    f64.const 0",
            "    f64.lt",
            "    local.set $neg",
            "    local.get $neg",
            "    if",
            "      local.get $v",
            "      f64.neg",
            "      local.set $v",
            "    end",
            "    local.get $v",
            "    f64.trunc",
            "    i64.trunc_f64_u",
            "    local.set $int_part",
            "    local.get $int_part",
            "    call $__fmt_u64",
            "    local.get $neg",
            "    if (result i32 i32)",
            "      local.set $ml_len",
            "      local.set $ml_ptr",
            "      local.get $ml_ptr",
            "      i32.const 1",
            "      i32.sub",
            f"      i32.const 45",
            "      i32.store8",
            "      local.get $ml_ptr",
            "      i32.const 1",
            "      i32.sub",
            "      local.get $ml_len",
            "      i32.const 1",
            "      i32.add",
            "    end",
            "  )",
        ]
        # Replace temp locals with declarations for valid WAT.
        lines[0] = "  (func $__fmt_default_tmpstr (param $v f64) (result i32 i32)"
        lines.insert(1, "    (local $ml_ptr i32)")
        lines.insert(2, "    (local $ml_len i32)")
        lines.insert(3, "    (local $neg i32)")
        lines.insert(4, "    (local $int_part i64)")
        lines = [
            "  (func $__fmt_default_tmpstr (param $v f64) (result f64 f64)",
            "    (local $ml_ptr i32)",
            "    (local $ml_len i32)",
            "    (local $neg i32)",
            "    (local $int_part i64)",
            "    local.get $v",
            "    f64.const 0",
            "    f64.lt",
            "    local.set $neg",
            "    local.get $neg",
            "    if",
            "      local.get $v",
            "      f64.neg",
            "      local.set $v",
            "    end",
            "    local.get $v",
            "    f64.trunc",
            "    i64.trunc_f64_u",
            "    local.set $int_part",
            "    local.get $int_part",
            "    call $__fmt_u64",
            "    local.set $ml_len",
            "    local.set $ml_ptr",
            "    local.get $neg",
            "    if",
            "      local.get $ml_ptr",
            "      i32.const 1",
            "      i32.sub",
            "      i32.const 45",
            "      i32.store8",
            "      local.get $ml_ptr",
            "      i32.const 1",
            "      i32.sub",
            "      local.set $ml_ptr",
            "      local.get $ml_len",
            "      i32.const 1",
            "      i32.add",
            "      local.set $ml_len",
            "    end",
            "    local.get $ml_ptr",
            "    f64.convert_i32_u",
            "    local.get $ml_len",
            "    f64.convert_i32_u",
            "  )",
            "  (func $__fmt_fixed1_tmpstr (param $v f64) (result f64 f64)",
            "    (local $int_part i64)",
            "    (local $frac_digit i32)",
            "    (local $ptr i32)",
            "    (local $len i32)",
            "    (local $neg i32)",
            "    (local $copy_i i32)",
            "    local.get $v",
            "    f64.const 0",
            "    f64.lt",
            "    local.set $neg",
            "    local.get $neg",
            "    if",
            "      local.get $v",
            "      f64.neg",
            "      local.set $v",
            "    end",
            "    local.get $v",
            "    f64.trunc",
            "    i64.trunc_f64_u",
            "    local.set $int_part",
            "    local.get $int_part",
            "    call $__fmt_u64",
            "    local.set $len",
            "    local.set $ptr",
            f"    i32.const {fmt}",
            "    local.set $copy_i",
            "    local.get $neg",
            "    if",
            "      local.get $copy_i",
            "      i32.const 45",
            "      i32.store8",
            "      local.get $copy_i",
            "      i32.const 1",
            "      i32.add",
            "      local.set $copy_i",
            "    end",
            "    block $copy_done",
            "      loop $copy_lp",
            "        local.get $len",
            "        i32.eqz",
            "        br_if $copy_done",
            "        local.get $copy_i",
            "        local.get $ptr",
            "        i32.load8_u",
            "        i32.store8",
            "        local.get $copy_i",
            "        i32.const 1",
            "        i32.add",
            "        local.set $copy_i",
            "        local.get $ptr",
            "        i32.const 1",
            "        i32.add",
            "        local.set $ptr",
            "        local.get $len",
            "        i32.const 1",
            "        i32.sub",
            "        local.set $len",
            "        br $copy_lp",
            "      end",
            "    end",
            "    local.get $copy_i",
            "    i32.const 46",
            "    i32.store8",
            "    local.get $copy_i",
            "    i32.const 1",
            "    i32.add",
            "    local.set $copy_i",
            "    local.get $v",
            "    local.get $v",
            "    f64.trunc",
            "    f64.sub",
            "    f64.const 10",
            "    f64.mul",
            "    f64.nearest",
            "    i32.trunc_f64_u",
            "    local.set $frac_digit",
            "    local.get $copy_i",
            "    local.get $frac_digit",
            "    i32.const 48",
            "    i32.add",
            "    i32.store8",
            f"    i32.const {fmt}",
            "    f64.convert_i32_u",
            "    local.get $neg",
            "    if (result f64)",
            "      f64.const 4",
            "    else",
            "      f64.const 3",
            "    end",
            "  )",
        ]
        self._funcs.append("\n".join(lines))

    def _emit_fstring_part_ptr_len(self, part, indent: str) -> bool:
        """Emit ptr/len f64 pairs for a supported f-string part."""
        if isinstance(part, str):
            offset, length = self._intern(part)
            self._emit(f"{indent}f64.const {float(offset)}")
            self._emit(f"{indent}f64.const {float(length)}")
            return True
        format_spec = getattr(part, "fstring_format_spec", "")
        if self._is_string_value(part):
            self._gen_expr(part, indent)
            self._gen_string_len_expr(part, indent)
            return True
        if format_spec not in ("", ".1f"):
            return False
        self._ensure_string_format_helpers()
        label = self._new_label()
        ptr_local = f"__fmt_ptr_{label}"
        len_local = f"__fmt_len_{label}"
        self._locals.update({ptr_local, len_local})
        self._gen_expr(part, indent)
        helper = "$__fmt_fixed1_tmpstr" if format_spec == ".1f" else "$__fmt_default_tmpstr"
        self._emit(f"{indent}call {helper}")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        return True

    def _gen_fstring_expr(self, node: FStringLiteral, indent: str) -> bool:
        """Lower a supported f-string by concatenating part ptr/len pairs."""
        if not node.parts:
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}i32.const 0")
            self._emit(f"{indent}global.set $__last_str_len")
            return True
        label = self._new_label()
        ptr_local = f"__fstr_ptr_{label}"
        len_local = f"__fstr_len_{label}"
        part_ptr = f"__fstr_part_ptr_{label}"
        part_len = f"__fstr_part_len_{label}"
        self._locals.update({ptr_local, len_local, part_ptr, part_len})
        self._ensure_str_concat_helper()
        first = True
        for part in node.parts:
            if not self._emit_fstring_part_ptr_len(part, indent):
                return False
            self._emit(f"{indent}local.set ${self._wat_symbol(part_len)}")
            self._emit(f"{indent}local.set ${self._wat_symbol(part_ptr)}")
            if first:
                self._emit(f"{indent}local.get ${self._wat_symbol(part_ptr)}")
                self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(part_len)}")
                self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
                first = False
            else:
                self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(part_ptr)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(part_len)}")
                self._emit(f"{indent}call $__str_concat")
                self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
                self._emit(f"{indent}local.get ${self._wat_symbol(part_len)}")
                self._emit(f"{indent}f64.add")
                self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit_last_str_len_from_f64(indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _is_sequence_expr(self, value) -> bool:
        """Return whether *value* is representable as a list/tuple pointer in WAT."""
        if isinstance(value, (ListLiteral, TupleLiteral, SetLiteral)):
            return True
        if isinstance(value, Identifier):
            return value.name in self._list_locals or value.name in self._tuple_locals
        if isinstance(value, CallExpr) and len(value.args) == 1:
            if _name(value.func) in (_LIST_NAMES | _TUPLE_NAMES | _SET_NAMES):
                return True
        if isinstance(value, CallExpr) and _name(value.func) in {"divmod", "sorted"}:
            return True
        if isinstance(value, (ListComprehension, SetComprehension, GeneratorExpr)):
            return True
        return False

    def _gen_unpack_assignment(self, target, value, indent: str) -> bool:
        """Lower tuple/starred unpacking from a list-like pointer value."""
        if not isinstance(target, (TupleLiteral, ListLiteral)) or not self._is_sequence_expr(value):
            return False
        elements = target.elements
        star_positions = [
            index for index, element in enumerate(elements)
            if isinstance(element, StarredExpr)
        ]
        if len(star_positions) > 1:
            return False
        for element in elements:
            if isinstance(element, Identifier):
                continue
            if isinstance(element, StarredExpr) and isinstance(element.value, Identifier):
                continue
            return False

        label = self._new_label()
        src_ptr = f"__unpack_ptr_{label}"
        src_len = f"__unpack_len_{label}"
        self._locals.update({src_ptr, src_len})
        self._gen_expr(value, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(src_len)}")

        def emit_load_at(index_from_start=None, index_from_end=None):
            self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            if index_from_start is not None:
                self._emit(f"{indent}i32.const {(index_from_start + 1) * 8}")
            else:
                self._emit(f"{indent}local.get ${self._wat_symbol(src_len)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const {index_from_end}")
                self._emit(f"{indent}i32.sub")
                self._emit(f"{indent}i32.const 8")
                self._emit(f"{indent}i32.mul")
                self._emit(f"{indent}i32.const 8")
                self._emit(f"{indent}i32.add")
            self._emit(f"{indent}i32.add")
            self._emit(f"{indent}f64.load")

        if not star_positions:
            for index, element in enumerate(elements):
                name = element.name
                self._locals.add(name)
                self._clear_assignment_tracking(name)
                emit_load_at(index_from_start=index)
                self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
            return True

        star_index = star_positions[0]
        prefix = elements[:star_index]
        suffix = elements[star_index + 1:]
        star_target = elements[star_index].value.name

        for index, element in enumerate(prefix):
            name = element.name
            self._locals.add(name)
            self._clear_assignment_tracking(name)
            emit_load_at(index_from_start=index)
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")

        for suffix_offset, element in enumerate(suffix):
            name = element.name
            self._locals.add(name)
            self._clear_assignment_tracking(name)
            emit_load_at(index_from_end=len(suffix) - suffix_offset)
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")

        star_ptr = f"__unpack_star_ptr_{label}"
        star_len = f"__unpack_star_len_{label}"
        star_idx = f"__unpack_star_idx_{label}"
        self._locals.update({star_ptr, star_len, star_idx, star_target})
        self._need_heap_ptr = True
        self._emit(f"{indent}local.get ${self._wat_symbol(src_len)}")
        self._emit(f"{indent}f64.const {float(len(prefix) + len(suffix))}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_len)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(star_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit_alloc_dynamic(star_ptr, indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(star_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(star_len)}")
        self._emit(f"{indent}f64.store")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_idx)}")
        blk = f"unpack_star_blk_{label}"
        loop = f"unpack_star_lp_{label}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_len)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const {len(prefix)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    f64.store")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(star_ptr)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_target)}")
        self._clear_assignment_tracking(star_target)
        self._list_locals.add(star_target)
        return True

    # -----------------------------------------------------------------------
    # match/case lowering helper
    # -----------------------------------------------------------------------

    def _emit(self, line: str):
        self._instrs.append(line)

    def _gen_stmts(self, stmts: list, indent: str):
        for stmt in stmts:
            self._gen_stmt(stmt, indent)

    def _collect_import_aliases(self, stmts: list) -> None:
        """Record simple import aliases for known native math lowerings."""
        recognized = {"sqrt", "floor", "ceil", "fabs", "pow"}
        for stmt in stmts:
            if isinstance(stmt, ImportStatement):
                module_alias = stmt.alias or stmt.module
                self._module_aliases[module_alias] = stmt.module
            elif isinstance(stmt, FromImportStatement) and stmt.module == "math":
                for imported_name, imported_alias in stmt.names:
                    local_name = imported_alias or imported_name
                    if imported_name in recognized:
                        self._imported_call_aliases[local_name] = f"math.{imported_name}"

    def _resolve_callable_alias(self, fname: str) -> str:
        """Resolve simple imported/module-qualified aliases for builtin lowering."""
        if fname in self._imported_call_aliases:
            return self._imported_call_aliases[fname]
        if "." in fname:
            module_name, attr_name = fname.split(".", 1)
            resolved_module = self._module_aliases.get(module_name, module_name)
            return f"{resolved_module}.{attr_name}"
        return fname

    def _returns_string_like(self, func_def: FunctionDef) -> bool:
        """Best-effort check for functions that return string-like values."""
        def _stmt_returns_string(stmt):
            if isinstance(stmt, ReturnStatement) and stmt.value is not None:
                return self._is_string_value(stmt.value) or isinstance(stmt.value, FStringLiteral)
            if isinstance(stmt, IfStatement):
                else_body = stmt.else_body or []
                return any(_stmt_returns_string(inner) for inner in stmt.body + else_body)
            return False

        return any(_stmt_returns_string(stmt) for stmt in func_def.body)

    def _exception_code_for(self, value) -> int:
        """Return a small numeric code for supported exception types."""
        exc_name = ""
        if isinstance(value, CallExpr):
            exc_name = _name(value.func)
        elif isinstance(value, Identifier):
            exc_name = value.name
        mapping = {
            "ValueError": 1,
            "RuntimeError": 2,
            "TypeError": 3,
            "AssertionError": 4,
        }
        return mapping.get(exc_name, 255 if value is not None else 255)

    def _closure_factory_spec(self, func_def: FunctionDef):
        """Return closure-factory lowering info for the supported make_counter-like shape."""
        if len(func_def.body) != 3:
            return None
        init_stmt, nested_stmt, return_stmt = func_def.body
        if not (
            isinstance(init_stmt, VariableDeclaration)
            and isinstance(nested_stmt, FunctionDef)
            and isinstance(return_stmt, ReturnStatement)
            and isinstance(return_stmt.value, Identifier)
            and _name(nested_stmt.name) == return_stmt.value.name
        ):
            return None
        if len(nested_stmt.body) != 3:
            return None
        nonlocal_stmt, assign_stmt, nested_return = nested_stmt.body
        capture_name = _name(init_stmt.name)
        if not (
            isinstance(nonlocal_stmt, LocalStatement)
            and capture_name in nonlocal_stmt.names
            and isinstance(assign_stmt, Assignment)
            and isinstance(assign_stmt.target, Identifier)
            and assign_stmt.target.name == capture_name
            and assign_stmt.op == "="
            and isinstance(nested_return, ReturnStatement)
            and isinstance(nested_return.value, Identifier)
            and nested_return.value.name == capture_name
        ):
            return None
        update_expr = assign_stmt.value
        if not (
            isinstance(update_expr, BinaryOp)
            and update_expr.op == "+"
            and isinstance(update_expr.left, Identifier)
            and update_expr.left.name == capture_name
            and isinstance(update_expr.right, NumeralLiteral)
            and float(update_expr.right.value) == 1.0
        ):
            return None
        return {
            "outer_name": _name(func_def.name),
            "nested_name": _name(nested_stmt.name),
            "capture_name": capture_name,
            "init_value": init_stmt.value,
        }

    def _emit_closure_factory_function(self, func_def: FunctionDef, emitted_name: str | None = None) -> bool:
        """Lower a supported closure-factory function plus its nested helper."""
        spec = self._closure_factory_spec(func_def)
        if spec is None:
            return False

        outer_name = emitted_name or spec["outer_name"]
        helper_name = f"{outer_name}__{spec['nested_name']}_closure"
        self._closure_factory_funcs[outer_name] = helper_name

        saved = self._save_func_state()
        self._locals = {"env"}
        self._emit("    ;; closure step: increment captured cell 0")
        self._emit("    local.get $env")
        self._emit("    i32.trunc_f64_u")
        self._emit("    i32.const 8")
        self._emit("    i32.add")
        self._emit("    local.get $env")
        self._emit("    i32.trunc_f64_u")
        self._emit("    i32.const 8")
        self._emit("    i32.add")
        self._emit("    f64.load")
        self._emit("    f64.const 1")
        self._emit("    f64.add")
        self._emit("    local.tee $env_val")
        self._emit("    f64.store")
        self._emit("    local.get $env_val")
        self._emit("    return")
        self._locals.add("env_val")
        body_instrs = list(self._instrs)
        lines = [f'  (func ${self._wat_symbol(helper_name)} (export "{helper_name}")']
        lines.append("    (param $env f64)")
        lines.append("    (result f64)")
        lines.append("    (local $env_val f64)")
        lines.extend(body_instrs)
        lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")
        self._funcs.append("\n".join(lines))
        self._restore_func_state(saved)

        saved = self._save_func_state()
        param_names = _real_params(func_def)
        self._locals = set(param_names)
        self._need_heap_ptr = True
        self._gen_list_alloc(ListLiteral([spec["init_value"]]), "    ")
        self._emit("    return")
        body_instrs = list(self._instrs)
        local_names = sorted(self._locals - set(param_names))
        wat_func_name = self._wat_symbol(outer_name)
        lines = [f'  (func ${wat_func_name} (export "{outer_name}")']
        for param_name in param_names:
            lines.append(f"    (param ${self._wat_symbol(param_name)} f64)")
        lines.append("    (result f64)")
        for local_name in local_names:
            lines.append(f"    (local ${self._wat_symbol(local_name)} f64)")
        lines.extend(body_instrs)
        lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")
        self._funcs.append("\n".join(lines))
        self._restore_func_state(saved)
        return True

    def _gen_stmt(self, stmt, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        if isinstance(stmt, VariableDeclaration):
            if isinstance(stmt.name, (TupleLiteral, ListLiteral)) and \
                    self._gen_unpack_assignment(stmt.name, stmt.value, indent):
                self._emit(f"{indent};; unpacking declaration lowered")
            else:
                name = _name(stmt.name)
                self._locals.add(name)
                self._emit(f"{indent};; let {name} = ...")
                self._gen_expr(stmt.value, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                self._update_assignment_tracking(name, stmt.value, indent)

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
                    self._update_assignment_tracking(name, stmt.value, indent)
                else:
                    # Compound assignment: a op= b
                    self._emit(f"{indent};; {name} {op} ...")
                    self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
                    self._gen_augmented_op(op, stmt.value, indent)
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                    self._clear_assignment_tracking(name)
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
            elif self._gen_unpack_assignment(target, stmt.value, indent):
                self._emit(f"{indent};; unpacking assignment lowered")
            else:
                self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")

        elif isinstance(stmt, AnnAssignment):
            if isinstance(stmt.target, Identifier):
                name = stmt.target.name
                self._locals.add(name)
                self._emit(f"{indent};; annotated assignment {name}: ...")
                if stmt.value is None:
                    self._emit(f"{indent}f64.const 0")
                    self._clear_assignment_tracking(name)
                else:
                    self._gen_expr(stmt.value, indent)
                    self._update_assignment_tracking(name, stmt.value, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
            else:
                self._emit(f"{indent};; annotated assignment with complex target (nop in WAT)")

        elif isinstance(stmt, ChainedAssignment):
            tmp_name = f"__chain_{self._new_label()}"
            self._locals.add(tmp_name)
            self._emit(f"{indent};; chained assignment")
            self._gen_expr(stmt.value, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(tmp_name)}")
            for target in stmt.targets:
                if isinstance(target, Identifier):
                    name = target.name
                    self._locals.add(name)
                    self._emit(f"{indent}local.get ${self._wat_symbol(tmp_name)}")
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                    self._update_assignment_tracking(name, stmt.value, indent)
                else:
                    self._emit(
                        f"{indent};; chained assignment target {type(target).__name__} "
                        f"not lowerable in WAT"
                    )

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
                resolved_fname = self._resolve_callable_alias(fname)
                if fname in _PRINT_NAMES:
                    self._gen_print(expr, indent)
                elif resolved_fname == "asyncio.run" and len(expr.args) == 1:
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}drop")
                elif resolved_fname == "asyncio.sleep":
                    self._emit(f"{indent}f64.const 0  ;; asyncio.sleep no-op in WAT")
                    self._emit(f"{indent}drop")
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
                    real_params = self._func_real_params.get(lowered, [])
                    if lowered in self._static_method_names and real_params[:1] == ["cls"]:
                        self._emit(f"{indent}f64.const 0  ;; implicit cls")
                        self._gen_call_args(expr, indent, lowered, skip_params=1)
                    else:
                        self._gen_call_args(expr, indent, lowered)
                    self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
                    self._emit(f"{indent}drop")
                elif self._class_method_target_from_call(expr):
                    lowered = self._class_method_target_from_call(expr)
                    obj_expr = expr.func.obj
                    cls = self._var_class_types.get(_name(obj_expr))
                    self._emit(f"{indent};; instance call {fname}(...)")
                    if lowered in self._static_method_names:
                        # @staticmethod/@classmethod: no instance pushed
                        real_params = self._func_real_params.get(lowered, [])
                        if real_params[:1] == ["cls"]:
                            self._emit(f"{indent}f64.const 0  ;; implicit cls")
                            self._gen_call_args(expr, indent, lowered, skip_params=1)
                        else:
                            self._gen_call_args(expr, indent, lowered)
                    elif cls and self._is_stateful_class(cls):
                        self._gen_expr(obj_expr, indent)   # push actual f64 pointer
                        self._gen_call_args(expr, indent, lowered, skip_params=1)
                    else:
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
                        self._gen_call_args(expr, indent, lowered, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
                    self._emit(f"{indent}drop")
                elif fname in self._closure_locals:
                    helper = self._closure_locals[fname]
                    self._emit(f"{indent};; call closure {fname}(...)")
                    self._emit(f"{indent}local.get ${self._wat_symbol(fname)}")
                    self._emit(f"{indent}call ${self._wat_symbol(helper)}")
                    self._emit(f"{indent}drop")
                elif fname in self._lambda_locals:
                    # Indirect call through lambda table (statement context — result dropped).
                    lam_fn = self._lambda_locals[fname]
                    arity = len(self._func_real_params.get(lam_fn, []))
                    self._emit(f"{indent};; call lambda {fname} via table (arity={arity})")
                    for arg in expr.args[:arity]:
                        self._gen_expr(arg, indent)
                    for _ in range(arity - len(expr.args)):
                        self._emit(f"{indent}f64.const 0")
                    self._emit(f"{indent}local.get ${self._wat_symbol(fname)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    param_sig = " ".join("f64" for _ in range(arity))
                    if param_sig:
                        self._emit(
                            f"{indent}call_indirect (table $lambda_table)"
                            f" (param {param_sig}) (result f64)"
                        )
                    else:
                        self._emit(
                            f"{indent}call_indirect (result f64)"
                        )
                    self._emit(f"{indent}drop")
                elif self._resolve_virtual_file_op(expr):
                    _alias, path, mode, method = self._resolve_virtual_file_op(expr)
                    if method == "write" and expr.args and isinstance(expr.args[0], StringLiteral):
                        text = expr.args[0].value
                        if "a" in mode:
                            self._virtual_file_contents[path] = (
                                self._virtual_file_contents.get(path, "") + text
                            )
                        else:
                            self._virtual_file_contents[path] = text
                        self._emit(f"{indent};; virtual file write {path!r}")
                    elif method == "read":
                        self._emit(f"{indent};; virtual file read {path!r} (result dropped)")
                    else:
                        self._emit(f"{indent};; virtual file op {method} omitted in WAT")
                elif (isinstance(expr.func, AttributeAccess)
                      and isinstance(expr.func.obj, Identifier)
                      and expr.func.attr in self._dispatch_func_names):
                    # Dynamic dispatch: receiver type unknown at compile time.
                    dispatch_fn = self._dispatch_func_names[expr.func.attr]
                    self._emit(f"{indent};; dynamic dispatch {expr.func.attr}()")
                    self._gen_expr(expr.func.obj, indent)
                    self._emit(f"{indent}call ${dispatch_fn}")
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

        elif isinstance(stmt, (ImportStatement, FromImportStatement)):
            self._emit(f"{indent};; import metadata already collected (nop in WAT)")

        elif isinstance(stmt, DelStatement):
            if isinstance(stmt.target, Identifier):
                name = stmt.target.name
                if name in self._locals:
                    self._emit(f"{indent}f64.const 0")
                    self._emit(f"{indent}local.set ${self._wat_symbol(name)}")
                self._clear_assignment_tracking(name)
            else:
                self._emit(f"{indent}nop")

        elif isinstance(stmt, (GlobalStatement, LocalStatement)):
            names = ", ".join(stmt.names)
            self._emit(f"{indent};; {type(stmt).__name__}: {names} (nop in WAT)")

        elif isinstance(stmt, AssertStatement):
            fail_label = f"assert_ok_{self._new_label()}"
            self._emit(f"{indent}block ${fail_label}")
            self._gen_cond(stmt.test, indent + "  ")
            self._emit(f"{indent}  br_if ${fail_label}")
            if self._try_stack:
                ctx = self._try_stack[-1]
                self._emit(f"{indent}  f64.const 4")
                self._emit(f"{indent}  local.set ${self._wat_symbol(ctx['code_local'])}")
                self._emit(f"{indent}  br ${ctx['label']}")
            else:
                self._emit(f"{indent}  i32.const 4")
                self._emit(f"{indent}  global.set $__last_exc_code")
                self._emit(f"{indent}  unreachable")
            self._emit(f"{indent}end")

        elif isinstance(stmt, RaiseStatement):
            if self._try_stack:
                ctx = self._try_stack[-1]
                code = self._exception_code_for(stmt.value)
                self._emit(f"{indent}f64.const {float(code)}")
                self._emit(f"{indent}local.set ${self._wat_symbol(ctx['code_local'])}")
                self._emit(f"{indent}br ${ctx['label']}")
            else:
                code = self._exception_code_for(stmt.value)
                self._emit(f"{indent}i32.const {code}")
                self._emit(f"{indent}global.set $__last_exc_code")
                self._emit(f"{indent}unreachable")

        elif isinstance(stmt, TryStatement):
            label = self._new_label()
            code_local = f"__exc_code_{label}"
            handled_local = f"__exc_handled_{label}"
            self._locals.update({code_local, handled_local})
            end_label = f"try_end_{label}"
            done_label = f"try_done_{label}"
            parent_ctx = self._try_stack[-1] if self._try_stack else None

            self._emit(f"{indent};; try")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}local.set ${self._wat_symbol(code_local)}")
            self._emit(f"{indent}block ${end_label}")
            self._try_stack.append({"code_local": code_local, "label": end_label})
            self._gen_stmts(stmt.body, indent + "  ")
            self._try_stack.pop()
            self._emit(f"{indent}end")

            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}local.set ${self._wat_symbol(handled_local)}")
            if stmt.handlers:
                for handler in stmt.handlers:
                    expected = self._exception_code_for(handler.exc_type)
                    match_label = f"try_match_{self._new_label()}"
                    self._emit(f"{indent}block ${match_label}")
                    self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                    self._emit(f"{indent}  f64.const {float(expected)}")
                    self._emit(f"{indent}  f64.ne")
                    self._emit(f"{indent}  br_if ${match_label}")
                    if handler.name:
                        self._locals.add(handler.name)
                        self._emit(f"{indent}  f64.const 0")
                        self._emit(f"{indent}  local.set ${self._wat_symbol(handler.name)}")
                    self._emit(f"{indent}  f64.const 1")
                    self._emit(f"{indent}  local.set ${self._wat_symbol(handled_local)}")
                    self._emit(f"{indent}  f64.const 0")
                    self._emit(f"{indent}  local.set ${self._wat_symbol(code_local)}")
                    self._gen_stmts(handler.body, indent + "  ")
                    self._emit(f"{indent}end")

            if stmt.else_body:
                self._emit(f"{indent}local.get ${self._wat_symbol(handled_local)}")
                self._emit(f"{indent}f64.const 0")
                self._emit(f"{indent}f64.eq")
                self._emit(f"{indent}local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}f64.const 0")
                self._emit(f"{indent}f64.eq")
                self._emit(f"{indent}i32.and")
                self._emit(f"{indent}if")
                self._gen_stmts(stmt.else_body, indent + "  ")
                self._emit(f"{indent}end")

            self._emit(f"{indent}local.get ${self._wat_symbol(code_local)}")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}f64.ne")
            self._emit(f"{indent}if")
            if parent_ctx is not None:
                self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}  local.set ${self._wat_symbol(parent_ctx['code_local'])}")
                self._emit(f"{indent}  br ${parent_ctx['label']}")
            else:
                self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}  i32.trunc_f64_u")
                self._emit(f"{indent}  global.set $__last_exc_code")
                self._emit(f"{indent}  unreachable")
            self._emit(f"{indent}end")

            if stmt.finally_body:
                self._emit(f"{indent};; finally")
                self._gen_stmts(stmt.finally_body, indent)

        elif isinstance(stmt, WithStatement):
            # Best-effort: lower the body; __enter__/__exit__ hooks are not
            # callable through the WAT f64 model without a vtable.
            self._emit(
                f"{indent};; with (context-manager hooks not lowerable in WAT)"
            )
            saved_aliases = dict(self._open_aliases)
            for _, alias in stmt.items:
                if alias:
                    self._locals.add(alias)
                    self._emit(
                        f"{indent}f64.const 0  "
                        f";; placeholder for 'as {alias}' binding"
                    )
                    self._emit(f"{indent}local.set ${self._wat_symbol(alias)}")
            for expr, alias in stmt.items:
                if not alias:
                    continue
                if not (isinstance(expr, CallExpr) and _name(expr.func) == "open" and expr.args):
                    continue
                path_arg = expr.args[0]
                mode = "r"
                if len(expr.args) >= 2 and isinstance(expr.args[1], StringLiteral):
                    mode = expr.args[1].value
                if isinstance(path_arg, StringLiteral):
                    self._open_aliases[alias] = (path_arg.value, mode)
            self._gen_stmts(stmt.body, indent)
            self._open_aliases = saved_aliases

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

        # Extract sep= and end= keyword arguments (StringLiteral values only).
        sep_val = " "   # default separator
        end_val = "\n"  # default end
        for kw_name, kw_node in (call_expr.keywords or []):
            if kw_name == "sep" and isinstance(kw_node, StringLiteral):
                sep_val = kw_node.value
            elif kw_name == "end" and isinstance(kw_node, StringLiteral):
                end_val = kw_node.value

        for i, arg in enumerate(args):
            if i > 0:
                self._emit_print_separator(sep_val, indent)
            if isinstance(arg, StringLiteral):
                offset, length = self._intern(arg.value)
                self._emit(f"{indent}i32.const {offset}   ;; str ptr")
                self._emit(f"{indent}i32.const {length}   ;; str len")
                self._emit(f"{indent}call $print_str")
            elif isinstance(arg, FStringLiteral):
                if self._gen_fstring_expr(arg, indent):
                    tmp_len = f"__print_fstr_len_{self._new_label()}"
                    self._locals.add(tmp_len)
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
                    self._emit(f"{indent}call $print_str")
                else:
                    self._emit(f"{indent}f64.const 0")
                    self._emit(f"{indent}call $print_f64")
            elif isinstance(arg, BooleanLiteral):
                self._emit(f"{indent}i32.const {1 if arg.value else 0}")
                self._emit(f"{indent}call $print_bool")
            elif isinstance(arg, Identifier) and arg.name in self._string_len_locals:
                len_local = self._string_len_locals[arg.name]
                self._emit(f"{indent}local.get ${self._wat_symbol(arg.name)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}call $print_str")
            elif isinstance(arg, Identifier) and arg.name in self._tuple_locals:
                self._emit_print_sequence(arg.name, "(", ")", indent)
            elif isinstance(arg, Identifier) and arg.name in self._list_locals:
                self._emit_print_sequence(arg.name, "[", "]", indent)
            elif isinstance(arg, CallExpr) and _name(arg.func) in self._string_return_funcs:
                tmp_len = f"__print_call_len_{self._new_label()}"
                self._locals.add(tmp_len)
                self._gen_expr(arg, indent)
                self._emit(f"{indent}global.get $__last_str_len")
                self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
                self._emit(f"{indent}call $print_str")
            elif isinstance(arg, NumeralLiteral) and "." in arg.value:
                # Float literal (e.g. 1.0, 3.14) — always print with decimal point.
                self._gen_expr(arg, indent)
                self._emit(f"{indent}call $print_f64_float")
            else:
                self._gen_expr(arg, indent)
                self._emit(f"{indent}call $print_f64")
        self._emit_print_end(end_val, indent)

    def _emit_print_separator(self, sep_val: str, indent: str):
        """Emit WAT instructions for the print separator."""
        if sep_val == " ":
            self._emit(f"{indent}call $print_sep")
        elif sep_val == "":
            pass  # no separator
        else:
            offset, length = self._intern(sep_val)
            self._emit(f"{indent}i32.const {offset}   ;; sep ptr")
            self._emit(f"{indent}i32.const {length}   ;; sep len")
            self._emit(f"{indent}call $print_str")

    def _emit_print_end(self, end_val: str, indent: str):
        """Emit WAT instructions for the print end string."""
        if end_val == "\n":
            self._emit(f"{indent}call $print_newline")
        elif end_val == "":
            pass  # no end
        else:
            offset, length = self._intern(end_val)
            self._emit(f"{indent}i32.const {offset}   ;; end ptr")
            self._emit(f"{indent}i32.const {length}   ;; end len")
            self._emit(f"{indent}call $print_str")

    def _emit_print_sequence(self, name: str, opening: str, closing: str, indent: str):
        """Emit Python-like printing for a list/tuple local."""
        lbl = self._new_label()
        idx_local = f"__print_idx_{lbl}"
        len_local = f"__print_len_{lbl}"
        self._locals.add(idx_local)
        self._locals.add(len_local)
        open_ptr, open_len = self._intern(opening)
        close_ptr, close_len = self._intern(closing)
        comma_ptr, comma_len = self._intern(", ")
        self._emit(f"{indent}i32.const {open_ptr}")
        self._emit(f"{indent}i32.const {open_len}")
        self._emit(f"{indent}call $print_str")
        self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")
        blk = f"print_seq_blk_{lbl}"
        loop = f"print_seq_lp_{lbl}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 0")
        self._emit(f"{indent}    f64.gt")
        self._emit(f"{indent}    if")
        self._emit(f"{indent}      i32.const {comma_ptr}")
        self._emit(f"{indent}      i32.const {comma_len}")
        self._emit(f"{indent}      call $print_str")
        self._emit(f"{indent}    end")
        self._emit(f"{indent}    local.get ${self._wat_symbol(name)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    call $print_f64")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}i32.const {close_ptr}")
        self._emit(f"{indent}i32.const {close_len}")
        self._emit(f"{indent}call $print_str")

    # -----------------------------------------------------------------------
    # Expression generation  (each call pushes exactly one f64)
    # -----------------------------------------------------------------------

    def _gen_expr(self, node, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
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
            offset, byte_len = self._intern(node.value)
            self._emit(f"{indent}f64.const {float(offset)}  ;; str offset (not a numeric value)")
            self._emit(f"{indent}i32.const {byte_len}")
            self._emit(f"{indent}global.set $__last_str_len")

        elif isinstance(node, CallExpr) and self._virtual_file_read_content(node) is not None:
            content = self._virtual_file_read_content(node)
            offset, byte_len = self._intern(content)
            self._emit(f"{indent}f64.const {float(offset)}  ;; virtual file read")
            self._emit(f"{indent}i32.const {byte_len}")
            self._emit(f"{indent}global.set $__last_str_len")

        elif isinstance(node, FStringLiteral):
            if not self._gen_fstring_expr(node, indent):
                self._emit(f"{indent}f64.const 0  ;; unsupported expr: FStringLiteral")

        elif isinstance(node, BytesLiteral):
            # Bytes literals stored in linear memory just like strings
            offset, _ = self._intern(node.value)
            self._emit(f"{indent}f64.const {float(offset)}  ;; bytes offset")

        elif isinstance(node, DictLiteral):
            if not self._gen_static_dict_alloc(node, indent):
                self._emit(f"{indent}f64.const 0  ;; unsupported expr: DictLiteral")

        elif isinstance(node, Identifier):
            if node.name in self._locals:
                self._emit(f"{indent}local.get ${self._wat_symbol(node.name)}")
                if node.name in self._string_len_locals:
                    len_local = self._string_len_locals[node.name]
                    self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
                    self._emit_last_str_len_from_f64(indent)
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

        elif isinstance(node, ConditionalExpr):
            self._gen_cond(node.condition, indent)
            self._emit(f"{indent}if (result f64)")
            self._gen_expr(node.true_expr, indent + "  ")
            self._emit(f"{indent}else")
            self._gen_expr(node.false_expr, indent + "  ")
            self._emit(f"{indent}end")

        elif isinstance(node, NamedExpr):
            if isinstance(node.target, Identifier):
                target_name = node.target.name
                self._locals.add(target_name)
                self._gen_expr(node.value, indent)
                self._emit(f"{indent}local.tee ${self._wat_symbol(target_name)}")
            else:
                self._gen_expr(node.value, indent)

        elif isinstance(node, CallExpr):
            # super().method(args) — lower to direct parent WAT call (expression ctx).
            _super_wat = self._resolve_super_call(node)
            if _super_wat is not None:
                self._emit(f"{indent}local.get ${self._wat_symbol('self')}")
                self._gen_call_args(node, indent, _super_wat, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(_super_wat)}")
                return
            fname = _name(node.func)
            resolved_fname = self._resolve_callable_alias(fname)
            if fname in _PRINT_NAMES:
                self._emit(f"{indent}f64.const 0  ;; print() used as expression")
            elif resolved_fname == "asyncio.run" and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
            elif resolved_fname == "asyncio.sleep":
                self._emit(f"{indent}f64.const 0  ;; asyncio.sleep no-op in WAT")
            elif fname in _ABS_NAMES and len(node.args) == 1:
                # abs(x) → f64.abs
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.abs")
            elif resolved_fname in {"math.sqrt", "sqrt"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.sqrt")
            elif resolved_fname in {"math.floor", "floor"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.floor")
            elif resolved_fname in {"math.ceil", "ceil"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.ceil")
            elif resolved_fname in {"math.fabs", "fabs"} and len(node.args) == 1:
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
            elif fname in _INT_NAMES and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, StringLiteral):
                    try:
                        parsed = int(float(arg.value.strip()))
                    except ValueError:
                        self._emit(f"{indent}f64.const 0  ;; int() parse failure")
                    else:
                        self._emit(f"{indent}f64.const {float(parsed)}")
                else:
                    self._gen_expr(arg, indent)
                    self._emit(f"{indent}i32.trunc_f64_s")
                    self._emit(f"{indent}f64.convert_i32_s")
            elif fname in _POW_NAMES and len(node.args) == 2:
                self._gen_expr(node.args[0], indent)
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}call $pow_f64")
            elif fname in _STR_NAMES and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
            elif fname in _LIST_NAMES and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, (ListComprehension, GeneratorExpr)) and \
                        self._gen_simple_comprehension_list(arg, indent):
                    pass
                elif isinstance(arg, CallExpr) and _name(arg.func) in self._sequence_func_names:
                    self._gen_expr(arg, indent)
                elif isinstance(arg, CallExpr) and _name(arg.func) in _ZIP_NAMES and \
                        self._gen_static_zip_list(arg, indent):
                    pass
                elif isinstance(arg, (ListLiteral, TupleLiteral, DictLiteral)):
                    self._gen_expr(arg, indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; unsupported call: {fname}(...)")
            elif fname in _TUPLE_NAMES and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, (ListLiteral, TupleLiteral)):
                    self._gen_expr(arg, indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; unsupported call: {fname}(...)")
            elif fname in _SET_NAMES and len(node.args) == 1:
                elements = self._static_set_elements(node.args[0])
                if elements is not None:
                    self._gen_list_alloc(ListLiteral(elements), indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; unsupported call: {fname}(...)")
            elif fname == "divmod" and len(node.args) == 2:
                self._gen_divmod_alloc(node.args[0], node.args[1], indent)
            elif fname == "sorted" and len(node.args) >= 1 and self._gen_sorted_copy(node.args[0], indent):
                pass
            elif fname in _SUM_NAMES and 1 <= len(node.args) <= 2:
                self._emit_sum_over_pointer(node.args[0], indent)
                if len(node.args) == 2:
                    self._gen_expr(node.args[1], indent)
                    self._emit(f"{indent}f64.add")
            elif fname in self._defined_func_names:
                # Known WAT function — emit args then call
                self._gen_call_args(node, indent, fname)
                self._emit(f"{indent}call ${self._wat_symbol(fname)}")
                if fname in self._string_return_funcs:
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._emit(f"{indent}drop")
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
                real_params = self._func_real_params.get(lowered, [])
                if lowered in self._static_method_names and real_params[:1] == ["cls"]:
                    self._emit(f"{indent}f64.const 0  ;; implicit cls")
                    self._gen_call_args(node, indent, lowered, skip_params=1)
                else:
                    self._gen_call_args(node, indent, lowered)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            elif fname in self._closure_locals:
                helper = self._closure_locals[fname]
                self._emit(f"{indent}local.get ${self._wat_symbol(fname)}")
                self._emit(f"{indent}call ${self._wat_symbol(helper)}")
            elif fname == "cls" and self._current_class in self._class_ctor_names:
                ctor = self._class_ctor_names[self._current_class]
                if self._is_stateful_class(self._current_class):
                    self._emit_stateful_ctor(
                        self._current_class, ctor, node, indent, keep_ref=True
                    )
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                    self._gen_call_args(node, indent, ctor, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
            elif self._class_method_target_from_call(node):
                lowered = self._class_method_target_from_call(node)
                obj_expr = node.func.obj
                cls = self._var_class_types.get(_name(obj_expr))
                if lowered in self._static_method_names:
                    # @staticmethod/@classmethod: no instance pushed
                    real_params = self._func_real_params.get(lowered, [])
                    if real_params[:1] == ["cls"]:
                        self._emit(f"{indent}f64.const 0  ;; implicit cls")
                        self._gen_call_args(node, indent, lowered, skip_params=1)
                    else:
                        self._gen_call_args(node, indent, lowered)
                elif cls and self._is_stateful_class(cls):
                    self._gen_expr(obj_expr, indent)   # push actual f64 pointer
                    self._gen_call_args(node, indent, lowered, skip_params=1)
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                    self._gen_call_args(node, indent, lowered, skip_params=1)
                self._emit(f"{indent}call ${self._wat_symbol(lowered)}")
            elif fname in self._lambda_locals:
                # Indirect call through lambda table.
                lam_fn = self._lambda_locals[fname]
                arity = len(self._func_real_params.get(lam_fn, []))
                self._emit(f"{indent};; call lambda {fname} via table (arity={arity})")
                for arg in node.args[:arity]:
                    self._gen_expr(arg, indent)
                # Pad missing args with 0.0.
                for _ in range(arity - len(node.args)):
                    self._emit(f"{indent}f64.const 0")
                # Push table index.
                self._emit(f"{indent}local.get ${self._wat_symbol(fname)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                # Emit call_indirect with inline type.
                param_sig = " ".join("f64" for _ in range(arity))
                if param_sig:
                    self._emit(
                        f"{indent}call_indirect (param {param_sig}) (result f64)"
                    )
                else:
                    self._emit(
                        f"{indent}call_indirect (result f64)"
                    )
            elif (isinstance(node.func, AttributeAccess)
                  and isinstance(node.func.obj, Identifier)
                  and node.func.attr in self._dispatch_func_names):
                # Dynamic dispatch: receiver type unknown at compile time.
                dispatch_fn = self._dispatch_func_names[node.func.attr]
                obj_expr = node.func.obj
                self._emit(f"{indent};; dynamic dispatch {node.func.attr}()")
                self._gen_expr(obj_expr, indent)
                self._emit(f"{indent}call ${dispatch_fn}")
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
            # Register lambda in the module-level table; its table index is its f64 value.
            table_idx = len(self._lambda_table)
            self._lambda_table.append(lam_name)
            self._emit(f"{indent}f64.const {float(table_idx)}  ;; lambda ${wat_lam} table idx")

        elif isinstance(node, (ListComprehension, SetComprehension,
                                DictComprehension, GeneratorExpr)):
            if isinstance(node, DictComprehension) and self._gen_simple_dict_comprehension(node, indent):
                return
            if self._gen_filtered_or_nested_comprehension_list(node, indent):
                return
            if isinstance(node, (ListComprehension, SetComprehension)) \
                    and self._gen_simple_comprehension_list(node, indent):
                return
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
            iterable_name = (
                _name(clause.iterable)
                if clause and isinstance(clause.iterable, Identifier) else None
            )
            is_list_comp = (
                len(node.clauses) == 1
                and (iterable_name in self._list_locals or iterable_name in self._tuple_locals)
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
                self._emit_counted_loop_increment(iter_var, lp, indent + "    ")
                self._emit(f"{indent}  end  ;; comp loop")
                self._emit(f"{indent}end  ;; comp block")
                self._emit(f"{indent}local.get ${self._wat_symbol(acc_var)}")
            elif is_list_comp:
                # [elem for x in list_var] — iterate using list header.
                n2 = self._new_label()
                iter_var_raw = (
                    _name(clause.target)
                    if isinstance(clause.target, Identifier) else f"__li_{n2}"
                )
                self._locals.add(iter_var_raw)
                acc_var2 = f"__lacc_{n2}"
                idx_var2 = f"__lidx_{n2}"
                len_var2 = f"__llen_{n2}"
                for loc in (acc_var2, idx_var2, len_var2):
                    self._locals.add(loc)
                blk2 = f"lcomp_blk_{n2}"
                lp2 = f"lcomp_lp_{n2}"

                self._emit(f"{indent};; listcomp over list variable {iterable_name!r}")
                # Load length from list header (offset 0).
                self._emit(f"{indent}local.get ${self._wat_symbol(iterable_name)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}f64.load")
                self._emit(f"{indent}local.set ${self._wat_symbol(len_var2)}")
                self._emit(f"{indent}f64.const 0")
                self._emit(f"{indent}local.set ${self._wat_symbol(idx_var2)}")
                self._emit(f"{indent}f64.const 0")
                self._emit(f"{indent}local.set ${self._wat_symbol(acc_var2)}")
                self._emit(f"{indent}block ${blk2}")
                self._emit(f"{indent}  loop ${lp2}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(idx_var2)}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(len_var2)}")
                self._emit(f"{indent}    f64.ge")
                self._emit(f"{indent}    br_if ${blk2}")
                # Load element: base + 8 + idx*8.
                self._emit(f"{indent}    local.get ${self._wat_symbol(iterable_name)}")
                self._emit(f"{indent}    i32.trunc_f64_u")
                self._emit(f"{indent}    local.get ${self._wat_symbol(idx_var2)}")
                self._emit(f"{indent}    i32.trunc_f64_u")
                self._emit(f"{indent}    i32.const 8")
                self._emit(f"{indent}    i32.mul")
                self._emit(f"{indent}    i32.const 8")
                self._emit(f"{indent}    i32.add")
                self._emit(f"{indent}    i32.add")
                self._emit(f"{indent}    f64.load")
                self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var_raw)}")
                self._gen_expr(node.element, indent + "    ")
                self._emit(f"{indent}    local.set ${self._wat_symbol(acc_var2)}")
                self._emit(f"{indent}    local.get ${self._wat_symbol(idx_var2)}")
                self._emit(f"{indent}    f64.const 1")
                self._emit(f"{indent}    f64.add")
                self._emit(f"{indent}    local.set ${self._wat_symbol(idx_var2)}")
                self._emit(f"{indent}    br ${lp2}")
                self._emit(f"{indent}  end  ;; lcomp loop")
                self._emit(f"{indent}end  ;; lcomp block")
                self._emit(f"{indent}local.get ${self._wat_symbol(acc_var2)}")
            else:
                self._emit(
                    f"{indent}f64.const 0  "
                    f";; unsupported expr: {type(node).__name__} "
                    f"(collections not representable as f64)"
                )

        elif (isinstance(node, AttributeAccess)
              and isinstance(node.obj, Identifier)):
            # self.attr or known_var.attr — field load or @property getter call.
            obj_name = node.obj.name
            if obj_name == "self" and self._current_class:
                cls = self._current_class
            else:
                cls = self._var_class_types.get(obj_name)
            # Check for @property getter first (takes priority over field load)
            prop_key = f"{cls}.{node.attr}" if cls else None
            prop_fn = self._property_getters.get(prop_key) if prop_key else None
            if prop_fn is not None:
                self._emit(f"{indent};; @property {obj_name}.{node.attr}()")
                if cls and self._is_stateful_class(cls):
                    self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                self._emit(f"{indent}call ${self._wat_symbol(prop_fn)}")
            else:
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

        elif isinstance(node, (ListLiteral, TupleLiteral, SetLiteral)):
            self._gen_list_alloc(node, indent)

        elif isinstance(node, IndexAccess):
            obj = node.obj
            if isinstance(obj, Identifier) and (
                obj.name in self._list_locals or obj.name in self._tuple_locals
            ):
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
            elif isinstance(obj, Identifier) and obj.name in self._string_len_locals:
                sname = obj.name
                if isinstance(node.index, SliceExpr):
                    # s[start:stop] — call $__str_slice, result is new heap ptr (f64).
                    self._ensure_str_slice_helper()
                    self._emit(f"{indent};; {sname}[start:stop] — string slice")
                    self._emit(f"{indent}local.get ${self._wat_symbol(sname)}")
                    # start default 0, stop default = length
                    if node.index.start:
                        self._gen_expr(node.index.start, indent)
                    else:
                        self._emit(f"{indent}f64.const 0")
                    if node.index.stop:
                        self._gen_expr(node.index.stop, indent)
                    else:
                        len_local = self._string_len_locals[sname]
                        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
                    self._emit(f"{indent}call $__str_slice")
                else:
                    # s[i] — return byte value at offset i as f64.
                    self._emit(f"{indent};; {sname}[i] — string byte access")
                    self._emit(f"{indent}local.get ${self._wat_symbol(sname)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._gen_expr(node.index, indent)
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}i32.add")
                    self._emit(f"{indent}i32.load8_u")
                    self._emit(f"{indent}f64.convert_i32_u  ;; char code as f64")
            elif isinstance(obj, Identifier) and obj.name in self._dict_key_maps \
                    and isinstance(node.index, StringLiteral):
                key_map = self._dict_key_maps[obj.name]
                if node.index.value in key_map:
                    element_index = key_map[node.index.value]
                    self._emit(f"{indent};; {obj.name}[{node.index.value!r}]")
                    self._emit(f"{indent}local.get ${self._wat_symbol(obj.name)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}i32.const {(element_index + 1) * 8}")
                    self._emit(f"{indent}i32.add")
                    self._emit(f"{indent}f64.load")
                else:
                    self._emit(f"{indent}f64.const 0  ;; unknown dict key: {node.index.value}")
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
    # Heap allocation helpers — use $ml_alloc instead of inline bump pointer
    # -----------------------------------------------------------------------

    def _emit_alloc(self, size: int, ptr_local: str, indent: str) -> None:
        """Allocate *size* bytes via $ml_alloc; store result (f64) in ptr_local."""
        self._emit(f"{indent}i32.const {size}")
        self._emit_alloc_dynamic(ptr_local, indent)

    def _emit_alloc_dynamic(self, ptr_local: str, indent: str) -> None:
        """Call $ml_alloc with size already on stack (i32); store result (f64) in ptr_local."""
        self._emit(f"{indent}call $ml_alloc")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")

    def _emit_free(self, ptr_local: str, size: int, indent: str) -> None:
        """Return a constant-size block at ptr_local (f64) to the free list."""
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const {size}")
        self._emit(f"{indent}call $ml_free")

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
        if op in ("in", "not in"):
            self._emit_membership_cmp(node.left, right, indent, negate=op == "not in")
            return
        self._gen_expr(node.left, indent)
        self._gen_expr(right, indent)
        _cmp_wat = {
            "==": "f64.eq", "!=": "f64.ne",
            "<":  "f64.lt", "<=": "f64.le",
            ">":  "f64.gt", ">=": "f64.ge",
            "is": "f64.eq", "is not": "f64.ne",
        }
        self._emit(f"{indent}{_cmp_wat.get(op, 'f64.eq')}")

    def _emit_membership_cmp(self, left, right, indent: str, negate: bool = False):
        """Push i32 for ``left in right`` when *right* is a literal list/tuple."""
        if isinstance(right, (ListLiteral, TupleLiteral)):
            tmp_name = f"__in_left_{self._new_label()}"
            self._locals.add(tmp_name)
            self._gen_expr(left, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(tmp_name)}")
            if not right.elements:
                self._emit(f"{indent}i32.const 0")
            else:
                for index, elem in enumerate(right.elements):
                    self._emit(f"{indent}local.get ${self._wat_symbol(tmp_name)}")
                    self._gen_expr(elem, indent)
                    self._emit(f"{indent}f64.eq")
                    if index:
                        self._emit(f"{indent}i32.or")
            if negate:
                self._emit(f"{indent}i32.eqz")
            return

        self._gen_expr(left, indent)
        self._gen_expr(right, indent)
        self._emit(f"{indent}f64.eq")
        if negate:
            self._emit(f"{indent}i32.eqz")

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

    def _ensure_str_concat_helper(self):
        """Emit the $__str_concat WAT helper function once per module.

        Signature: (ptr1: f64, len1: f64, ptr2: f64, len2: f64) -> f64 (new ptr)
        Copies bytes from both source strings into the bump-allocated heap region
        and returns the base pointer as f64.
        """
        if self._str_concat_helper_emitted:
            return
        self._str_concat_helper_emitted = True
        self._need_heap_ptr = True
        lines = [
            "  (func $__str_concat (param $sc_p1 f64) (param $sc_l1 f64)"
            " (param $sc_p2 f64) (param $sc_l2 f64) (result f64)",
            "    (local $sc_i f64)",
            "    (local $sc_dst f64)",
            "    ;; save current heap_ptr as result base",
            "    global.get $__heap_ptr",
            "    f64.convert_i32_u",
            "    local.set $sc_dst",
            "    ;; copy bytes from p1",
            "    f64.const 0",
            "    local.set $sc_i",
            "    block $sc_b1",
            "      loop $sc_lp1",
            "        local.get $sc_i",
            "        local.get $sc_l1",
            "        f64.ge",
            "        br_if $sc_b1",
            "        global.get $__heap_ptr",
            "        local.get $sc_i",
            "        i32.trunc_f64_u",
            "        i32.add",
            "        local.get $sc_p1",
            "        i32.trunc_f64_u",
            "        local.get $sc_i",
            "        i32.trunc_f64_u",
            "        i32.add",
            "        i32.load8_u",
            "        i32.store8",
            "        local.get $sc_i",
            "        f64.const 1",
            "        f64.add",
            "        local.set $sc_i",
            "        br $sc_lp1",
            "      end",
            "    end",
            "    ;; copy bytes from p2",
            "    f64.const 0",
            "    local.set $sc_i",
            "    block $sc_b2",
            "      loop $sc_lp2",
            "        local.get $sc_i",
            "        local.get $sc_l2",
            "        f64.ge",
            "        br_if $sc_b2",
            "        global.get $__heap_ptr",
            "        local.get $sc_l1",
            "        i32.trunc_f64_u",
            "        local.get $sc_i",
            "        i32.trunc_f64_u",
            "        i32.add",
            "        i32.add",
            "        local.get $sc_p2",
            "        i32.trunc_f64_u",
            "        local.get $sc_i",
            "        i32.trunc_f64_u",
            "        i32.add",
            "        i32.load8_u",
            "        i32.store8",
            "        local.get $sc_i",
            "        f64.const 1",
            "        f64.add",
            "        local.set $sc_i",
            "        br $sc_lp2",
            "      end",
            "    end",
            "    ;; advance heap_ptr by (len1+len2) rounded up to 8",
            "    global.get $__heap_ptr",
            "    local.get $sc_l1",
            "    i32.trunc_f64_u",
            "    local.get $sc_l2",
            "    i32.trunc_f64_u",
            "    i32.add",
            "    i32.const 7",
            "    i32.add",
            "    i32.const -8",
            "    i32.and",
            "    i32.add",
            "    global.set $__heap_ptr",
            "    local.get $sc_dst",
            "  )",
        ]
        self._funcs.append("\n".join(lines))

    def _ensure_str_slice_helper(self):
        """Emit the $__str_slice WAT helper function once per module.

        Signature: (ptr: f64, start: f64, stop: f64) -> f64 (new ptr)
        Copies bytes ptr[start..stop) into heap and returns new base as f64.
        """
        if self._str_slice_helper_emitted:
            return
        self._str_slice_helper_emitted = True
        self._need_heap_ptr = True
        lines = [
            "  (func $__str_slice (param $ss_p f64) (param $ss_s f64)"
            " (param $ss_e f64) (result f64)",
            "    (local $ss_i f64)",
            "    (local $ss_dst f64)",
            "    ;; clamp stop to >= start",
            "    local.get $ss_e",
            "    local.get $ss_s",
            "    f64.lt",
            "    if",
            "      local.get $ss_s",
            "      local.set $ss_e",
            "    end",
            "    ;; save heap_ptr as result base",
            "    global.get $__heap_ptr",
            "    f64.convert_i32_u",
            "    local.set $ss_dst",
            "    ;; copy bytes p[start..stop)",
            "    local.get $ss_s",
            "    local.set $ss_i",
            "    block $ss_blk",
            "      loop $ss_lp",
            "        local.get $ss_i",
            "        local.get $ss_e",
            "        f64.ge",
            "        br_if $ss_blk",
            "        global.get $__heap_ptr",
            "        local.get $ss_i",
            "        i32.trunc_f64_u",
            "        local.get $ss_s",
            "        i32.trunc_f64_u",
            "        i32.sub",
            "        i32.add",
            "        local.get $ss_p",
            "        i32.trunc_f64_u",
            "        local.get $ss_i",
            "        i32.trunc_f64_u",
            "        i32.add",
            "        i32.load8_u",
            "        i32.store8",
            "        local.get $ss_i",
            "        f64.const 1",
            "        f64.add",
            "        local.set $ss_i",
            "        br $ss_lp",
            "      end",
            "    end",
            "    ;; advance heap_ptr by (stop-start) rounded to 8",
            "    global.get $__heap_ptr",
            "    local.get $ss_e",
            "    i32.trunc_f64_u",
            "    local.get $ss_s",
            "    i32.trunc_f64_u",
            "    i32.sub",
            "    i32.const 7",
            "    i32.add",
            "    i32.const -8",
            "    i32.and",
            "    i32.add",
            "    global.set $__heap_ptr",
            "    local.get $ss_dst",
            "  )",
        ]
        self._funcs.append("\n".join(lines))

    def _gen_for_list(self, stmt: ForLoop, list_name: str, iter_var: str,
                      blk: str, lp: str, n: int, indent: str):
        """Lower ``for target in list_var`` using the linear-memory list header.

        List layout (from _gen_list_alloc): [len_f64, elem0, elem1, …]
        all values are f64 (8 bytes each).  The f64 held in *list_name* is the
        heap base pointer cast to f64.
        """
        base_local = f"__flbase_{n}"   # f64 holding i32 base ptr
        len_local = f"__fllen_{n}"     # f64 element count
        idx_local = f"__flidx_{n}"     # f64 loop index
        for loc in (base_local, len_local, idx_local):
            self._locals.add(loc)

        # Save base pointer and load length from header (offset 0).
        self._emit(f"{indent};; for {iter_var} in {list_name} (list)")
        self._emit(f"{indent}local.get ${self._wat_symbol(list_name)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(base_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(list_name)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        # Init index to 0.
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")

        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        # Exit when idx >= len.
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        # Load element: base + 8 + idx*8.
        self._emit(f"{indent}    local.get ${self._wat_symbol(base_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
        self._gen_stmts(stmt.body, indent + "    ")
        # Increment index.
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end  ;; loop")
        self._emit(f"{indent}end  ;; block (for list)")

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
