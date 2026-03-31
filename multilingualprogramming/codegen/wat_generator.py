#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Generate executable WAT modules from multilingual AST programs."""
# pylint: disable=mixed-line-endings,too-many-lines

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
    ImportStatement,
    FromImportStatement,
    IfStatement,
    WhileLoop,
    ForLoop,
    FunctionDef,
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
)
from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.codegen.wat_generator_core import WATGeneratorCoreMixin
from multilingualprogramming.codegen.wat_generator_expression import WATGeneratorExpressionMixin
from multilingualprogramming.codegen.wat_generator_loop import WATGeneratorLoopMixin
from multilingualprogramming.codegen.wat_generator_manifest import WATGeneratorManifestMixin
from multilingualprogramming.codegen.wat_generator_match import WATGeneratorMatchMixin
from multilingualprogramming.codegen.wat_generator_oop import WATGeneratorOOPMixin
from multilingualprogramming.codegen.wat_generator_orchestrator import (
    WATGeneratorOrchestratorMixin,
)
from multilingualprogramming.codegen.wat_generator_sequence import WATGeneratorSequenceMixin
from multilingualprogramming.codegen.wat_generator_support import (
    _ABS_NAMES,
    _ARGC_NAMES,
    _ARGV_NAMES,
    _DOM_BUILTINS,
    _DOM_CANONICAL_NAMES,
    _DOM_HOST_SIGNATURES,
    _FILTER_NAMES,
    _INPUT_NAMES,
    _INT_NAMES,
    _ROUND_NAMES,
    _LEN_NAMES,
    _MAP_NAMES,
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
    _name,
    _real_params,
)

class WATCodeGenerator(
    WATGeneratorOrchestratorMixin,
    WATGeneratorCoreMixin,
    WATGeneratorExpressionMixin,
    WATGeneratorOOPMixin,
    WATGeneratorSequenceMixin,
):  # pylint: disable=too-many-instance-attributes
    """Visitor-based WAT source code generator."""

    def __init__(self):  # pylint: disable=too-many-statements
        self._instrs: list[str] = []
        self._locals: set[str] = set()
        self._label_count: int = 0
        self._loop_stack: list[tuple[str, str]] = []
        self._data: bytearray = bytearray()
        self._strings: dict[str, tuple[int, int]] = {}
        self._funcs: list[str] = []
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
        # True when any DOM builtin is used (triggers env host import emission).
        self._uses_dom: bool = False
        # Target platform: "browser" emits env DOM imports; "wasi" skips them.
        self._wasm_target: str = "browser"
        # True while emitting a user-defined f64-returning function body.
        # Used to decide between "f64.const 0; return" and "unreachable" on raise.
        self._in_user_func: bool = False
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
        # @property setter/deleter registrations: "ClassName.attr" -> lowered WAT func name.
        self._property_setters: dict[str, str] = {}
        self._property_deleters: dict[str, str] = {}
        # Special dunder method registrations: "ClassName.__str__" -> lowered WAT func name.
        self._class_special_methods: dict[str, str] = {}
        # Tracks whether the fixedN format helper has been emitted per N.
        self._str_slice_step_helper_emitted: bool = False

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

    def _is_static_dict_get_call(self, node) -> bool:
        """Return True for ``dict.get("key"[, default])`` on tracked static dicts."""
        return (
            isinstance(node.func, AttributeAccess)
            and node.func.attr == "get"
            and isinstance(node.func.obj, Identifier)
            and node.func.obj.name in self._dict_key_maps
            and len(node.args) >= 1
            and isinstance(node.args[0], StringLiteral)
        )

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

    def _gen_stmt(self, stmt, indent: str):  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        line = getattr(stmt, "line", 0)
        col = getattr(stmt, "column", 0)
        if line:
            self._emit(f"{indent};; @{line}:{col}")
        if isinstance(stmt, VariableDeclaration):
            if isinstance(stmt.name, (TupleLiteral, ListLiteral)) and \
                    self._gen_unpack_assignment(stmt.name, stmt.value, indent):
                self._emit(f"{indent};; unpacking declaration lowered")
            else:
                name = _name(stmt.name)
                self._emit(f"{indent};; let {name} = ...")
                self._gen_expr(stmt.value, indent)
                if not self._is_module_global(name):
                    self._locals.add(name)
                self._emit_name_set(name, indent)
                self._update_assignment_tracking(name, stmt.value, indent)

        elif isinstance(stmt, Assignment):
            target = stmt.target
            if isinstance(target, Identifier):
                name = target.name
                op = stmt.op
                if op == "=":
                    self._emit(f"{indent};; {name} = ...")
                    self._gen_expr(stmt.value, indent)
                    if not self._is_module_global(name):
                        self._locals.add(name)
                    self._emit_name_set(name, indent)
                    self._update_assignment_tracking(name, stmt.value, indent)
                else:
                    # Compound assignment: a op= b
                    self._emit(f"{indent};; {name} {op} ...")
                    if not self._is_module_global(name):
                        self._locals.add(name)
                    self._emit_name_get(name, indent)
                    self._gen_augmented_op(op, stmt.value, indent)
                    self._emit_name_set(name, indent)
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
                # Check for @property setter before direct field store.
                prop_setter_key = f"{cls}.{attr}" if cls else None
                prop_setter_fn = (
                    self._property_setters.get(prop_setter_key)
                    if prop_setter_key else None
                )
                if prop_setter_fn is not None and stmt.op == "=":
                    self._emit(f"{indent};; @property.setter {obj_name}.{attr}(val)")
                    self._emit(f"{indent}local.get ${self._wat_symbol(obj_name)}")
                    self._gen_expr(stmt.value, indent)
                    self._emit(f"{indent}call ${self._wat_symbol(prop_setter_fn)}")
                    self._emit(f"{indent}drop")
                    # Continue to next statement.
                offset = self._resolve_field(cls, attr) if cls else None
                if prop_setter_fn is None and offset is not None:
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
                elif prop_setter_fn is None:
                    self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")
            elif self._gen_unpack_assignment(target, stmt.value, indent):
                self._emit(f"{indent};; unpacking assignment lowered")
            else:
                self._emit(f"{indent};; (complex assignment target — unsupported in WAT)")

        elif isinstance(stmt, AnnAssignment):
            if isinstance(stmt.target, Identifier):
                name = stmt.target.name
                self._emit(f"{indent};; annotated assignment {name}: ...")
                if stmt.value is None:
                    self._emit(f"{indent}f64.const 0")
                    self._clear_assignment_tracking(name)
                else:
                    self._gen_expr(stmt.value, indent)
                    self._update_assignment_tracking(name, stmt.value, indent)
                if not self._is_module_global(name):
                    self._locals.add(name)
                self._emit_name_set(name, indent)
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
                    self._emit(f"{indent}local.get ${self._wat_symbol(tmp_name)}")
                    if not self._is_module_global(name):
                        self._locals.add(name)
                    self._emit_name_set(name, indent)
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
                elif fname in _INPUT_NAMES and len(expr.args) <= 1:
                    self._gen_expr(expr, indent)
                    self._emit(f"{indent}drop")
                elif fname in _ARGC_NAMES and len(expr.args) == 0:
                    self._emit(f"{indent}call $argc")
                    self._emit(f"{indent}drop")
                elif fname in _ARGV_NAMES and len(expr.args) == 1:
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}call $argv")
                    self._emit(f"{indent}drop")
                elif fname in _DOM_CANONICAL_NAMES:
                    self._gen_dom_call(fname, expr.args, indent)
                    wat_name = _DOM_BUILTINS[fname]
                    if _DOM_HOST_SIGNATURES[wat_name][1]:
                        self._emit(f"{indent}drop")
                elif fname in self._defined_func_names:
                    # Known WAT function — emit args then call
                    self._emit(f"{indent};; call {fname}(...)")
                    self._gen_call_args(expr, indent, fname)
                    self._emit(f"{indent}call ${self._wat_symbol(fname)}")
                    self._emit(f"{indent}drop")
                elif fname in self._class_ctor_names:
                    ctor = self._class_ctor_names[fname]
                    if self._needs_runtime_object(fname):
                        self._emit(f"{indent};; ctor {fname}(...) [stateful]")
                        self._emit_runtime_object_ctor(fname, ctor, expr, indent, keep_ref=False)
                    else:
                        self._emit(f"{indent};; ctor {fname}(...) -> {ctor}(...)")
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
                        self._gen_call_args(expr, indent, ctor, skip_params=1)
                        self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
                        self._emit(f"{indent}drop")
                elif fname in self._class_bases:
                    if self._needs_runtime_object(fname):
                        self._emit(f"{indent};; default ctor {fname}() [runtime object]")
                        self._emit_runtime_object_ctor(
                            fname, None, expr, indent, keep_ref=False,
                        )
                    else:
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
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
                    elif cls and self._needs_runtime_object(cls):
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
                elif (isinstance(expr.func, AttributeAccess)
                      and expr.func.attr in ("strip", "lstrip", "rstrip")
                      and not expr.args):
                    # s.strip() statement context — result is discarded
                    self._emit(f"{indent};; {expr.func.attr}() (result discarded)")
                    self._gen_expr(expr.func.obj, indent)
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._emit(f"{indent}call $__str_strip")
                    self._emit(f"{indent}drop")
                elif (isinstance(expr.func, AttributeAccess)
                      and expr.func.attr in ("find", "index")
                      and len(expr.args) == 1):
                    # s.find(needle) statement context — result is discarded
                    needle_arg = expr.args[0]
                    self._emit(f"{indent};; {expr.func.attr}(needle) (result discarded)")
                    self._gen_expr(expr.func.obj, indent)
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._gen_expr(needle_arg, indent)
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._emit(f"{indent}call $__str_find")
                    self._emit(f"{indent}drop")
                elif (isinstance(expr.func, AttributeAccess)
                      and expr.func.attr == "append"
                      and isinstance(expr.func.obj, Identifier)
                      and self._is_tracked_list_name(expr.func.obj.name)
                      and len(expr.args) == 1):
                    # lst.append(x) → allocate new list, update local
                    obj_name = expr.func.obj.name
                    self._emit(f"{indent};; {obj_name}.append(x)")
                    self._emit_name_get(obj_name, indent)
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}call $__list_append")
                    self._emit_name_set(obj_name, indent)
                elif (isinstance(expr.func, AttributeAccess)
                      and expr.func.attr == "pop"
                      and isinstance(expr.func.obj, Identifier)
                      and self._is_tracked_list_name(expr.func.obj.name)
                      and not expr.args):
                    # lst.pop() statement — result discarded
                    obj_name = expr.func.obj.name
                    self._emit(f"{indent};; {obj_name}.pop() (result discarded)")
                    self._emit_name_get(obj_name, indent)
                    self._emit(f"{indent}call $__list_pop")
                    self._emit(f"{indent}drop")
                elif (isinstance(expr.func, AttributeAccess)
                      and expr.func.attr == "extend"
                      and isinstance(expr.func.obj, Identifier)
                      and self._is_tracked_list_name(expr.func.obj.name)
                      and len(expr.args) == 1):
                    # lst.extend(other) → allocate new list, update local
                    obj_name = expr.func.obj.name
                    self._emit(f"{indent};; {obj_name}.extend(other)")
                    self._emit_name_get(obj_name, indent)
                    self._gen_expr(expr.args[0], indent)
                    self._emit(f"{indent}call $__list_extend")
                    self._emit_name_set(obj_name, indent)
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
                if getattr(self, "_in_user_func", False):
                    self._emit(f"{indent}  f64.const 0  ;; propagate AssertionError")
                    self._emit(f"{indent}  return")
                else:
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
                if getattr(self, "_in_user_func", False):
                    # Inside a user function: return dummy f64.const 0 so the
                    # caller's try/except can check $__last_exc_code (best-effort
                    # cross-function propagation).
                    self._emit(f"{indent}f64.const 0  ;; propagate exception to caller")
                    self._emit(f"{indent}return")
                else:
                    self._emit(f"{indent}unreachable")

        elif isinstance(stmt, TryStatement):
            label = self._new_label()
            code_local = f"__exc_code_{label}"
            handled_local = f"__exc_handled_{label}"
            self._locals.update({code_local, handled_local})
            end_label = f"try_end_{label}"
            parent_ctx = self._try_stack[-1] if self._try_stack else None

            self._emit(f"{indent};; try")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}local.set ${self._wat_symbol(code_local)}")
            self._emit(f"{indent}block ${end_label}")
            self._try_stack.append({"code_local": code_local, "label": end_label})
            self._gen_stmts(stmt.body, indent + "  ")
            self._try_stack.pop()
            self._emit(f"{indent}end")

            # Merge cross-function exception: if a callee set $__last_exc_code
            # but this function's code_local is still 0, adopt the global code.
            # Best-effort: does not short-circuit mid-body; only catches raises
            # from the last call before the body exits cleanly.
            self._emit(f"{indent};; merge cross-function exception (best-effort)")
            self._emit(f"{indent}local.get ${self._wat_symbol(code_local)}")
            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}f64.eq")
            self._emit(f"{indent}if")
            self._emit(f"{indent}  global.get $__last_exc_code")
            self._emit(f"{indent}  i32.const 0")
            self._emit(f"{indent}  i32.ne")
            self._emit(f"{indent}  if")
            self._emit(f"{indent}    global.get $__last_exc_code")
            self._emit(f"{indent}    f64.convert_i32_u")
            self._emit(f"{indent}    local.set ${self._wat_symbol(code_local)}")
            self._emit(f"{indent}  end")
            self._emit(f"{indent}end")

            self._emit(f"{indent}f64.const 0")
            self._emit(f"{indent}local.set ${self._wat_symbol(handled_local)}")
            if stmt.handlers:
                for handler in stmt.handlers:
                    match_label = f"try_match_{self._new_label()}"
                    self._emit(f"{indent}block ${match_label}")
                    self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                    if self._is_catch_all_handler(handler):
                        # catch any raised exception (code != 0)
                        self._emit(f"{indent}  f64.const 0")
                        self._emit(f"{indent}  f64.eq")
                        self._emit(f"{indent}  br_if ${match_label}")
                    else:
                        expected = self._exception_code_for(handler.exc_type)
                        self._emit(f"{indent}  f64.const {float(expected)}")
                        self._emit(f"{indent}  f64.ne")
                        self._emit(f"{indent}  br_if ${match_label}")
                    if handler.name:
                        self._locals.add(handler.name)
                        self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                        self._emit(f"{indent}  local.set ${self._wat_symbol(handler.name)}")
                    self._emit(f"{indent}  f64.const 1")
                    self._emit(f"{indent}  local.set ${self._wat_symbol(handled_local)}")
                    self._emit(f"{indent}  f64.const 0")
                    self._emit(f"{indent}  local.set ${self._wat_symbol(code_local)}")
                    # Clear the global so outer try blocks don't see a stale code.
                    self._emit(f"{indent}  i32.const 0")
                    self._emit(f"{indent}  global.set $__last_exc_code")
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
            if stmt.finally_body:
                self._emit(f"{indent}  ;; finally (unhandled exception path)")
                self._gen_stmts(stmt.finally_body, indent + "  ")
            if parent_ctx is not None:
                self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}  local.set ${self._wat_symbol(parent_ctx['code_local'])}")
                # Also update global so the parent merge-check can see it.
                self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}  i32.trunc_f64_u")
                self._emit(f"{indent}  global.set $__last_exc_code")
                self._emit(f"{indent}  br ${parent_ctx['label']}")
            else:
                self._emit(f"{indent}  local.get ${self._wat_symbol(code_local)}")
                self._emit(f"{indent}  i32.trunc_f64_u")
                self._emit(f"{indent}  global.set $__last_exc_code")
                if getattr(self, "_in_user_func", False):
                    self._emit(f"{indent}  f64.const 0  ;; propagate exception to caller")
                    self._emit(f"{indent}  return")
                else:
                    self._emit(f"{indent}  unreachable")
            self._emit(f"{indent}end")

            if stmt.finally_body:
                self._emit(f"{indent};; finally (normal/handled path)")
                self._gen_stmts(stmt.finally_body, indent)

        elif isinstance(stmt, WithStatement):
            saved_aliases = dict(self._open_aliases)
            for expr, alias in stmt.items:
                # Detect open() calls for virtual file handling.
                if (isinstance(expr, CallExpr) and _name(expr.func) == "open"
                        and expr.args and alias):
                    path_arg = expr.args[0]
                    mode = "r"
                    if len(expr.args) >= 2 and isinstance(expr.args[1], StringLiteral):
                        mode = expr.args[1].value
                    if isinstance(path_arg, StringLiteral):
                        self._open_aliases[alias] = (path_arg.value, mode)
                    if alias:
                        self._locals.add(alias)
                        self._emit(f"{indent}f64.const 0  ;; open handle placeholder")
                        self._emit(f"{indent}local.set ${self._wat_symbol(alias)}")
                    continue
                # Try to call __enter__ if the expr is a known class constructor.
                cls_name = None
                enter_fn = None
                exit_fn = None
                if isinstance(expr, CallExpr):
                    func_name = _name(expr.func)
                    cls_name = (
                        func_name if func_name in self._class_bases else None
                    )
                if cls_name:
                    enter_key = f"{cls_name}.__enter__"
                    exit_key = f"{cls_name}.__exit__"
                    enter_fn = self._class_attr_call_names.get(enter_key)
                    exit_fn = self._class_attr_call_names.get(exit_key)
                if enter_fn:
                    self._emit(f"{indent};; with {cls_name}() as {alias}: __enter__/__exit__")
                    # Allocate instance.
                    ctor = self._class_ctor_names.get(cls_name)
                    if self._needs_runtime_object(cls_name):
                        self._emit_runtime_object_ctor(
                            cls_name, ctor, expr, indent, keep_ref=True,
                        )
                    else:
                        self._emit(f"{indent}f64.const 0  ;; implicit self")
                    obj_local = f"__with_obj_{self._new_label()}"
                    self._locals.add(obj_local)
                    self._emit(f"{indent}local.set ${self._wat_symbol(obj_local)}")
                    # Call __enter__.
                    self._emit(f"{indent}local.get ${self._wat_symbol(obj_local)}")
                    self._emit(f"{indent}call ${self._wat_symbol(enter_fn)}")
                    if alias:
                        self._locals.add(alias)
                        self._emit(f"{indent}local.set ${self._wat_symbol(alias)}")
                    else:
                        self._emit(f"{indent}drop")
                    # Body.
                    self._gen_stmts(stmt.body, indent)
                    # Call __exit__(None, None, None) — use 0 for all args.
                    if exit_fn:
                        self._emit(f"{indent}local.get ${self._wat_symbol(obj_local)}")
                        self._emit(f"{indent}f64.const 0  ;; exc_type=None")
                        self._emit(f"{indent}f64.const 0  ;; exc_val=None")
                        self._emit(f"{indent}f64.const 0  ;; traceback=None")
                        self._emit(f"{indent}call ${self._wat_symbol(exit_fn)}")
                        self._emit(f"{indent}drop")
                    self._open_aliases = saved_aliases
                    return
                # Fallback: run body without __enter__/__exit__.
                self._emit(
                    f"{indent};; with (context-manager hooks not lowerable in WAT)"
                )
                if alias:
                    self._locals.add(alias)
                    self._emit(
                        f"{indent}f64.const 0  ;; placeholder for 'as {alias}'"
                    )
                    self._emit(f"{indent}local.set ${self._wat_symbol(alias)}")
            self._gen_stmts(stmt.body, indent)
            self._open_aliases = saved_aliases

        elif isinstance(stmt, FunctionDef):
            # Lift nested (non-capturing) function defs to module level.
            nested_name = _name(stmt.name)
            outer_prefix = (
                f"{self._current_class}__{self._current_func_name}"
                if getattr(self, "_current_func_name", None)
                else nested_name
            )
            lifted_name = f"__nested_{outer_prefix}__{nested_name}"
            self._emit(
                f"{indent};; nested def {nested_name} -> lifted as {lifted_name}"
            )
            # Register so it can be called by name inside the outer scope.
            self._defined_func_names.add(lifted_name)
            self._func_real_params[lifted_name] = _real_params(stmt)
            # Emit the function at module level.
            self._emit_function(stmt, emitted_name=lifted_name)
            # Bind the nested name as a lambda-table entry in the current scope.
            if self._lambda_table and self._lambda_table[-1] != lifted_name:
                pass  # lambda_table already updated by _emit_function
            self._lambda_locals[nested_name] = lifted_name

        elif isinstance(stmt, MatchStatement):
            self._gen_match(stmt, indent)

        else:
            self._emit(f"{indent};; (unsupported statement: {type(stmt).__name__})")

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
            if self._emit_name_get(node.name, indent):
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
            elif fname in _ROUND_NAMES and len(node.args) == 1:
                # round(x) → f64.nearest (IEEE 754 round-half-to-even)
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.nearest")
            elif resolved_fname in {"math.floor", "floor"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.floor")
            elif resolved_fname in {"math.ceil", "ceil"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.ceil")
            elif resolved_fname in {"math.fabs", "fabs"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.abs")
            elif resolved_fname in {"math.trunc", "trunc"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.trunc")
            elif resolved_fname in {"math.sin", "sin"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_sin")
            elif resolved_fname in {"math.cos", "cos"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_cos")
            elif resolved_fname in {"math.tan", "tan"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_tan")
            elif resolved_fname in {"math.exp", "exp"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_exp")
            elif resolved_fname in {"math.log", "log"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_log")
            elif resolved_fname in {"math.log2", "log2"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_log2")
            elif resolved_fname in {"math.log10", "log10"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_log10")
            elif resolved_fname in {"math.atan", "atan"} and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $math_atan")
            elif resolved_fname in {"math.atan2", "atan2"} and len(node.args) == 2:
                self._gen_expr(node.args[0], indent)
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}call $math_atan2")
            elif resolved_fname in {"math.hypot", "hypot"} and len(node.args) == 2:
                # hypot(a,b) = sqrt(a²+b²)
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.const 2.0")
                self._emit(f"{indent}call $pow_f64")
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}f64.const 2.0")
                self._emit(f"{indent}call $pow_f64")
                self._emit(f"{indent}f64.add")
                self._emit(f"{indent}f64.sqrt")
            elif resolved_fname in {"math.degrees"} and len(node.args) == 1:
                # degrees(x) = x * 180/π
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.const 57.29577951308232")
                self._emit(f"{indent}f64.mul")
            elif resolved_fname in {"math.radians"} and len(node.args) == 1:
                # radians(x) = x * π/180
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}f64.const 0.017453292519943295")
                self._emit(f"{indent}f64.mul")
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
            elif fname in _INPUT_NAMES and len(node.args) <= 1:
                # input() / input("prompt") — reads one line from stdin via fd_read
                if node.args and isinstance(node.args[0], StringLiteral):
                    ptr, slen = self._intern(node.args[0].value)
                    self._emit(f"{indent}i32.const {ptr}")
                    self._emit(f"{indent}i32.const {slen}")
                else:
                    self._emit(f"{indent}i32.const 0")
                    self._emit(f"{indent}i32.const 0")
                self._emit(f"{indent}call $input")
            elif fname in _ARGC_NAMES and len(node.args) == 0:
                self._emit(f"{indent}call $argc")
            elif fname in _ARGV_NAMES and len(node.args) == 1:
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}call $argv")
            elif fname in _DOM_CANONICAL_NAMES:
                self._gen_dom_call(fname, node.args, indent)
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
            elif fname == "isinstance" and len(node.args) == 2:
                obj_expr, cls_expr = node.args[0], node.args[1]
                if isinstance(cls_expr, Identifier) and cls_expr.name in self._class_ids:
                    cls_id = self._class_ids[cls_expr.name]
                    self._emit(f"{indent};; isinstance({_name(obj_expr)}, {cls_expr.name})")
                    self._gen_expr(obj_expr, indent)
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}i32.const 8")
                    self._emit(f"{indent}i32.sub")
                    self._emit(f"{indent}i32.load")
                    self._emit(f"{indent}i32.const {cls_id}")
                    self._emit(f"{indent}i32.eq")
                    self._emit(f"{indent}f64.convert_i32_u")
                else:
                    self._emit(f"{indent}f64.const 0  ;; isinstance: unknown class")
            elif resolved_fname in {"json.dumps", "dumps"} and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, Identifier) and (
                    arg.name in self._list_locals or arg.name in self._tuple_locals
                ):
                    self._emit(f"{indent};; json.dumps(list) → JSON array string")
                    self._gen_expr(arg, indent)
                    self._emit(f"{indent}call $__json_encode_list")
                else:
                    # Fallback: emit "null" for unsupported types
                    null_ptr, null_len = self._intern("null")
                    self._emit(f"{indent}i32.const {null_ptr}")
                    self._emit(f"{indent}i32.const {null_len}")
                    self._emit(f"{indent}global.set $__last_str_len")
                    self._emit(f"{indent}i32.const {null_ptr}")
                    self._emit(f"{indent}f64.convert_i32_u")
            elif fname in _STR_NAMES and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, StringLiteral) or (
                    isinstance(arg, Identifier) and arg.name in self._string_len_locals
                ):
                    self._gen_expr(arg, indent)
                else:
                    self._gen_expr(arg, indent)
                    self._emit(f"{indent}call $__str_from_f64")
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
                elif (isinstance(arg, CallExpr)
                      and _name(arg.func) in _MAP_NAMES
                      and len(arg.args) == 2):
                    fn_arg, lst_arg = arg.args[0], arg.args[1]
                    fn_name = _name(fn_arg)
                    lst_name = _name(lst_arg) if isinstance(lst_arg, Identifier) else None
                    if (isinstance(fn_arg, Identifier)
                            and fn_name in self._defined_func_names
                            and lst_name and lst_name in self._list_locals):
                        self._gen_map_list(fn_name, lst_name, indent)
                    else:
                        self._emit(f"{indent}f64.const 0  ;; unsupported: map(...)")
                elif (isinstance(arg, CallExpr)
                      and _name(arg.func) in _FILTER_NAMES
                      and len(arg.args) == 2):
                    fn_arg, lst_arg = arg.args[0], arg.args[1]
                    fn_name = _name(fn_arg)
                    lst_name = _name(lst_arg) if isinstance(lst_arg, Identifier) else None
                    if (isinstance(fn_arg, Identifier)
                            and fn_name in self._defined_func_names
                            and lst_name and lst_name in self._list_locals):
                        self._gen_filter_list(fn_name, lst_name, indent)
                    else:
                        self._emit(f"{indent}f64.const 0  ;; unsupported: filter(...)")
                elif (isinstance(arg, Identifier)
                      and arg.name in self._list_locals):
                    # list(existing_list) → shallow copy
                    self._gen_list_copy(arg.name, indent)
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
            elif (
                fname == "sorted"
                and len(node.args) >= 1
                and self._gen_sorted_copy(node.args[0], indent)
            ):
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
                if self._needs_runtime_object(fname):
                    self._emit_runtime_object_ctor(fname, ctor, node, indent, keep_ref=True)
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
                    self._gen_call_args(node, indent, ctor, skip_params=1)
                    self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
            elif fname in self._class_bases:
                if self._needs_runtime_object(fname):
                    self._emit_runtime_object_ctor(fname, None, node, indent, keep_ref=True)
                else:
                    self._emit(f"{indent}f64.const 0  ;; implicit self")
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
                if self._needs_runtime_object(self._current_class):
                    self._emit_runtime_object_ctor(
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
                elif cls and self._needs_runtime_object(cls):
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
                  and node.func.attr in ("strip", "lstrip", "rstrip")
                  and not node.args):
                # s.strip() → $__str_strip(ptr, last_str_len)
                self._emit(f"{indent};; {node.func.attr}()")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                if node.func.attr == "lstrip":
                    # lstrip: strip leading only — use strip and re-push length as-is
                    # (best-effort: lstrip uses full strip because right boundary is fixed)
                    pass
                elif node.func.attr == "rstrip":
                    pass
                self._emit(f"{indent}call $__str_strip")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr in ("find", "index")
                  and len(node.args) == 1):
                # s.find(needle) → $__str_find(hptr, hlen, nptr, nlen) → f64 index
                needle_arg = node.args[0]
                self._emit(f"{indent};; {node.func.attr}(needle)")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")     # hptr
                self._emit(f"{indent}global.get $__last_str_len")  # hlen
                # Pushes the needle f64 ptr and refreshes $__last_str_len.
                self._gen_expr(needle_arg, indent)
                self._emit(f"{indent}i32.trunc_f64_u")     # nptr
                self._emit(f"{indent}global.get $__last_str_len")  # nlen
                self._emit(f"{indent}call $__str_find")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr in ("upper", "lower")
                  and not node.args):
                # s.upper() / s.lower()
                helper = "__str_upper" if node.func.attr == "upper" else "__str_lower"
                self._emit(f"{indent};; .{node.func.attr}()")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._emit(f"{indent}call ${helper}")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr in ("startswith", "endswith")
                  and len(node.args) == 1):
                # s.startswith(prefix) / s.endswith(suffix) → i32 → f64
                helper = "__str_startswith" if node.func.attr == "startswith" else "__str_endswith"
                self._emit(f"{indent};; .{node.func.attr}()")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._emit(f"{indent}call ${helper}")
                self._emit(f"{indent}f64.convert_i32_u")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr == "count"
                  and len(node.args) == 1):
                # s.count(needle) → f64
                self._emit(f"{indent};; .count(needle)")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._emit(f"{indent}call $__str_count")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr == "replace"
                  and len(node.args) == 2):
                # s.replace(old, new) → f64 ptr
                self._emit(f"{indent};; .replace(old, new)")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._gen_expr(node.args[0], indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._gen_expr(node.args[1], indent)
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}global.get $__last_str_len")
                self._emit(f"{indent}call $__str_replace")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr == "pop"
                  and isinstance(node.func.obj, Identifier)
                  and node.func.obj.name in self._list_locals
                  and not node.args):
                # lst.pop() → last element (modifies count in-place)
                obj_name = node.func.obj.name
                self._emit(f"{indent};; {obj_name}.pop()")
                self._gen_expr(node.func.obj, indent)
                self._emit(f"{indent}call $__list_pop")
            elif self._is_static_dict_get_call(node):
                # d.get(key) / d.get(key, default)
                key_map = self._dict_key_maps[node.func.obj.name]
                key = node.args[0].value
                obj_sym = self._wat_symbol(node.func.obj.name)
                if key in key_map:
                    element_index = key_map[key]
                    self._emit(f"{indent};; {node.func.obj.name}.get({key!r})")
                    self._emit(f"{indent}local.get ${obj_sym}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}i32.const {(element_index + 1) * 8}")
                    self._emit(f"{indent}i32.add")
                    self._emit(f"{indent}f64.load")
                elif len(node.args) >= 2:
                    self._gen_expr(node.args[1], indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; dict.get: key not found")
            elif (isinstance(node.func, AttributeAccess)
                  and node.func.attr in ("values", "keys", "items")
                  and isinstance(node.func.obj, Identifier)
                  and node.func.obj.name in self._dict_key_maps
                  and not node.args):
                self._gen_dict_method(node.func.attr, node.func.obj.name, indent)
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
            self._append_wat_function(
                lam_name,
                param_names,
                body_instrs,
                implicit_return=False,
            )
            self._defined_func_names.add(lam_name)
            self._func_real_params[lam_name] = param_names

            self._restore_func_state(saved)
            # Register lambda in the module-level table; its table index is its f64 value.
            table_idx = len(self._lambda_table)
            self._lambda_table.append(lam_name)
            self._emit(f"{indent}f64.const {float(table_idx)}  ;; lambda table idx")

        elif isinstance(node, (ListComprehension, SetComprehension,
                                DictComprehension, GeneratorExpr)):
            if (
                isinstance(node, DictComprehension)
                and self._gen_simple_dict_comprehension(node, indent)
            ):
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
                self._emit_sequence_value_load(
                    iterable_name, idx_var2, indent + "    "
                )
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
              and isinstance(node.obj, Identifier)
              and node.obj.name == "math"):
            # math.pi, math.e, math.tau, math.inf constants
            math_constants = {
                "pi": "3.141592653589793",
                "e": "2.718281828459045",
                "tau": "6.283185307179586",
                "inf": "inf",
                "nan": "nan",
            }
            val = math_constants.get(node.attr)
            if val is not None:
                self._emit(f"{indent}f64.const {val}")
            else:
                self._emit(f"{indent}f64.const 0  ;; unsupported: math.{node.attr}")

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
                if cls and self._needs_runtime_object(cls):
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
                self._is_tracked_list_name(obj.name) or self._is_tracked_tuple_name(obj.name)
            ):
                # list[i] / tuple[i]  →  load from base + 8 + i*8
                self._emit(f"{indent};; {obj.name}[i]")
                self._emit_name_get(obj.name, indent)
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
                    # s[i] — return a one-character string slice like Python.
                    self._ensure_str_slice_helper()
                    self._emit(f"{indent};; {sname}[i] — single-character string")
                    self._emit(f"{indent}local.get ${self._wat_symbol(sname)}")
                    self._gen_expr(node.index, indent)
                    self._gen_expr(node.index, indent)
                    self._emit(f"{indent}f64.const 1")
                    self._emit(f"{indent}f64.add")
                    self._emit(f"{indent}call $__str_slice")
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

    def _gen_match(self, stmt, indent: str):
        raise NotImplementedError

    def _gen_for(self, stmt, indent: str):
        raise NotImplementedError

    def _emit_counted_loop_increment(self, iter_var: str, loop_label: str, indent: str):
        raise NotImplementedError

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
            "    local.get $ss_e",
            "    i32.trunc_f64_u",
            "    local.get $ss_s",
            "    i32.trunc_f64_u",
            "    i32.sub",
            "    global.set $__last_str_len",
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
        self._emit_sequence_len_setup(base_local, len_local, idx_local, indent)

        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        # Exit when idx >= len.
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit_sequence_value_load(base_local, idx_local, indent + "    ")
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


    # -----------------------------------------------------------------------
    # dict / list / map / filter helpers
    # -----------------------------------------------------------------------

    def _gen_dict_method(self, method: str, dict_name: str, indent: str) -> None:  # pylint: disable=too-many-statements
        """Emit dict.values(), dict.keys(), or dict.items()."""
        key_map = self._dict_key_maps[dict_name]
        keys = sorted(key_map.keys(), key=lambda k: key_map[k])
        n = len(keys)
        dict_sym = self._wat_symbol(dict_name)

        if method == "values":
            # The dict IS a list of values — just return the pointer.
            self._emit(f"{indent};; {dict_name}.values()")
            self._emit(f"{indent}local.get ${dict_sym}")

        elif method == "keys":
            # Allocate a list of interned string pointers for each key.
            lbl = self._new_label()
            ptr_local = f"__dkeys_{lbl}"
            self._locals.add(ptr_local)
            self._emit(f"{indent};; {dict_name}.keys()")
            self._emit_alloc((n + 1) * 8, ptr_local, indent)
            self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}f64.const {float(n)}")
            self._emit(f"{indent}f64.store")
            for i, key in enumerate(keys):
                offset, _ = self._intern(key)
                self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const {(i + 1) * 8}")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}f64.const {float(offset)}")
                self._emit(f"{indent}f64.store")
            self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
            self._list_locals.add(ptr_local)

        elif method == "items":
            # Allocate outer list + one 2-element tuple per item.
            lbl = self._new_label()
            outer_ptr = f"__ditems_{lbl}"
            self._locals.add(outer_ptr)
            self._emit(f"{indent};; {dict_name}.items()")
            self._emit_alloc((n + 1) * 8, outer_ptr, indent)
            self._emit(f"{indent}local.get ${self._wat_symbol(outer_ptr)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}f64.const {float(n)}")
            self._emit(f"{indent}f64.store")
            for i, key in enumerate(keys):
                key_offset, _ = self._intern(key)
                val_idx = key_map[key]
                pair_lbl = self._new_label()
                pair_ptr = f"__dpair_{pair_lbl}"
                self._locals.add(pair_ptr)
                self._emit_alloc(3 * 8, pair_ptr, indent)
                # count = 2
                self._emit(f"{indent}local.get ${self._wat_symbol(pair_ptr)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}f64.const 2.0")
                self._emit(f"{indent}f64.store")
                # key ptr
                self._emit(f"{indent}local.get ${self._wat_symbol(pair_ptr)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const 8")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}f64.const {float(key_offset)}")
                self._emit(f"{indent}f64.store")
                # value
                self._emit(f"{indent}local.get ${self._wat_symbol(pair_ptr)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const 16")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}local.get ${dict_sym}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const {(val_idx + 1) * 8}")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}f64.load")
                self._emit(f"{indent}f64.store")
                # store pair in outer list
                self._emit(f"{indent}local.get ${self._wat_symbol(outer_ptr)}")
                self._emit(f"{indent}i32.trunc_f64_u")
                self._emit(f"{indent}i32.const {(i + 1) * 8}")
                self._emit(f"{indent}i32.add")
                self._emit(f"{indent}local.get ${self._wat_symbol(pair_ptr)}")
                self._emit(f"{indent}f64.store")
            self._emit(f"{indent}local.get ${self._wat_symbol(outer_ptr)}")
            self._list_locals.add(outer_ptr)

    def _gen_map_list(self, fn_name: str, src_list: str, indent: str) -> None:  # pylint: disable=too-many-statements
        """Emit list(map(fn_name, src_list)) — applies fn to each element."""
        n = self._new_label()
        src_sym = self._wat_symbol(src_list)
        base_local = f"__map_base_{n}"
        len_local  = f"__map_len_{n}"
        idx_local  = f"__map_idx_{n}"
        out_ptr    = f"__map_out_{n}"
        for loc in (base_local, len_local, idx_local, out_ptr):
            self._locals.add(loc)
        self._emit(f"{indent};; list(map({fn_name}, {src_list}))")
        self._emit(f"{indent}local.get ${src_sym}")
        self._emit(f"{indent}local.set ${self._wat_symbol(base_local)}")
        self._emit_sequence_len_setup(base_local, len_local, idx_local, indent)
        # Allocate output: (count+1)*8 bytes
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit(f"{indent}call $ml_alloc")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")
        lp = f"map_lp_{n}"
        blk = f"map_blk_{n}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        # out[(idx+1)] = fn(src[idx])
        self._emit(f"{indent}    local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 1")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.add")
        self._emit_sequence_value_load(base_local, idx_local, indent + "    ")
        self._emit(f"{indent}    call ${self._wat_symbol(fn_name)}")
        self._emit(f"{indent}    f64.store")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._list_locals.add(out_ptr)

    def _gen_filter_list(self, fn_name: str, src_list: str, indent: str) -> None:  # pylint: disable=too-many-statements
        """Emit list(filter(fn_name, src_list)) — keeps elements where fn returns truthy."""
        n = self._new_label()
        src_sym = self._wat_symbol(src_list)
        base_local = f"__flt_base_{n}"
        len_local  = f"__flt_len_{n}"
        idx_local  = f"__flt_idx_{n}"
        out_ptr    = f"__flt_out_{n}"
        out_idx    = f"__flt_oidx_{n}"
        for loc in (base_local, len_local, idx_local, out_ptr, out_idx):
            self._locals.add(loc)
        self._emit(f"{indent};; list(filter({fn_name}, {src_list}))")
        self._emit(f"{indent}local.get ${src_sym}")
        self._emit(f"{indent}local.set ${self._wat_symbol(base_local)}")
        self._emit_sequence_len_setup(base_local, len_local, idx_local, indent)
        # Allocate output with max size (same as input)
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit(f"{indent}call $ml_alloc")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(out_idx)}")
        lp = f"flt_lp_{n}"
        blk = f"flt_blk_{n}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit_sequence_value_load(base_local, idx_local, indent + "    ")
        self._emit(f"{indent}    call ${self._wat_symbol(fn_name)}")
        self._emit(f"{indent}    f64.const 0")
        self._emit(f"{indent}    f64.ne")
        self._emit(f"{indent}    if")
        # store src[idx] at out[out_idx+1]
        self._emit(f"{indent}      local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}      i32.trunc_f64_u")
        self._emit(f"{indent}      local.get ${self._wat_symbol(out_idx)}")
        self._emit(f"{indent}      i32.trunc_f64_u")
        self._emit(f"{indent}      i32.const 1")
        self._emit(f"{indent}      i32.add")
        self._emit(f"{indent}      i32.const 8")
        self._emit(f"{indent}      i32.mul")
        self._emit(f"{indent}      i32.add")
        self._emit_sequence_value_load(base_local, idx_local, indent + "      ")
        self._emit(f"{indent}      f64.store")
        self._emit(f"{indent}      local.get ${self._wat_symbol(out_idx)}")
        self._emit(f"{indent}      f64.const 1")
        self._emit(f"{indent}      f64.add")
        self._emit(f"{indent}      local.set ${self._wat_symbol(out_idx)}")
        self._emit(f"{indent}    end")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        # update count at out[0]
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_idx)}")
        self._emit(f"{indent}f64.store")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._list_locals.add(out_ptr)

    def _gen_list_copy(self, src_list: str, indent: str) -> None:  # pylint: disable=too-many-statements
        """Emit a shallow copy of src_list as a new heap-allocated list."""
        n = self._new_label()
        src_sym = self._wat_symbol(src_list)
        base_local = f"__cp_base_{n}"
        len_local  = f"__cp_len_{n}"
        idx_local  = f"__cp_idx_{n}"
        out_ptr    = f"__cp_out_{n}"
        for loc in (base_local, len_local, idx_local, out_ptr):
            self._locals.add(loc)
        self._emit(f"{indent};; list({src_list}) — shallow copy")
        self._emit(f"{indent}local.get ${src_sym}")
        self._emit(f"{indent}local.set ${self._wat_symbol(base_local)}")
        self._emit_sequence_len_setup(base_local, len_local, idx_local, indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit(f"{indent}call $ml_alloc")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")
        lp = f"cp_lp_{n}"
        blk = f"cp_blk_{n}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(out_ptr)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    i32.trunc_f64_u")
        self._emit(f"{indent}    i32.const 1")
        self._emit(f"{indent}    i32.add")
        self._emit(f"{indent}    i32.const 8")
        self._emit(f"{indent}    i32.mul")
        self._emit(f"{indent}    i32.add")
        self._emit_sequence_value_load(base_local, idx_local, indent + "    ")
        self._emit(f"{indent}    f64.store")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(out_ptr)}")
        self._list_locals.add(out_ptr)


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


WATCodeGenerator.generate_abi_manifest = WATGeneratorManifestMixin.generate_abi_manifest
WATCodeGenerator.generate_js_host_shim = WATGeneratorManifestMixin.generate_js_host_shim
WATCodeGenerator.generate_renderer_template = WATGeneratorManifestMixin.generate_renderer_template
for _method_name in (
    "_gen_match",
    "_emit_default_match_case",
    "_emit_literal_match_case",
    "_emit_scalar_match_case",
    "_emit_capture_match_case",
    "_emit_sequence_match_case",
    "_emit_sequence_length_check",
    "_emit_sequence_element_check",
    "_emit_case_guard",
    "_emit_case_body",
    "_emit_unsupported_match_case",
    "_emit_or_match_case",
    "_emit_as_match_case",
    "_emit_class_match_case",
    "_emit_mapping_match_case",
):
    setattr(WATCodeGenerator, _method_name, getattr(WATGeneratorMatchMixin, _method_name))
for _method_name in (
    "_gen_for",
    "_resolve_for_iter_var",
    "_decode_range_iterable",
    "_emit_range_for",
    "_emit_counted_loop_increment",
):
    setattr(WATCodeGenerator, _method_name, getattr(WATGeneratorLoopMixin, _method_name))
setattr(
    WATCodeGenerator,
    "_build_stream_buffer_helpers",
    getattr(WATGeneratorManifestMixin, "_build_stream_buffer_helpers"),
)
