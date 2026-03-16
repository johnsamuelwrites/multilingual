#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Expression and match/case lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    BinaryOp,
    BooleanLiteral,
    CallExpr,
    ForLoop,
    Identifier,
    ListLiteral,
    MatchStatement,
    NoneLiteral,
    NumeralLiteral,
    StringLiteral,
    TupleLiteral,
)

from multilingualprogramming.codegen.wat_generator_support import _name
from multilingualprogramming.codegen.wat_generator_support import _RANGE_NAMES


class WATGeneratorExpressionMixin:
    """Helpers for lowering complex expressions and match/case blocks."""

    @staticmethod
    def mixin_role() -> str:
        """Return a short description of the mixin's responsibility."""
        return "expression-lowering"

    def _gen_binop(self, node: BinaryOp, indent: str):  # noqa: C901
        op = node.op
        if op in ("==", "!=", "<", "<=", ">", ">="):
            self._gen_cmp_from_binop(node, indent)
            self._emit(f"{indent}f64.convert_i32_s")
            return
        if op in ("&", "|", "^"):
            self._emit_bitwise_binop(node, indent)
            return
        if op in ("<<", ">>"):
            self._emit_shift_binop(node, indent)
            return
        if op == "%":
            self._emit_modulo_binop(node, indent)
            return
        if op == "//":
            self._emit_floor_div_binop(node, indent)
            return
        if op == "**":
            self._emit_pow_binop(node, indent)
            return
        if op == "+" and self._is_string_binop(node):
            self._emit_string_concat_binop(node, indent)
            return
        self._emit_numeric_binop(node, indent)

    def _emit_modulo_binop(self, node: BinaryOp, indent: str):
        if isinstance(node.left, Identifier):
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
        self._gen_expr(node.left, indent)
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}f64.div")
        self._emit(f"{indent}f64.floor")
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}f64.mul")
        self._emit(f"{indent}f64.sub")

    def _emit_floor_div_binop(self, node: BinaryOp, indent: str):
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}f64.div")
        self._emit(f"{indent}f64.floor")

    def _emit_pow_binop(self, node: BinaryOp, indent: str):
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}call $pow_f64")

    def _is_string_binop(self, node: BinaryOp) -> bool:
        return self._is_string_value(node.left) and self._is_string_value(node.right)

    def _is_string_value(self, expr) -> bool:
        return isinstance(expr, StringLiteral) or (
            isinstance(expr, Identifier) and expr.name in self._string_len_locals
        )

    def _emit_string_concat_binop(self, node: BinaryOp, indent: str):
        if isinstance(node.left, StringLiteral) and isinstance(node.right, StringLiteral):
            result = node.left.value + node.right.value
            offset, _ = self._intern(result)
            self._emit(f"{indent}f64.const {float(offset)}  ;; str concat (compile-time)")
            return
        self._ensure_str_concat_helper()
        self._emit(f"{indent};; str concat (runtime)")
        self._emit_string_value_with_len(node.left, indent)
        self._emit_string_value_with_len(node.right, indent)
        self._emit(f"{indent}call $__str_concat")

    def _emit_string_value_with_len(self, expr, indent: str):
        self._gen_expr(expr, indent)
        if isinstance(expr, StringLiteral):
            _, byte_len = self._intern(expr.value)
            self._emit(f"{indent}f64.const {float(byte_len)}")
            return
        len_local = self._string_len_locals[expr.name]
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")

    def _emit_numeric_binop(self, node: BinaryOp, indent: str):
        arith = {"+": "f64.add", "-": "f64.sub", "*": "f64.mul", "/": "f64.div"}
        self._gen_expr(node.left, indent)
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}{arith.get(node.op, 'f64.add')}  ;; op={node.op!r}")

    def _emit_bitwise_binop(self, node: BinaryOp, indent: str):
        instr = {"&": "i32.and", "|": "i32.or", "^": "i32.xor"}[node.op]
        self._gen_expr(node.left, indent)
        self._emit(f"{indent}i32.trunc_f64_s")
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}i32.trunc_f64_s")
        self._emit(f"{indent}{instr}")
        self._emit(f"{indent}f64.convert_i32_s")

    def _emit_shift_binop(self, node: BinaryOp, indent: str):
        instr = {"<<": "i32.shl", ">>": "i32.shr_s"}[node.op]
        self._gen_expr(node.left, indent)
        self._emit(f"{indent}i32.trunc_f64_s")
        self._gen_expr(node.right, indent)
        self._emit(f"{indent}i32.trunc_f64_s")
        self._emit(f"{indent}{instr}")
        self._emit(f"{indent}f64.convert_i32_s")

    def _gen_match(self, stmt: MatchStatement, indent: str):
        """Lower a match/case statement to nested WAT control flow."""
        n = self._new_label()
        subj_local = f"__match_subj_{n}"
        blk = f"__match_end_{n}"
        self._locals.add(subj_local)
        subj_var_name = _name(stmt.subject) if isinstance(stmt.subject, Identifier) else None
        subj_is_list = bool(
            subj_var_name
            and (subj_var_name in self._list_locals or subj_var_name in self._tuple_locals)
        )

        self._emit(f"{indent};; match ...")
        self._gen_expr(stmt.subject, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}block ${blk}")

        for case in stmt.cases:
            if self._emit_default_match_case(case, blk, indent):
                continue
            if self._emit_literal_match_case(case, subj_local, blk, indent):
                continue
            if self._emit_capture_match_case(case, subj_local, blk, indent):
                continue
            if self._emit_sequence_match_case(case, subj_local, subj_is_list, blk, indent):
                continue
            self._emit_unsupported_match_case(case, indent)

        self._emit(f"{indent}end  ;; match")

    def _emit_default_match_case(self, case, blk: str, indent: str) -> bool:
        if not (getattr(case, "is_default", False) or case.pattern is None):
            return False
        self._emit(f"{indent}  ;; case _: (default)")
        self._gen_stmts(case.body, indent + "    ")
        self._emit(f"{indent}  br ${blk}")
        return True

    def _emit_literal_match_case(
        self,
        case,
        subj_local: str,
        blk: str,
        indent: str,
    ) -> bool:
        pattern = case.pattern
        if isinstance(pattern, NumeralLiteral):
            value = self._to_f64(pattern.value)
            self._emit_scalar_match_case(case, subj_local, blk, indent, value, f"{value}")
            return True
        if isinstance(pattern, BooleanLiteral):
            value = float(1 if pattern.value else 0)
            self._emit_scalar_match_case(case, subj_local, blk, indent, value, f"{bool(value)}")
            return True
        if isinstance(pattern, StringLiteral):
            pat_offset, _ = self._intern(pattern.value)
            self._emit_scalar_match_case(
                case,
                subj_local,
                blk,
                indent,
                float(pat_offset),
                repr(pattern.value),
            )
            return True
        if isinstance(pattern, NoneLiteral):
            self._emit_scalar_match_case(case, subj_local, blk, indent, 0.0, "None")
            return True
        return False

    def _emit_scalar_match_case(
        self,
        case,
        subj_local: str,
        blk: str,
        indent: str,
        value: float,
        label: str,
    ) -> None:
        self._emit(f"{indent}  ;; case {label}:")
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  f64.const {value}")
        self._emit(f"{indent}  f64.eq")
        self._emit_case_guard(case, indent + "  ")
        self._emit_case_body(case, blk, indent)

    def _emit_capture_match_case(self, case, subj_local: str, blk: str, indent: str) -> bool:
        if not isinstance(case.pattern, Identifier):
            return False
        cap_name = _name(case.pattern)
        self._emit(f"{indent}  ;; case {cap_name}: (capture variable - always matches)")
        self._locals.add(cap_name)
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  local.set ${self._wat_symbol(cap_name)}")
        if getattr(case, "guard", None):
            self._gen_cond(case.guard, indent + "  ")
            self._emit(f"{indent}  if")
            self._gen_stmts(case.body, indent + "    ")
            self._emit(f"{indent}    br ${blk}")
            self._emit(f"{indent}  end")
            return True
        self._gen_stmts(case.body, indent + "  ")
        self._emit(f"{indent}  br ${blk}")
        return True

    def _emit_sequence_match_case(
        self,
        case,
        subj_local: str,
        subj_is_list: bool,
        blk: str,
        indent: str,
    ) -> bool:
        if not (isinstance(case.pattern, (TupleLiteral, ListLiteral)) and subj_is_list):
            return False
        elements = case.pattern.elements
        pat_repr = ", ".join(str(getattr(elem, "value", "?")) for elem in elements)
        self._emit(f"{indent}  ;; case ({pat_repr},): element-wise comparison")
        self._emit_sequence_length_check(subj_local, len(elements), indent)
        for i, elem in enumerate(elements):
            self._emit_sequence_element_check(subj_local, i, elem, indent)
        self._emit_case_guard(case, indent + "  ")
        self._emit_case_body(case, blk, indent)
        return True

    def _emit_sequence_length_check(self, subj_local: str, size: int, indent: str):
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  i32.trunc_f64_u")
        self._emit(f"{indent}  f64.load")
        self._emit(f"{indent}  f64.const {float(size)}")
        self._emit(f"{indent}  f64.eq")

    def _emit_sequence_element_check(self, subj_local: str, index: int, elem, indent: str):
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  i32.trunc_f64_u")
        self._emit(f"{indent}  i32.const {8 + index * 8}")
        self._emit(f"{indent}  i32.add")
        self._emit(f"{indent}  f64.load")
        self._gen_expr(elem, indent + "  ")
        self._emit(f"{indent}  f64.eq")
        self._emit(f"{indent}  i32.and")

    def _emit_case_guard(self, case, indent: str):
        if getattr(case, "guard", None):
            self._gen_cond(case.guard, indent)
            self._emit(f"{indent}i32.and")

    def _emit_case_body(self, case, blk: str, indent: str):
        self._emit(f"{indent}  if")
        self._gen_stmts(case.body, indent + "    ")
        self._emit(f"{indent}    br ${blk}")
        self._emit(f"{indent}  end")

    def _emit_unsupported_match_case(self, case, indent: str):
        self._emit(
            f"{indent}  ;; case {type(case.pattern).__name__}: "
            f"complex pattern not lowerable in WAT - stub"
        )

    def _gen_for(self, stmt: ForLoop, indent: str):
        n = self._new_label()
        blk = f"for_blk_{n}"
        lp = f"for_lp_{n}"
        range_end_local = f"__re{n}"
        self._loop_stack.append((blk, lp))
        self._locals.add(range_end_local)

        iter_var = self._resolve_for_iter_var(stmt.target)
        self._locals.add(iter_var)
        range_start, range_end = self._decode_range_iterable(stmt.iterable)

        if range_end is not None:
            self._emit_range_for(
                stmt,
                iter_var,
                range_start,
                range_end,
                {"range_end_local": range_end_local, "blk": blk, "lp": lp},
                indent,
            )
        else:
            iterable_name = _name(stmt.iterable) if isinstance(stmt.iterable, Identifier) else None
            if iterable_name and iterable_name in self._list_locals:
                self._gen_for_list(stmt, iterable_name, iter_var, blk, lp, n, indent)
            else:
                self._emit(f"{indent};; for loop over non-range iterable - not supported in WAT")

        self._loop_stack.pop()

    def _resolve_for_iter_var(self, target) -> str:
        if isinstance(target, Identifier):
            return target.name
        if isinstance(target, str):
            return target
        return "__for_i"

    def _decode_range_iterable(self, iterable) -> tuple[NumeralLiteral, object | None]:
        range_start = NumeralLiteral("0")
        range_end = None
        if not isinstance(iterable, CallExpr):
            return range_start, range_end
        if _name(iterable.func) not in _RANGE_NAMES:
            return range_start, range_end
        if len(iterable.args) == 1:
            return range_start, iterable.args[0]
        if len(iterable.args) >= 2:
            return iterable.args[0], iterable.args[1]
        return range_start, range_end

    def _emit_range_for(
        self,
        stmt: ForLoop,
        iter_var: str,
        range_start,
        range_end,
        loop_ctx: dict[str, str],
        indent: str,
    ):
        range_end_local = loop_ctx["range_end_local"]
        blk = loop_ctx["blk"]
        lp = loop_ctx["lp"]
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
        self._emit_counted_loop_increment(iter_var, lp, indent + "    ")
        self._emit(f"{indent}  end  ;; loop")
        self._emit(f"{indent}end  ;; block (for)")

    def _emit_counted_loop_increment(self, iter_var: str, loop_label: str, indent: str):
        """Increment a numeric loop variable and branch back to the loop head."""
        self._emit(f"{indent}local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}f64.const 1")
        self._emit(f"{indent}f64.add")
        self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}br ${loop_label}")
