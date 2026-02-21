# Python Compatibility Matrix

This matrix defines the current compatibility baseline for `multilingual`.

Baseline source of truth:
- `examples/complete_features_en.ml`

Target runtime:
- CPython `3.12.x`

## Scope Statement

`multilingual` supports a broad Python 3.12-aligned syntax/runtime subset, but
it is **not** full drop-in compatibility for every existing Python project and
third-party ecosystem.

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
- `docs/reference.md` ("Language Features")

## Keyword and Built-in Coverage Status

| Coverage area | Status | Notes |
|---|---|---|
| Python keywords (3.12) | Complete in keyword registry | Includes full keyword surface such as `del`, `nonlocal`, `match`, `case`, async keywords, etc. |
| Localized built-in aliases | Partial by design | `resources/usm/builtins_aliases.json` currently provides a curated set (12 concepts), not all CPython built-ins. |
| Canonical Python built-in names | Fully available | Canonical names (for example `len`, `print`, `super`) remain usable across languages via runtime namespace. |

## Not Guaranteed Yet

The following are not claimed as universally compatible at this stage:

- Arbitrary Python projects running unchanged
- Full behavioral parity with all CPython edge cases
- Full third-party package/runtime ecosystem compatibility
- Every advanced metaprogramming/introspection scenario
- Complete localization aliases for every CPython built-in function/type

## Recommendation

When evaluating compatibility for a real codebase:

1. Start from this matrix.
2. Run focused smoke tests with `multilingual run ...`.
3. Track gaps as concrete syntax/runtime items in tests and docs.
