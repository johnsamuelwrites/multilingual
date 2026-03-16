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
        heap_base = max((len(self._data) + 7) // 8 * 8, 64)
        self._emit_wasi_runtime(heap_base)
        lines = ["(module"]
        lines += [
            '  (import "wasi_snapshot_preview1" "fd_write"'
            ' (func $fd_write (param i32 i32 i32 i32) (result i32)))',
            f'  (memory (export "memory") {self._WASM_PAGES})',
        ]
        if self._data:
            escaped = "".join(f"\\{b:02x}" for b in self._data)
            lines.append(f'  (data (i32.const 0) "{escaped}")')
        # $__heap_ptr is always declared: $ml_alloc references it unconditionally.
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
  ;; Integer values (v == trunc(v), |v| < 1e15) are printed as "N.0".
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
  ;; ── End WASI runtime ─────────────────────────────────────────────────────"""
        self._funcs.insert(0, runtime)

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
