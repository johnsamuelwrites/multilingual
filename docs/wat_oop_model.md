# WAT/WASM OOP Object Model

This document describes how object-oriented programming constructs are compiled
to WebAssembly Text (WAT) by `WATCodeGenerator`.

## Overview

WAT operates on a flat linear memory with a small set of value types (`i32`,
`i64`, `f64`, `f32`). There is no native struct or object type. To support
classes and instances the generator uses:

1. **Method lowering** — each class method becomes a standalone WAT function
   with a mangled name.
2. **Bump-pointer heap** — a single mutable `i32` global tracks the next free
   byte; object allocation moves this pointer forward.
3. **f64-encoded pointers** — the generator carries object addresses as `f64`
   values (the project's universal value type) and converts to/from `i32` only
   at memory-access sites.
4. **Compile-time field layout** — the code generator scans `self.attr = …`
   assignments at codegen time to build a fixed `{field_name → byte_offset}`
   map per class; no runtime type information is needed.

## Stateful vs. Stateless Classes

The generator distinguishes two kinds of classes:

| Kind | Definition | WAT behaviour |
|------|-----------|---------------|
| **Stateless** | No `self.attr = …` in any method | `f64.const 0` passed as `self`; no heap allocation |
| **Stateful** | At least one `self.attr = …` | Heap allocation on every constructor call; `self` carries the heap address |

Stateless classes (pure utility classes, mixin methods that operate only on
their arguments) compile identically to before and carry no allocation overhead.

## Memory Layout

```
Linear memory (WAT, 64 KB default page)
┌──────────────────────────────┐  ← offset 0
│  String data section         │  ← interned string literals (immutable)
│  (len bytes, UTF-8 encoded)  │
├──────────────────────────────┤  ← HEAP_BASE
│  Object heap                 │  ← bump-allocated instances
│  (grows upward)              │
└──────────────────────────────┘  ← 65535
```

`HEAP_BASE` is computed at code-generation time:

```
HEAP_BASE = max( ceil(string_data_len / 8) * 8, 64 )
```

Aligning to 8 bytes ensures `f64` fields are naturally aligned;
the minimum of 64 prevents accidental overlap with metadata near offset 0.

The heap pointer is a single WAT global:

```wat
(global $__heap_ptr (mut i32) (i32.const HEAP_BASE))
```

## Object Instance Layout

Each object is a contiguous run of `f64` values in linear memory.
Field order is determined by **first-seen `self.attr = …` assignment** across
all methods, scanning in source order (`__init__` first, then remaining methods).

Example — a `Counter` class with two fields:

```python
class Counter:
    def __init__(self, x, y):
        self.x = x      # first seen → byte offset 0
        self.y = y      # second seen → byte offset 8
```

Instance layout:

```
base + 0   : f64  (self.x)
base + 8   : f64  (self.y)
```

Object size: `number_of_fields × 8` bytes.

## Constructor Calls

`Counter(10, 20)` (expression context) lowers to:

```wat
;; alloc Counter (16 bytes)
global.get $__heap_ptr
i32.const 16
i32.add
global.set $__heap_ptr         ;; advance heap pointer

global.get $__heap_ptr         ;; base = new_ptr - size
i32.const 16
i32.sub
f64.convert_i32_u              ;; self as f64

f64.const 10.0                 ;; arg x
f64.const 20.0                 ;; arg y
call $Counter____init__
drop                           ;; __init__ return value discarded

global.get $__heap_ptr         ;; push object reference
i32.const 16
i32.sub
f64.convert_i32_u              ;; object ref as f64
```

The result is the heap address of the new instance, encoded as `f64`.

In statement context (`Counter(10, 20)` not assigned to anything) the final
two lines (object ref push) are omitted.

## Field Store and Load

**`self.x = val`** compiles to:

```wat
local.get $self          ;; f64 pointer
i32.trunc_f64_u          ;; → i32 address
i32.const 0              ;; field offset of x
i32.add
{val instructions}       ;; push f64 value
f64.store
```

**`self.x`** (load) compiles to:

```wat
local.get $self
i32.trunc_f64_u
i32.const 0
i32.add
f64.load
```

**Compound assignment `self.x += delta`** saves the new value to a temporary
`f64` local, then recomputes the address for the store:

```wat
local.get $self          ;; load old value
i32.trunc_f64_u
i32.const 0
i32.add
f64.load
{delta instructions}
f64.add
local.set $__attr_val_N  ;; save new value

local.get $self          ;; store new value
i32.trunc_f64_u
i32.const 0
i32.add
local.get $__attr_val_N
f64.store
```

## Instance Method Calls

After `let c = Counter(10, 20)`, the generator tracks `c → Counter` in its
class-type map. A call `c.increment()` lowers to:

```wat
local.get $c             ;; push actual object pointer (f64)
call $Counter__increment
drop
```

For **stateless** classes the old behaviour is preserved — `f64.const 0` is
passed as `self` and the method operates solely on its explicit arguments.

## Method Name Mangling

All class methods become top-level WAT exports with the naming scheme:

```
{ClassName}__{method_name}
```

Examples:

| Source | WAT symbol |
|--------|-----------|
| `Counter.__init__` | `$Counter____init__` |
| `Counter.get` | `$Counter__get` |
| `Point.distance` | `$Point__distance` |

The double underscore separator ensures no collision with plain functions.
WAT export names match the mangled form; `_wat_symbol()` further sanitizes
non-alphanumeric characters for WAT identifier safety.

## External Attribute Access

`obj.attr` read outside the class (e.g., in `__main__` after
`let obj = Class(...)`) is also lowered to `f64.load` when the generator can
statically determine the class of `obj` from its `_var_class_types` map.

Example:

```python
let c = Counter(10, 20)
print(c.x)
```

Lowers to:

```wat
local.get $c
i32.trunc_f64_u
i32.const 0
i32.add
f64.load
call $print_f64
call $print_newline
```

## Limitations

| Feature | Status |
|---------|--------|
| Single-field and multi-field instances | Supported |
| `self.attr` read and write inside methods | Supported |
| Compound `self.attr +=` / `-=` / `*=` / `/=` | Supported |
| External `obj.attr` read (statically known class) | Supported |
| Instance method calls (statically tracked object) | Supported |
| Multiple independent instances | Supported |
| Inheritance / method resolution from base class | Not supported (methods of base class not inherited in WAT) |
| Dynamic dispatch / polymorphism | Not supported |
| `__str__`, `__repr__`, `__del__` and other dunder methods | Not lowered; fall to stubs if called dynamically |
| `@staticmethod`, `@classmethod`, `@property` decorators | Decorator metadata ignored; methods lowered as regular WAT functions |
| `super()` calls | Not supported in WAT lowering |
| Nested classes | Not supported |
| Closures over instance state | Not supported |

## Detection Utility

`has_stub_calls(wat_text)` (in `wat_generator.py`) returns `True` if the
generated WAT contains `";; unsupported call:"` markers, indicating at least
one call could not be fully lowered. Use this in tests to distinguish
fully-compiled WAT from WAT with Python-only stubs.

## Example End-to-End

```python
class Counter:
    def __init__(self, start):
        self.value = start

    def increment(self):
        self.value = self.value + 1

    def get(self):
        return self.value

let c = Counter(10)
c.increment()
print(c.get())   # prints 11
```

Generated WAT (abbreviated):

```wat
(module
  (import "env" "print_f64" (func $print_f64 (param f64)))
  ...
  (memory (export "memory") 1)
  (global $__heap_ptr (mut i32) (i32.const 64))

  (func $Counter____init__ (export "Counter____init__")
    (param $self f64)
    (param $start f64)
    (result f64)
    ;; self.value = start
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    local.get $start
    f64.store
    f64.const 0  ;; implicit return
  )

  (func $Counter__increment (export "Counter__increment")
    (param $self f64)
    (result f64)
    (local $__attr_val_1 f64)
    ;; self.value = self.value + 1
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    f64.load
    f64.const 1.0
    f64.add
    local.set $__attr_val_1
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    local.get $__attr_val_1
    f64.store
    f64.const 0
  )

  (func $Counter__get (export "Counter__get")
    (param $self f64)
    (result f64)
    ;; return self.value
    local.get $self
    i32.trunc_f64_u
    i32.const 0
    i32.add
    f64.load
    return
    f64.const 0
  )

  (func $__main (export "__main")
    (local $c f64)
    ;; let c = Counter(10)
    ;; alloc Counter (8 bytes)
    global.get $__heap_ptr
    i32.const 8
    i32.add
    global.set $__heap_ptr
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u
    f64.const 10.0
    call $Counter____init__
    drop
    global.get $__heap_ptr
    i32.const 8
    i32.sub
    f64.convert_i32_u
    local.set $c
    ;; c.increment()
    local.get $c
    call $Counter__increment
    drop
    ;; print(c.get())
    local.get $c
    call $Counter__get
    call $print_f64
    call $print_newline
  )
)
```

## Related

- Source: [multilingualprogramming/codegen/wat_generator.py](../multilingualprogramming/codegen/wat_generator.py)
- Tests: [tests/wat_generator_test.py](../tests/wat_generator_test.py) — `WATOopObjectModelTestSuite`, `WATClassWasmExecutionTestSuite`
- Architecture overview: [WASM_ARCHITECTURE_OVERVIEW.md](WASM_ARCHITECTURE_OVERVIEW.md)
