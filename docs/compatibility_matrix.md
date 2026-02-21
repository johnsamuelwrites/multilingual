# Python Compatibility Matrix

This matrix defines the current compatibility baseline for `multilingual`.

Baseline source of truth:
- `examples/complete_features_en.ml`
- `tests/` (858 tests across 78 test suites)

Target runtime:
- CPython `3.12.x`

## Scope Statement

`multilingual` supports a broad Python 3.12-aligned syntax/runtime subset, but
it is **not** full drop-in compatibility for every existing Python project and
third-party ecosystem.

## Supported Languages

17 natural languages are supported with localized keywords and error messages:

| Language | Code | Example keyword (`if`) |
|---|---|---|
| English | `en` | `if` |
| French | `fr` | `si` |
| Spanish | `es` | `si` |
| German | `de` | `wenn` |
| Hindi | `hi` | `अगर` |
| Arabic | `ar` | `إذا` |
| Bengali | `bn` | `যদি` |
| Tamil | `ta` | `என்றால்` |
| Chinese | `zh` | `如果` |
| Japanese | `ja` | `もし` |
| Italian | `it` | `se` |
| Portuguese | `pt` | `se` |
| Polish | `pl` | `jezeli` |
| Dutch | `nl` | `als` |
| Swedish | `sv` | `om` |
| Danish | `da` | `hvis` |
| Finnish | `fi` | `jos` |

## Supported Baseline (Current)

### Core Constructs

| Area | Status | Notes / Example |
|---|---|---|
| Imports | Supported | `import math`, `from math import sqrt as root_fn` |
| Wildcard imports | Supported | `from os import *` |
| Variable declarations | Supported | `let x = 0`, `const PI = 3.14` |
| Type annotations | Supported | `let x: int = 0`, `def f(x: int) -> str:` |
| Arithmetic and expressions | Supported | `+`, `-`, `*`, `/`, `//`, `%`, `**`, bitwise ops |
| Augmented assignment | Supported | `+=`, `-=`, `*=`, `/=`, `**=`, `//=`, `%=`, `&=`, `\|=`, `^=`, `<<=`, `>>=` |
| Chained assignment | Supported | `a = b = c = 0` |
| Starred unpacking | Supported | `a, *rest = [1, 2, 3]`, `first, *mid, last = items` |

### Data Structures

| Area | Status | Notes / Example |
|---|---|---|
| Lists | Supported | literals, iteration, indexing, slicing |
| Dictionaries | Supported | literals, comprehensions, unpacking (`**d`) |
| Sets | Supported | literals, comprehensions |
| Tuples | Supported | literals, unpacking |
| Strings | Supported | single/double quotes, triple-quoted, f-strings |
| F-string format specs | Supported | `f"{x:.2f}"`, `f"{x!r}"`, `f"{x!s}"`, `f"{x!a}"` |
| Hex/octal/binary literals | Supported | `0xFF`, `0o77`, `0b1010` |
| Scientific notation | Supported | `1.5e10` |

### Control Flow

| Area | Status | Notes / Example |
|---|---|---|
| `if` / `elif` / `else` | Supported | full conditional chains |
| `while` loops | Supported | `while condition:` |
| `while` / `else` | Supported | else block runs when loop completes without `break` |
| `for` loops | Supported | `for item in items:`, tuple unpacking targets |
| `for` / `else` | Supported | else block runs when loop completes without `break` |
| `break` / `continue` | Supported | loop control |
| `pass` | Supported | no-op placeholder |
| `match` / `case` | Supported | structural pattern matching |
| `case` guard clauses | Supported | `case n if n > 0:` |
| `case` OR patterns | Supported | `case 1 \| 2 \| 3:` |
| `case` AS bindings | Supported | `case pattern as name:` |
| `case _` (default) | Supported | wildcard/default case |
| Ternary expressions | Supported | `x if cond else y` |

### Functions and Classes

| Area | Status | Notes / Example |
|---|---|---|
| Function definitions | Supported | `def f(x):`, with defaults, `*args`, `**kwargs` |
| Positional-only params | Supported | `def f(a, b, /, c):` |
| Keyword-only params | Supported | `def f(a, *, b):` |
| Return annotations | Supported | `def f() -> int:` |
| Decorators | Supported | `@decorator` on functions and classes |
| Lambda expressions | Supported | `lambda x: x + 1` |
| `yield` / `yield from` | Supported | generator functions and delegation |
| `async def` / `await` | Supported | async functions, `async for`, `async with` |
| Class definitions | Supported | inheritance, methods, attributes |
| Walrus operator | Supported | `(x := expr)` |

### Error Handling

| Area | Status | Notes / Example |
|---|---|---|
| `try` / `except` / `else` / `finally` | Supported | full exception handling |
| `raise` | Supported | bare `raise`, `raise ValueError("msg")` |
| `raise` ... `from` | Supported | exception chaining: `raise X from Y` |
| `assert` | Supported | `assert expr`, `assert expr, msg` |

### Scope and Variables

| Area | Status | Notes / Example |
|---|---|---|
| `global` | Supported | declares global scope; defines name in local scope |
| `nonlocal` | Supported | declares enclosing scope; defines name in local scope |
| `del` | Supported | `del variable` |

### Comprehensions and Generators

| Area | Status | Notes / Example |
|---|---|---|
| List comprehensions | Supported | `[x for x in items if cond]`, nested clauses |
| Dict comprehensions | Supported | `{k: v for k, v in items}` |
| Set comprehensions | Supported | `{x for x in items if cond}`, nested clauses |
| Generator expressions | Supported | `(x for x in items)` |

### Context Managers

| Area | Status | Notes / Example |
|---|---|---|
| `with` statement | Supported | `with open(f) as h:` |
| Multiple contexts | Supported | `with A() as a, B() as b:` |
| `async with` | Supported | async context managers |

## Keyword and Built-in Coverage Status

| Coverage area | Status | Notes |
|---|---|---|
| Python keywords (3.12) | Complete | 51 concept IDs across 7 categories in keyword registry |
| Universal built-in functions | 70+ available | `len`, `range`, `abs`, `pow`, `divmod`, `complex`, `format`, `ascii`, `compile`, `eval`, `exec`, `globals`, `locals`, `issubclass`, `delattr`, `slice`, `aiter`, `anext`, and more |
| Exception types | 45+ available | `BaseException`, `KeyboardInterrupt`, `ValueError`, `TypeError`, `KeyError`, `ModuleNotFoundError`, `ExceptionGroup`, `BaseExceptionGroup`, all warning subclasses, and more |
| Special values | Available | `True`, `False`, `None`, `Ellipsis`, `NotImplemented` |
| Localized built-in aliases | 41 concepts | `range`, `len`, `sum`, `abs`, `min`, `max`, `sorted`, `reversed`, `enumerate`, `map`, `filter`, `isinstance`, `type`, `input`, `any`, `all`, `round`, `pow`, `hash`, `callable`, `iter`, `next`, `chr`, `ord`, `repr`, `dir`, `format`, `frozenset`, `bytes`, `divmod`, `issubclass`, `hasattr`, `getattr`, `setattr`, `delattr`, and more — each with aliases across all 16 non-English languages |
| Canonical Python built-in names | Fully available | Canonical names (e.g., `len`, `print`, `super`) remain usable across all languages via runtime namespace |

## Surface Syntax Normalization

SOV (Subject-Object-Verb) and RTL (Right-to-Left) languages can use natural
word order. The surface normalizer rewrites tokens to canonical order before
parsing.

| Statement | Languages with normalization | Example (Japanese) |
|---|---|---|
| `for` loop | ja, ar, es, pt, hi, bn, ta | iterable-first: `範囲(6) 内の 各 i に対して:` |
| `while` loop | ja, ar, hi, bn, ta | condition-first: `condition 間:` |
| `if` statement | ja, ar, hi, bn, ta | condition-first: `condition もし:` |
| `with` statement | ja, ar, hi, bn, ta | expression-first: `expression 付き:` |

## Test Coverage

858 tests across 78 test suites covering:

| Test area | Suite count | Description |
|---|---|---|
| Numerals and dates | 8 | Multilingual numerals, Unicode, Roman, complex, fractions, datetime |
| Lexer | 2 | Tokenization and lexer behavior |
| Parser | 5 | Expressions, statements, compounds, multilingual, errors |
| Semantic analysis | 6 | Scopes, constants, control flow, definitions, multilingual errors, symbol table |
| Code generation | 4 | Expressions, statements, compounds, multilingual |
| Execution | 4 | Basic, multilingual, transpile, errors |
| Critical features | 8 | Triple-quoted strings, slices, parameters, tuples, comprehensions, decorators, f-strings |
| Language completeness and CLI features | 8 | Augmented assignment, membership/identity, ternary, assert, chained assignment, CLI, REPL |
| Advanced language features | 23 | Loop else, yield/raise from, set comprehensions, parameter separators, f-string formatting, match guards/OR/AS, global/nonlocal, builtins, exceptions, surface normalization, data quality, extended builtins, alias resolution, alias execution, starred unpacking, integration, multilingual |
| Infrastructure | 10 | Keyword registry, AST nodes, AST printer, error messages, runtime builtins, REPL |

## Not Guaranteed Yet

The following are not claimed as universally compatible at this stage:

- Arbitrary Python projects running unchanged
- Full behavioral parity with all CPython edge cases
- Full third-party package/runtime ecosystem compatibility
- Every advanced metaprogramming/introspection scenario
- Complete localization aliases for every CPython built-in function/type (41 of 70+ have aliases)
- Starred unpacking in deeply nested expression contexts
- Complex decorator chains with arguments

## Recommendation

When evaluating compatibility for a real codebase:

1. Start from this matrix.
2. Run focused smoke tests with `multilingual run ...`.
3. Track gaps as concrete syntax/runtime items in tests and docs.
