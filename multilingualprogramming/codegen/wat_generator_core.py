#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core shared methods for the WAT generator."""

import re


class WATGeneratorCoreMixin:
    """Core module/string/symbol helpers for WATCodeGenerator."""

    _data: bytearray
    _strings: dict[str, tuple[int, int]]
    _class_obj_sizes: dict[str, int]
    _need_heap_ptr: bool
    _lambda_table: list[str]
    _funcs: list[str]
    _label_count: int = 0
    _wat_symbols: dict[str, str]
    _used_wat_symbols: set[str]

    @staticmethod
    def state_attribute_names() -> tuple[str, ...]:
        """Return the core mutable state fields required by the mixin."""
        return (
            "_data",
            "_strings",
            "_class_obj_sizes",
            "_need_heap_ptr",
            "_lambda_table",
            "_funcs",
            "_label_count",
            "_wat_symbols",
            "_used_wat_symbols",
        )

    def _build_module(self) -> str:
        lines = ["(module"]
        lines += [
            '  (import "env" "print_str"     (func $print_str     (param i32 i32)))',
            '  (import "env" "print_f64"     (func $print_f64     (param f64)))',
            '  (import "env" "print_bool"    (func $print_bool    (param i32)))',
            '  (import "env" "print_sep"     (func $print_sep))',
            '  (import "env" "print_newline" (func $print_newline))',
            '  (import "env" "pow_f64"       (func $pow_f64       (param f64 f64) (result f64)))',
            '  (memory (export "memory") 1)',
        ]
        if self._data:
            escaped = "".join(f"\\{b:02x}" for b in self._data)
            lines.append(f'  (data (i32.const 0) "{escaped}")')
        has_stateful = any(size > 0 for size in self._class_obj_sizes.values())
        if has_stateful or self._need_heap_ptr:
            heap_base = max((len(self._data) + 7) // 8 * 8, 64)
            lines.append(f'  (global $__heap_ptr (mut i32) (i32.const {heap_base}))')
        if self._lambda_table:
            n = len(self._lambda_table)
            lines.append(f'  (table {n} funcref)')
            elems = " ".join(f"${self._wat_symbol(fn)}" for fn in self._lambda_table)
            lines.append(f'  (elem (i32.const 0) {elems})')
        lines.extend(self._funcs)
        lines.append(")")
        return "\n".join(lines)

    def _intern(self, s: str) -> tuple[int, int]:
        """Return (byte_offset, byte_length) for a string in the data section."""
        if s not in self._strings:
            encoded = s.encode("utf-8")
            offset = len(self._data)
            self._data.extend(encoded)
            self._strings[s] = (offset, len(encoded))
        return self._strings[s]

    def _new_label(self) -> int:
        self._label_count += 1
        return self._label_count

    def _wat_symbol(self, name: str) -> str:
        """Return a deterministic, WAT-safe symbol for a source identifier."""
        key = str(name)
        if key in self._wat_symbols:
            return self._wat_symbols[key]

        safe = re.sub(r"[^A-Za-z0-9_.$]", "_", key)
        if not safe:
            safe = "sym"
        if safe[0].isdigit():
            safe = f"n_{safe}"

        candidate = safe
        suffix = 2
        while candidate in self._used_wat_symbols:
            candidate = f"{safe}_{suffix}"
            suffix += 1

        self._used_wat_symbols.add(candidate)
        self._wat_symbols[key] = candidate
        return candidate
