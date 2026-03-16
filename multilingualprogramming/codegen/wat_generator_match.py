#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Match/case lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    BooleanLiteral,
    Identifier,
    ListLiteral,
    MatchStatement,
    NoneLiteral,
    NumeralLiteral,
    StringLiteral,
    TupleLiteral,
)

from multilingualprogramming.codegen.wat_generator_support import _name


class WATGeneratorMatchMixin:
    """Helpers for lowering match/case constructs."""

    @staticmethod
    def mixin_role() -> str:
        """Return a short description of the mixin's responsibility."""
        return "match-lowering"

    def _gen_match(self, stmt: MatchStatement, indent: str):
        """Lower a match/case statement to a WAT block + nested if instructions."""
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
            self._emit_scalar_match_case(
                case,
                subj_local,
                blk,
                indent,
                self._to_f64(pattern.value),
                f"{self._to_f64(pattern.value)}",
            )
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
    ):
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
