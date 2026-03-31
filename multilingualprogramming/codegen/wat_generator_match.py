#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Match/case lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    BinaryOp,
    BooleanLiteral,
    CallExpr,
    DictLiteral,
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
            and (
                self._is_tracked_list_name(subj_var_name)
                or self._is_tracked_tuple_name(subj_var_name)
            )
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
            if self._emit_or_match_case(case, subj_local, blk, indent):
                continue
            if self._emit_as_match_case(case, subj_local, blk, indent):
                continue
            if self._emit_class_match_case(case, subj_local, blk, indent):
                continue
            if self._emit_mapping_match_case(case, subj_local, blk, indent):
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

    def _emit_or_match_case(self, case, subj_local: str, blk: str, indent: str) -> bool:
        """Handle OR patterns: ``case a | b | c:``  (BinaryOp chain with ``|``)."""
        pattern = case.pattern
        if not (isinstance(pattern, BinaryOp) and pattern.op == "|"):
            return False
        # Collect all alternatives from the BinaryOp chain.
        alternatives = []
        node = pattern
        while isinstance(node, BinaryOp) and node.op == "|":
            alternatives.append(node.right)
            node = node.left
        alternatives.append(node)
        alternatives.reverse()
        self._emit(f"{indent}  ;; case a | b | ... (OR pattern)")
        # Emit: (subj == alt0) | (subj == alt1) | ...
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._gen_expr(alternatives[0], indent + "  ")
        self._emit(f"{indent}  f64.eq")
        for alt in alternatives[1:]:
            self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
            self._gen_expr(alt, indent + "  ")
            self._emit(f"{indent}  f64.eq")
            self._emit(f"{indent}  i32.or")
        self._emit_case_guard(case, indent + "  ")
        self._emit_case_body(case, blk, indent)
        return True

    def _emit_as_match_case(self, case, subj_local: str, blk: str, indent: str) -> bool:
        """Handle AS patterns: ``case pattern as name:``  (BinaryOp with `` as ``)."""
        pattern = case.pattern
        if not (isinstance(pattern, BinaryOp) and pattern.op == " as "):
            return False
        inner_pattern = pattern.left
        name_node = pattern.right
        if not isinstance(name_node, Identifier):
            return False
        cap_name = name_node.name
        self._emit(f"{indent}  ;; case <pattern> as {cap_name}:")
        self._locals.add(cap_name)
        # First bind the subject to the capture variable.
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  local.set ${self._wat_symbol(cap_name)}")
        # Then check the inner pattern (fake a case with the inner pattern).
        class _FakeCase:  # pylint: disable=too-few-public-methods
            def __init__(self, pat, guard, body):
                self.pattern = pat
                self.guard = guard
                self.body = body
                self.is_default = False
        fake_case = _FakeCase(inner_pattern, getattr(case, "guard", None), case.body)
        # Try literal or capture inner pattern.
        if self._emit_literal_match_case(fake_case, subj_local, blk, indent):
            return True
        # Wildcard inner pattern — always matches.
        self._gen_stmts(case.body, indent + "  ")
        self._emit(f"{indent}  br ${blk}")
        return True

    def _emit_class_match_case(self, case, subj_local: str, blk: str, indent: str) -> bool:
        """Handle class patterns: ``case Point(x=px, y=py):``."""
        pattern = case.pattern
        if not isinstance(pattern, CallExpr):
            return False
        class_name = _name(pattern.func)
        if class_name not in self._class_ids:
            return False
        class_id = self._class_ids[class_name]
        field_layout = self._class_field_layouts.get(class_name, {})
        self._emit(f"{indent}  ;; case {class_name}(...): class pattern")
        # Check type tag at self_ptr - 8.
        self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
        self._emit(f"{indent}  i32.trunc_f64_u")
        self._emit(f"{indent}  i32.const 8")
        self._emit(f"{indent}  i32.sub")
        self._emit(f"{indent}  i32.load")
        self._emit(f"{indent}  i32.const {class_id}")
        self._emit(f"{indent}  i32.eq")
        # Bind keyword captures and check values.
        for kw_name, kw_node in (pattern.keywords or []):
            if not isinstance(kw_node, Identifier):
                continue
            cap_name = kw_node.name
            offset = field_layout.get(kw_name)
            if offset is None:
                continue
            self._locals.add(cap_name)
            self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
            self._emit(f"{indent}  i32.trunc_f64_u")
            self._emit(f"{indent}  i32.const {offset}")
            self._emit(f"{indent}  i32.add")
            self._emit(f"{indent}  f64.load")
            self._emit(f"{indent}  local.set ${self._wat_symbol(cap_name)}")
        self._emit_case_guard(case, indent + "  ")
        self._emit_case_body(case, blk, indent)
        return True

    def _emit_mapping_match_case(self, case, subj_local: str, blk: str, indent: str) -> bool:
        """Handle mapping patterns: ``case {"key": value}:``."""
        pattern = case.pattern
        if not isinstance(pattern, DictLiteral):
            return False
        # Look up which variable holds the subject dict.
        dict_keys = self._dict_key_maps.get(subj_local)
        self._emit(f"{indent}  ;; case {{...}}: mapping pattern")
        cond_started = False
        for entry in (pattern.entries or []):
            if not (isinstance(entry, tuple) and len(entry) == 2):
                continue
            key_node, val_node = entry
            if not isinstance(key_node, StringLiteral):
                continue
            key_str = key_node.value
            if dict_keys is not None and key_str in dict_keys:
                idx = dict_keys[key_str]
                # Load the value at this index from the subject dict.
                self._emit(f"{indent}  local.get ${self._wat_symbol(subj_local)}")
                self._emit(f"{indent}  i32.trunc_f64_u")
                self._emit(f"{indent}  i32.const {8 + idx * 8}")
                self._emit(f"{indent}  i32.add")
                self._emit(f"{indent}  f64.load")
                if isinstance(val_node, Identifier):
                    cap_name = val_node.name
                    self._locals.add(cap_name)
                    self._emit(f"{indent}  local.set ${self._wat_symbol(cap_name)}")
                    if not cond_started:
                        self._emit(f"{indent}  i32.const 1  ;; key present")
                        cond_started = True
                else:
                    self._gen_expr(val_node, indent + "  ")
                    self._emit(f"{indent}  f64.eq")
                    if cond_started:
                        self._emit(f"{indent}  i32.and")
                    else:
                        cond_started = True
        if not cond_started:
            self._emit(f"{indent}  i32.const 1  ;; empty mapping pattern — always matches")
        self._emit_case_guard(case, indent + "  ")
        self._emit_case_body(case, blk, indent)
        return True

    def _emit_unsupported_match_case(self, case, indent: str):
        self._emit(
            f"{indent}  ;; case {type(case.pattern).__name__}: "
            f"complex pattern not lowerable in WAT - stub"
        )
