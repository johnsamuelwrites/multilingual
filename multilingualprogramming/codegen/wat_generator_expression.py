#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Expression lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import BinaryOp, Identifier, StringLiteral


class WATGeneratorExpressionMixin:
    """Helpers for lowering complex expressions."""

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
