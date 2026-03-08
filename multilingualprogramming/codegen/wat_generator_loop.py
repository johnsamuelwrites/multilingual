#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Loop lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import CallExpr, ForLoop, Identifier, NumeralLiteral

from multilingualprogramming.codegen.wat_generator_support import _RANGE_NAMES, _name


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
