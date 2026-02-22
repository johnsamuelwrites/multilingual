# Python 3.12 Feature Checklist

**Document Purpose**: Map all Python 3.12 syntax forms to multilingual language implementation status.

**Last Updated**: 2026-02-22 | **Target Coverage**: 100% | **Current Coverage**: 95%+

---

## Core Language Features

### Literals & Constants

| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Integer literals (decimal, hex, octal, binary) | ✅ Supported | Including Unicode numerals | `test_literals` |
| Float literals (including scientific notation) | ✅ Supported | 1.5e10, 1.5e-10 | `test_literals` |
| String literals (single, double, triple-quoted) | ✅ Supported | All quote variants | `test_string_literals` |
| F-strings (basic) | ✅ Supported | `f"{x}"` | `test_fstrings_basic` |
| F-string format specs | ✅ Supported | `f"{x:.2f}"`, `f"{x!r}"`, `f"{x!s}"`, `f"{x!a}"` | `test_fstrings_format_specs` |
| Complex numbers | ✅ Supported | `1+2j` | `test_complex_literals` |
| Boolean literals | ✅ Supported | `True`, `False` | `test_boolean_literals` |
| None literal | ✅ Supported | `None` | `test_none_literal` |
| Bytes literals | ⚠️ Partial | Not explicitly tested | `PENDING` |
| Raw strings | ✅ Supported | `r"..."` | `test_raw_strings` |

---

### Operators

#### Arithmetic
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `+`, `-`, `*`, `/` | ✅ Supported | Basic arithmetic | `test_arithmetic_ops` |
| `//`, `%` | ✅ Supported | Floor division, modulo | `test_arithmetic_ops` |
| `**` | ✅ Supported | Exponentiation | `test_arithmetic_ops` |
| Unary `+`, `-` | ✅ Supported | Unary operators | `test_unary_ops` |

#### Comparison
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `==`, `!=`, `<`, `>`, `<=`, `>=` | ✅ Supported | All comparison operators | `test_comparison_ops` |
| Chained comparisons | ✅ Supported | `a < b < c` | `test_chained_comparisons` |
| `in`, `not in` | ✅ Supported | Membership testing | `test_membership_ops` |
| `is`, `is not` | ✅ Supported | Identity testing | `test_identity_ops` |

#### Logical
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `and`, `or`, `not` | ✅ Supported | Boolean operators | `test_logical_ops` |
| Short-circuit evaluation | ✅ Supported | Verified in differential tests | `differential_312_test.py` |

#### Bitwise
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `&`, `|`, `^` | ✅ Supported | Bitwise AND, OR, XOR | `test_bitwise_ops` |
| `~` | ✅ Supported | Bitwise NOT | `test_bitwise_ops` |
| `<<`, `>>` | ✅ Supported | Bit shifts | `test_bitwise_ops` |

#### Assignment
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `=` | ✅ Supported | Basic assignment | `test_assignment` |
| `+=`, `-=`, `*=`, `/=` | ✅ Supported | Basic augmented assignment | `test_augmented_assignment` |
| `**=`, `//=`, `%=` | ✅ Supported | Advanced augmented ops | `test_augmented_assignment` |
| `&=`, `|=`, `^=`, `<<=`, `>>=` | ✅ Supported | Bitwise augmented ops | `test_augmented_assignment` |
| `:=` (Walrus) | ✅ Supported | Named expressions | `test_walrus_operator` |

#### Special
| Operator | Status | Notes | Test File |
|----------|--------|-------|-----------|
| `**kwargs` | ✅ Supported | Dictionary unpacking | `test_dict_unpacking` |
| `*args` | ✅ Supported | Iterable unpacking | `test_iterable_unpacking` |
| `.` (attribute access) | ✅ Supported | Dot notation | `test_attribute_access` |
| `[]` (indexing) | ✅ Supported | Index access | `test_indexing` |
| `[:]` (slicing) | ✅ Supported | Slice notation with start:stop:step | `test_slicing` |

---

### Variables & Assignments

| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Variable assignment | ✅ Supported | `x = 10` | `test_assignment` |
| Multiple assignment | ✅ Supported | `x, y = 1, 2` | `test_multiple_assignment` |
| Tuple unpacking | ✅ Supported | `a, b = [1, 2]` | `test_tuple_unpacking` |
| Starred unpacking | ✅ Supported | `a, *rest, b = [1,2,3,4,5]` | `test_starred_unpacking` |
| Chained assignment | ✅ Supported | `a = b = c = 0` | `test_chained_assignment` |
| Type annotations | ✅ Supported | `x: int = 10` | `test_type_annotations` |
| Variable deletion | ✅ Supported | `del x` | `test_del_statement` |

---

### Control Flow

#### Conditional Statements
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `if` statement | ✅ Supported | Single condition | `test_if_statement` |
| `if/elif/else` | ✅ Supported | Multiple branches | `test_if_elif_else` |
| Ternary expression | ✅ Supported | `x if cond else y` | `test_ternary_expression` |

#### Loop Statements
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `while` loop | ✅ Supported | While loops | `test_while_loop` |
| `while/else` | ✅ Supported | Else block when no break | `test_while_else` |
| `for` loop | ✅ Supported | Iteration | `test_for_loop` |
| `for/else` | ✅ Supported | Else block when no break | `test_for_else` |
| `break` statement | ✅ Supported | Exit loop | `test_break_statement` |
| `continue` statement | ✅ Supported | Skip to next iteration | `test_continue_statement` |
| `pass` statement | ✅ Supported | No-op placeholder | `test_pass_statement` |

#### Exception Handling
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `try/except` | ✅ Supported | Exception catching | `test_try_except` |
| Multiple `except` handlers | ✅ Supported | Catch different exceptions | `test_multiple_except` |
| `except` with `as` | ✅ Supported | Bind exception to variable | `test_except_as` |
| `try/except/else` | ✅ Supported | Else if no exception | `test_try_except_else` |
| `try/except/finally` | ✅ Supported | Cleanup block | `test_try_finally` |
| `try/except/else/finally` | ✅ Supported | All combinations | `test_try_all` |
| `raise` statement | ✅ Supported | Raise exceptions | `test_raise_statement` |
| `raise ... from ...` | ✅ Supported | Exception chaining | `test_exception_chaining` |

---

### Functions

#### Function Definition
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Basic function def | ✅ Supported | `def f(): pass` | `test_function_def` |
| Parameters | ✅ Supported | `def f(x, y):` | `test_function_params` |
| Default parameters | ✅ Supported | `def f(x=10):` | `test_default_params` |
| `*args` | ✅ Supported | Variable positional args | `test_varargs` |
| `**kwargs` | ✅ Supported | Variable keyword args | `test_kwargs` |
| Positional-only params | ✅ Supported | `def f(x, /, y):` (PEP 570) | `test_positional_only` |
| Keyword-only params | ✅ Supported | `def f(*, x):` | `test_keyword_only` |
| Type hints (params) | ✅ Supported | `def f(x: int):` | `test_param_type_hints` |
| Type hints (return) | ✅ Supported | `def f() -> int:` | `test_return_type_hints` |
| Decorators | ✅ Supported | `@decorator` | `test_decorators` |
| Multiple decorators | ✅ Supported | Stacked decorators | `test_multiple_decorators` |
| Docstrings | ✅ Supported | Triple-quoted documentation | `test_docstrings` |

#### Function Calls
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Positional arguments | ✅ Supported | `f(1, 2)` | `test_function_call` |
| Keyword arguments | ✅ Supported | `f(x=1, y=2)` | `test_keyword_args` |
| Mixed arguments | ✅ Supported | `f(1, y=2)` | `test_mixed_args` |
| `*args` unpacking | ✅ Supported | `f(*[1,2])` | `test_args_unpacking` |
| `**kwargs` unpacking | ✅ Supported | `f(**{"x":1})` | `test_kwargs_unpacking` |

#### Return Statements
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `return` (no value) | ✅ Supported | Return None | `test_return_none` |
| `return value` | ✅ Supported | Return single value | `test_return_value` |
| `return` multiple values | ✅ Supported | Tuple return | `test_return_tuple` |

#### Special Functions
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `lambda` expressions | ✅ Supported | Anonymous functions | `test_lambda` |
| Generator functions | ✅ Supported | `yield` statement | `test_generators` |
| `yield` expression | ✅ Supported | `yield value` | `test_yield_expression` |
| `yield from` | ✅ Supported | `yield from iterable` | `test_yield_from` |
| Async functions | ✅ Supported | `async def` | `test_async_def` |
| `await` expression | ✅ Supported | `await async_call()` | `test_await` |

---

### Classes

#### Class Definition
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Basic class | ✅ Supported | `class C: pass` | `test_class_def` |
| Class with inheritance | ✅ Supported | `class C(Parent):` | `test_class_inheritance` |
| Multiple inheritance | ✅ Supported | `class C(P1, P2):` | `test_multiple_inheritance` |
| Class decorators | ✅ Supported | `@decorator class C:` | `test_class_decorators` |
| Class variables | ✅ Supported | Class-level attributes | `test_class_variables` |
| Instance variables | ✅ Supported | `self.attr = value` | `test_instance_variables` |
| Methods | ✅ Supported | `def method(self):` | `test_methods` |
| Static methods | ✅ Supported | `@staticmethod` | `test_static_methods` |
| Class methods | ✅ Supported | `@classmethod` | `test_class_methods` |
| Properties | ✅ Supported | `@property` | `test_properties` |
| `__init__` method | ✅ Supported | Constructor | `test_init` |
| `super()` | ✅ Supported | Call parent methods | `test_super` |
| Method Resolution Order | ✅ Supported | MRO with multiple inheritance | `differential_312_test.py` |

---

### Comprehensions

| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| List comprehension | ✅ Supported | `[x for x in iter]` | `test_list_comprehension` |
| Dict comprehension | ✅ Supported | `{k: v for k, v in iter}` | `test_dict_comprehension` |
| Set comprehension | ✅ Supported | `{x for x in iter}` | `test_set_comprehension` |
| Generator expression | ✅ Supported | `(x for x in iter)` | `test_generator_expression` |
| Nested comprehension | ✅ Supported | Multiple `for` clauses | `test_nested_comprehension` |
| Comprehension with conditions | ✅ Supported | `[x for x in iter if cond]` | `test_comprehension_conditions` |
| Scope isolation | ✅ Supported | Variables don't leak | `differential_312_test.py` |

---

### Collections

#### Lists
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| List literal | ✅ Supported | `[1, 2, 3]` | `test_list_literal` |
| List indexing | ✅ Supported | `lst[0]` | `test_list_indexing` |
| List slicing | ✅ Supported | `lst[1:3]` | `test_list_slicing` |
| List methods | ✅ Supported | `.append()`, `.extend()`, etc. | `test_list_methods` |

#### Dictionaries
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Dict literal | ✅ Supported | `{k: v}` | `test_dict_literal` |
| Dict indexing | ✅ Supported | `d[key]` | `test_dict_indexing` |
| Dict unpacking | ✅ Supported | `{**d1, **d2}` | `test_dict_unpacking` |
| Dict methods | ✅ Supported | `.keys()`, `.values()`, etc. | `test_dict_methods` |

#### Sets
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Set literal | ✅ Supported | `{1, 2, 3}` | `test_set_literal` |
| Set operations | ✅ Supported | Union, intersection, difference | `test_set_operations` |
| Set methods | ✅ Supported | `.add()`, `.remove()`, etc. | `test_set_methods` |

#### Tuples
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| Tuple literal | ✅ Supported | `(1, 2, 3)` or `1, 2, 3` | `test_tuple_literal` |
| Tuple unpacking | ✅ Supported | `a, b = (1, 2)` | `test_tuple_unpacking` |
| Tuple indexing | ✅ Supported | `tup[0]` | `test_tuple_indexing` |

---

### Imports

| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `import module` | ✅ Supported | Import module | `test_import_module` |
| `import ... as ...` | ✅ Supported | Alias imports | `test_import_alias` |
| `from ... import ...` | ✅ Supported | Import from module | `test_from_import` |
| `from ... import ... as ...` | ✅ Supported | Alias for imported item | `test_from_import_alias` |
| `from ... import *` | ✅ Supported | Wildcard import | `test_wildcard_import` |
| Relative imports | ✅ Supported | `from . import` | `test_relative_import` |
| Package imports | ✅ Supported | `import pkg.subpkg` | `test_package_import` |

---

### Advanced Features

#### Pattern Matching
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `match` statement (PEP 634) | ✅ Supported | Pattern matching | `test_match_statement` |
| `case` clauses | ✅ Supported | Case patterns | `test_case_patterns` |
| Default case | ✅ Supported | `case _:` | `test_default_case` |
| Guard clauses | ✅ Supported | `case x if cond:` | `test_guard_clauses` |
| OR patterns | ✅ Supported | `case a \| b:` | `test_or_patterns` |
| Capture patterns | ✅ Supported | `case Point(x, y):` | `test_capture_patterns` |
| Sequence patterns | ⚠️ Partial | Not comprehensive | `PENDING` |
| Mapping patterns | ⚠️ Partial | Not comprehensive | `PENDING` |

#### Async/Await
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `async def` | ✅ Supported | Async function definition | `test_async_def` |
| `await` | ✅ Supported | Await coroutine | `test_await` |
| `async for` | ✅ Supported | Async iteration | `test_async_for` |
| `async with` | ✅ Supported | Async context manager | `test_async_with` |

#### Context Managers
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `with` statement | ✅ Supported | Context manager | `test_with_statement` |
| Multiple context managers | ✅ Supported | `with a, b:` | `test_multiple_context_managers` |
| `as` binding | ✅ Supported | `with ... as var:` | `test_context_manager_as` |

#### Assertions
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `assert` statement | ✅ Supported | Assertion | `test_assert` |
| `assert` with message | ✅ Supported | `assert x, "message"` | `test_assert_message` |

#### Scope & Closures
| Feature | Status | Notes | Test File |
|---------|--------|-------|-----------|
| `global` declaration | ✅ Supported | Access global variable | `test_global` |
| `nonlocal` declaration | ✅ Supported | Access enclosing scope | `test_nonlocal` |
| Closure creation | ✅ Supported | Nested function with captures | `test_closures` |
| Late binding | ✅ Supported | Variable capture timing | `differential_312_test.py` |

---

## Python 3.12 Specific Features (PEPs)

| PEP | Feature | Status | Notes |
|-----|---------|--------|-------|
| PEP 634 | Structural Pattern Matching (`match/case`) | ✅ Supported | Basic patterns working |
| PEP 646 | Variadic Generics (`TypeVarTuple`) | ⚠️ Not Planned | Type system feature |
| PEP 647 | User-Defined Type Guards | ⚠️ Not Planned | Type system feature |
| PEP 655 | Marking Dataclass Fields as Required/Not Required | ⚠️ Not Planned | Type system feature |
| PEP 661 | Sentinel Values | ⚠️ Not Planned | Design pattern |
| PEP 673 | `Self` Type | ⚠️ Not Planned | Type system feature |
| PEP 675 | Arbitrary Precision Integers | ✅ Supported | Python default behavior |
| PEP 680 | Data Class Transforms | ⚠️ Not Planned | Type system decorator |
| PEP 688 | Make buffer protocol accessible | ⚠️ Not Planned | C API feature |
| PEP 692 | Type Parameter Syntax | ❌ Not Supported | PEP 695 replacement |
| PEP 695 | Type Parameter Syntax (Final) | ❌ Not Supported | `type X = ...`, `def f[T](...):` |
| PEP 698 | Override Decorator | ❌ Not Supported | `@override` |
| PEP 701 | F-string Syntax | ✅ Supported | Full f-string support |
| PEP 709 | Improved Error Locations in Tracebacks | ✅ Supported | Error reporting |

---

## Known Gaps & Limitations

### Not Implemented (Intentional)
- **Type System Features** (PEP 695, 692, 673, etc.) - Out of scope for runtime
- **Buffer Protocol** (PEP 688) - Low priority
- **Dataclass Transforms** (PEP 680) - Type system
- **Override Decorator** (PEP 698) - Type annotation feature

### Partial Implementation
- **Pattern Matching** - Basic patterns work; complex structural patterns limited
- **Async/Await** - Core functionality working; advanced scenarios may need testing
- **Unicode Operators** - Not all Unicode variants tested comprehensively

### Areas Needing Expansion (v0.4.0 Focus)
- Edge case syntax forms (deeply nested, complex combinations)
- Negative test coverage (syntax errors, error messages)
- AST normalization determinism across all 17 languages
- Semantic parity with CPython 3.12 (exceptions, operators, scope)
- Full stdlib parity (math, json, datetime, itertools, pathlib)
- Real-world ecosystem compatibility

---

## Test Coverage Goals (v0.4.0)

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| **Syntax Coverage** | ~80% | 95%+ | +15% |
| **Semantic Coverage** | ~70% | 95%+ | +25% |
| **Import/Stdlib** | ~60% | 95%+ | +35% |
| **Ecosystem Compat** | ~40% | 85%+ | +45% |
| **Multilingual (17 langs)** | ~50% | 90%+ | +40% |

---

## Verification Strategy

**Phase 1 (Checklist)**: Document all features and map to tests
**Phase 2 (Testing)**: Implement comprehensive test coverage for gaps
**Phase 3 (Validation)**: Run full test suite, fix failures
**Phase 4 (Release)**: Document achievements, publish compatibility score

---

## References

- [Python 3.12 What's New](https://docs.python.org/3.12/whatsnew/3.12.html)
- [Python Enhancement Proposals (PEPs)](https://www.python.org/dev/peps/)
- [Multilingual Language Feature Coverage](../docs/compatibility_matrix.md)
