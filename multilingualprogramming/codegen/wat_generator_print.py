#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Print-lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    BooleanLiteral,
    CallExpr,
    FStringLiteral,
    Identifier,
    NumeralLiteral,
    StringLiteral,
)
from multilingualprogramming.codegen.wat_generator_support import _name


class WATGeneratorPrintMixin:
    """Helpers for lowering ``print(...)`` calls to WAT."""

    def supports_print_lowering(self) -> bool:
        """Expose print lowering support for mixin-aware callers."""
        return True

    def _print_options(self, call_expr: CallExpr) -> tuple[str, str]:
        """Return ``(sep, end)`` for a print call."""
        sep_val = " "
        end_val = "\n"
        for kw_name, kw_node in (call_expr.keywords or []):
            if kw_name == "sep" and isinstance(kw_node, StringLiteral):
                sep_val = kw_node.value
            elif kw_name == "end" and isinstance(kw_node, StringLiteral):
                end_val = kw_node.value
        return sep_val, end_val

    def _gen_print(self, call_expr: CallExpr, indent: str):
        """Emit WAT for a ``print(...)`` call."""
        self._emit(f"{indent};; print(...)")
        sep_val, end_val = self._print_options(call_expr)
        for index, arg in enumerate(call_expr.args):
            if index > 0:
                self._emit_print_separator(sep_val, indent)
            self._emit_print_arg(arg, indent)
        self._emit_print_end(end_val, indent)

    def _emit_print_arg(self, arg, indent: str) -> None:
        """Emit one print argument."""
        if isinstance(arg, StringLiteral):
            self._emit_print_literal_string(arg.value, indent, note="str")
            return
        if isinstance(arg, FStringLiteral):
            self._emit_print_fstring(arg, indent)
            return
        if isinstance(arg, BooleanLiteral):
            self._emit(f"{indent}i32.const {1 if arg.value else 0}")
            self._emit(f"{indent}call $print_bool")
            return
        if isinstance(arg, Identifier) and arg.name in self._string_len_locals:
            self._emit_tracked_string_print(arg.name, indent)
            return
        if isinstance(arg, Identifier) and arg.name in self._tuple_locals:
            self._emit_print_sequence(arg.name, "(", ")", indent)
            return
        if isinstance(arg, Identifier) and arg.name in self._list_locals:
            self._emit_print_sequence(arg.name, "[", "]", indent)
            return
        if isinstance(arg, CallExpr) and _name(arg.func) in self._string_return_funcs:
            self._emit_print_string_call(arg, indent)
            return
        if isinstance(arg, NumeralLiteral) and "." in arg.value:
            self._gen_expr(arg, indent)
            self._emit(f"{indent}call $print_f64_float")
            return
        self._gen_expr(arg, indent)
        self._emit(f"{indent}call $print_f64")

    def _emit_print_literal_string(self, value: str, indent: str, note: str) -> None:
        """Emit a string literal directly."""
        offset, length = self._intern(value)
        self._emit(f"{indent}i32.const {offset}   ;; {note} ptr")
        self._emit(f"{indent}i32.const {length}   ;; {note} len")
        self._emit(f"{indent}call $print_str")

    def _emit_print_fstring(self, arg: FStringLiteral, indent: str) -> None:
        """Emit a formatted string argument."""
        if self._gen_fstring_expr(arg, indent):
            tmp_len = f"__print_fstr_len_{self._new_label()}"
            self._locals.add(tmp_len)
            self._emit(f"{indent}global.get $__last_str_len")
            self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
            self._emit(f"{indent}call $print_str")
            return
        self._emit(f"{indent}f64.const 0")
        self._emit(f"{indent}call $print_f64")

    def _emit_tracked_string_print(self, name: str, indent: str) -> None:
        """Print a tracked string local plus its stored byte length."""
        len_local = self._string_len_locals[name]
        self._emit(f"{indent}local.get ${self._wat_symbol(name)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(len_local)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}call $print_str")

    def _emit_print_string_call(self, arg: CallExpr, indent: str) -> None:
        """Print a function call known to return a string-like pointer."""
        tmp_len = f"__print_call_len_{self._new_label()}"
        self._locals.add(tmp_len)
        self._gen_expr(arg, indent)
        self._emit(f"{indent}global.get $__last_str_len")
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}call $print_str")

    def _emit_print_separator(self, sep_val: str, indent: str):
        """Emit WAT instructions for the print separator."""
        if sep_val == " ":
            self._emit(f"{indent}call $print_sep")
            return
        if sep_val == "":
            return
        self._emit_print_literal_string(sep_val, indent, note="sep")

    def _emit_print_end(self, end_val: str, indent: str):
        """Emit WAT instructions for the print end string."""
        if end_val == "\n":
            self._emit(f"{indent}call $print_newline")
            return
        if end_val == "":
            return
        self._emit_print_literal_string(end_val, indent, note="end")

    def _emit_print_sequence(self, name: str, opening: str, closing: str, indent: str):
        """Emit Python-like printing for a list/tuple local."""
        lbl = self._new_label()
        idx_local = f"__print_idx_{lbl}"
        len_local = f"__print_len_{lbl}"
        self._locals.update({idx_local, len_local})
        open_ptr, open_len = self._intern(opening)
        close_ptr, close_len = self._intern(closing)
        comma_ptr, comma_len = self._intern(", ")
        self._emit(f"{indent}i32.const {open_ptr}")
        self._emit(f"{indent}i32.const {open_len}")
        self._emit(f"{indent}call $print_str")
        self._emit_sequence_len_setup(name, len_local, idx_local, indent)
        self._emit_print_sequence_loop(
            name, idx_local, len_local, comma_ptr, comma_len, indent, lbl
        )
        self._emit(f"{indent}i32.const {close_ptr}")
        self._emit(f"{indent}i32.const {close_len}")
        self._emit(f"{indent}call $print_str")

    def _emit_print_sequence_loop(
        self,
        name: str,
        idx_local: str,
        len_local: str,
        comma_ptr: int,
        comma_len: int,
        indent: str,
        lbl: int,
    ) -> None:
        """Emit the loop that prints sequence elements."""
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
        self._emit_sequence_value_load(name, idx_local, indent + "    ")
        self._emit(f"{indent}    call $print_f64")
        self._emit(f"{indent}    local.get ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    f64.const 1")
        self._emit(f"{indent}    f64.add")
        self._emit(f"{indent}    local.set ${self._wat_symbol(idx_local)}")
        self._emit(f"{indent}    br ${loop}")
        self._emit(f"{indent}  end")
        self._emit(f"{indent}end")
