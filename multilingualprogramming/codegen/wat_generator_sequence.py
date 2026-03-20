#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Sequence, generator, and comprehension helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    CallExpr,
    DictComprehension,
    DictLiteral,
    ForLoop,
    FunctionDef,
    GeneratorExpr,
    Identifier,
    ListComprehension,
    ListLiteral,
    NumeralLiteral,
    SetComprehension,
    SetLiteral,
    StarredExpr,
    TupleLiteral,
    YieldStatement,
)
from multilingualprogramming.codegen.wat_generator_print import WATGeneratorPrintMixin
from multilingualprogramming.codegen.wat_generator_runtime import WATGeneratorRuntimeMixin
from multilingualprogramming.codegen.wat_generator_support import (
    _LIST_NAMES,
    _RANGE_NAMES,
    _SET_NAMES,
    _STR_NAMES,
    _TUPLE_NAMES,
    _name,
    _real_params,
)


class WATGeneratorSequenceMixin(WATGeneratorRuntimeMixin, WATGeneratorPrintMixin):
    """Lower sequence-oriented constructs to WAT."""

    def supports_sequence_lowering(self) -> bool:
        """Expose sequence lowering support for mixin-aware callers."""
        return True

    def _add_local_names(self, *names: str) -> None:
        self._locals.update(name for name in names if isinstance(name, str))

    def _emit_length_allocation(
        self, ptr_local: str, len_local: str, indent: str
    ) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}i32.const 1")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit_alloc_dynamic(ptr_local, indent)

    def _emit_sequence_header(
        self, ptr_local: str, len_local: str, indent: str
    ) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.store")

    def _emit_sequence_element_address(
        self,
        ptr_local: str,
        idx_local: str,
        indent: str,
        *,
        extra_offset: int = 0,
    ) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        if extra_offset:
            self._emit(f"{indent}i32.const {extra_offset}")
            self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.mul")
        self._emit(f"{indent}i32.const 8")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.add")

    def _emit_sequence_value_load(
        self, ptr_local: str, idx_local: str, indent: str, *, extra_offset: int = 0
    ) -> None:
        self._emit_sequence_element_address(
            ptr_local, idx_local, indent, extra_offset=extra_offset
        )
        self._emit(f"{indent}f64.load")

    def _emit_sequence_len_setup(
        self, ptr_local: str, len_local: str, idx_local: str, indent: str
    ) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")

    def _emit_local_increment(self, local_name: str, indent: str) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(local_name)}")
        self._emit(f"{indent}f64.const 1")
        self._emit(f"{indent}f64.add")
        self._emit(f"{indent}local.set ${self._wat_symbol(local_name)}")

    def _gen_sorted_copy(self, seq_expr, indent: str) -> bool:
        ctx = self._sorted_copy_context(seq_expr)
        if ctx is None:
            return False
        self._emit_sorted_copy_setup(ctx, indent)
        self._emit_sorted_copy_loop(ctx, indent)
        self._emit_sorted_bubble_sort(ctx, indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['dst_ptr'])}")
        return True

    def _sorted_copy_context(self, seq_expr):
        if not (
            isinstance(seq_expr, Identifier)
            and (seq_expr.name in self._list_locals or seq_expr.name in self._tuple_locals)
        ):
            return None
        label = self._new_label()
        ctx = {
            "name": seq_expr.name,
            "label": label,
            "src_ptr": f"__sort_src_{label}",
            "dst_ptr": f"__sort_dst_{label}",
            "len_local": f"__sort_len_{label}",
            "i_local": f"__sort_i_{label}",
            "j_local": f"__sort_j_{label}",
            "a_local": f"__sort_a_{label}",
            "b_local": f"__sort_b_{label}",
        }
        self._add_local_names(*ctx.values())
        self._need_heap_ptr = True
        return ctx

    def _emit_sorted_copy_setup(self, ctx, indent: str) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['name'])}")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['src_ptr'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['src_ptr'])}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['len_local'])}")
        self._emit_length_allocation(ctx["dst_ptr"], ctx["len_local"], indent)
        self._emit_sequence_header(ctx["dst_ptr"], ctx["len_local"], indent)

    def _emit_sorted_copy_loop(self, ctx, indent: str) -> None:
        block_label = f"sort_copy_blk_{ctx['label']}"
        loop_label = f"sort_copy_lp_{ctx['label']}"
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['i_local'])}")
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['i_local'])}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['len_local'])}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        self._emit_sequence_element_address(
            ctx["dst_ptr"], ctx["i_local"], indent + "    "
        )
        self._emit_sequence_element_address(
            ctx["src_ptr"], ctx["i_local"], indent + "    "
        )
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    f64.store")
        self._emit_local_increment(ctx["i_local"], indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")

    def _emit_sorted_bubble_sort(self, ctx, indent: str) -> None:
        outer_block = f"sort_outer_blk_{ctx['label']}"
        outer_loop = f"sort_outer_lp_{ctx['label']}"
        inner_block = f"sort_inner_blk_{ctx['label']}"
        inner_loop = f"sort_inner_lp_{ctx['label']}"
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['i_local'])}")
        self._emit(f"{indent}block ${outer_block}")
        self._emit(f"{indent}  loop ${outer_loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['i_local'])}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['len_local'])}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${outer_block}")
        self._emit(f"{indent}    f64.const 0")
        self._emit(f"{indent}    local.set ${self._wat_symbol(ctx['j_local'])}")
        self._emit(f"{indent}    block ${inner_block}")
        self._emit(f"{indent}      loop ${inner_loop}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['j_local'])}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['len_local'])}")
        self._emit(f"{indent}        f64.const 1")
        self._emit(f"{indent}        f64.sub")
        self._emit(f"{indent}        f64.ge")
        self._emit(f"{indent}        br_if ${inner_block}")
        self._emit_sequence_element_address(
            ctx["dst_ptr"], ctx["j_local"], indent + "        "
        )
        self._emit(f"{indent}        f64.load")
        self._emit(f"{indent}        local.set ${self._wat_symbol(ctx['a_local'])}")
        self._emit_sequence_element_address(
            ctx["dst_ptr"], ctx["j_local"], indent + "        ", extra_offset=1
        )
        self._emit(f"{indent}        f64.load")
        self._emit(f"{indent}        local.set ${self._wat_symbol(ctx['b_local'])}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['a_local'])}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['b_local'])}")
        self._emit(f"{indent}        f64.gt")
        self._emit(f"{indent}        if")
        self._emit_sequence_element_address(
            ctx["dst_ptr"], ctx["j_local"], indent + "          "
        )
        self._emit(f"{indent}          local.get ${self._wat_symbol(ctx['b_local'])}")
        self._emit(f"{indent}          f64.store")
        self._emit_sequence_element_address(
            ctx["dst_ptr"], ctx["j_local"], indent + "          ", extra_offset=1
        )
        self._emit(f"{indent}          local.get ${self._wat_symbol(ctx['a_local'])}")
        self._emit(f"{indent}          f64.store")
        self._emit(f"{indent}        end")
        self._emit_local_increment(ctx["j_local"], indent + "        ")
        self._emit(f"{indent}        br ${inner_loop}")
        self._emit(f"{indent}      end")
        self._emit(f"{indent}    end")
        self._emit_local_increment(ctx["i_local"], indent + "    ")
        self._emit(f"{indent}    br ${outer_loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")

    def _static_length(self, node):
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
        if not (isinstance(iterable, CallExpr) and _name(iterable.func) in _RANGE_NAMES):
            return None
        if len(iterable.args) == 1:
            return NumeralLiteral("0"), iterable.args[0]
        if len(iterable.args) == 2:
            return iterable.args[0], iterable.args[1]
        return None

    def _static_dict_comp_keys(self, node):
        if not isinstance(node, DictComprehension) or len(node.clauses) != 1:
            return None
        clause = node.clauses[0]
        if clause.conditions:
            return None
        bounds = self._parse_range_bounds(clause.iterable)
        if bounds is None:
            return None
        start_node, end_node = bounds
        if not (
            isinstance(start_node, NumeralLiteral)
            and isinstance(end_node, NumeralLiteral)
        ):
            return None
        if not (
            isinstance(clause.target, Identifier)
            and isinstance(node.key, CallExpr)
            and _name(node.key.func) in _STR_NAMES
            and len(node.key.args) == 1
            and isinstance(node.key.args[0], Identifier)
            and node.key.args[0].name == clause.target.name
        ):
            return None
        start = int(float(start_node.value))
        end = int(float(end_node.value))
        return [str(value) for value in range(start, end)]

    def _gen_simple_dict_comprehension(self, node, indent: str) -> bool:
        keys = self._static_dict_comp_keys(node)
        bounds = self._parse_range_bounds(node.clauses[0].iterable) if keys else None
        if keys is None or bounds is None:
            return False
        label = self._new_label()
        ptr_local = f"__dict_comp_ptr_{label}"
        idx_local = f"__dict_comp_idx_{label}"
        iter_var = node.clauses[0].target.name
        len_local = f"__dict_comp_len_{label}"
        self._add_local_names(ptr_local, idx_local, iter_var, len_local)
        self._need_heap_ptr = True
        self._emit(f"{indent}f64.const {float(len(keys))}")
        self._emit(f"{indent}local.set ${self._wat_symbol(len_local)}")
        self._emit_length_allocation(ptr_local, len_local, indent)
        self._emit_sequence_header(ptr_local, len_local, indent)
        self._emit(f"{indent}f64.const {float(int(float(bounds[0].value)))}")
        self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(idx_local)}")
        block_label = f"dict_comp_blk_{label}"
        loop_label = f"dict_comp_lp_{label}"
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        self._emit_sequence_element_address(ptr_local, idx_local, indent + "    ")
        self._gen_expr(node.value, indent + "    ")
        self._emit(f"{indent}    f64.store")
        self._emit_local_increment(iter_var, indent + "    ")
        self._emit_local_increment(idx_local, indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _simple_generator_spec(self, func_def: FunctionDef):
        """Return lowering spec for supported generator shapes, or None."""
        if len(func_def.body) != 1:
            return None
        stmt = func_def.body[0]
        # Shape 1: yield range(n)  /  yield range(start, stop)
        if isinstance(stmt, YieldStatement) and not stmt.is_from:
            bounds = self._parse_range_bounds(stmt.value)
            if bounds is not None:
                iter_name = f"__gen_item_{self._new_label()}"
                return ("range", bounds[0], bounds[1], iter_name, Identifier(iter_name))
        # Shape 1b: yield from range(n)  /  yield from range(start, stop)
        if isinstance(stmt, YieldStatement) and stmt.is_from:
            bounds = self._parse_range_bounds(stmt.value)
            if bounds is not None:
                iter_name = f"__gen_item_{self._new_label()}"
                return ("range", bounds[0], bounds[1], iter_name, Identifier(iter_name))
        # Shape 2: yield from seq  (tracked list/tuple)
        if isinstance(stmt, YieldStatement) and stmt.is_from:
            if isinstance(stmt.value, Identifier):
                src = stmt.value.name
                if src in self._list_locals or src in self._tuple_locals:
                    return ("list_copy", src)
        # Shape 3: for x in range(...): yield expr
        if isinstance(stmt, ForLoop):
            bounds = self._parse_range_bounds(stmt.iterable)
            if bounds is not None and len(stmt.body) == 1:
                inner = stmt.body[0]
                if isinstance(inner, YieldStatement) and not inner.is_from:
                    if isinstance(stmt.target, Identifier):
                        return ("range", bounds[0], bounds[1],
                                stmt.target.name, inner.value or stmt.target)
        # Shape 4: for x in list_var: yield x  (or yield expr)
        if isinstance(stmt, ForLoop):
            if isinstance(stmt.iterable, Identifier):
                src = stmt.iterable.name
                if (src in self._list_locals or src in self._tuple_locals) and len(stmt.body) == 1:
                    inner = stmt.body[0]
                    if isinstance(inner, YieldStatement) and not inner.is_from:
                        if isinstance(stmt.target, Identifier):
                            return ("list_iter", src, stmt.target.name,
                                    inner.value or stmt.target)
        return None

    def _emit_simple_generator_function(
        self, func_def: FunctionDef, emitted_name: str | None = None
    ) -> bool:
        spec = self._simple_generator_spec(func_def)
        if spec is None:
            return False
        saved = self._save_func_state()
        func_name = emitted_name or _name(func_def.name)
        param_names = _real_params(func_def)
        self._locals = set(param_names)
        self._need_heap_ptr = True

        if spec[0] == "list_copy":
            # yield from seq — return a copy of the source list as the generator result.
            src_name = spec[1]
            self._emit(f"    ;; generator: yield from {src_name}")
            self._emit(f"    local.get ${self._wat_symbol(src_name)}")
            self._emit("    return")

        elif spec[0] == "list_iter":
            # for x in list_var: yield expr — iterate and materialise.
            _, src_name, iter_var, element_expr = spec
            label = self._new_label()
            src_ptr = f"__gen_src_{label}"
            ptr_local = f"__gen_ptr_{label}"
            idx_local = f"__gen_idx_{label}"
            len_local = f"__gen_len_{label}"
            self._add_local_names(src_ptr, ptr_local, idx_local, len_local, iter_var)
            self._emit(f"    local.get ${self._wat_symbol(src_name)}")
            self._emit(f"    local.set ${self._wat_symbol(src_ptr)}")
            self._emit(f"    local.get ${self._wat_symbol(src_ptr)}")
            self._emit("    i32.trunc_f64_u")
            self._emit("    f64.load")
            self._emit(f"    local.set ${self._wat_symbol(len_local)}")
            self._emit_length_allocation(ptr_local, len_local, "    ")
            self._emit_sequence_header(ptr_local, len_local, "    ")
            self._emit("    f64.const 0")
            self._emit(f"    local.set ${self._wat_symbol(idx_local)}")
            blk = f"gen_blk_{label}"
            lp = f"gen_lp_{label}"
            self._emit(f"    block ${blk}")
            self._emit(f"      loop ${lp}")
            self._emit(f"        local.get ${self._wat_symbol(idx_local)}")
            self._emit(f"        local.get ${self._wat_symbol(len_local)}")
            self._emit("        f64.ge")
            self._emit(f"        br_if ${blk}")
            self._emit_sequence_value_load(src_ptr, idx_local, "        ")
            self._emit(f"        local.set ${self._wat_symbol(iter_var)}")
            self._emit_sequence_element_address(ptr_local, idx_local, "        ")
            self._gen_expr(element_expr, "        ")
            self._emit("        f64.store")
            self._emit_local_increment(idx_local, "        ")
            self._emit(f"        br ${lp}")
            self._emit("      end")
            self._emit("    end")
            self._emit(f"    local.get ${self._wat_symbol(ptr_local)}")
            self._emit("    return")

        else:
            # range-based generator
            _, start_node, end_node, iter_var, element_expr = spec
            label = self._new_label()
            ptr_local = f"__gen_ptr_{label}"
            idx_local = f"__gen_idx_{label}"
            len_local = f"__gen_len_{label}"
            end_local = f"__gen_end_{label}"
            self._add_local_names(iter_var, ptr_local, idx_local, len_local, end_local)
            self._gen_expr(start_node, "    ")
            self._emit(f"    local.set ${self._wat_symbol(iter_var)}")
            self._gen_expr(end_node, "    ")
            self._emit(f"    local.set ${self._wat_symbol(end_local)}")
            self._emit(f"    local.get ${self._wat_symbol(end_local)}")
            self._emit(f"    local.get ${self._wat_symbol(iter_var)}")
            self._emit("    f64.sub")
            self._emit(f"    local.set ${self._wat_symbol(len_local)}")
            self._emit_length_allocation(ptr_local, len_local, "    ")
            self._emit_sequence_header(ptr_local, len_local, "    ")
            self._emit("    f64.const 0")
            self._emit(f"    local.set ${self._wat_symbol(idx_local)}")
            block_label = f"gen_blk_{label}"
            loop_label = f"gen_lp_{label}"
            self._emit(f"    block ${block_label}")
            self._emit(f"      loop ${loop_label}")
            self._emit(f"        local.get ${self._wat_symbol(iter_var)}")
            self._emit(f"        local.get ${self._wat_symbol(end_local)}")
            self._emit("        f64.ge")
            self._emit(f"        br_if ${block_label}")
            self._emit_sequence_element_address(ptr_local, idx_local, "        ")
            self._gen_expr(element_expr, "        ")
            self._emit("        f64.store")
            self._emit_local_increment(iter_var, "        ")
            self._emit_local_increment(idx_local, "        ")
            self._emit(f"        br ${loop_label}")
            self._emit("      end")
            self._emit("    end")
            self._emit(f"    local.get ${self._wat_symbol(ptr_local)}")
            self._emit("    return")

        self._append_wat_function(func_name, param_names, list(self._instrs))
        self._sequence_func_names.add(func_name)
        self._restore_func_state(saved)
        return True

    def _gen_filtered_or_nested_comprehension_list(self, node, indent: str) -> bool:
        if not isinstance(node, (ListComprehension, SetComprehension, GeneratorExpr)):
            return False
        if len(node.clauses) == 1:
            if self._gen_filtered_range_comprehension(node, indent):
                return True
            return self._gen_filtered_list_comprehension(node, indent)
        if len(node.clauses) == 2:
            return self._gen_nested_range_comprehension(node, indent)
        return False

    def _gen_filtered_list_comprehension(self, node, indent: str) -> bool:
        """Lower ``[expr for x in list_var if cond]`` when iterable is a tracked list/tuple."""
        clause = node.clauses[0]
        if not clause.conditions:
            return False
        iterable = clause.iterable
        if not isinstance(iterable, Identifier):
            return False
        if iterable.name not in self._list_locals and iterable.name not in self._tuple_locals:
            return False
        src_name = iterable.name
        iter_var = (
            _name(clause.target)
            if isinstance(clause.target, Identifier)
            else f"__comp_item_{self._new_label()}"
        )
        label = self._new_label()
        src_ptr = f"__flt_src_{label}"
        ptr_local = f"__flt_dst_{label}"
        src_len = f"__flt_src_len_{label}"
        write_idx = f"__flt_write_{label}"
        read_idx = f"__flt_read_{label}"
        self._add_local_names(src_ptr, ptr_local, src_len, write_idx, read_idx, iter_var)
        self._need_heap_ptr = True
        # Source list pointer and length.
        self._emit(f"{indent}local.get ${self._wat_symbol(src_name)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(src_len)}")
        # Allocate output list with capacity = source length (worst case).
        self._emit_length_allocation(ptr_local, src_len, indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(write_idx)}")
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(read_idx)}")
        blk = f"flt_blk_{label}"
        lp = f"flt_lp_{label}"
        self._emit(f"{indent}block ${blk}")
        self._emit(f"{indent}  loop ${lp}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(read_idx)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(src_len)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${blk}")
        self._emit_sequence_value_load(src_ptr, read_idx, indent + "    ")
        self._emit(f"{indent}    local.set ${self._wat_symbol(iter_var)}")
        for cond in clause.conditions:
            self._gen_cond(cond, indent + "    ")
            self._emit(f"{indent}    if")
            self._emit_sequence_element_address(ptr_local, write_idx, indent + "      ")
            self._gen_expr(node.element, indent + "      ")
            self._emit(f"{indent}      f64.store")
            self._emit_local_increment(write_idx, indent + "      ")
            self._emit(f"{indent}    end")
        self._emit_local_increment(read_idx, indent + "    ")
        self._emit(f"{indent}    br ${lp}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit_sequence_header(ptr_local, write_idx, indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _gen_filtered_range_comprehension(self, node, indent: str) -> bool:
        clause = node.clauses[0]
        bounds = self._parse_range_bounds(clause.iterable)
        if bounds is None or not clause.conditions:
            return False
        label = self._new_label()
        ptr_local = f"__comp_ptr_{label}"
        write_idx = f"__comp_write_{label}"
        cap_local = f"__comp_cap_{label}"
        iter_var = (
            _name(clause.target)
            if isinstance(clause.target, Identifier)
            else f"__comp_item_{label}"
        )
        end_local = f"__comp_end_{label}"
        self._add_local_names(ptr_local, write_idx, cap_local, iter_var, end_local)
        self._need_heap_ptr = True
        self._gen_expr(bounds[0], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(iter_var)}")
        self._gen_expr(bounds[1], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(cap_local)}")
        self._emit_length_allocation(ptr_local, cap_local, indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(write_idx)}")
        block_label = f"comp_filter_blk_{label}"
        loop_label = f"comp_filter_lp_{label}"
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(iter_var)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(end_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        for cond in clause.conditions:
            self._gen_cond(cond, indent + "    ")
            self._emit(f"{indent}    if")
            self._emit_sequence_element_address(ptr_local, write_idx, indent + "      ")
            self._gen_expr(node.element, indent + "      ")
            self._emit(f"{indent}      f64.store")
            self._emit_local_increment(write_idx, indent + "      ")
            self._emit(f"{indent}    end")
        self._emit_local_increment(iter_var, indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit_sequence_header(ptr_local, write_idx, indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(ptr_local)}")
        return True

    def _gen_nested_range_comprehension(self, node, indent: str) -> bool:
        outer, inner = node.clauses
        outer_bounds = self._parse_range_bounds(outer.iterable)
        inner_bounds = self._parse_range_bounds(inner.iterable)
        if outer_bounds is None or inner_bounds is None or outer.conditions or inner.conditions:
            return False
        label = self._new_label()
        ctx = self._nested_comprehension_context(label, outer, inner)
        self._need_heap_ptr = True
        self._emit_nested_comprehension_setup(ctx, outer_bounds, inner_bounds, indent)
        self._emit_nested_comprehension_loops(ctx, node.element, indent)
        self._emit_sequence_header(ctx["ptr_local"], ctx["write_idx"], indent)
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['ptr_local'])}")
        return True

    def _nested_comprehension_context(self, label: int, outer, inner) -> dict:
        ctx = {
            "ptr_local": f"__comp_ptr_{label}",
            "write_idx": f"__comp_write_{label}",
            "cap_local": f"__comp_cap_{label}",
            "outer_var": (
                _name(outer.target)
                if isinstance(outer.target, Identifier)
                else f"__comp_outer_{label}"
            ),
            "inner_var": (
                _name(inner.target)
                if isinstance(inner.target, Identifier)
                else f"__comp_inner_{label}"
            ),
            "outer_end": f"__comp_outer_end_{label}",
            "inner_start": f"__comp_inner_start_{label}",
            "inner_end": f"__comp_inner_end_{label}",
            "outer_span": f"__comp_outer_span_{label}",
            "inner_span": f"__comp_inner_span_{label}",
            "label": label,
        }
        self._add_local_names(*ctx.values())
        return ctx

    def _emit_nested_comprehension_setup(
        self, ctx, outer_bounds, inner_bounds, indent: str
    ) -> None:
        self._gen_expr(outer_bounds[0], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['outer_var'])}")
        self._gen_expr(outer_bounds[1], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['outer_end'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['outer_end'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['outer_var'])}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['outer_span'])}")
        self._gen_expr(inner_bounds[0], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['inner_start'])}")
        self._gen_expr(inner_bounds[1], indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['inner_end'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['inner_end'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['inner_start'])}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['inner_span'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['outer_span'])}")
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['inner_span'])}")
        self._emit(f"{indent}f64.mul")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['cap_local'])}")
        self._emit_length_allocation(ctx["ptr_local"], ctx["cap_local"], indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['write_idx'])}")

    def _emit_nested_comprehension_loops(self, ctx, element_expr, indent: str) -> None:
        outer_block = f"comp_outer_blk_{ctx['label']}"
        outer_loop = f"comp_outer_lp_{ctx['label']}"
        inner_block = f"comp_inner_blk_{ctx['label']}"
        inner_loop = f"comp_inner_lp_{ctx['label']}"
        self._emit(f"{indent}block ${outer_block}")
        self._emit(f"{indent}  loop ${outer_loop}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['outer_var'])}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['outer_end'])}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${outer_block}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['inner_start'])}")
        self._emit(f"{indent}    local.set ${self._wat_symbol(ctx['inner_var'])}")
        self._emit(f"{indent}    block ${inner_block}")
        self._emit(f"{indent}      loop ${inner_loop}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['inner_var'])}")
        self._emit(f"{indent}        local.get ${self._wat_symbol(ctx['inner_end'])}")
        self._emit(f"{indent}        f64.ge")
        self._emit(f"{indent}        br_if ${inner_block}")
        self._emit_sequence_element_address(
            ctx["ptr_local"], ctx["write_idx"], indent + "        "
        )
        self._gen_expr(element_expr, indent + "        ")
        self._emit(f"{indent}        f64.store")
        self._emit_local_increment(ctx["write_idx"], indent + "        ")
        self._emit_local_increment(ctx["inner_var"], indent + "        ")
        self._emit(f"{indent}        br ${inner_loop}")
        self._emit(f"{indent}      end")
        self._emit(f"{indent}    end")
        self._emit_local_increment(ctx["outer_var"], indent + "    ")
        self._emit(f"{indent}    br ${outer_loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")

    def _emit_sum_over_pointer(self, ptr_expr, indent: str) -> None:
        label = self._new_label()
        ptr_local = f"__sum_ptr_{label}"
        idx_local = f"__sum_idx_{label}"
        len_local = f"__sum_len_{label}"
        acc_local = f"__sum_acc_{label}"
        block_label = f"sum_blk_{label}"
        loop_label = f"sum_lp_{label}"
        self._add_local_names(ptr_local, idx_local, len_local, acc_local)
        self._gen_expr(ptr_expr, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
        self._emit_sequence_len_setup(ptr_local, len_local, idx_local, indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(acc_local)}")
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(acc_local)}")
        self._emit_sequence_element_address(ptr_local, idx_local, indent + "    ")
        self._emit(f"{indent}    f64.load")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(acc_local)}")
        self._emit_local_increment(idx_local, indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
        self._emit(f"{indent}local.get ${self._wat_symbol(acc_local)}")

    def _gen_simple_comprehension_list(self, node, indent: str) -> bool:
        clause = node.clauses[0] if node.clauses else None
        if clause is None or len(node.clauses) != 1 or clause.conditions:
            return False
        iterable_name = (
            _name(clause.iterable) if isinstance(clause.iterable, Identifier) else None
        )
        is_range = (
            isinstance(clause.iterable, CallExpr)
            and _name(clause.iterable.func) in _RANGE_NAMES
        )
        is_list = iterable_name in self._list_locals
        if not (is_range or is_list):
            return False
        ctx = self._simple_comprehension_context(clause)
        self._emit_simple_comprehension_setup(ctx, clause, indent, is_range)
        self._emit_simple_comprehension_loop(
            ctx, node.element, indent, iterable_name, is_list
        )
        self._emit(f"{indent}local.get ${self._wat_symbol(ctx['ptr_local'])}")
        return True

    def _simple_comprehension_context(self, clause) -> dict:
        label = self._new_label()
        iter_var = (
            _name(clause.target)
            if isinstance(clause.target, Identifier)
            else f"__comp_item_{label}"
        )
        ctx = {
            "label": label,
            "iter_var": iter_var,
            "ptr_local": f"__comp_ptr_{label}",
            "idx_local": f"__comp_idx_{label}",
            "len_local": f"__comp_len_{label}",
            "src_len_local": f"__comp_src_len_{label}",
            "end_local": f"__comp_end_{label}",
        }
        self._add_local_names(*ctx.values())
        self._need_heap_ptr = True
        return ctx

    def _emit_simple_comprehension_setup(
        self, ctx, clause, indent: str, is_range: bool
    ) -> None:
        if is_range:
            start_node, end_node = self._parse_range_bounds(clause.iterable)
            self._gen_expr(start_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(ctx['iter_var'])}")
            self._gen_expr(end_node, indent)
            self._emit(f"{indent}local.set ${self._wat_symbol(ctx['end_local'])}")
            self._emit(f"{indent}local.get ${self._wat_symbol(ctx['end_local'])}")
            self._emit(f"{indent}local.get ${self._wat_symbol(ctx['iter_var'])}")
            self._emit(f"{indent}f64.sub")
            self._emit(f"{indent}local.set ${self._wat_symbol(ctx['len_local'])}")
        else:
            iterable_name = _name(clause.iterable)
            self._emit(f"{indent}local.get ${self._wat_symbol(iterable_name)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}f64.load")
            self._emit(f"{indent}local.set ${self._wat_symbol(ctx['src_len_local'])}")
            self._emit(f"{indent}local.get ${self._wat_symbol(ctx['src_len_local'])}")
            self._emit(f"{indent}local.set ${self._wat_symbol(ctx['len_local'])}")
        self._emit_length_allocation(ctx["ptr_local"], ctx["len_local"], indent)
        self._emit_sequence_header(ctx["ptr_local"], ctx["len_local"], indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(ctx['idx_local'])}")

    def _emit_simple_comprehension_loop(
        self,
        ctx,
        element_expr,
        indent: str,
        iterable_name: str | None,
        is_list: bool,
    ) -> None:
        block_label = f"comp_list_blk_{ctx['label']}"
        loop_label = f"comp_list_lp_{ctx['label']}"
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['idx_local'])}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(ctx['len_local'])}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        if is_list and iterable_name is not None:
            self._emit_sequence_element_address(
                iterable_name, ctx["idx_local"], indent + "    "
            )
            self._emit(f"{indent}    f64.load")
            self._emit(f"{indent}    local.set ${self._wat_symbol(ctx['iter_var'])}")
        self._emit_sequence_element_address(
            ctx["ptr_local"], ctx["idx_local"], indent + "    "
        )
        self._gen_expr(element_expr, indent + "    ")
        self._emit(f"{indent}    f64.store")
        self._emit_local_increment(ctx["idx_local"], indent + "    ")
        if iterable_name is None:
            self._emit_local_increment(ctx["iter_var"], indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")

    def _is_sequence_expr(self, value) -> bool:
        if isinstance(value, (ListLiteral, TupleLiteral, SetLiteral)):
            return True
        if isinstance(value, Identifier):
            return value.name in self._list_locals or value.name in self._tuple_locals
        if (
            isinstance(value, CallExpr)
            and len(value.args) == 1
            and _name(value.func) in (_LIST_NAMES | _TUPLE_NAMES | _SET_NAMES)
        ):
            return True
        if isinstance(value, CallExpr) and _name(value.func) in {"divmod", "sorted"}:
            return True
        return isinstance(value, (ListComprehension, SetComprehension, GeneratorExpr))

    def _gen_unpack_assignment(self, target, value, indent: str) -> bool:
        if not isinstance(target, (TupleLiteral, ListLiteral)) or not self._is_sequence_expr(value):
            return False
        elements = target.elements
        star_positions = [
            index for index, element in enumerate(elements)
            if isinstance(element, StarredExpr)
        ]
        if len(star_positions) > 1 or not self._valid_unpack_elements(elements):
            return False
        label = self._new_label()
        src_ptr = f"__unpack_ptr_{label}"
        src_len = f"__unpack_len_{label}"
        self._add_local_names(src_ptr, src_len)
        self._gen_expr(value, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}f64.load")
        self._emit(f"{indent}local.set ${self._wat_symbol(src_len)}")
        if not star_positions:
            self._emit_unpack_targets(elements, src_ptr, src_len, indent)
            return True
        return self._emit_star_unpack(
            elements, star_positions[0], src_ptr, src_len, indent, label
        )

    @staticmethod
    def _valid_unpack_elements(elements) -> bool:
        for element in elements:
            if isinstance(element, Identifier):
                continue
            if isinstance(element, StarredExpr) and isinstance(element.value, Identifier):
                continue
            return False
        return True

    def _emit_unpack_load(
        self,
        src_ptr: str,
        src_len: str,
        indent: str,
        *,
        index: int | None = None,
        from_end: int | None = None,
    ) -> None:
        self._emit(f"{indent}local.get ${self._wat_symbol(src_ptr)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        if index is not None:
            self._emit(f"{indent}i32.const {(index + 1) * 8}")
        else:
            self._emit(f"{indent}local.get ${self._wat_symbol(src_len)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}i32.const {from_end}")
            self._emit(f"{indent}i32.sub")
            self._emit(f"{indent}i32.const 8")
            self._emit(f"{indent}i32.mul")
            self._emit(f"{indent}i32.const 8")
            self._emit(f"{indent}i32.add")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}f64.load")

    def _emit_unpack_targets(
        self, elements, src_ptr: str, src_len: str, indent: str
    ) -> None:
        for index, element in enumerate(elements):
            name = element.name
            self._locals.add(name)
            self._clear_assignment_tracking(name)
            self._emit_unpack_load(src_ptr, src_len, indent, index=index)
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")

    def _emit_star_unpack(
        self,
        elements,
        star_index: int,
        src_ptr: str,
        src_len: str,
        indent: str,
        label: int,
    ) -> bool:
        prefix = elements[:star_index]
        suffix = elements[star_index + 1:]
        star_target = elements[star_index].value.name
        self._emit_unpack_targets(prefix, src_ptr, src_len, indent)
        self._emit_unpack_suffix_targets(suffix, src_ptr, src_len, indent)
        star_ptr = f"__unpack_star_ptr_{label}"
        star_len = f"__unpack_star_len_{label}"
        star_idx = f"__unpack_star_idx_{label}"
        self._add_local_names(star_ptr, star_len, star_idx, star_target)
        self._need_heap_ptr = True
        self._emit(f"{indent}local.get ${self._wat_symbol(src_len)}")
        self._emit(f"{indent}f64.const {float(len(prefix) + len(suffix))}")
        self._emit(f"{indent}f64.sub")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_len)}")
        self._emit_length_allocation(star_ptr, star_len, indent)
        self._emit_sequence_header(star_ptr, star_len, indent)
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_idx)}")
        self._emit_star_unpack_loop(
            prefix, src_ptr, star_ptr, star_len, star_idx, indent, label
        )
        self._emit(f"{indent}local.get ${self._wat_symbol(star_ptr)}")
        self._emit(f"{indent}local.set ${self._wat_symbol(star_target)}")
        self._clear_assignment_tracking(star_target)
        self._list_locals.add(star_target)
        return True

    def _emit_unpack_suffix_targets(self, suffix, src_ptr: str, src_len: str, indent: str):
        for suffix_offset, element in enumerate(suffix):
            name = element.name
            self._locals.add(name)
            self._clear_assignment_tracking(name)
            self._emit_unpack_load(
                src_ptr, src_len, indent, from_end=len(suffix) - suffix_offset
            )
            self._emit(f"{indent}local.set ${self._wat_symbol(name)}")

    def _emit_star_unpack_loop(
        self,
        prefix,
        src_ptr: str,
        star_ptr: str,
        star_len: str,
        star_idx: str,
        indent: str,
        label: int,
    ) -> None:
        block_label = f"unpack_star_blk_{label}"
        loop_label = f"unpack_star_lp_{label}"
        self._emit(f"{indent}block ${block_label}")
        self._emit(f"{indent}  loop ${loop_label}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_idx)}")
        self._emit(f"{indent}    local.get ${self._wat_symbol(star_len)}")
        self._emit(f"{indent}    f64.ge")
        self._emit(f"{indent}    br_if ${block_label}")
        self._emit_sequence_element_address(star_ptr, star_idx, indent + "    ")
        self._emit_sequence_value_load(
            src_ptr, star_idx, indent + "    ", extra_offset=len(prefix)
        )
        self._emit(f"{indent}    f64.store")
        self._emit_local_increment(star_idx, indent + "    ")
        self._emit(f"{indent}    br ${loop_label}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
