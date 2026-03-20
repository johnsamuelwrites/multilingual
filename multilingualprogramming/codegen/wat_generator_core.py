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
    _uses_dom: bool
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
            "_uses_dom",
            "_lambda_table",
            "_funcs",
            "_label_count",
            "_wat_symbols",
            "_used_wat_symbols",
        )

    def _build_module(self) -> str:
        heap_base = max((len(self._data) + 7) // 8 * 8, 64)
        self._emit_wasi_runtime(heap_base)
        if self._uses_dom and getattr(self, "_wasm_target", "browser") != "wasi":
            self._emit_dom_runtime()
        lines = ["(module"]
        lines += [
            '  (import "wasi_snapshot_preview1" "fd_write"'
            ' (func $fd_write (param i32 i32 i32 i32) (result i32)))',
            '  (import "wasi_snapshot_preview1" "fd_read"'
            ' (func $fd_read (param i32 i32 i32 i32) (result i32)))',
            '  (import "wasi_snapshot_preview1" "args_sizes_get"'
            ' (func $args_sizes_get (param i32 i32) (result i32)))',
            '  (import "wasi_snapshot_preview1" "args_get"'
            ' (func $args_get (param i32 i32) (result i32)))',
        ]
        if self._uses_dom and getattr(self, "_wasm_target", "browser") != "wasi":
            from multilingualprogramming.codegen.wat_generator_support import (  # pylint: disable=import-outside-toplevel
                _DOM_HOST_SIGNATURES,
            )
            for wat_name, (params, ret) in _DOM_HOST_SIGNATURES.items():
                param_str = " ".join(f"(param {t})" for t in params)
                ret_str = f" (result {ret})" if ret else ""
                lines.append(
                    f'  (import "env" "{wat_name}"'
                    f' (func ${wat_name} {param_str}{ret_str}))'
                )
        lines.append(f'  (memory (export "memory") {self._WASM_PAGES})')
        if self._data:
            escaped = "".join(f"\\{b:02x}" for b in self._data)
            lines.append(f'  (data (i32.const 0) "{escaped}")')
        # $__heap_ptr is always declared: $ml_alloc references it unconditionally.
        lines.append(f'  (global $__heap_ptr (mut i32) (i32.const {heap_base}))')
        lines.append('  (global $__last_str_len (mut i32) (i32.const 0))')
        lines.append('  (global $__ml_argc (mut i32) (i32.const 0))')
        lines.append(
            '  (global $__last_exc_code (export "__last_exception_code") (mut i32) (i32.const 0))'
        )
        if self._lambda_table:
            n = len(self._lambda_table)
            lines.append(f'  (table {n} funcref)')
            elems = " ".join(f"${self._wat_symbol(fn)}" for fn in self._lambda_table)
            lines.append(f'  (elem (i32.const 0) {elems})')
        lines.extend(self._funcs)
        lines.append(")")
        return "\n".join(lines)

    @staticmethod
    def function_state_attribute_names() -> tuple[str, ...]:
        """Return mutable function-generation fields shared across mixins."""
        return (
            "_instrs",
            "_locals",
            "_loop_stack",
            "_var_class_types",
            "_current_class",
            "_string_len_locals",
            "_list_locals",
            "_tuple_locals",
            "_dict_key_maps",
            "_lambda_locals",
            "_closure_locals",
            "_try_stack",
            "_open_aliases",
            "_virtual_file_contents",
        )

    @staticmethod
    def function_state_reset_factories() -> tuple[tuple[str, object], ...]:
        """Return factories used when entering nested function emission."""
        return (
            ("_instrs", list),
            ("_locals", set),
            ("_loop_stack", list),
            ("_var_class_types", dict),
            ("_string_len_locals", dict),
            ("_list_locals", set),
            ("_tuple_locals", set),
            ("_dict_key_maps", dict),
            ("_lambda_locals", dict),
            ("_closure_locals", dict),
            ("_try_stack", list),
            ("_open_aliases", dict),
            ("_virtual_file_contents", dict),
        )

    def _capture_func_state(self):
        """Snapshot mutable function-generation state for nested emission."""
        return tuple(getattr(self, name) for name in self.function_state_attribute_names())

    def _restore_captured_func_state(self, saved) -> None:
        """Restore a snapshot produced by :meth:`_capture_func_state`."""
        for name, value in zip(self.function_state_attribute_names(), saved):
            setattr(self, name, value)

    def _reset_func_state(self) -> None:
        """Reset nested-function state while preserving the current class."""
        for name, factory in self.function_state_reset_factories():
            setattr(self, name, factory())

    def _append_wat_function(
        self,
        func_name: str,
        param_names: list[str],
        body_instrs: list[str],
        local_names: list[str] | None = None,
        *,
        implicit_return: bool = True,
    ) -> None:
        """Append a standard exported WAT function to the module."""
        if local_names is None:
            local_names = sorted(self._locals - set(param_names))
        wat_func_name = self._wat_symbol(func_name)
        lines = [f'  (func ${wat_func_name} (export "{func_name}")']
        for param_name in param_names:
            lines.append(f"    (param ${self._wat_symbol(param_name)} f64)")
        lines.append("    (result f64)")
        for local_name in local_names:
            lines.append(f"    (local ${self._wat_symbol(local_name)} f64)")
        lines.extend(body_instrs)
        if implicit_return:
            lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")
        self._funcs.append("\n".join(lines))

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

    # Total WASM memory pages.  4 pages = 256 KB — enough for all current
    # examples.  Scratch area lives in the last 64 bytes of the last page so
    # the heap (which grows from the data section upward) can never reach it.
    _WASM_PAGES: int = 4

    def _emit_wasi_runtime(self, heap_base: int) -> None:
        """Emit self-contained WAT functions for I/O and math.

        Replaces the six former ``env`` host imports with internal WAT
        implementations backed by the single WASI ``fd_write`` syscall.

        Scratch memory layout (last 64 bytes of the last page):
          SCRATCH+0 ..+7   iovec struct {ptr:i32, len:i32}
          SCRATCH+8 ..+11  nwritten (i32)
          SCRATCH+12..+63  formatting buffer (52 bytes)
            - 20 bytes for $__fmt_u64 (integer digits, written backward from MEM_END)
            -  6 bytes for $__fmt_frac6 (fractional digits)
            - remaining bytes for single-char writes
        where SCRATCH = _WASM_PAGES * 65536 - 64  and  MEM_END = _WASM_PAGES * 65536.
        """
        mem_end = self._WASM_PAGES * 65536
        scratch = mem_end - 64
        iovec = scratch           # iovec.ptr  (i32 at scratch+0)
        iovec_len = scratch + 4   # iovec.len  (i32 at scratch+4)
        nwritten = scratch + 8    # nwritten   (i32 at scratch+8)
        fmt = scratch + 12        # format buffer base
        input_buf = mem_end - 320  # 256-byte stdin line buffer (before scratch)
        input_buf_size = 256
        # argv static layout (top 1024 bytes minus lower areas):
        argv_data = mem_end - 1024  # 512-byte buffer for null-terminated arg strings
        argv_ptrs = mem_end - 512   # 128-byte table of i32 ptrs (32 args max)
        argc_addr = mem_end - 384   # 4-byte i32 storing argc after init

        runtime = f"""
  ;; ── WASI runtime ────────────────────────────────────────────────────────────
  ;; Write `len` bytes at `ptr` to stdout via WASI fd_write.
  (func $__wasi_write (param $ptr i32) (param $len i32)
    i32.const {iovec}
    local.get $ptr
    i32.store
    i32.const {iovec_len}
    local.get $len
    i32.store
    i32.const 1
    i32.const {iovec}
    i32.const 1
    i32.const {nwritten}
    call $fd_write
    drop
  )
  ;; Write `len` bytes at `ptr` to file-descriptor `fd` via WASI fd_write.
  (func $__wasi_write_fd (param $fd i32) (param $ptr i32) (param $len i32)
    i32.const {iovec}
    local.get $ptr
    i32.store
    i32.const {iovec_len}
    local.get $len
    i32.store
    local.get $fd
    i32.const {iovec}
    i32.const 1
    i32.const {nwritten}
    call $fd_write
    drop
  )
  ;; Format a non-negative i64 as decimal, writing backwards from address {mem_end}.
  ;; Returns: (start_ptr: i32, byte_len: i32)
  (func $__fmt_u64 (param $n i64) (result i32 i32)
    (local $ptr i32)
    (local $digit i32)
    i32.const {mem_end}
    local.set $ptr
    local.get $n
    i64.const 0
    i64.eq
    if
      local.get $ptr
      i32.const 1
      i32.sub
      local.tee $ptr
      i32.const 48
      i32.store8
    else
      block $done
        loop $lp
          local.get $n
          i64.const 0
          i64.le_u
          br_if $done
          local.get $n
          i64.const 10
          i64.rem_u
          i32.wrap_i64
          i32.const 48
          i32.add
          local.set $digit
          local.get $n
          i64.const 10
          i64.div_u
          local.set $n
          local.get $ptr
          i32.const 1
          i32.sub
          local.tee $ptr
          local.get $digit
          i32.store8
          br $lp
        end
      end
    end
    local.get $ptr
    i32.const {mem_end}
    local.get $ptr
    i32.sub
  )
  ;; Write 6 decimal digits of n (0..999999) to {fmt}..{fmt+5}, strip trailing
  ;; zeros (keep at least 1).  Returns: (ptr={fmt}, trimmed_len: i32)
  (func $__fmt_frac6 (param $n i64) (result i32 i32)
    (local $trimmed i32)
    i32.const {fmt}
    local.get $n
    i64.const 100000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const {fmt+1}
    local.get $n
    i64.const 100000
    i64.rem_u
    i64.const 10000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const {fmt+2}
    local.get $n
    i64.const 10000
    i64.rem_u
    i64.const 1000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const {fmt+3}
    local.get $n
    i64.const 1000
    i64.rem_u
    i64.const 100
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const {fmt+4}
    local.get $n
    i64.const 100
    i64.rem_u
    i64.const 10
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const {fmt+5}
    local.get $n
    i64.const 10
    i64.rem_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 6
    local.set $trimmed
    block $done
      loop $strip
        local.get $trimmed
        i32.const 1
        i32.le_s
        br_if $done
        i32.const {fmt}
        local.get $trimmed
        i32.const 1
        i32.sub
        i32.add
        i32.load8_u
        i32.const 48
        i32.eq
        i32.eqz
        br_if $done
        local.get $trimmed
        i32.const 1
        i32.sub
        local.set $trimmed
        br $strip
      end
    end
    i32.const {fmt}
    local.get $trimmed
  )
  ;; Print a newline.
  (func $print_newline
    i32.const {fmt}
    i32.const 10
    i32.store8
    i32.const {fmt}
    i32.const 1
    call $__wasi_write
  )
  ;; Print a space separator.
  (func $print_sep
    i32.const {fmt}
    i32.const 32
    i32.store8
    i32.const {fmt}
    i32.const 1
    call $__wasi_write
  )
  ;; Print a UTF-8 string from linear memory.
  (func $print_str (param $ptr i32) (param $len i32)
    local.get $ptr
    local.get $len
    call $__wasi_write
  )
  ;; Print a boolean: non-zero -> "True", zero -> "False".
  (func $print_bool (param $v i32)
    local.get $v
    i32.eqz
    if
      i32.const {fmt}
      i32.const 70
      i32.store8
      i32.const {fmt+1}
      i32.const 97
      i32.store8
      i32.const {fmt+2}
      i32.const 108
      i32.store8
      i32.const {fmt+3}
      i32.const 115
      i32.store8
      i32.const {fmt+4}
      i32.const 101
      i32.store8
      i32.const {fmt}
      i32.const 5
      call $__wasi_write
    else
      i32.const {fmt}
      i32.const 84
      i32.store8
      i32.const {fmt+1}
      i32.const 114
      i32.store8
      i32.const {fmt+2}
      i32.const 117
      i32.store8
      i32.const {fmt+3}
      i32.const 101
      i32.store8
      i32.const {fmt}
      i32.const 4
      call $__wasi_write
    end
  )
  ;; Print a double-precision float.
  ;; Integer values (v == trunc(v), |v| < 1e15) are printed as plain "N".
  ;; Other values are printed with up to 6 fractional decimal places.
  (func $print_f64 (param $v f64)
    (local $int_part i64)
    (local $frac f64)
    (local $frac_scaled i64)
    (local $ptr i32)
    (local $len i32)
    local.get $v
    local.get $v
    f64.ne
    if
      i32.const {fmt}
      i32.const 110
      i32.store8
      i32.const {fmt+1}
      i32.const 97
      i32.store8
      i32.const {fmt+2}
      i32.const 110
      i32.store8
      i32.const {fmt}
      i32.const 3
      call $__wasi_write
      return
    end
    local.get $v
    f64.const 0.0
    f64.lt
    if
      i32.const {fmt}
      i32.const 45
      i32.store8
      i32.const {fmt}
      i32.const 1
      call $__wasi_write
      local.get $v
      f64.neg
      local.set $v
    end
    local.get $v
    f64.const inf
    f64.eq
    if
      i32.const {fmt}
      i32.const 105
      i32.store8
      i32.const {fmt+1}
      i32.const 110
      i32.store8
      i32.const {fmt+2}
      i32.const 102
      i32.store8
      i32.const {fmt}
      i32.const 3
      call $__wasi_write
      return
    end
    local.get $v
    f64.trunc
    local.get $v
    f64.eq
    local.get $v
    f64.const 1000000000000000.0
    f64.lt
    i32.and
    if
      local.get $v
      i64.trunc_f64_u
      local.set $int_part
      local.get $int_part
      call $__fmt_u64
      local.set $len
      local.set $ptr
      local.get $ptr
      local.get $len
      call $__wasi_write
      return
    end
    local.get $v
    f64.trunc
    i64.trunc_f64_u
    local.set $int_part
    local.get $int_part
    call $__fmt_u64
    local.set $len
    local.set $ptr
    local.get $ptr
    local.get $len
    call $__wasi_write
    i32.const {fmt}
    i32.const 46
    i32.store8
    i32.const {fmt}
    i32.const 1
    call $__wasi_write
    local.get $v
    local.get $v
    f64.trunc
    f64.sub
    local.set $frac
    local.get $frac
    f64.const 1000000.0
    f64.mul
    f64.nearest
    i64.trunc_f64_u
    local.set $frac_scaled
    local.get $frac_scaled
    i64.const 0
    i64.eq
    if
      i32.const {fmt}
      i32.const 48
      i32.store8
      i32.const {fmt}
      i32.const 1
      call $__wasi_write
    else
      local.get $frac_scaled
      call $__fmt_frac6
      local.set $len
      local.set $ptr
      local.get $ptr
      local.get $len
      call $__wasi_write
    end
  )
  ;; Self-contained power: base^exp.
  ;; Exact for exp in {0, 1, 0.5, -0.5} and integer exponents up to 2^31-1.
  ;; Non-integer, non-half exponents return NaN.
  (func $pow_f64 (param $base f64) (param $exp f64) (result f64)
    (local $result f64)
    (local $n i32)
    (local $neg i32)
    local.get $exp
    f64.const 0.0
    f64.eq
    if
      f64.const 1.0
      return
    end
    local.get $exp
    f64.const 1.0
    f64.eq
    if
      local.get $base
      return
    end
    local.get $exp
    f64.const 0.5
    f64.eq
    if
      local.get $base
      f64.sqrt
      return
    end
    local.get $exp
    f64.const -0.5
    f64.eq
    if
      f64.const 1.0
      local.get $base
      f64.sqrt
      f64.div
      return
    end
    f64.const 0.0
    local.get $exp
    f64.lt
    local.set $neg
    local.get $exp
    f64.abs
    local.set $exp
    local.get $exp
    f64.trunc
    local.get $exp
    f64.ne
    if
      f64.const nan
      return
    end
    local.get $exp
    i32.trunc_f64_u
    local.set $n
    f64.const 1.0
    local.set $result
    block $done
      loop $lp
        local.get $n
        i32.eqz
        br_if $done
        local.get $result
        local.get $base
        f64.mul
        local.set $result
        local.get $n
        i32.const 1
        i32.sub
        local.set $n
        br $lp
      end
    end
    local.get $neg
    if
      f64.const 1.0
      local.get $result
      f64.div
      local.set $result
    end
    local.get $result
  )
  ;; ── Allocator ────────────────────────────────────────────────────────────
  ;; Three segregated free lists by size class (≤32, ≤64, ≤256 bytes).
  ;; Larger blocks are bump-allocated and never freed (no GC needed for them).
  (global $__fl_s32  (mut i32) (i32.const 0))
  (global $__fl_s64  (mut i32) (i32.const 0))
  (global $__fl_s256 (mut i32) (i32.const 0))
  ;; Heap base: fixed at compile time for reset support.
  (global $__heap_base i32 (i32.const {heap_base}))
  ;; Allocate `size` bytes; returns i32 pointer.
  ;; Checks the appropriate free list first, falls back to bump allocation.
  (func $ml_alloc (param $size i32) (result i32)
    (local $head i32) (local $ptr i32)
    block $miss
      local.get $size
      i32.const 32
      i32.le_s
      if
        global.get $__fl_s32
        local.tee $head
        i32.eqz
        br_if $miss
        local.get $head
        i32.load
        global.set $__fl_s32
        local.get $head
        return
      end
      local.get $size
      i32.const 64
      i32.le_s
      if
        global.get $__fl_s64
        local.tee $head
        i32.eqz
        br_if $miss
        local.get $head
        i32.load
        global.set $__fl_s64
        local.get $head
        return
      end
      local.get $size
      i32.const 256
      i32.le_s
      if
        global.get $__fl_s256
        local.tee $head
        i32.eqz
        br_if $miss
        local.get $head
        i32.load
        global.set $__fl_s256
        local.get $head
        return
      end
    end
    global.get $__heap_ptr
    local.set $ptr
    local.get $ptr
    local.get $size
    i32.add
    global.set $__heap_ptr
    local.get $ptr
  )
  ;; Return `size` bytes at `ptr` to the appropriate free list.
  ;; Blocks larger than 256 bytes are not tracked (bump-only region).
  (func $ml_free (param $ptr i32) (param $size i32)
    local.get $size
    i32.const 32
    i32.le_s
    if
      local.get $ptr
      global.get $__fl_s32
      i32.store
      local.get $ptr
      global.set $__fl_s32
      return
    end
    local.get $size
    i32.const 64
    i32.le_s
    if
      local.get $ptr
      global.get $__fl_s64
      i32.store
      local.get $ptr
      global.set $__fl_s64
      return
    end
    local.get $size
    i32.const 256
    i32.le_s
    if
      local.get $ptr
      global.get $__fl_s256
      i32.store
      local.get $ptr
      global.set $__fl_s256
      return
    end
  )
  ;; Reset heap to its initial state and clear all free lists.
  ;; Exported so the browser host can call it between "run" invocations.
  (func $__ml_reset (export "__ml_reset")
    global.get $__heap_base
    global.set $__heap_ptr
    i32.const 0
    global.set $__fl_s32
    i32.const 0
    global.set $__fl_s64
    i32.const 0
    global.set $__fl_s256
  )
  ;; Return the byte length of the last string-valued function result.
  ;; JS callers: invoke immediately after a string-returning export, then
  ;; decode memory.buffer[ptr .. ptr+len] as UTF-8.
  (func $__ml_str_len (export "__ml_str_len") (result i32)
    global.get $__last_str_len
  )
  ;; Print a double-precision float always showing a decimal point.
  ;; Integer values (v == trunc(v), |v| < 1e15) are printed as "N.0".
  ;; Use this when the source literal was written as 1.0, 2.0, etc.
  (func $print_f64_float (param $v f64)
    (local $int_part i64)
    (local $frac f64)
    (local $frac_scaled i64)
    (local $ptr i32)
    (local $len i32)
    local.get $v
    local.get $v
    f64.ne
    if
      i32.const {fmt}
      i32.const 110
      i32.store8
      i32.const {fmt+1}
      i32.const 97
      i32.store8
      i32.const {fmt+2}
      i32.const 110
      i32.store8
      i32.const {fmt}
      i32.const 3
      call $__wasi_write
      return
    end
    local.get $v
    f64.const 0.0
    f64.lt
    if
      i32.const {fmt}
      i32.const 45
      i32.store8
      i32.const {fmt}
      i32.const 1
      call $__wasi_write
      local.get $v
      f64.neg
      local.set $v
    end
    local.get $v
    f64.const inf
    f64.eq
    if
      i32.const {fmt}
      i32.const 105
      i32.store8
      i32.const {fmt+1}
      i32.const 110
      i32.store8
      i32.const {fmt+2}
      i32.const 102
      i32.store8
      i32.const {fmt}
      i32.const 3
      call $__wasi_write
      return
    end
    local.get $v
    f64.trunc
    local.get $v
    f64.eq
    local.get $v
    f64.const 1000000000000000.0
    f64.lt
    i32.and
    if
      local.get $v
      i64.trunc_f64_u
      local.set $int_part
      local.get $int_part
      call $__fmt_u64
      local.set $len
      local.set $ptr
      local.get $ptr
      local.get $len
      call $__wasi_write
      i32.const {fmt}
      i32.const 46
      i32.store8
      i32.const {fmt+1}
      i32.const 48
      i32.store8
      i32.const {fmt}
      i32.const 2
      call $__wasi_write
      return
    end
    local.get $v
    f64.trunc
    i64.trunc_f64_u
    local.set $int_part
    local.get $int_part
    call $__fmt_u64
    local.set $len
    local.set $ptr
    local.get $ptr
    local.get $len
    call $__wasi_write
    i32.const {fmt}
    i32.const 46
    i32.store8
    i32.const {fmt}
    i32.const 1
    call $__wasi_write
    local.get $v
    local.get $v
    f64.trunc
    f64.sub
    local.set $frac
    local.get $frac
    f64.const 1000000.0
    f64.mul
    f64.nearest
    i64.trunc_f64_u
    local.set $frac_scaled
    local.get $frac_scaled
    i64.const 0
    i64.eq
    if
      i32.const {fmt}
      i32.const 48
      i32.store8
      i32.const {fmt}
      i32.const 1
      call $__wasi_write
    else
      local.get $frac_scaled
      call $__fmt_frac6
      local.set $len
      local.set $ptr
      local.get $ptr
      local.get $len
      call $__wasi_write
    end
  )
  ;; argv support ─────────────────────────────────────────────────────────────
  ;; $__ml_argc caches the argument count after $__ml_init_argv is called.
  ;; Populated at module startup; never written by user code.
  ;; Init: reads argc + argv via WASI args_sizes_get / args_get into static buffers.
  ;; Layout: argv_data [{argv_data}..{argv_data+511}], argv_ptrs [{argv_ptrs}..{argv_ptrs+127}]
  (func $__ml_init_argv
    i32.const {argc_addr}
    i32.const {scratch}
    call $args_sizes_get
    drop
    i32.const {argc_addr}
    i32.load
    global.set $__ml_argc
    i32.const {argv_ptrs}
    i32.const {argv_data}
    call $args_get
    drop
  )
  ;; Return argument count as f64.
  (func $argc (export "argc") (result f64)
    global.get $__ml_argc
    f64.convert_i32_u
  )
  ;; Return i-th argument as a string (ptr as f64, length in $__last_str_len).
  (func $argv (param $i f64) (result f64)
    (local $idx i32)
    (local $ptr i32)
    (local $cur i32)
    local.get $i
    i32.trunc_f64_u
    local.tee $idx
    global.get $__ml_argc
    i32.ge_u
    if
      i32.const 0
      global.set $__last_str_len
      f64.const 0
      return
    end
    i32.const {argv_ptrs}
    local.get $idx
    i32.const 4
    i32.mul
    i32.add
    i32.load
    local.tee $ptr
    local.set $cur
    block $len_done
      loop $len_loop
        local.get $cur
        i32.load8_u
        i32.eqz
        br_if $len_done
        local.get $cur
        i32.const 1
        i32.add
        local.set $cur
        br $len_loop
      end
    end
    local.get $cur
    local.get $ptr
    i32.sub
    global.set $__last_str_len
    local.get $ptr
    f64.convert_i32_u
  )
  ;; Read one line from stdin (fd 0) into a fixed buffer, strip trailing CR/LF.
  ;; Writes the prompt (if len > 0) to stdout first.
  ;; Returns: buffer address as f64; sets $__last_str_len to byte length.
  ;; Input buffer: [{input_buf} .. {input_buf + input_buf_size - 1}] ({input_buf_size} bytes).
  ;; In browser mode, delegates to $ml_input_host (JS window.prompt).
  (func $input (param $prompt_ptr i32) (param $prompt_len i32) (result f64)
    (local $nread i32)
    (local $tail i32)
    (local $byte i32)
    local.get $prompt_len
    i32.const 0
    i32.gt_s
    if
      local.get $prompt_ptr
      local.get $prompt_len
      call $__wasi_write
    end
    ;; iovec: ptr = input_buf, len = input_buf_size
    i32.const {iovec}
    i32.const {input_buf}
    i32.store
    i32.const {iovec_len}
    i32.const {input_buf_size}
    i32.store
    i32.const 0
    i32.const {iovec}
    i32.const 1
    i32.const {nwritten}
    call $fd_read
    drop
    i32.const {nwritten}
    i32.load
    local.set $nread
    ;; strip trailing CR (13) and LF (10)
    block $strip_done
      loop $strip_loop
        local.get $nread
        i32.const 0
        i32.le_s
        br_if $strip_done
        i32.const {input_buf}
        local.get $nread
        i32.const 1
        i32.sub
        i32.add
        i32.load8_u
        local.set $byte
        local.get $byte
        i32.const 10
        i32.eq
        local.get $byte
        i32.const 13
        i32.eq
        i32.or
        if
          local.get $nread
          i32.const 1
          i32.sub
          local.set $nread
          br $strip_loop
        end
        br $strip_done
      end
    end
    local.get $nread
    global.set $__last_str_len
    i32.const {input_buf}
    f64.convert_i32_u
  )
  ;; Strip leading and trailing ASCII whitespace (space/tab/CR/LF) from a string.
  ;; Params: $ptr i32, $len i32 (via $__last_str_len on entry).
  ;; Returns f64 = new ptr (i32 as f64); $__last_str_len set to new length.
  ;; The result points into the original linear-memory slice (no copy).
  (func $__str_strip (param $ptr i32) (param $len i32) (result f64)
    (local $end i32)
    (local $b i32)
    local.get $ptr
    local.get $len
    i32.add
    local.set $end
    ;; skip leading whitespace
    block $ldone
      loop $ltrim
        local.get $ptr
        local.get $end
        i32.ge_u
        br_if $ldone
        local.get $ptr
        i32.load8_u
        local.set $b
        local.get $b
        i32.const 32
        i32.eq
        local.get $b
        i32.const 9
        i32.eq
        i32.or
        local.get $b
        i32.const 13
        i32.eq
        i32.or
        local.get $b
        i32.const 10
        i32.eq
        i32.or
        i32.eqz
        br_if $ldone
        local.get $ptr
        i32.const 1
        i32.add
        local.set $ptr
        br $ltrim
      end
    end
    ;; skip trailing whitespace
    block $rdone
      loop $rtrim
        local.get $end
        local.get $ptr
        i32.le_u
        br_if $rdone
        local.get $end
        i32.const 1
        i32.sub
        i32.load8_u
        local.set $b
        local.get $b
        i32.const 32
        i32.eq
        local.get $b
        i32.const 9
        i32.eq
        i32.or
        local.get $b
        i32.const 13
        i32.eq
        i32.or
        local.get $b
        i32.const 10
        i32.eq
        i32.or
        i32.eqz
        br_if $rdone
        local.get $end
        i32.const 1
        i32.sub
        local.set $end
        br $rtrim
      end
    end
    local.get $end
    local.get $ptr
    i32.sub
    global.set $__last_str_len
    local.get $ptr
    f64.convert_i32_u
  )
  ;; Find needle in haystack, returning start index as f64 (-1.0 if not found).
  ;; Params (all i32): $hptr, $hlen = haystack ptr+len; $nptr, $nlen = needle ptr+len.
  ;; The needle ptr+len are passed as i32 (caller converts from f64).
  (func $__str_find
    (param $hptr i32) (param $hlen i32)
    (param $nptr i32) (param $nlen i32)
    (result f64)
    (local $i i32)
    (local $j i32)
    (local $match i32)
    (local $limit i32)
    ;; edge: empty needle always found at 0
    local.get $nlen
    i32.const 0
    i32.le_s
    if
      f64.const 0
      return
    end
    ;; edge: needle longer than haystack → not found
    local.get $hlen
    local.get $nlen
    i32.lt_s
    if
      f64.const -1
      return
    end
    local.get $hlen
    local.get $nlen
    i32.sub
    local.set $limit
    i32.const 0
    local.set $i
    block $found
      loop $outer
        local.get $i
        local.get $limit
        i32.gt_s
        br_if $found
        i32.const 1
        local.set $match
        i32.const 0
        local.set $j
        block $mismatch
          loop $inner
            local.get $j
            local.get $nlen
            i32.ge_s
            br_if $mismatch
            local.get $hptr
            local.get $i
            i32.add
            local.get $j
            i32.add
            i32.load8_u
            local.get $nptr
            local.get $j
            i32.add
            i32.load8_u
            i32.ne
            if
              i32.const 0
              local.set $match
              br $mismatch
            end
            local.get $j
            i32.const 1
            i32.add
            local.set $j
            br $inner
          end
        end
        local.get $match
        if
          local.get $i
          f64.convert_i32_s
          return
        end
        local.get $i
        i32.const 1
        i32.add
        local.set $i
        br $outer
      end
    end
    f64.const -1
  )
  ;; ── End WASI runtime ─────────────────────────────────────────────────────"""
        self._funcs.insert(0, runtime)

    def _emit_dom_runtime(self) -> None:
        """Emit thin WAT wrapper functions for DOM host builtins.

        These wrappers present the caller-facing interface (string args as
        ptr+len, handles as f64) and forward to the env.* host imports.
        The dom_value wrapper uses argv_data as its internal string buffer.
        """
        from multilingualprogramming.codegen.wat_generator_support import (  # pylint: disable=import-outside-toplevel
            _DOM_CALLER_PARAMS,
            _DOM_CALLER_RETURNS,
        )
        mem_end = self._WASM_PAGES * 65536
        dom_buf = mem_end - 1536   # dedicated DOM value buffer (below argv_data at -1024)
        dom_buf_size = 255

        wrappers = ["  ;; ── DOM runtime wrappers ───────────────────────────────────────────────"]
        for fname, wat_host in {
            "dom_get":    "ml_dom_get",
            "dom_text":   "ml_dom_set_text",
            "dom_html":   "ml_dom_set_html",
            "dom_value":  "ml_dom_get_value",
            "dom_attr":   "ml_dom_set_attr",
            "dom_create": "ml_dom_create",
            "dom_append": "ml_dom_append",
            "dom_style":  "ml_dom_style",
            "dom_remove": "ml_dom_remove",
            "dom_class":  "ml_dom_set_class",
        }.items():
            caller_params = _DOM_CALLER_PARAMS.get(fname, [])
            ret = _DOM_CALLER_RETURNS.get(fname, "")

            # Build WAT param list
            params = []
            for i, pkind in enumerate(caller_params):
                if pkind == "str":
                    params.append(f"(param $p{i}_ptr i32)")
                    params.append(f"(param $p{i}_len i32)")
                else:
                    params.append(f"(param $p{i} f64)")
            result = " (result f64)" if ret in ("f64", "ret_str") else ""
            param_str = " ".join(params)

            fn_lines = [f"  (func ${fname} {param_str}{result}"]
            # Push args to host import
            for i, pkind in enumerate(caller_params):
                if pkind == "str":
                    fn_lines.append(f"    local.get $p{i}_ptr")
                    fn_lines.append(f"    local.get $p{i}_len")
                else:
                    fn_lines.append(f"    local.get $p{i}")

            if fname == "dom_value":
                # dom_value: append internal buffer args then call
                fn_lines.append(f"    i32.const {dom_buf}")
                fn_lines.append(f"    i32.const {dom_buf_size}")
                fn_lines.append(f"    call ${wat_host}")
                fn_lines.append("    global.set $__last_str_len")
                fn_lines.append(f"    i32.const {dom_buf}")
                fn_lines.append("    f64.convert_i32_u")
            else:
                fn_lines.append(f"    call ${wat_host}")

            fn_lines.append("  )")
            wrappers.append("\n".join(fn_lines))

        self._funcs.append("\n".join(wrappers))

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
