(module
  (import "wasi_snapshot_preview1" "fd_write" (func $fd_write (param i32 i32 i32 i32) (result i32)))
  (memory (export "memory") 4)
  (data (i32.const 0) "\2d\48\61\73\20\61\20\64\6f\63\73\74\72\69\6e\67\2e\63\6f\6d\62\69\6e\65\64\6f\6b\5b\5d\2c\20\28\29\79\65\73\6e\6f\6f\74\68\65\72\6f\6e\65\74\77\6f\64\65\66\61\75\6c\74\68\65\6c\6c\6f\20\77\6f\72\6c\64\6e\6f\6e\65\68\69\62\79\65\67\6f\6f\64\62\79\65\75\6e\6b\6e\6f\77\6e\64\65\66\69\6e\65\64\6e\75\6c\6c")
  (global $__heap_ptr (mut i32) (i32.const 104))
  (global $__last_str_len (mut i32) (i32.const 0))
  (table 1 funcref)
  (elem (i32.const 0) $__lambda_55)

  ;; ── WASI runtime ────────────────────────────────────────────────────────────
  ;; Write `len` bytes at `ptr` to stdout via WASI fd_write.
  (func $__wasi_write (param $ptr i32) (param $len i32)
    i32.const 262080
    local.get $ptr
    i32.store
    i32.const 262084
    local.get $len
    i32.store
    i32.const 1
    i32.const 262080
    i32.const 1
    i32.const 262088
    call $fd_write
    drop
  )
  ;; Format a non-negative i64 as decimal, writing backwards from address 262144.
  ;; Returns: (start_ptr: i32, byte_len: i32)
  (func $__fmt_u64 (param $n i64) (result i32 i32)
    (local $ptr i32)
    (local $digit i32)
    i32.const 262144
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
    i32.const 262144
    local.get $ptr
    i32.sub
  )
  ;; Write 6 decimal digits of n (0..999999) to 262092..262097, strip trailing
  ;; zeros (keep at least 1).  Returns: (ptr=262092, trimmed_len: i32)
  (func $__fmt_frac6 (param $n i64) (result i32 i32)
    (local $trimmed i32)
    i32.const 262092
    local.get $n
    i64.const 100000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 262093
    local.get $n
    i64.const 100000
    i64.rem_u
    i64.const 10000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 262094
    local.get $n
    i64.const 10000
    i64.rem_u
    i64.const 1000
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 262095
    local.get $n
    i64.const 1000
    i64.rem_u
    i64.const 100
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 262096
    local.get $n
    i64.const 100
    i64.rem_u
    i64.const 10
    i64.div_u
    i32.wrap_i64
    i32.const 48
    i32.add
    i32.store8
    i32.const 262097
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
        i32.const 262092
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
    i32.const 262092
    local.get $trimmed
  )
  ;; Print a newline.
  (func $print_newline
    i32.const 262092
    i32.const 10
    i32.store8
    i32.const 262092
    i32.const 1
    call $__wasi_write
  )
  ;; Print a space separator.
  (func $print_sep
    i32.const 262092
    i32.const 32
    i32.store8
    i32.const 262092
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
      i32.const 262092
      i32.const 70
      i32.store8
      i32.const 262093
      i32.const 97
      i32.store8
      i32.const 262094
      i32.const 108
      i32.store8
      i32.const 262095
      i32.const 115
      i32.store8
      i32.const 262096
      i32.const 101
      i32.store8
      i32.const 262092
      i32.const 5
      call $__wasi_write
    else
      i32.const 262092
      i32.const 84
      i32.store8
      i32.const 262093
      i32.const 114
      i32.store8
      i32.const 262094
      i32.const 117
      i32.store8
      i32.const 262095
      i32.const 101
      i32.store8
      i32.const 262092
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
      i32.const 262092
      i32.const 110
      i32.store8
      i32.const 262093
      i32.const 97
      i32.store8
      i32.const 262094
      i32.const 110
      i32.store8
      i32.const 262092
      i32.const 3
      call $__wasi_write
      return
    end
    local.get $v
    f64.const 0.0
    f64.lt
    if
      i32.const 262092
      i32.const 45
      i32.store8
      i32.const 262092
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
      i32.const 262092
      i32.const 105
      i32.store8
      i32.const 262093
      i32.const 110
      i32.store8
      i32.const 262094
      i32.const 102
      i32.store8
      i32.const 262092
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
      i32.const 262092
      i32.const 46
      i32.store8
      i32.const 262093
      i32.const 48
      i32.store8
      i32.const 262092
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
    i32.const 262092
    i32.const 46
    i32.store8
    i32.const 262092
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
      i32.const 262092
      i32.const 48
      i32.store8
      i32.const 262092
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
  ;; Exact for exp in (0, 1, 0.5, -0.5) and integer exponents up to 2^31-1.
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
  (global $__heap_base i32 (i32.const 104))
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
  ;; ── End WASI runtime ─────────────────────────────────────────────────────
  (func $bump_global (export "bump_global")
    (result f64)
    (local $shared_counter f64)
    ;; GlobalStatement: shared_counter (nop in WAT)
    ;; shared_counter = ...
    local.get $shared_counter
    f64.const 2.0
    f64.add  ;; op='+'
    local.set $shared_counter
    local.get $shared_counter
    return
    f64.const 0  ;; implicit return
  )
  (func $make_counter__step_closure (export "make_counter__step_closure")
    (param $env f64)
    (result f64)
    (local $env_val f64)
    ;; closure step: increment captured cell 0
    local.get $env
    i32.trunc_f64_u
    i32.const 8
    i32.add
    local.get $env
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.load
    f64.const 1
    f64.add
    local.tee $env_val
    f64.store
    local.get $env_val
    return
    f64.const 0  ;; implicit return
  )
  (func $make_counter (export "make_counter")
    (param $start f64)
    (result f64)
    (local $__list_1_ptr f64)
    ;; list/tuple literal [1 elements]
    i32.const 16
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_1_ptr
    local.get $__list_1_ptr
    i32.trunc_f64_u
    f64.const 1.0
    f64.store
    local.get $__list_1_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    local.get $start
    f64.store
    local.get $__list_1_ptr
    return
    f64.const 0  ;; implicit return
  )
  (func $__str_concat (param $sc_p1 f64) (param $sc_l1 f64) (param $sc_p2 f64) (param $sc_l2 f64) (result f64)
    (local $sc_i f64)
    (local $sc_dst f64)
    ;; save current heap_ptr as result base
    global.get $__heap_ptr
    f64.convert_i32_u
    local.set $sc_dst
    ;; copy bytes from p1
    f64.const 0
    local.set $sc_i
    block $sc_b1
      loop $sc_lp1
        local.get $sc_i
        local.get $sc_l1
        f64.ge
        br_if $sc_b1
        global.get $__heap_ptr
        local.get $sc_i
        i32.trunc_f64_u
        i32.add
        local.get $sc_p1
        i32.trunc_f64_u
        local.get $sc_i
        i32.trunc_f64_u
        i32.add
        i32.load8_u
        i32.store8
        local.get $sc_i
        f64.const 1
        f64.add
        local.set $sc_i
        br $sc_lp1
      end
    end
    ;; copy bytes from p2
    f64.const 0
    local.set $sc_i
    block $sc_b2
      loop $sc_lp2
        local.get $sc_i
        local.get $sc_l2
        f64.ge
        br_if $sc_b2
        global.get $__heap_ptr
        local.get $sc_l1
        i32.trunc_f64_u
        local.get $sc_i
        i32.trunc_f64_u
        i32.add
        i32.add
        local.get $sc_p2
        i32.trunc_f64_u
        local.get $sc_i
        i32.trunc_f64_u
        i32.add
        i32.load8_u
        i32.store8
        local.get $sc_i
        f64.const 1
        f64.add
        local.set $sc_i
        br $sc_lp2
      end
    end
    ;; advance heap_ptr by (len1+len2) rounded up to 8
    global.get $__heap_ptr
    local.get $sc_l1
    i32.trunc_f64_u
    local.get $sc_l2
    i32.trunc_f64_u
    i32.add
    i32.const 7
    i32.add
    i32.const -8
    i32.and
    i32.add
    global.set $__heap_ptr
    local.get $sc_dst
  )
  (func $__fmt_default_tmpstr (param $v f64) (result i32 i32)
    (local $ml_ptr i32)
    (local $ml_len i32)
    (local $neg i32)
    (local $int_part i64)
    local.get $v
    f64.const 0
    f64.lt
    local.set $neg
    local.get $neg
    if
      local.get $v
      f64.neg
      local.set $v
    end
    local.get $v
    f64.trunc
    i64.trunc_f64_u
    local.set $int_part
    local.get $int_part
    call $__fmt_u64
    local.set $ml_len
    local.set $ml_ptr
    local.get $neg
    if
      local.get $ml_ptr
      i32.const 1
      i32.sub
      i32.const 45
      i32.store8
      local.get $ml_ptr
      i32.const 1
      i32.sub
      local.set $ml_ptr
      local.get $ml_len
      i32.const 1
      i32.add
      local.set $ml_len
    end
    local.get $ml_ptr
    local.get $ml_len
  )
  (func $__fmt_fixed1_tmpstr (param $v f64) (result i32 i32)
    (local $int_part i64)
    (local $frac_digit i32)
    (local $ptr i32)
    (local $len i32)
    (local $neg i32)
    (local $copy_i i32)
    local.get $v
    f64.const 0
    f64.lt
    local.set $neg
    local.get $neg
    if
      local.get $v
      f64.neg
      local.set $v
    end
    local.get $v
    f64.trunc
    i64.trunc_f64_u
    local.set $int_part
    local.get $int_part
    call $__fmt_u64
    local.set $len
    local.set $ptr
    i32.const 262092
    local.set $copy_i
    local.get $neg
    if
      local.get $copy_i
      i32.const 45
      i32.store8
      local.get $copy_i
      i32.const 1
      i32.add
      local.set $copy_i
    end
    block $copy_done
      loop $copy_lp
        local.get $len
        i32.eqz
        br_if $copy_done
        local.get $copy_i
        local.get $ptr
        i32.load8_u
        i32.store8
        local.get $copy_i
        i32.const 1
        i32.add
        local.set $copy_i
        local.get $ptr
        i32.const 1
        i32.add
        local.set $ptr
        local.get $len
        i32.const 1
        i32.sub
        local.set $len
        br $copy_lp
      end
    end
    local.get $copy_i
    i32.const 46
    i32.store8
    local.get $copy_i
    i32.const 1
    i32.add
    local.set $copy_i
    local.get $v
    local.get $v
    f64.trunc
    f64.sub
    f64.const 10
    f64.mul
    f64.nearest
    i32.trunc_f64_u
    local.set $frac_digit
    local.get $copy_i
    local.get $frac_digit
    i32.const 48
    i32.add
    i32.store8
    i32.const 262092
    local.get $neg
    if (result i32)
      i32.const 4
    else
      i32.const 3
    end
  )
  (func $format_tag (export "format_tag")
    (param $a f64)
    (param $b f64)
    (result f64)
    (local $__fmt_len_3 f64)
    (local $__fmt_len_4 f64)
    (local $__fmt_ptr_3 f64)
    (local $__fmt_ptr_4 f64)
    (local $__fstr_len_2 f64)
    (local $__fstr_part_len_2 f64)
    (local $__fstr_part_ptr_2 f64)
    (local $__fstr_ptr_2 f64)
    local.get $a
    call $__fmt_default_tmpstr
    local.set $__fmt_len_3
    local.set $__fmt_ptr_3
    local.get $__fmt_ptr_3
    f64.convert_i32_u
    local.get $__fmt_len_3
    f64.convert_i32_u
    local.set $__fstr_part_len_2
    local.set $__fstr_part_ptr_2
    local.get $__fstr_part_ptr_2
    local.set $__fstr_ptr_2
    local.get $__fstr_part_len_2
    local.set $__fstr_len_2
    f64.const 0.0
    f64.const 1.0
    local.set $__fstr_part_len_2
    local.set $__fstr_part_ptr_2
    local.get $__fstr_ptr_2
    local.get $__fstr_len_2
    local.get $__fstr_part_ptr_2
    local.get $__fstr_part_len_2
    call $__str_concat
    local.set $__fstr_ptr_2
    local.get $__fstr_len_2
    local.get $__fstr_part_len_2
    f64.add
    local.set $__fstr_len_2
    local.get $b
    call $__fmt_fixed1_tmpstr
    local.set $__fmt_len_4
    local.set $__fmt_ptr_4
    local.get $__fmt_ptr_4
    f64.convert_i32_u
    local.get $__fmt_len_4
    f64.convert_i32_u
    local.set $__fstr_part_len_2
    local.set $__fstr_part_ptr_2
    local.get $__fstr_ptr_2
    local.get $__fstr_len_2
    local.get $__fstr_part_ptr_2
    local.get $__fstr_part_len_2
    call $__str_concat
    local.set $__fstr_ptr_2
    local.get $__fstr_len_2
    local.get $__fstr_part_len_2
    f64.add
    local.set $__fstr_len_2
    local.get $__fstr_len_2
    i32.trunc_f64_u
    global.set $__last_str_len
    local.get $__fstr_ptr_2
    return
    f64.const 0  ;; implicit return
  )
  (func $produce_three (export "produce_three")
    (result f64)
    (local $__gen_end_8 f64)
    (local $__gen_idx_6 f64)
    (local $__gen_len_7 f64)
    (local $__gen_ptr_5 f64)
    (local $idx f64)
    f64.const 0.0
    local.set $idx
    f64.const 3.0
    local.set $__gen_end_8
    local.get $__gen_end_8
    local.get $idx
    f64.sub
    local.set $__gen_len_7
    local.get $__gen_len_7
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__gen_ptr_5
    local.get $__gen_ptr_5
    i32.trunc_f64_u
    local.get $__gen_len_7
    f64.store
    f64.const 0
    local.set $__gen_idx_6
    block $gen_blk_9
      loop $gen_lp_9
        local.get $idx
        local.get $__gen_end_8
        f64.ge
        br_if $gen_blk_9
        local.get $__gen_ptr_5
        i32.trunc_f64_u
        local.get $__gen_idx_6
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $idx
        f64.store
        local.get $idx
        f64.const 1
        f64.add
        local.set $idx
        local.get $__gen_idx_6
        f64.const 1
        f64.add
        local.set $__gen_idx_6
        br $gen_lp_9
      end
    end
    local.get $__gen_ptr_5
    return
    f64.const 0  ;; implicit return
  )
  (func $delegating_gen (export "delegating_gen")
    (result f64)
    (local $__gen_end_14 f64)
    (local $__gen_idx_12 f64)
    (local $__gen_item_10 f64)
    (local $__gen_len_13 f64)
    (local $__gen_ptr_11 f64)
    f64.const 0.0
    local.set $__gen_item_10
    f64.const 3.0
    local.set $__gen_end_14
    local.get $__gen_end_14
    local.get $__gen_item_10
    f64.sub
    local.set $__gen_len_13
    local.get $__gen_len_13
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__gen_ptr_11
    local.get $__gen_ptr_11
    i32.trunc_f64_u
    local.get $__gen_len_13
    f64.store
    f64.const 0
    local.set $__gen_idx_12
    block $gen_blk_15
      loop $gen_lp_15
        local.get $__gen_item_10
        local.get $__gen_end_14
        f64.ge
        br_if $gen_blk_15
        local.get $__gen_ptr_11
        i32.trunc_f64_u
        local.get $__gen_idx_12
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__gen_item_10
        f64.store
        local.get $__gen_item_10
        f64.const 1
        f64.add
        local.set $__gen_item_10
        local.get $__gen_idx_12
        f64.const 1
        f64.add
        local.set $__gen_idx_12
        br $gen_lp_15
      end
    end
    local.get $__gen_ptr_11
    return
    f64.const 0  ;; implicit return
  )
  (func $annotated (export "annotated")
    (param $x f64)
    (param $y f64)
    (result f64)
    local.get $x
    local.get $y
    f64.add  ;; op='+'
    return
    f64.const 0  ;; implicit return
  )
  (func $multi_params (export "multi_params")
    (param $base f64)
    (param $extra f64)
    (result f64)
    (local $__sum_acc_16 f64)
    (local $__sum_idx_16 f64)
    (local $__sum_len_16 f64)
    (local $__sum_ptr_16 f64)
    local.get $base
    local.get $extra
    f64.add  ;; op='+'
    f64.const 0  ;; unresolved: args
    local.set $__sum_ptr_16
    local.get $__sum_ptr_16
    i32.trunc_f64_u
    f64.load
    local.set $__sum_len_16
    f64.const 0
    local.set $__sum_idx_16
    f64.const 0
    local.set $__sum_acc_16
    block $sum_blk_16
      loop $sum_lp_16
        local.get $__sum_idx_16
        local.get $__sum_len_16
        f64.ge
        br_if $sum_blk_16
        local.get $__sum_acc_16
        local.get $__sum_ptr_16
        i32.trunc_f64_u
        local.get $__sum_idx_16
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.add
        local.set $__sum_acc_16
        local.get $__sum_idx_16
        f64.const 1
        f64.add
        local.set $__sum_idx_16
        br $sum_lp_16
      end
    end
    local.get $__sum_acc_16
    f64.add  ;; op='+'
    return
    f64.const 0  ;; implicit return
  )
  (func $doubler (export "doubler")
    (param $func f64)
    (result f64)
    ;; nested def wrap — skipped in WAT
    f64.const 0  ;; unresolved: wrap
    return
    f64.const 0  ;; implicit return
  )
  (func $ten (export "ten")
    (result f64)
    f64.const 10.0
    return
    f64.const 0  ;; implicit return
  )
  (func $with_doc (export "with_doc")
    (result f64)
    f64.const 1.0  ;; str offset (not a numeric value)
    i32.const 16
    global.set $__last_str_len
    drop
    i32.const 1
    f64.convert_i32_s
    return
    f64.const 0  ;; implicit return
  )
  (func $async_double (export "async_double")
    (param $n f64)
    (result f64)
    f64.const 0  ;; asyncio.sleep no-op in WAT
    drop
    local.get $n
    f64.const 2.0
    f64.mul  ;; op='*'
    return
    f64.const 0  ;; implicit return
  )
  (func $async_gen (export "async_gen")
    (result f64)
    (local $__gen_end_20 f64)
    (local $__gen_idx_18 f64)
    (local $__gen_len_19 f64)
    (local $__gen_ptr_17 f64)
    (local $v f64)
    f64.const 0.0
    local.set $v
    f64.const 3.0
    local.set $__gen_end_20
    local.get $__gen_end_20
    local.get $v
    f64.sub
    local.set $__gen_len_19
    local.get $__gen_len_19
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__gen_ptr_17
    local.get $__gen_ptr_17
    i32.trunc_f64_u
    local.get $__gen_len_19
    f64.store
    f64.const 0
    local.set $__gen_idx_18
    block $gen_blk_21
      loop $gen_lp_21
        local.get $v
        local.get $__gen_end_20
        f64.ge
        br_if $gen_blk_21
        local.get $__gen_ptr_17
        i32.trunc_f64_u
        local.get $__gen_idx_18
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $v
        f64.store
        local.get $v
        f64.const 1
        f64.add
        local.set $v
        local.get $__gen_idx_18
        f64.const 1
        f64.add
        local.set $__gen_idx_18
        br $gen_lp_21
      end
    end
    local.get $__gen_ptr_17
    return
    f64.const 0  ;; implicit return
  )
  (func $async_for_task (export "async_for_task")
    (result f64)
    (local $__re22 f64)
    (local $av f64)
    (local $total f64)
    ;; let total = ...
    f64.const 0.0
    local.set $total
    ;; for loop over non-range iterable - not supported in WAT
    local.get $total
    return
    f64.const 0  ;; implicit return
  )
  (func $async_with_task (export "async_with_task")
    (result f64)
    (local $value f64)
    ;; with (context-manager hooks not lowerable in WAT)
    f64.const 0  ;; placeholder for 'as value' binding
    local.set $value
    local.get $value
    return
    f64.const 0  ;; implicit return
  )
  (func $CounterBox____init__ (export "CounterBox____init__")
    (param $self f64)
    (param $start_base f64)
    (result f64)
    ;; self.value = ...
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    local.get $start_base
    f64.store
    f64.const 0  ;; implicit return
  )
  (func $CounterBoxChild____init__ (export "CounterBoxChild____init__")
    (param $self f64)
    (param $start_base f64)
    (result f64)
    local.get $self
    local.get $start_base
    call $CounterBox____init__
    drop  ;; super().__init__ return value discarded
    ;; self.value = ...
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    ;; load self.value
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    f64.load
    f64.const 1.0
    f64.add  ;; op='+'
    f64.store
    f64.const 0  ;; implicit return
  )
  (func $Mixin__mix (export "Mixin__mix")
    (param $self f64)
    (result f64)
    f64.const 1.0
    return
    f64.const 0  ;; implicit return
  )
  (func $BaseTwo____init__ (export "BaseTwo____init__")
    (param $self f64)
    (param $start f64)
    (result f64)
    ;; self.value = ...
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    local.get $start
    f64.store
    f64.const 0  ;; implicit return
  )
  (func $Combined__label (export "Combined__label")
    (result f64)
    f64.const 17.0  ;; str offset (not a numeric value)
    i32.const 8
    global.set $__last_str_len
    return
    f64.const 0  ;; implicit return
  )
  (func $Combined__build (export "Combined__build")
    (param $cls f64)
    (param $v f64)
    (result f64)
    ;; alloc Combined (type_tag=8 + fields=8 bytes)
    global.get $__heap_ptr
    i32.const 3   ;; class_id for Combined
    i32.store
    global.get $__heap_ptr
    i32.const 16
    i32.add
    global.set $__heap_ptr
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u  ;; self ptr as f64 (past type-tag)
    local.get $v
    call $BaseTwo____init__
    drop  ;; discard __init__ return value
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u  ;; object ref as f64
    return
    f64.const 0  ;; implicit return
  )
  (func $Combined__doubled (export "Combined__doubled")
    (param $self f64)
    (result f64)
    ;; load self.value
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    f64.load
    f64.const 2.0
    f64.mul  ;; op='*'
    return
    f64.const 0  ;; implicit return
  )
  (func $AsyncCtxEn____aenter__ (export "AsyncCtxEn____aenter__")
    (param $self f64)
    (result f64)
    f64.const 5.0
    return
    f64.const 0  ;; implicit return
  )
  (func $AsyncCtxEn____aexit__ (export "AsyncCtxEn____aexit__")
    (param $self f64)
    (param $exc_type f64)
    (param $exc f64)
    (param $tb f64)
    (result f64)
    i32.const 0
    f64.convert_i32_s
    return
    f64.const 0  ;; implicit return
  )
  (func $__lambda_55 (export "__lambda_55")
    (param $x f64)
    (result f64)
    local.get $x
    local.get $x
    f64.mul  ;; op='*'
  )
  (func $__str_slice (param $ss_p f64) (param $ss_s f64) (param $ss_e f64) (result f64)
    (local $ss_i f64)
    (local $ss_dst f64)
    ;; clamp stop to >= start
    local.get $ss_e
    local.get $ss_s
    f64.lt
    if
      local.get $ss_s
      local.set $ss_e
    end
    ;; save heap_ptr as result base
    global.get $__heap_ptr
    f64.convert_i32_u
    local.set $ss_dst
    ;; copy bytes p[start..stop)
    local.get $ss_s
    local.set $ss_i
    block $ss_blk
      loop $ss_lp
        local.get $ss_i
        local.get $ss_e
        f64.ge
        br_if $ss_blk
        global.get $__heap_ptr
        local.get $ss_i
        i32.trunc_f64_u
        local.get $ss_s
        i32.trunc_f64_u
        i32.sub
        i32.add
        local.get $ss_p
        i32.trunc_f64_u
        local.get $ss_i
        i32.trunc_f64_u
        i32.add
        i32.load8_u
        i32.store8
        local.get $ss_i
        f64.const 1
        f64.add
        local.set $ss_i
        br $ss_lp
      end
    end
    ;; advance heap_ptr by (stop-start) rounded to 8
    global.get $__heap_ptr
    local.get $ss_e
    i32.trunc_f64_u
    local.get $ss_s
    i32.trunc_f64_u
    i32.sub
    i32.const 7
    i32.add
    i32.const -8
    i32.and
    i32.add
    global.set $__heap_ptr
    local.get $ss_dst
  )
  (func $__main (export "__main")
    (local $__aug_a_53 f64)
    (local $__aug_b_53 f64)
    (local $__chain_54 f64)
    (local $__comp_cap_41 f64)
    (local $__comp_cap_56 f64)
    (local $__comp_cap_60 f64)
    (local $__comp_cap_61 f64)
    (local $__comp_cap_69 f64)
    (local $__comp_end_42 f64)
    (local $__comp_end_57 f64)
    (local $__comp_end_59 f64)
    (local $__comp_end_61 f64)
    (local $__comp_end_70 f64)
    (local $__comp_idx_42 f64)
    (local $__comp_idx_57 f64)
    (local $__comp_idx_59 f64)
    (local $__comp_idx_70 f64)
    (local $__comp_inner_end_60 f64)
    (local $__comp_inner_span_60 f64)
    (local $__comp_inner_start_60 f64)
    (local $__comp_len_42 f64)
    (local $__comp_len_57 f64)
    (local $__comp_len_59 f64)
    (local $__comp_len_70 f64)
    (local $__comp_outer_end_60 f64)
    (local $__comp_outer_span_60 f64)
    (local $__comp_ptr_41 f64)
    (local $__comp_ptr_42 f64)
    (local $__comp_ptr_56 f64)
    (local $__comp_ptr_57 f64)
    (local $__comp_ptr_59 f64)
    (local $__comp_ptr_60 f64)
    (local $__comp_ptr_61 f64)
    (local $__comp_ptr_69 f64)
    (local $__comp_ptr_70 f64)
    (local $__comp_src_len_42 f64)
    (local $__comp_src_len_57 f64)
    (local $__comp_src_len_59 f64)
    (local $__comp_src_len_70 f64)
    (local $__comp_write_41 f64)
    (local $__comp_write_56 f64)
    (local $__comp_write_60 f64)
    (local $__comp_write_61 f64)
    (local $__comp_write_69 f64)
    (local $__dict_end_58 f64)
    (local $__dict_idx_58 f64)
    (local $__dict_len_58 f64)
    (local $__dict_ptr_58 f64)
    (local $__divmod_left_43 f64)
    (local $__divmod_q_45 f64)
    (local $__divmod_right_44 f64)
    (local $__flbase_67 f64)
    (local $__flidx_67 f64)
    (local $__fllen_67 f64)
    (local $__list_23_ptr f64)
    (local $__list_24_ptr f64)
    (local $__list_25_ptr f64)
    (local $__list_27_ptr f64)
    (local $__list_28_ptr f64)
    (local $__list_36_ptr f64)
    (local $__list_38_ptr f64)
    (local $__list_40_ptr f64)
    (local $__list_46_ptr f64)
    (local $__list_65_ptr f64)
    (local $__list_66_ptr f64)
    (local $__list_68_ptr f64)
    (local $__list_74_ptr f64)
    (local $__match_subj_63 f64)
    (local $__match_subj_71 f64)
    (local $__match_subj_72 f64)
    (local $__match_subj_73 f64)
    (local $__match_subj_75 f64)
    (local $__mod_left_31 f64)
    (local $__mod_left_62 f64)
    (local $__print_idx_32 f64)
    (local $__print_idx_47 f64)
    (local $__print_idx_48 f64)
    (local $__print_idx_49 f64)
    (local $__print_idx_51 f64)
    (local $__print_idx_52 f64)
    (local $__print_idx_64 f64)
    (local $__print_idx_76 f64)
    (local $__print_len_32 f64)
    (local $__print_len_47 f64)
    (local $__print_len_48 f64)
    (local $__print_len_49 f64)
    (local $__print_len_51 f64)
    (local $__print_len_52 f64)
    (local $__print_len_64 f64)
    (local $__print_len_76 f64)
    (local $__re30 f64)
    (local $__re33 f64)
    (local $__re67 f64)
    (local $__sort_a_50 f64)
    (local $__sort_b_50 f64)
    (local $__sort_dst_50 f64)
    (local $__sort_i_50 f64)
    (local $__sort_j_50 f64)
    (local $__sort_len_50 f64)
    (local $__sort_src_50 f64)
    (local $__sum_acc_29 f64)
    (local $__sum_idx_29 f64)
    (local $__sum_len_29 f64)
    (local $__sum_ptr_29 f64)
    (local $__unpack_len_26 f64)
    (local $__unpack_len_35 f64)
    (local $__unpack_len_37 f64)
    (local $__unpack_len_39 f64)
    (local $__unpack_ptr_26 f64)
    (local $__unpack_ptr_35 f64)
    (local $__unpack_ptr_37 f64)
    (local $__unpack_ptr_39 f64)
    (local $__unpack_star_idx_26 f64)
    (local $__unpack_star_idx_35 f64)
    (local $__unpack_star_idx_37 f64)
    (local $__unpack_star_idx_39 f64)
    (local $__unpack_star_len_26 f64)
    (local $__unpack_star_len_35 f64)
    (local $__unpack_star_len_37 f64)
    (local $__unpack_star_len_39 f64)
    (local $__unpack_star_ptr_26 f64)
    (local $__unpack_star_ptr_35 f64)
    (local $__unpack_star_ptr_37 f64)
    (local $__unpack_star_ptr_39 f64)
    (local $a f64)
    (local $async_for_result f64)
    (local $async_result f64)
    (local $async_with_result f64)
    (local $aug f64)
    (local $b f64)
    (local $bau f64)
    (local $bdata f64)
    (local $bdata_strlen f64)
    (local $bin_num f64)
    (local $bit_a f64)
    (local $bit_l f64)
    (local $bit_o f64)
    (local $bit_r f64)
    (local $bit_x f64)
    (local $blen f64)
    (local $c f64)
    (local $ca f64)
    (local $cb f64)
    (local $cc f64)
    (local $chained f64)
    (local $child_box f64)
    (local $comb f64)
    (local $comp_list f64)
    (local $d f64)
    (local $dec_r f64)
    (local $delegated f64)
    (local $dict_c f64)
    (local $divmod_result f64)
    (local $doubled_list f64)
    (local $file_text f64)
    (local $file_text_strlen f64)
    (local $filter_c f64)
    (local $first_item f64)
    (local $first_step f64)
    (local $fixed_values f64)
    (local $flag_ok f64)
    (local $formatted f64)
    (local $formatted_strlen f64)
    (local $gen_c f64)
    (local $handle_r f64)
    (local $handle_w f64)
    (local $handled f64)
    (local $hex_num f64)
    (local $i f64)
    (local $init f64)
    (local $item f64)
    (local $items_found f64)
    (local $iter_list f64)
    (local $iter_sum f64)
    (local $iter_val f64)
    (local $j f64)
    (local $k f64)
    (local $last_item f64)
    (local $list_c f64)
    (local $loop_acc f64)
    (local $mc f64)
    (local $mcr f64)
    (local $merged_map f64)
    (local $middle f64)
    (local $middle_items f64)
    (local $mn f64)
    (local $mnr f64)
    (local $mnr_strlen f64)
    (local $mr f64)
    (local $mr_strlen f64)
    (local $ms f64)
    (local $ms_strlen f64)
    (local $msr f64)
    (local $msr_strlen f64)
    (local $mt f64)
    (local $mtr f64)
    (local $mtr_strlen f64)
    (local $multi_exc f64)
    (local $multi_result f64)
    (local $mv f64)
    (local $n f64)
    (local $nested_c f64)
    (local $next_count f64)
    (local $oct_num f64)
    (local $pow_aug f64)
    (local $power_result f64)
    (local $produced_total f64)
    (local $prop f64)
    (local $rest f64)
    (local $root_value f64)
    (local $sci_num f64)
    (local $second_step f64)
    (local $seed f64)
    (local $shared_counter f64)
    (local $sq f64)
    (local $squared_set f64)
    (local $str_a f64)
    (local $str_a_strlen f64)
    (local $str_b f64)
    (local $str_b_strlen f64)
    (local $str_cat f64)
    (local $str_cat_strlen f64)
    (local $str_idx f64)
    (local $str_slc f64)
    (local $temp_value f64)
    (local $ternary f64)
    (local $try_else f64)
    (local $tup_elem f64)
    (local $tup_lit f64)
    (local $typed f64)
    (local $unique_values f64)
    (local $v f64)
    (local $walrus_value f64)
    (local $while_else_val f64)
    (local $x f64)
    (local $zipped_pairs f64)
    ;; import metadata already collected (nop in WAT)
    ;; import metadata already collected (nop in WAT)
    ;; import metadata already collected (nop in WAT)
    ;; let shared_counter = ...
    f64.const 3.0
    local.set $shared_counter
    ;; let next_count = ...
    f64.const 5.0
    call $make_counter
    local.set $next_count
    ;; let first_step = ...
    local.get $next_count
    call $make_counter__step_closure
    local.set $first_step
    ;; let second_step = ...
    local.get $next_count
    call $make_counter__step_closure
    local.set $second_step
    ;; with (context-manager hooks not lowerable in WAT)
    f64.const 0  ;; placeholder for 'as handle_w' binding
    local.set $handle_w
    ;; virtual file write 'tmp_complete_en.txt'
    ;; let file_text = ...
    f64.const 25.0  ;; str offset (not a numeric value)
    i32.const 0
    global.set $__last_str_len
    local.set $file_text
    f64.const 0.0
    local.set $file_text_strlen
    ;; with (context-manager hooks not lowerable in WAT)
    f64.const 0  ;; placeholder for 'as handle_r' binding
    local.set $handle_r
    ;; file_text = ...
    f64.const 25.0  ;; virtual file read
    i32.const 2
    global.set $__last_str_len
    local.set $file_text
    f64.const 2.0
    local.set $file_text_strlen
    ;; let zipped_pairs = ...
    ;; list/tuple literal [3 elements]
    i32.const 32
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_23_ptr
    local.get $__list_23_ptr
    i32.trunc_f64_u
    f64.const 3.0
    f64.store
    local.get $__list_23_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 0.0
    f64.store
    local.get $__list_23_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 0.0
    f64.store
    local.get $__list_23_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 0.0
    f64.store
    local.get $__list_23_ptr
    local.set $zipped_pairs
    ;; let unique_values = ...
    ;; list/tuple literal [3 elements]
    i32.const 32
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_24_ptr
    local.get $__list_24_ptr
    i32.trunc_f64_u
    f64.const 3.0
    f64.store
    local.get $__list_24_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 1.0
    f64.store
    local.get $__list_24_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 2.0
    f64.store
    local.get $__list_24_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 3.0
    f64.store
    local.get $__list_24_ptr
    local.set $unique_values
    ;; let fixed_values = ...
    ;; list/tuple literal [3 elements]
    i32.const 32
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_25_ptr
    local.get $__list_25_ptr
    i32.trunc_f64_u
    f64.const 3.0
    f64.store
    local.get $__list_25_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_25_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_25_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_25_ptr
    local.set $fixed_values
    ;; list/tuple literal [4 elements]
    i32.const 40
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_27_ptr
    local.get $__list_27_ptr
    i32.trunc_f64_u
    f64.const 4.0
    f64.store
    local.get $__list_27_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 1.0
    f64.store
    local.get $__list_27_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 2.0
    f64.store
    local.get $__list_27_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 3.0
    f64.store
    local.get $__list_27_ptr
    i32.trunc_f64_u
    i32.const 32
    i32.add
    f64.const 4.0
    f64.store
    local.get $__list_27_ptr
    local.set $__unpack_ptr_26
    local.get $__unpack_ptr_26
    i32.trunc_f64_u
    f64.load
    local.set $__unpack_len_26
    local.get $__unpack_ptr_26
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.load
    local.set $first_item
    local.get $__unpack_ptr_26
    i32.trunc_f64_u
    local.get $__unpack_len_26
    i32.trunc_f64_u
    i32.const 1
    i32.sub
    i32.const 8
    i32.mul
    i32.const 8
    i32.add
    i32.add
    f64.load
    local.set $last_item
    local.get $__unpack_len_26
    f64.const 2.0
    f64.sub
    local.set $__unpack_star_len_26
    local.get $__unpack_star_len_26
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__unpack_star_ptr_26
    local.get $__unpack_star_ptr_26
    i32.trunc_f64_u
    local.get $__unpack_star_len_26
    f64.store
    f64.const 0
    local.set $__unpack_star_idx_26
    block $unpack_star_blk_26
      loop $unpack_star_lp_26
        local.get $__unpack_star_idx_26
        local.get $__unpack_star_len_26
        f64.ge
        br_if $unpack_star_blk_26
        local.get $__unpack_star_ptr_26
        i32.trunc_f64_u
        local.get $__unpack_star_idx_26
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__unpack_ptr_26
        i32.trunc_f64_u
        i32.const 1
        local.get $__unpack_star_idx_26
        i32.trunc_f64_u
        i32.add
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.store
        local.get $__unpack_star_idx_26
        f64.const 1
        f64.add
        local.set $__unpack_star_idx_26
        br $unpack_star_lp_26
      end
    end
    local.get $__unpack_star_ptr_26
    local.set $middle_items
    ;; unpacking assignment lowered
    ;; let merged_map = ...
    ;; list/tuple literal [2 elements]
    i32.const 24
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_28_ptr
    local.get $__list_28_ptr
    i32.trunc_f64_u
    f64.const 2.0
    f64.store
    local.get $__list_28_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 1.0
    f64.store
    local.get $__list_28_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 2.0
    f64.store
    local.get $__list_28_ptr
    local.set $merged_map
    ;; let formatted = ...
    f64.const 7.0
    f64.const 3.5
    call $format_tag
    global.get $__last_str_len
    drop
    local.set $formatted
    global.get $__last_str_len
    f64.convert_i32_u
    local.set $formatted_strlen
    ;; let seed = ...
    f64.const 0.0
    local.set $seed
    ;; let walrus_value = ...
    local.get $seed
    f64.const 9.0
    f64.add  ;; op='+'
    local.tee $seed
    local.set $walrus_value
    ;; let produced_total = ...
    call $produce_three
    local.set $__sum_ptr_29
    local.get $__sum_ptr_29
    i32.trunc_f64_u
    f64.load
    local.set $__sum_len_29
    f64.const 0
    local.set $__sum_idx_29
    f64.const 0
    local.set $__sum_acc_29
    block $sum_blk_29
      loop $sum_lp_29
        local.get $__sum_idx_29
        local.get $__sum_len_29
        f64.ge
        br_if $sum_blk_29
        local.get $__sum_acc_29
        local.get $__sum_ptr_29
        i32.trunc_f64_u
        local.get $__sum_idx_29
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.add
        local.set $__sum_acc_29
        local.get $__sum_idx_29
        f64.const 1
        f64.add
        local.set $__sum_idx_29
        br $sum_lp_29
      end
    end
    local.get $__sum_acc_29
    local.set $produced_total
    ;; let handled = ...
    i32.const 0
    f64.convert_i32_s
    local.set $handled
    ;; try (best-effort: no WASM exception handling)
    ;; if ...
    local.get $unique_values
    i32.trunc_f64_u
    f64.load  ;; list length from header
    f64.const 2.0
    f64.gt
    if
      ;; raise omitted in WAT best-effort mode
    end  ;; if
    ;; except handler(s) omitted (WAT cannot intercept exceptions)
    ;; finally
    ;; let root_value = ...
    f64.const 16.0
    f64.sqrt
    i32.trunc_f64_s
    f64.convert_i32_s
    local.set $root_value
    ;; let temp_value = ...
    f64.const 99.0
    local.set $temp_value
    f64.const 0
    local.set $temp_value
    ;; del temp_value (best-effort local clear)
    ;; let loop_acc = ...
    f64.const 0.0
    local.set $loop_acc
    ;; for n in range(...)
    f64.const 0.0
    local.set $n
    f64.const 6.0
    local.set $__re30
    block $for_blk_30
      loop $for_lp_30
        local.get $n
        local.get $__re30
        f64.ge
        br_if $for_blk_30
        ;; if ...
        local.get $n
        f64.const 0.0
        f64.eq
        if
          nop
        end  ;; if
        ;; if ...
        local.get $n
        f64.const 4.0
        f64.eq
        if
          br $for_blk_30
        end  ;; if
        ;; if ...
        local.get $n
        local.set $__mod_left_31
        local.get $__mod_left_31
        local.get $__mod_left_31
        f64.const 2.0
        f64.div
        f64.floor
        f64.const 2.0
        f64.mul
        f64.sub
        f64.const 0.0
        f64.eq
        if
          br $for_lp_30
        end  ;; if
        ;; loop_acc = ...
        local.get $loop_acc
        local.get $n
        f64.add  ;; op='+'
        local.set $loop_acc
        local.get $n
        f64.const 1
        f64.add
        local.set $n
        br $for_lp_30
      end  ;; loop
    end  ;; block (for)
    ;; let flag_ok = ...
    i32.const 1
    i32.const 0
    i32.eqz
    i32.and
    f64.convert_i32_s
    local.set $flag_ok
    ;; assert omitted in WAT best-effort mode
    ;; let child_box = ...
    ;; alloc CounterBoxChild (type_tag=8 + fields=8 bytes)
    global.get $__heap_ptr
    i32.const 1   ;; class_id for CounterBoxChild
    i32.store
    global.get $__heap_ptr
    i32.const 16
    i32.add
    global.set $__heap_ptr
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u  ;; self ptr as f64 (past type-tag)
    f64.const 40.0
    call $CounterBoxChild____init__
    drop  ;; discard __init__ return value
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u  ;; object ref as f64
    local.set $child_box
    ;; print(...)
    call $bump_global
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $first_step
    call $print_f64
    call $print_sep
    local.get $second_step
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $file_text
    i32.trunc_f64_u
    local.get $file_text_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_newline
    ;; print(...)
    local.get $zipped_pairs
    i32.trunc_f64_u
    f64.load  ;; list length from header
    call $print_f64
    call $print_sep
    local.get $unique_values
    i32.trunc_f64_u
    f64.load  ;; list length from header
    call $print_f64
    call $print_sep
    ;; fixed_values[i]
    local.get $fixed_values
    i32.trunc_f64_u
    f64.const 1.0
    i32.trunc_f64_u
    i32.const 8
    i32.mul
    i32.const 8  ;; skip length header
    i32.add
    i32.add
    f64.load
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $first_item
    call $print_f64
    call $print_sep
    i32.const 27
    i32.const 1
    call $print_str
    local.get $middle_items
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_32
    f64.const 0
    local.set $__print_idx_32
    block $print_seq_blk_32
      loop $print_seq_lp_32
        local.get $__print_idx_32
        local.get $__print_len_32
        f64.ge
        br_if $print_seq_blk_32
        local.get $__print_idx_32
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $middle_items
        i32.trunc_f64_u
        local.get $__print_idx_32
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_32
        f64.const 1
        f64.add
        local.set $__print_idx_32
        br $print_seq_lp_32
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_sep
    local.get $last_item
    call $print_f64
    call $print_newline
    ;; print(...)
    ;; load child_box.value
    local.get $child_box
    i32.trunc_f64_u
    i32.const 0
    i32.add
    f64.load
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $produced_total
    call $print_f64
    call $print_sep
    local.get $root_value
    call $print_f64
    call $print_sep
    local.get $handled
    call $print_f64
    call $print_newline
    ;; print(...)
    ;; merged_map['x']
    local.get $merged_map
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.load
    ;; merged_map['y']
    local.get $merged_map
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.load
    f64.add  ;; op='+'
    call $print_f64
    call $print_sep
    local.get $formatted
    i32.trunc_f64_u
    local.get $formatted_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_sep
    local.get $walrus_value
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $loop_acc
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $shared_counter
    f64.const 0
    f64.eq
    f64.convert_i32_s
    call $print_f64
    call $print_newline
    ;; let items_found = ...
    i32.const 0
    f64.convert_i32_s
    local.set $items_found
    ;; for item in range(...)
    f64.const 0.0
    local.set $item
    f64.const 3.0
    local.set $__re33
    block $for_blk_33
      loop $for_lp_33
        local.get $item
        local.get $__re33
        f64.ge
        br_if $for_blk_33
        ;; if ...
        local.get $item
        f64.const 10.0
        f64.eq
        if
          ;; items_found = ...
          i32.const 1
          f64.convert_i32_s
          local.set $items_found
          br $for_blk_33
        end  ;; if
        local.get $item
        f64.const 1
        f64.add
        local.set $item
        br $for_lp_33
      end  ;; loop
    end  ;; block (for)
    ;; let while_else_val = ...
    f64.const 0.0
    local.set $while_else_val
    ;; while ...
    block $while_blk_34
      loop $while_lp_34
        local.get $while_else_val
        f64.const 2.0
        f64.lt
        i32.eqz
        br_if $while_blk_34
        ;; while_else_val = ...
        local.get $while_else_val
        f64.const 1.0
        f64.add  ;; op='+'
        local.set $while_else_val
        br $while_lp_34
      end  ;; loop
    end  ;; block (while)
    ;; list/tuple literal [4 elements]
    i32.const 40
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_36_ptr
    local.get $__list_36_ptr
    i32.trunc_f64_u
    f64.const 4.0
    f64.store
    local.get $__list_36_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_36_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_36_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_36_ptr
    i32.trunc_f64_u
    i32.const 32
    i32.add
    f64.const 40.0
    f64.store
    local.get $__list_36_ptr
    local.set $__unpack_ptr_35
    local.get $__unpack_ptr_35
    i32.trunc_f64_u
    f64.load
    local.set $__unpack_len_35
    local.get $__unpack_ptr_35
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.load
    local.set $a
    local.get $__unpack_len_35
    f64.const 1.0
    f64.sub
    local.set $__unpack_star_len_35
    local.get $__unpack_star_len_35
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__unpack_star_ptr_35
    local.get $__unpack_star_ptr_35
    i32.trunc_f64_u
    local.get $__unpack_star_len_35
    f64.store
    f64.const 0
    local.set $__unpack_star_idx_35
    block $unpack_star_blk_35
      loop $unpack_star_lp_35
        local.get $__unpack_star_idx_35
        local.get $__unpack_star_len_35
        f64.ge
        br_if $unpack_star_blk_35
        local.get $__unpack_star_ptr_35
        i32.trunc_f64_u
        local.get $__unpack_star_idx_35
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__unpack_ptr_35
        i32.trunc_f64_u
        i32.const 1
        local.get $__unpack_star_idx_35
        i32.trunc_f64_u
        i32.add
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.store
        local.get $__unpack_star_idx_35
        f64.const 1
        f64.add
        local.set $__unpack_star_idx_35
        br $unpack_star_lp_35
      end
    end
    local.get $__unpack_star_ptr_35
    local.set $rest
    ;; unpacking assignment lowered
    ;; list/tuple literal [4 elements]
    i32.const 40
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_38_ptr
    local.get $__list_38_ptr
    i32.trunc_f64_u
    f64.const 4.0
    f64.store
    local.get $__list_38_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_38_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_38_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_38_ptr
    i32.trunc_f64_u
    i32.const 32
    i32.add
    f64.const 40.0
    f64.store
    local.get $__list_38_ptr
    local.set $__unpack_ptr_37
    local.get $__unpack_ptr_37
    i32.trunc_f64_u
    f64.load
    local.set $__unpack_len_37
    local.get $__unpack_ptr_37
    i32.trunc_f64_u
    local.get $__unpack_len_37
    i32.trunc_f64_u
    i32.const 1
    i32.sub
    i32.const 8
    i32.mul
    i32.const 8
    i32.add
    i32.add
    f64.load
    local.set $b
    local.get $__unpack_len_37
    f64.const 1.0
    f64.sub
    local.set $__unpack_star_len_37
    local.get $__unpack_star_len_37
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__unpack_star_ptr_37
    local.get $__unpack_star_ptr_37
    i32.trunc_f64_u
    local.get $__unpack_star_len_37
    f64.store
    f64.const 0
    local.set $__unpack_star_idx_37
    block $unpack_star_blk_37
      loop $unpack_star_lp_37
        local.get $__unpack_star_idx_37
        local.get $__unpack_star_len_37
        f64.ge
        br_if $unpack_star_blk_37
        local.get $__unpack_star_ptr_37
        i32.trunc_f64_u
        local.get $__unpack_star_idx_37
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__unpack_ptr_37
        i32.trunc_f64_u
        i32.const 0
        local.get $__unpack_star_idx_37
        i32.trunc_f64_u
        i32.add
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.store
        local.get $__unpack_star_idx_37
        f64.const 1
        f64.add
        local.set $__unpack_star_idx_37
        br $unpack_star_lp_37
      end
    end
    local.get $__unpack_star_ptr_37
    local.set $init
    ;; unpacking assignment lowered
    ;; list/tuple literal [4 elements]
    i32.const 40
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_40_ptr
    local.get $__list_40_ptr
    i32.trunc_f64_u
    f64.const 4.0
    f64.store
    local.get $__list_40_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_40_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_40_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_40_ptr
    i32.trunc_f64_u
    i32.const 32
    i32.add
    f64.const 40.0
    f64.store
    local.get $__list_40_ptr
    local.set $__unpack_ptr_39
    local.get $__unpack_ptr_39
    i32.trunc_f64_u
    f64.load
    local.set $__unpack_len_39
    local.get $__unpack_ptr_39
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.load
    local.set $c
    local.get $__unpack_ptr_39
    i32.trunc_f64_u
    local.get $__unpack_len_39
    i32.trunc_f64_u
    i32.const 1
    i32.sub
    i32.const 8
    i32.mul
    i32.const 8
    i32.add
    i32.add
    f64.load
    local.set $d
    local.get $__unpack_len_39
    f64.const 2.0
    f64.sub
    local.set $__unpack_star_len_39
    local.get $__unpack_star_len_39
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__unpack_star_ptr_39
    local.get $__unpack_star_ptr_39
    i32.trunc_f64_u
    local.get $__unpack_star_len_39
    f64.store
    f64.const 0
    local.set $__unpack_star_idx_39
    block $unpack_star_blk_39
      loop $unpack_star_lp_39
        local.get $__unpack_star_idx_39
        local.get $__unpack_star_len_39
        f64.ge
        br_if $unpack_star_blk_39
        local.get $__unpack_star_ptr_39
        i32.trunc_f64_u
        local.get $__unpack_star_idx_39
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__unpack_ptr_39
        i32.trunc_f64_u
        i32.const 1
        local.get $__unpack_star_idx_39
        i32.trunc_f64_u
        i32.add
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.store
        local.get $__unpack_star_idx_39
        f64.const 1
        f64.add
        local.set $__unpack_star_idx_39
        br $unpack_star_lp_39
      end
    end
    local.get $__unpack_star_ptr_39
    local.set $middle
    ;; unpacking assignment lowered
    ;; let squared_set = ...
    f64.const 0.0
    local.set $x
    f64.const 5.0
    local.set $__comp_end_42
    local.get $__comp_end_42
    local.get $x
    f64.sub
    local.set $__comp_len_42
    local.get $__comp_len_42
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_42
    local.get $__comp_ptr_42
    i32.trunc_f64_u
    local.get $__comp_len_42
    f64.store
    f64.const 0
    local.set $__comp_idx_42
    block $comp_list_blk_42
      loop $comp_list_lp_42
        local.get $__comp_idx_42
        local.get $__comp_len_42
        f64.ge
        br_if $comp_list_blk_42
        local.get $__comp_ptr_42
        i32.trunc_f64_u
        local.get $__comp_idx_42
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $x
        local.get $x
        f64.mul  ;; op='*'
        f64.store
        local.get $x
        f64.const 1
        f64.add
        local.set $x
        local.get $__comp_idx_42
        f64.const 1
        f64.add
        local.set $__comp_idx_42
        br $comp_list_lp_42
      end
    end
    local.get $__comp_ptr_42
    local.set $squared_set
    ;; let power_result = ...
    f64.const 2.0
    f64.const 8.0
    call $pow_f64
    local.set $power_result
    ;; let divmod_result = ...
    f64.const 17.0
    local.set $__divmod_left_43
    f64.const 5.0
    local.set $__divmod_right_44
    local.get $__divmod_left_43
    local.get $__divmod_right_44
    f64.div
    f64.floor
    local.set $__divmod_q_45
    ;; list/tuple literal [2 elements]
    i32.const 24
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_46_ptr
    local.get $__list_46_ptr
    i32.trunc_f64_u
    f64.const 2.0
    f64.store
    local.get $__list_46_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    local.get $__divmod_q_45
    f64.store
    local.get $__list_46_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    local.get $__divmod_left_43
    local.get $__divmod_q_45
    local.get $__divmod_right_44
    f64.mul  ;; op='*'
    f64.sub  ;; op='-'
    f64.store
    local.get $__list_46_ptr
    local.set $divmod_result
    ;; let delegated = ...
    call $delegating_gen
    local.set $delegated
    ;; print(...)
    local.get $items_found
    call $print_f64
    call $print_sep
    local.get $while_else_val
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $a
    call $print_f64
    call $print_sep
    i32.const 27
    i32.const 1
    call $print_str
    local.get $rest
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_47
    f64.const 0
    local.set $__print_idx_47
    block $print_seq_blk_47
      loop $print_seq_lp_47
        local.get $__print_idx_47
        local.get $__print_len_47
        f64.ge
        br_if $print_seq_blk_47
        local.get $__print_idx_47
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $rest
        i32.trunc_f64_u
        local.get $__print_idx_47
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_47
        f64.const 1
        f64.add
        local.set $__print_idx_47
        br $print_seq_lp_47
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_sep
    i32.const 27
    i32.const 1
    call $print_str
    local.get $init
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_48
    f64.const 0
    local.set $__print_idx_48
    block $print_seq_blk_48
      loop $print_seq_lp_48
        local.get $__print_idx_48
        local.get $__print_len_48
        f64.ge
        br_if $print_seq_blk_48
        local.get $__print_idx_48
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $init
        i32.trunc_f64_u
        local.get $__print_idx_48
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_48
        f64.const 1
        f64.add
        local.set $__print_idx_48
        br $print_seq_lp_48
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_sep
    local.get $b
    call $print_f64
    call $print_sep
    local.get $c
    call $print_f64
    call $print_sep
    i32.const 27
    i32.const 1
    call $print_str
    local.get $middle
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_49
    f64.const 0
    local.set $__print_idx_49
    block $print_seq_blk_49
      loop $print_seq_lp_49
        local.get $__print_idx_49
        local.get $__print_len_49
        f64.ge
        br_if $print_seq_blk_49
        local.get $__print_idx_49
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $middle
        i32.trunc_f64_u
        local.get $__print_idx_49
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_49
        f64.const 1
        f64.add
        local.set $__print_idx_49
        br $print_seq_lp_49
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_sep
    local.get $d
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $squared_set
    local.set $__sort_src_50
    local.get $__sort_src_50
    i32.trunc_f64_u
    f64.load
    local.set $__sort_len_50
    local.get $__sort_len_50
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__sort_dst_50
    local.get $__sort_dst_50
    i32.trunc_f64_u
    local.get $__sort_len_50
    f64.store
    f64.const 0
    local.set $__sort_i_50
    block $sort_copy_blk_50
      loop $sort_copy_lp_50
        local.get $__sort_i_50
        local.get $__sort_len_50
        f64.ge
        br_if $sort_copy_blk_50
        local.get $__sort_dst_50
        i32.trunc_f64_u
        local.get $__sort_i_50
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $__sort_src_50
        i32.trunc_f64_u
        local.get $__sort_i_50
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        f64.store
        local.get $__sort_i_50
        f64.const 1
        f64.add
        local.set $__sort_i_50
        br $sort_copy_lp_50
      end
    end
    f64.const 0
    local.set $__sort_i_50
    block $sort_outer_blk_50
      loop $sort_outer_lp_50
        local.get $__sort_i_50
        local.get $__sort_len_50
        f64.ge
        br_if $sort_outer_blk_50
        f64.const 0
        local.set $__sort_j_50
        block $sort_inner_blk_50
          loop $sort_inner_lp_50
            local.get $__sort_j_50
            local.get $__sort_len_50
            f64.const 1
            f64.sub
            f64.ge
            br_if $sort_inner_blk_50
            local.get $__sort_dst_50
            i32.trunc_f64_u
            local.get $__sort_j_50
            i32.trunc_f64_u
            i32.const 8
            i32.mul
            i32.const 8
            i32.add
            i32.add
            f64.load
            local.set $__sort_a_50
            local.get $__sort_dst_50
            i32.trunc_f64_u
            local.get $__sort_j_50
            i32.trunc_f64_u
            i32.const 1
            i32.add
            i32.const 8
            i32.mul
            i32.const 8
            i32.add
            i32.add
            f64.load
            local.set $__sort_b_50
            local.get $__sort_a_50
            local.get $__sort_b_50
            f64.gt
            if
              local.get $__sort_dst_50
              i32.trunc_f64_u
              local.get $__sort_j_50
              i32.trunc_f64_u
              i32.const 8
              i32.mul
              i32.const 8
              i32.add
              i32.add
              local.get $__sort_b_50
              f64.store
              local.get $__sort_dst_50
              i32.trunc_f64_u
              local.get $__sort_j_50
              i32.trunc_f64_u
              i32.const 1
              i32.add
              i32.const 8
              i32.mul
              i32.const 8
              i32.add
              i32.add
              local.get $__sort_a_50
              f64.store
            end
            local.get $__sort_j_50
            f64.const 1
            f64.add
            local.set $__sort_j_50
            br $sort_inner_lp_50
          end
        end
        local.get $__sort_i_50
        f64.const 1
        f64.add
        local.set $__sort_i_50
        br $sort_outer_lp_50
      end
    end
    local.get $__sort_dst_50
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $power_result
    call $print_f64
    call $print_sep
    i32.const 31
    i32.const 1
    call $print_str
    local.get $divmod_result
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_51
    f64.const 0
    local.set $__print_idx_51
    block $print_seq_blk_51
      loop $print_seq_lp_51
        local.get $__print_idx_51
        local.get $__print_len_51
        f64.ge
        br_if $print_seq_blk_51
        local.get $__print_idx_51
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $divmod_result
        i32.trunc_f64_u
        local.get $__print_idx_51
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_51
        f64.const 1
        f64.add
        local.set $__print_idx_51
        br $print_seq_lp_51
      end
    end
    i32.const 32
    i32.const 1
    call $print_str
    call $print_newline
    ;; print(...)
    i32.const 27
    i32.const 1
    call $print_str
    local.get $delegated
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_52
    f64.const 0
    local.set $__print_idx_52
    block $print_seq_blk_52
      loop $print_seq_lp_52
        local.get $__print_idx_52
        local.get $__print_len_52
        f64.ge
        br_if $print_seq_blk_52
        local.get $__print_idx_52
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $delegated
        i32.trunc_f64_u
        local.get $__print_idx_52
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_52
        f64.const 1
        f64.add
        local.set $__print_idx_52
        br $print_seq_lp_52
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_newline
    ;; let hex_num = ...
    f64.const 0.0
    local.set $hex_num
    ;; let oct_num = ...
    f64.const 0.0
    local.set $oct_num
    ;; let bin_num = ...
    f64.const 0.0
    local.set $bin_num
    ;; let sci_num = ...
    f64.const 1500.0
    local.set $sci_num
    ;; let aug = ...
    f64.const 10.0
    local.set $aug
    ;; aug += ...
    local.get $aug
    f64.const 5.0
    f64.add
    local.set $aug
    ;; aug -= ...
    local.get $aug
    f64.const 2.0
    f64.sub
    local.set $aug
    ;; aug *= ...
    local.get $aug
    f64.const 3.0
    f64.mul
    local.set $aug
    ;; aug //= ...
    local.get $aug
    f64.const 4.0
    f64.div
    f64.floor
    local.set $aug
    ;; aug %= ...
    local.get $aug
    local.tee $__aug_a_53
    f64.const 3.0
    local.tee $__aug_b_53
    f64.div
    f64.floor
    local.get $__aug_b_53
    f64.mul
    f64.neg
    local.get $__aug_a_53
    f64.add  ;; a - floor(a/b)*b
    local.set $aug
    ;; let bit_a = ...
    f64.const 0.0
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.and
    f64.convert_i32_s
    local.set $bit_a
    ;; let bit_o = ...
    f64.const 0.0
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.or
    f64.convert_i32_s
    local.set $bit_o
    ;; let bit_x = ...
    f64.const 0.0
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.xor
    f64.convert_i32_s
    local.set $bit_x
    ;; let bit_l = ...
    f64.const 1.0
    i32.trunc_f64_s
    f64.const 3.0
    i32.trunc_f64_s
    i32.shl
    f64.convert_i32_s
    local.set $bit_l
    ;; let bit_r = ...
    f64.const 64.0
    i32.trunc_f64_s
    f64.const 2.0
    i32.trunc_f64_s
    i32.shr_s
    f64.convert_i32_s
    local.set $bit_r
    ;; chained assignment
    f64.const 0.0
    local.set $__chain_54
    local.get $__chain_54
    local.set $ca
    local.get $__chain_54
    local.set $cb
    local.get $__chain_54
    local.set $cc
    ;; annotated assignment typed: ...
    f64.const 99.0
    local.set $typed
    ;; let ternary = ...
    local.get $typed
    f64.const 0.0
    f64.gt
    if (result f64)
      f64.const 33.0  ;; str offset (not a numeric value)
      i32.const 3
      global.set $__last_str_len
    else
      f64.const 36.0  ;; str offset (not a numeric value)
      i32.const 2
      global.set $__last_str_len
    end
    local.set $ternary
    ;; let multi_result = ...
    f64.const 10.0
    f64.const 2.0
    call $multi_params
    local.set $multi_result
    ;; let sq = ...
    f64.const 0.0  ;; lambda $__lambda_55 table idx
    local.set $sq
    ;; let list_c = ...
    f64.const 0.0
    local.set $x
    f64.const 4.0
    local.set $__comp_end_57
    local.get $__comp_end_57
    local.get $x
    f64.sub
    local.set $__comp_len_57
    local.get $__comp_len_57
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_57
    local.get $__comp_ptr_57
    i32.trunc_f64_u
    local.get $__comp_len_57
    f64.store
    f64.const 0
    local.set $__comp_idx_57
    block $comp_list_blk_57
      loop $comp_list_lp_57
        local.get $__comp_idx_57
        local.get $__comp_len_57
        f64.ge
        br_if $comp_list_blk_57
        local.get $__comp_ptr_57
        i32.trunc_f64_u
        local.get $__comp_idx_57
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $x
        f64.const 2.0
        f64.mul  ;; op='*'
        f64.store
        local.get $x
        f64.const 1
        f64.add
        local.set $x
        local.get $__comp_idx_57
        f64.const 1
        f64.add
        local.set $__comp_idx_57
        br $comp_list_lp_57
      end
    end
    local.get $__comp_ptr_57
    local.set $list_c
    ;; let dict_c = ...
    f64.const 0.0
    local.set $k
    f64.const 3.0
    local.set $__dict_end_58
    local.get $__dict_end_58
    local.get $k
    f64.sub
    local.set $__dict_len_58
    local.get $__dict_len_58
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__dict_ptr_58
    local.get $__dict_ptr_58
    i32.trunc_f64_u
    local.get $__dict_len_58
    f64.store
    f64.const 0
    local.set $__dict_idx_58
    block $dict_comp_blk_58
      loop $dict_comp_lp_58
        local.get $k
        local.get $__dict_end_58
        f64.ge
        br_if $dict_comp_blk_58
        local.get $__dict_ptr_58
        i32.trunc_f64_u
        local.get $__dict_idx_58
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $k
        local.get $k
        f64.mul  ;; op='*'
        f64.store
        local.get $__dict_idx_58
        f64.const 1
        f64.add
        local.set $__dict_idx_58
        local.get $k
        f64.const 1
        f64.add
        local.set $k
        br $dict_comp_lp_58
      end
    end
    local.get $__dict_ptr_58
    local.set $dict_c
    ;; let gen_c = ...
    f64.const 0.0
    local.set $x
    f64.const 3.0
    local.set $__comp_end_59
    local.get $__comp_end_59
    local.get $x
    f64.sub
    local.set $__comp_len_59
    local.get $__comp_len_59
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_59
    local.get $__comp_ptr_59
    i32.trunc_f64_u
    local.get $__comp_len_59
    f64.store
    f64.const 0
    local.set $__comp_idx_59
    block $comp_list_blk_59
      loop $comp_list_lp_59
        local.get $__comp_idx_59
        local.get $__comp_len_59
        f64.ge
        br_if $comp_list_blk_59
        local.get $__comp_ptr_59
        i32.trunc_f64_u
        local.get $__comp_idx_59
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $x
        f64.const 1.0
        f64.add  ;; op='+'
        f64.store
        local.get $x
        f64.const 1
        f64.add
        local.set $x
        local.get $__comp_idx_59
        f64.const 1
        f64.add
        local.set $__comp_idx_59
        br $comp_list_lp_59
      end
    end
    local.get $__comp_ptr_59
    local.set $gen_c
    ;; let nested_c = ...
    f64.const 0.0
    local.set $i
    f64.const 2.0
    local.set $__comp_outer_end_60
    local.get $__comp_outer_end_60
    local.get $i
    f64.sub
    local.set $__comp_outer_span_60
    f64.const 0.0
    local.set $__comp_inner_start_60
    f64.const 2.0
    local.set $__comp_inner_end_60
    local.get $__comp_inner_end_60
    local.get $__comp_inner_start_60
    f64.sub
    local.set $__comp_inner_span_60
    local.get $__comp_outer_span_60
    local.get $__comp_inner_span_60
    f64.mul
    local.set $__comp_cap_60
    local.get $__comp_cap_60
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_60
    local.get $__comp_ptr_60
    i32.trunc_f64_u
    f64.const 0
    f64.store
    f64.const 0
    local.set $__comp_write_60
    block $comp_outer_blk_60
      loop $comp_outer_lp_60
        local.get $i
        local.get $__comp_outer_end_60
        f64.ge
        br_if $comp_outer_blk_60
        local.get $__comp_inner_start_60
        local.set $j
        block $comp_inner_blk_60
          loop $comp_inner_lp_60
            local.get $j
            local.get $__comp_inner_end_60
            f64.ge
            br_if $comp_inner_blk_60
            local.get $__comp_ptr_60
            i32.trunc_f64_u
            local.get $__comp_write_60
            i32.trunc_f64_u
            i32.const 8
            i32.mul
            i32.const 8
            i32.add
            i32.add
            local.get $i
            local.get $j
            f64.add  ;; op='+'
            f64.store
            local.get $__comp_write_60
            f64.const 1
            f64.add
            local.set $__comp_write_60
            local.get $j
            f64.const 1
            f64.add
            local.set $j
            br $comp_inner_lp_60
          end
        end
        local.get $i
        f64.const 1
        f64.add
        local.set $i
        br $comp_outer_lp_60
      end
    end
    local.get $__comp_ptr_60
    i32.trunc_f64_u
    local.get $__comp_write_60
    f64.store
    local.get $__comp_ptr_60
    local.set $nested_c
    ;; let filter_c = ...
    f64.const 0.0
    local.set $x
    f64.const 6.0
    local.set $__comp_end_61
    local.get $__comp_end_61
    local.get $x
    f64.sub
    local.set $__comp_cap_61
    local.get $__comp_cap_61
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_61
    local.get $__comp_ptr_61
    i32.trunc_f64_u
    f64.const 0
    f64.store
    f64.const 0
    local.set $__comp_write_61
    block $comp_filter_blk_61
      loop $comp_filter_lp_61
        local.get $x
        local.get $__comp_end_61
        f64.ge
        br_if $comp_filter_blk_61
        local.get $x
        local.set $__mod_left_62
        local.get $__mod_left_62
        local.get $__mod_left_62
        f64.const 2.0
        f64.div
        f64.floor
        f64.const 2.0
        f64.mul
        f64.sub
        f64.const 0.0
        f64.eq
        if
          local.get $__comp_ptr_61
          i32.trunc_f64_u
          local.get $__comp_write_61
          i32.trunc_f64_u
          i32.const 8
          i32.mul
          i32.const 8
          i32.add
          i32.add
          local.get $x
          f64.store
          local.get $__comp_write_61
          f64.const 1
          f64.add
          local.set $__comp_write_61
        end
        local.get $x
        f64.const 1
        f64.add
        local.set $x
        br $comp_filter_lp_61
      end
    end
    local.get $__comp_ptr_61
    i32.trunc_f64_u
    local.get $__comp_write_61
    f64.store
    local.get $__comp_ptr_61
    local.set $filter_c
    ;; let try_else = ...
    f64.const 0.0
    local.set $try_else
    ;; try (best-effort: no WASM exception handling)
    ;; try_else = ...
    f64.const 7.0
    local.set $try_else
    ;; except handler(s) omitted (WAT cannot intercept exceptions)
    ;; try-else omitted (no exception state available in WAT)
    ;; let chained = ...
    i32.const 0
    f64.convert_i32_s
    local.set $chained
    ;; try (best-effort: no WASM exception handling)
    ;; try (best-effort: no WASM exception handling)
    ;; raise omitted in WAT best-effort mode
    ;; except handler(s) omitted (WAT cannot intercept exceptions)
    ;; except handler(s) omitted (WAT cannot intercept exceptions)
    ;; let multi_exc = ...
    f64.const 0.0
    local.set $multi_exc
    ;; try (best-effort: no WASM exception handling)
    ;; raise omitted in WAT best-effort mode
    ;; except handler(s) omitted (WAT cannot intercept exceptions)
    ;; let mv = ...
    f64.const 2.0
    local.set $mv
    ;; let mr = ...
    f64.const 38.0  ;; str offset (not a numeric value)
    i32.const 5
    global.set $__last_str_len
    local.set $mr
    f64.const 5.0
    local.set $mr_strlen
    ;; match ...
    local.get $mv
    local.set $__match_subj_63
    block $__match_end_63
      ;; case 1.0:
      local.get $__match_subj_63
      f64.const 1.0
      f64.eq
      if
        ;; mr = ...
        f64.const 43.0  ;; str offset (not a numeric value)
        i32.const 3
        global.set $__last_str_len
        local.set $mr
        f64.const 3.0
        local.set $mr_strlen
        br $__match_end_63
      end
      ;; case 2.0:
      local.get $__match_subj_63
      f64.const 2.0
      f64.eq
      if
        ;; mr = ...
        f64.const 46.0  ;; str offset (not a numeric value)
        i32.const 3
        global.set $__last_str_len
        local.set $mr
        f64.const 3.0
        local.set $mr_strlen
        br $__match_end_63
      end
      ;; case _: (default)
        ;; mr = ...
        f64.const 49.0  ;; str offset (not a numeric value)
        i32.const 7
        global.set $__last_str_len
        local.set $mr
        f64.const 7.0
        local.set $mr_strlen
      br $__match_end_63
    end  ;; match
    ;; let dec_r = ...
    call $ten
    local.set $dec_r
    ;; let comb = ...
    f64.const 0  ;; implicit cls
    f64.const 3.0
    call $Combined__build
    local.set $comb
    ;; let prop = ...
    ;; @property comb.doubled()
    local.get $comb
    call $Combined__doubled
    local.set $prop
    ;; print(...)
    local.get $hex_num
    call $print_f64
    call $print_sep
    local.get $oct_num
    call $print_f64
    call $print_sep
    local.get $bin_num
    call $print_f64
    call $print_sep
    local.get $sci_num
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $aug
    call $print_f64
    call $print_sep
    local.get $bit_a
    call $print_f64
    call $print_sep
    local.get $bit_o
    call $print_f64
    call $print_sep
    local.get $bit_x
    call $print_f64
    call $print_sep
    local.get $bit_l
    call $print_f64
    call $print_sep
    local.get $bit_r
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $ca
    call $print_f64
    call $print_sep
    local.get $cb
    call $print_f64
    call $print_sep
    local.get $cc
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $typed
    call $print_f64
    call $print_sep
    f64.const 3.0
    f64.const 1.5
    call $annotated
    call $print_f64
    call $print_sep
    local.get $ternary
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $multi_result
    call $print_f64
    call $print_sep
    ;; call lambda sq via table (arity=1)
    f64.const 5.0
    local.get $sq
    i32.trunc_f64_u
    call_indirect (param f64) (result f64)
    call $print_f64
    call $print_newline
    ;; print(...)
    i32.const 27
    i32.const 1
    call $print_str
    local.get $list_c
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_64
    f64.const 0
    local.set $__print_idx_64
    block $print_seq_blk_64
      loop $print_seq_lp_64
        local.get $__print_idx_64
        local.get $__print_len_64
        f64.ge
        br_if $print_seq_blk_64
        local.get $__print_idx_64
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $list_c
        i32.trunc_f64_u
        local.get $__print_idx_64
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_64
        f64.const 1
        f64.add
        local.set $__print_idx_64
        br $print_seq_lp_64
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_sep
    local.get $dict_c
    call $print_f64
    call $print_sep
    local.get $gen_c
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $nested_c
    call $print_f64
    call $print_sep
    local.get $filter_c
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $try_else
    call $print_f64
    call $print_sep
    local.get $chained
    call $print_f64
    call $print_sep
    local.get $multi_exc
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $mr
    i32.trunc_f64_u
    local.get $mr_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_sep
    local.get $dec_r
    call $print_f64
    call $print_sep
    local.get $prop
    call $print_f64
    call $print_newline
    ;; print(...)
    call $with_doc
    call $print_f64
    call $print_newline
    ;; let bau = ...
    f64.const 0.0
    local.set $bau
    ;; bau &= ...
    local.get $bau
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.and
    f64.convert_i32_s
    local.set $bau
    ;; bau |= ...
    local.get $bau
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.or
    f64.convert_i32_s
    local.set $bau
    ;; bau ^= ...
    local.get $bau
    i32.trunc_f64_s
    f64.const 0.0
    i32.trunc_f64_s
    i32.xor
    f64.convert_i32_s
    local.set $bau
    ;; bau <<= ...
    local.get $bau
    i32.trunc_f64_s
    f64.const 1.0
    i32.trunc_f64_s
    i32.shl
    f64.convert_i32_s
    local.set $bau
    ;; bau >>= ...
    local.get $bau
    i32.trunc_f64_s
    f64.const 2.0
    i32.trunc_f64_s
    i32.shr_s
    f64.convert_i32_s
    local.set $bau
    ;; let pow_aug = ...
    f64.const 2.0
    local.set $pow_aug
    ;; pow_aug **= ...
    local.get $pow_aug
    f64.const 4.0
    call $pow_f64
    local.set $pow_aug
    ;; let bdata = ...
    f64.const 56.0  ;; bytes offset
    local.set $bdata
    f64.const 5.0
    local.set $bdata_strlen
    ;; let blen = ...
    local.get $bdata_strlen
    local.set $blen
    ;; let str_a = ...
    f64.const 56.0  ;; str offset (not a numeric value)
    i32.const 5
    global.set $__last_str_len
    local.set $str_a
    f64.const 5.0
    local.set $str_a_strlen
    ;; let str_b = ...
    f64.const 61.0  ;; str offset (not a numeric value)
    i32.const 6
    global.set $__last_str_len
    local.set $str_b
    f64.const 6.0
    local.set $str_b_strlen
    ;; let str_cat = ...
    ;; str concat (runtime)
    local.get $str_a
    local.get $str_a_strlen
    i32.trunc_f64_u
    global.set $__last_str_len
    local.get $str_a_strlen
    local.get $str_b
    local.get $str_b_strlen
    i32.trunc_f64_u
    global.set $__last_str_len
    local.get $str_b_strlen
    call $__str_concat
    local.set $str_cat
    local.get $str_a_strlen
    local.get $str_b_strlen
    f64.add
    local.set $str_cat_strlen
    ;; let str_idx = ...
    ;; str_a[i] — string byte access
    local.get $str_a
    i32.trunc_f64_u
    f64.const 1.0
    i32.trunc_f64_u
    i32.add
    i32.load8_u
    f64.convert_i32_u  ;; char code as f64
    local.set $str_idx
    ;; let str_slc = ...
    ;; str_a[start:stop] — string slice
    local.get $str_a
    f64.const 1.0
    f64.const 3.0
    call $__str_slice
    local.set $str_slc
    ;; let tup_lit = ...
    ;; list/tuple literal [3 elements]
    i32.const 32
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_65_ptr
    local.get $__list_65_ptr
    i32.trunc_f64_u
    f64.const 3.0
    f64.store
    local.get $__list_65_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_65_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_65_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_65_ptr
    local.set $tup_lit
    ;; let tup_elem = ...
    ;; tup_lit[i]
    local.get $tup_lit
    i32.trunc_f64_u
    f64.const 1.0
    i32.trunc_f64_u
    i32.const 8
    i32.mul
    i32.const 8  ;; skip length header
    i32.add
    i32.add
    f64.load
    local.set $tup_elem
    ;; let iter_list = ...
    ;; list/tuple literal [3 elements]
    i32.const 32
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_66_ptr
    local.get $__list_66_ptr
    i32.trunc_f64_u
    f64.const 3.0
    f64.store
    local.get $__list_66_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 10.0
    f64.store
    local.get $__list_66_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 20.0
    f64.store
    local.get $__list_66_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 30.0
    f64.store
    local.get $__list_66_ptr
    local.set $iter_list
    ;; let iter_sum = ...
    f64.const 0.0
    local.set $iter_sum
    ;; for iter_val in iter_list (list)
    local.get $iter_list
    local.set $__flbase_67
    local.get $iter_list
    i32.trunc_f64_u
    f64.load
    local.set $__fllen_67
    f64.const 0
    local.set $__flidx_67
    block $for_blk_67
      loop $for_lp_67
        local.get $__flidx_67
        local.get $__fllen_67
        f64.ge
        br_if $for_blk_67
        local.get $__flbase_67
        i32.trunc_f64_u
        local.get $__flidx_67
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        local.set $iter_val
        ;; iter_sum = ...
        local.get $iter_sum
        local.get $iter_val
        f64.add  ;; op='+'
        local.set $iter_sum
        local.get $__flidx_67
        f64.const 1
        f64.add
        local.set $__flidx_67
        br $for_lp_67
      end  ;; loop
    end  ;; block (for list)
    ;; let comp_list = ...
    ;; list/tuple literal [4 elements]
    i32.const 40
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_68_ptr
    local.get $__list_68_ptr
    i32.trunc_f64_u
    f64.const 4.0
    f64.store
    local.get $__list_68_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 1.0
    f64.store
    local.get $__list_68_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 2.0
    f64.store
    local.get $__list_68_ptr
    i32.trunc_f64_u
    i32.const 24
    i32.add
    f64.const 3.0
    f64.store
    local.get $__list_68_ptr
    i32.trunc_f64_u
    i32.const 32
    i32.add
    f64.const 4.0
    f64.store
    local.get $__list_68_ptr
    local.set $comp_list
    ;; let doubled_list = ...
    local.get $comp_list
    i32.trunc_f64_u
    f64.load
    local.set $__comp_src_len_70
    local.get $__comp_src_len_70
    local.set $__comp_len_70
    local.get $__comp_len_70
    i32.trunc_f64_u
    i32.const 1
    i32.add
    i32.const 8
    i32.mul
    call $ml_alloc
    f64.convert_i32_u
    local.set $__comp_ptr_70
    local.get $__comp_ptr_70
    i32.trunc_f64_u
    local.get $__comp_len_70
    f64.store
    f64.const 0
    local.set $__comp_idx_70
    block $comp_list_blk_70
      loop $comp_list_lp_70
        local.get $__comp_idx_70
        local.get $__comp_len_70
        f64.ge
        br_if $comp_list_blk_70
        local.get $comp_list
        i32.trunc_f64_u
        local.get $__comp_idx_70
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        local.set $v
        local.get $__comp_ptr_70
        i32.trunc_f64_u
        local.get $__comp_idx_70
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        local.get $v
        f64.const 2.0
        f64.mul  ;; op='*'
        f64.store
        local.get $__comp_idx_70
        f64.const 1
        f64.add
        local.set $__comp_idx_70
        br $comp_list_lp_70
      end
    end
    local.get $__comp_ptr_70
    local.set $doubled_list
    ;; let ms = ...
    f64.const 56.0  ;; str offset (not a numeric value)
    i32.const 5
    global.set $__last_str_len
    local.set $ms
    f64.const 5.0
    local.set $ms_strlen
    ;; let msr = ...
    f64.const 67.0  ;; str offset (not a numeric value)
    i32.const 4
    global.set $__last_str_len
    local.set $msr
    f64.const 4.0
    local.set $msr_strlen
    ;; match ...
    local.get $ms
    local.get $ms_strlen
    i32.trunc_f64_u
    global.set $__last_str_len
    local.set $__match_subj_71
    block $__match_end_71
      ;; case 'hello':
      local.get $__match_subj_71
      f64.const 56.0
      f64.eq
      if
        ;; msr = ...
        f64.const 71.0  ;; str offset (not a numeric value)
        i32.const 2
        global.set $__last_str_len
        local.set $msr
        f64.const 2.0
        local.set $msr_strlen
        br $__match_end_71
      end
      ;; case 'bye':
      local.get $__match_subj_71
      f64.const 73.0
      f64.eq
      if
        ;; msr = ...
        f64.const 76.0  ;; str offset (not a numeric value)
        i32.const 7
        global.set $__last_str_len
        local.set $msr
        f64.const 7.0
        local.set $msr_strlen
        br $__match_end_71
      end
      ;; case _: (default)
        ;; msr = ...
        f64.const 83.0  ;; str offset (not a numeric value)
        i32.const 7
        global.set $__last_str_len
        local.set $msr
        f64.const 7.0
        local.set $msr_strlen
      br $__match_end_71
    end  ;; match
    ;; let mn = ...
    f64.const 0
    local.set $mn
    ;; let mnr = ...
    f64.const 90.0  ;; str offset (not a numeric value)
    i32.const 7
    global.set $__last_str_len
    local.set $mnr
    f64.const 7.0
    local.set $mnr_strlen
    ;; match ...
    local.get $mn
    local.set $__match_subj_72
    block $__match_end_72
      ;; case None:
      local.get $__match_subj_72
      f64.const 0.0
      f64.eq
      if
        ;; mnr = ...
        f64.const 97.0  ;; str offset (not a numeric value)
        i32.const 4
        global.set $__last_str_len
        local.set $mnr
        f64.const 4.0
        local.set $mnr_strlen
        br $__match_end_72
      end
      ;; case _: (default)
        ;; mnr = ...
        f64.const 38.0  ;; str offset (not a numeric value)
        i32.const 5
        global.set $__last_str_len
        local.set $mnr
        f64.const 5.0
        local.set $mnr_strlen
      br $__match_end_72
    end  ;; match
    ;; let mc = ...
    f64.const 42.0
    local.set $mc
    ;; let mcr = ...
    f64.const 0.0
    local.set $mcr
    ;; match ...
    local.get $mc
    local.set $__match_subj_73
    block $__match_end_73
      ;; case 42.0:
      local.get $__match_subj_73
      f64.const 42.0
      f64.eq
      if
        ;; mcr = ...
        local.get $mc
        local.set $mcr
        br $__match_end_73
      end
      ;; case _: (default)
        ;; mcr = ...
        f64.const 0.0
        local.set $mcr
      br $__match_end_73
    end  ;; match
    ;; let mt = ...
    ;; list/tuple literal [2 elements]
    i32.const 24
    call $ml_alloc
    f64.convert_i32_u
    local.set $__list_74_ptr
    local.get $__list_74_ptr
    i32.trunc_f64_u
    f64.const 2.0
    f64.store
    local.get $__list_74_ptr
    i32.trunc_f64_u
    i32.const 8
    i32.add
    f64.const 1.0
    f64.store
    local.get $__list_74_ptr
    i32.trunc_f64_u
    i32.const 16
    i32.add
    f64.const 2.0
    f64.store
    local.get $__list_74_ptr
    local.set $mt
    ;; let mtr = ...
    f64.const 36.0  ;; str offset (not a numeric value)
    i32.const 2
    global.set $__last_str_len
    local.set $mtr
    f64.const 2.0
    local.set $mtr_strlen
    ;; match ...
    local.get $mt
    local.set $__match_subj_75
    block $__match_end_75
      ;; case (1, 2,): element-wise comparison
      local.get $__match_subj_75
      i32.trunc_f64_u
      f64.load
      f64.const 2.0
      f64.eq
      local.get $__match_subj_75
      i32.trunc_f64_u
      i32.const 8
      i32.add
      f64.load
      f64.const 1.0
      f64.eq
      i32.and
      local.get $__match_subj_75
      i32.trunc_f64_u
      i32.const 16
      i32.add
      f64.load
      f64.const 2.0
      f64.eq
      i32.and
      if
        ;; mtr = ...
        f64.const 33.0  ;; str offset (not a numeric value)
        i32.const 3
        global.set $__last_str_len
        local.set $mtr
        f64.const 3.0
        local.set $mtr_strlen
        br $__match_end_75
      end
      ;; case _: (default)
        ;; mtr = ...
        f64.const 36.0  ;; str offset (not a numeric value)
        i32.const 2
        global.set $__last_str_len
        local.set $mtr
        f64.const 2.0
        local.set $mtr_strlen
      br $__match_end_75
    end  ;; match
    ;; let async_result = ...
    f64.const 5.0
    call $async_double
    local.set $async_result
    ;; let async_for_result = ...
    call $async_for_task
    local.set $async_for_result
    ;; let async_with_result = ...
    call $async_with_task
    local.set $async_with_result
    ;; print(...)
    local.get $bau
    call $print_f64
    call $print_sep
    local.get $pow_aug
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $blen
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $str_cat
    i32.trunc_f64_u
    local.get $str_cat_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_sep
    local.get $str_idx
    call $print_f64
    call $print_sep
    local.get $str_slc
    call $print_f64
    call $print_newline
    ;; print(...)
    local.get $tup_elem
    call $print_f64
    call $print_sep
    local.get $iter_sum
    call $print_f64
    call $print_newline
    ;; print(...)
    i32.const 27
    i32.const 1
    call $print_str
    local.get $doubled_list
    i32.trunc_f64_u
    f64.load
    local.set $__print_len_76
    f64.const 0
    local.set $__print_idx_76
    block $print_seq_blk_76
      loop $print_seq_lp_76
        local.get $__print_idx_76
        local.get $__print_len_76
        f64.ge
        br_if $print_seq_blk_76
        local.get $__print_idx_76
        f64.const 0
        f64.gt
        if
          i32.const 29
          i32.const 2
          call $print_str
        end
        local.get $doubled_list
        i32.trunc_f64_u
        local.get $__print_idx_76
        i32.trunc_f64_u
        i32.const 8
        i32.mul
        i32.const 8
        i32.add
        i32.add
        f64.load
        call $print_f64
        local.get $__print_idx_76
        f64.const 1
        f64.add
        local.set $__print_idx_76
        br $print_seq_lp_76
      end
    end
    i32.const 28
    i32.const 1
    call $print_str
    call $print_newline
    ;; print(...)
    local.get $msr
    i32.trunc_f64_u
    local.get $msr_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_sep
    local.get $mnr
    i32.trunc_f64_u
    local.get $mnr_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_sep
    local.get $mcr
    call $print_f64
    call $print_sep
    local.get $mtr
    i32.trunc_f64_u
    local.get $mtr_strlen
    i32.trunc_f64_u
    call $print_str
    call $print_newline
    ;; print(...)
    local.get $async_result
    call $print_f64
    call $print_sep
    local.get $async_for_result
    call $print_f64
    call $print_sep
    local.get $async_with_result
    call $print_f64
    call $print_newline
  )
)