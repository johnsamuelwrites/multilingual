# Python Compatibility Matrix

This matrix defines the current compatibility baseline for `multilingual`.

Baseline source of truth:
- `examples/complete_features_en.ml`

## Scope Statement

`multilingual` is currently compatible with a broad subset of Python-style
language constructs, but it is **not** full drop-in compatibility for all
existing Python code and all third-party ecosystems.

## Supported Baseline (Current)

The following constructs are exercised in the baseline example and considered
available in the current implementation.

| Area | Status | Notes / Example |
|---|---|---|
| Imports | Supported | `import math`, `from math import sqrt as root_fn` |
| Variable declarations | Supported | `let acc_total = 0` |
| Arithmetic and expressions | Supported | numeric and boolean expressions |
| Lists | Supported | list literals and iteration |
| `for` loops | Supported | `for item in items:` |
| `while` loops | Supported | `while condition:` |
| Conditionals | Supported | `if` / `else` |
| Functions | Supported | `def ...`, `return` |
| List comprehensions | Supported | including `if` filter clause |
| Boolean logic | Supported | `True`, `False`, `and`, `not` |
| Assertions | Supported | `assert expr` |
| Exceptions | Supported | `try` / `except` / `finally` |
| Classes | Supported | class definition, methods, attributes |
| Method calls | Supported | instance method invocation |
| Built-in calls | Supported | e.g. `len`, `int`, `print` |
| Identity checks | Supported | `is` with `None` |

## Also Supported (Documented Elsewhere)

These features are documented and tested in project docs/examples, even if they
are not all present in `complete_features_en.ml`.

- Type annotations
- Set literals
- Multiple context managers
- Dictionary unpacking
- Hex/octal/binary literals
- Scientific notation
- Async constructs (`async def`, `await`, `async for`, `async with`)
- Walrus operator (`:=`)

See:
- `README.md` ("Additional syntax now supported")
- `docs/README.md` ("Language Features")

## Not Guaranteed Yet

The following are not claimed as universally compatible at this stage:

- Arbitrary Python projects running unchanged
- Full behavioral parity with all CPython edge cases
- Full third-party package/runtime ecosystem compatibility
- Every advanced metaprogramming/introspection scenario

## Recommendation

When evaluating compatibility for a real codebase:

1. Start from this matrix.
2. Run focused smoke tests with `multilingual run ...`.
3. Track gaps as concrete syntax/runtime items in tests and docs.
