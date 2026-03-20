#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Print-lowering helpers for the WAT generator."""

from multilingualprogramming.parser.ast_nodes import (
    AttributeAccess,
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

    def _print_options(self, call_expr: CallExpr) -> tuple[str, str, int]:
        """Return ``(sep, end, fd)`` for a print call.  fd=1 stdout, fd=2 stderr."""
        sep_val = " "
        end_val = "\n"
        fd = 1  # default: stdout
        for kw_name, kw_node in (call_expr.keywords or []):
            if kw_name == "sep" and isinstance(kw_node, StringLiteral):
                sep_val = kw_node.value
            elif kw_name == "end" and isinstance(kw_node, StringLiteral):
                end_val = kw_node.value
            elif kw_name == "file":
                # Detect sys.stderr / sys.stdout
                if isinstance(kw_node, AttributeAccess):
                    attr = kw_node.attr
                    if attr == "stderr":
                        fd = 2
                    elif attr == "stdout":
                        fd = 1
        return sep_val, end_val, fd

    def _gen_print(self, call_expr: CallExpr, indent: str):
        """Emit WAT for a ``print(...)`` call."""
        self._emit(f"{indent};; print(...)")
        sep_val, end_val, fd = self._print_options(call_expr)
        if fd != 1:
            # Temporarily override the write fd for this print call.
            self._print_fd_override = fd
        for index, arg in enumerate(call_expr.args):
            if index > 0:
                self._emit_print_separator(sep_val, indent)
            self._emit_print_arg(arg, indent)
        self._emit_print_end(end_val, indent)
        if fd != 1:
            del self._print_fd_override

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
            if arg.name in self._zip_pair_locals:
                self._emit_print_zip_pair_sequence(arg.name, indent)
                return
            self._emit_print_sequence(arg.name, "[", "]", indent)
            return
        if self._is_zip_pair_list_expr(arg):
            self._emit_print_zip_pair_sequence_expr(arg, indent)
            return
        if self._value_tracks_as_tuple(arg):
            self._emit_print_sequence_expr(arg, "(", ")", indent)
            return
        if self._value_tracks_as_list(arg):
            self._emit_print_sequence_expr(arg, "[", "]", indent)
            return
        if isinstance(arg, CallExpr) and _name(arg.func) in self._string_return_funcs:
            self._emit_print_string_call(arg, indent)
            return
        if self._is_string_value(arg):
            self._emit_print_string_expr(arg, indent)
            return
        # If the argument is a tracked class instance and has __str__, call it.
        if isinstance(arg, Identifier):
            cls_name = self._var_class_types.get(arg.name)
            if cls_name:
                str_key = f"{cls_name}.__str__"
                str_fn = self._class_special_methods.get(str_key)
                if str_fn:
                    self._emit(f"{indent};; print(obj) via {cls_name}.__str__")
                    tmp_len = f"__print_str_len_{self._new_label()}"
                    self._locals.add(tmp_len)
                    self._emit(f"{indent}local.get ${self._wat_symbol(arg.name)}")
                    self._emit(f"{indent}call ${self._wat_symbol(str_fn)}")
                    self._emit(f"{indent}global.get $__last_str_len")
                    self._emit(f"{indent}f64.convert_i32_u")
                    self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
                    self._emit(f"{indent}i32.trunc_f64_u")
                    self._emit(f"{indent}call $print_str")
                    return
        if isinstance(arg, NumeralLiteral) and "." in arg.value:
            self._gen_expr(arg, indent)
            self._emit(f"{indent}call $print_f64_float")
            return
        self._gen_expr(arg, indent)
        self._emit(f"{indent}call $print_f64")

    def _print_fd(self) -> int:
        """Return the active print file descriptor (1=stdout, 2=stderr)."""
        return getattr(self, "_print_fd_override", 1)

    def _emit_write_fd(self, ptr_instr: str, len_instr: str, indent: str) -> None:
        """Emit a write to the active print fd (stdout or stderr)."""
        fd = self._print_fd()
        if fd == 1:
            self._emit(f"{indent}{ptr_instr}")
            self._emit(f"{indent}{len_instr}")
            self._emit(f"{indent}call $print_str")
        else:
            self._emit(f"{indent}i32.const {fd}  ;; fd={fd}")
            self._emit(f"{indent}{ptr_instr}")
            self._emit(f"{indent}{len_instr}")
            self._emit(f"{indent}call $__wasi_write_fd")

    def _emit_print_literal_string(self, value: str, indent: str, note: str) -> None:
        """Emit a string literal directly."""
        offset, length = self._intern(value)
        fd = self._print_fd()
        if fd == 1:
            self._emit(f"{indent}i32.const {offset}   ;; {note} ptr")
            self._emit(f"{indent}i32.const {length}   ;; {note} len")
            self._emit(f"{indent}call $print_str")
        else:
            self._emit(f"{indent}i32.const {fd}  ;; fd={fd}")
            self._emit(f"{indent}i32.const {offset}   ;; {note} ptr")
            self._emit(f"{indent}i32.const {length}   ;; {note} len")
            self._emit(f"{indent}call $__wasi_write_fd")

    def _emit_print_fstring(self, arg: FStringLiteral, indent: str) -> None:
        """Emit a formatted string argument."""
        if self._gen_fstring_expr(arg, indent):
            tmp_len = f"__print_fstr_len_{self._new_label()}"
            self._locals.add(tmp_len)
            self._emit(f"{indent}global.get $__last_str_len")
            self._emit(f"{indent}f64.convert_i32_u")
            self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
            self._emit(f"{indent}i32.trunc_f64_u")
            self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
            self._emit(f"{indent}i32.trunc_f64_u")
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
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}call $print_str")

    def _emit_print_string_expr(self, arg, indent: str) -> None:
        """Print a string-valued expression using $__last_str_len metadata."""
        tmp_len = f"__print_expr_len_{self._new_label()}"
        self._locals.add(tmp_len)
        self._gen_expr(arg, indent)
        self._emit(f"{indent}global.get $__last_str_len")
        self._emit(f"{indent}f64.convert_i32_u")
        self._emit(f"{indent}local.set ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
        self._emit(f"{indent}local.get ${self._wat_symbol(tmp_len)}")
        self._emit(f"{indent}i32.trunc_f64_u")
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

    def _emit_print_sequence_expr(
        self, expr, opening: str, closing: str, indent: str
    ) -> None:
        """Print a list/tuple-producing expression by first storing its pointer."""
        lbl = self._new_label()
        ptr_local = f"__print_ptr_{lbl}"
        idx_local = f"__print_idx_{lbl}"
        len_local = f"__print_len_{lbl}"
        self._locals.update({ptr_local, idx_local, len_local})
        self._gen_expr(expr, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
        open_ptr, open_len = self._intern(opening)
        close_ptr, close_len = self._intern(closing)
        comma_ptr, comma_len = self._intern(", ")
        self._emit(f"{indent}i32.const {open_ptr}")
        self._emit(f"{indent}i32.const {open_len}")
        self._emit(f"{indent}call $print_str")
        self._emit_sequence_len_setup(ptr_local, len_local, idx_local, indent)
        self._emit_print_sequence_loop(
            ptr_local, idx_local, len_local, comma_ptr, comma_len, indent, lbl
        )
        self._emit(f"{indent}i32.const {close_ptr}")
        self._emit(f"{indent}i32.const {close_len}")
        self._emit(f"{indent}call $print_str")

    def _is_zip_pair_list_expr(self, expr) -> bool:
        """Return True for list(zip(...)) expressions with static tuple pairs."""
        return self._materialized_zip_elements_from_list_call(expr) is not None

    def _emit_print_zip_pair_sequence(self, name: str, indent: str) -> None:
        """Print a tracked list whose elements are tuple pointers from zip(...)."""
        self._emit_print_zip_pair_pointer(name, indent)

    def _emit_print_zip_pair_sequence_expr(self, expr, indent: str) -> None:
        """Print a list(zip(...)) expression whose elements are tuple pointers."""
        lbl = self._new_label()
        ptr_local = f"__print_zip_ptr_{lbl}"
        self._locals.add(ptr_local)
        self._gen_expr(expr, indent)
        self._emit(f"{indent}local.set ${self._wat_symbol(ptr_local)}")
        self._emit_print_zip_pair_pointer(ptr_local, indent)

    def _emit_print_zip_pair_pointer(self, ptr_local: str, indent: str) -> None:
        """Print an outer list whose items are tuple pointers."""
        lbl = self._new_label()
        idx_local = f"__print_zip_idx_{lbl}"
        len_local = f"__print_zip_len_{lbl}"
        elem_ptr_local = f"__print_zip_elem_{lbl}"
        self._locals.update({idx_local, len_local, elem_ptr_local})
        open_ptr, open_len = self._intern("[")
        close_ptr, close_len = self._intern("]")
        comma_ptr, comma_len = self._intern(", ")
        self._emit(f"{indent}i32.const {open_ptr}")
        self._emit(f"{indent}i32.const {open_len}")
        self._emit(f"{indent}call $print_str")
        self._emit_sequence_len_setup(ptr_local, len_local, idx_local, indent)
        blk = f"print_zip_blk_{lbl}"
        loop = f"print_zip_lp_{lbl}"
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
        self._emit_sequence_value_load(ptr_local, idx_local, indent + "    ")
        self._emit(f"{indent}    local.set ${self._wat_symbol(elem_ptr_local)}")
        self._emit_print_sequence_pointer(elem_ptr_local, "(", ")", indent + "    ")
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

    def _emit_print_sequence_pointer(
        self, ptr_local: str, opening: str, closing: str, indent: str
    ) -> None:
        """Print a list/tuple pointed to by a local f64 pointer."""
        lbl = self._new_label()
        idx_local = f"__print_ptr_idx_{lbl}"
        len_local = f"__print_ptr_len_{lbl}"
        self._locals.update({idx_local, len_local})
        open_ptr, open_len = self._intern(opening)
        close_ptr, close_len = self._intern(closing)
        comma_ptr, comma_len = self._intern(", ")
        self._emit(f"{indent}i32.const {open_ptr}")
        self._emit(f"{indent}i32.const {open_len}")
        self._emit(f"{indent}call $print_str")
        self._emit_sequence_len_setup(ptr_local, len_local, idx_local, indent)
        self._emit_print_sequence_loop(
            ptr_local, idx_local, len_local, comma_ptr, comma_len, indent, lbl
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
