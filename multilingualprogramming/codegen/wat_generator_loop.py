#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Loop lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    CallExpr,
    ForLoop,
    Identifier,
    ListLiteral,
    NumeralLiteral,
    TupleLiteral,
)

from multilingualprogramming.codegen.wat_generator_support import (
    _ENUMERATE_NAMES,
    _RANGE_NAMES,
    _name,
)


class WATGeneratorLoopMixin:
    """Helpers for lowering loop constructs."""

    @staticmethod
    def mixin_role() -> str:
        """Return a short description of the mixin's responsibility."""
        return "loop-lowering"

    def _gen_for(self, stmt: ForLoop, indent: str):
        n = self._new_label()
        blk = f"for_blk_{n}"
        lp = f"for_lp_{n}"
        range_end_local = f"__re{n}"
        self._loop_stack.append((blk, lp))
        self._locals.add(range_end_local)

        # Detect enumerate(iterable) — must come before range check.
        if (isinstance(stmt.iterable, CallExpr)
                and _name(stmt.iterable.func) in _ENUMERATE_NAMES
                and stmt.iterable.args):
            enum_arg = stmt.iterable.args[0]
            enum_list_name = _name(enum_arg) if isinstance(enum_arg, Identifier) else None
            if enum_list_name and (
                enum_list_name in self._list_locals or enum_list_name in self._tuple_locals
            ):
                self._gen_for_enumerate_list(stmt, enum_list_name, blk, lp, n, indent)
                self._loop_stack.pop()
                return

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
            if iterable_name and (
                iterable_name in self._list_locals or iterable_name in self._tuple_locals
            ):
                self._gen_for_list(stmt, iterable_name, iter_var, blk, lp, n, indent)
            elif (isinstance(stmt.iterable, CallExpr)
                  and _name(stmt.iterable.func) in self._sequence_func_names):
                # for x in some_func_returning_sequence(...): materialize inline.
                tmp_list = f"__for_seq_{n}"
                self._locals.add(tmp_list)
                self._gen_expr(stmt.iterable, indent)
                self._emit(f"{indent}local.set ${self._wat_symbol(tmp_list)}")
                self._list_locals.add(tmp_list)
                self._gen_for_list(stmt, tmp_list, iter_var, blk, lp, n, indent)
                self._list_locals.discard(tmp_list)
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

    def _gen_for_enumerate_list(
        self, stmt: ForLoop, list_name: str,
        blk: str, lp: str, n: int, indent: str
    ):
        """Lower ``for (idx, val) in enumerate(list_name)``."""
        # Unpack the two-element tuple/list target.
        target = stmt.target
        if isinstance(target, (TupleLiteral, ListLiteral)) and len(target.elements) == 2:
            idx_var = _name(target.elements[0])
            val_var = _name(target.elements[1])
        else:
            idx_var = "__enum_idx"
            val_var = self._resolve_for_iter_var(target)

        base_local = f"__elbase_{n}"
        len_local  = f"__ellen_{n}"
        for loc in (idx_var, val_var, base_local, len_local):
            self._locals.add(loc)

        self._emit(f"{indent};; for ({idx_var}, {val_var}) in enumerate({list_name})")
        self._emit(f"{indent}local.get ${self._wat_symbol(list_name)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(base_local)}")
        self._emit_sequence_len_setup(base_local, len_local, idx_var, indent)
        # idx_var was set to 0 by _emit_sequence_len_setup (it initializes $idx to 0).

        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_var)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit_sequence_value_load(base_local, idx_var, indent + "    ")
        self._emit(f"{indent}    local.set ${self._wat_symbol(val_var)}")
        self._gen_stmts(stmt.body, indent + "    ")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_var)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_var)}")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end  ;; loop")
        self._emit(f"{indent}end  ;; block (for enumerate)")
