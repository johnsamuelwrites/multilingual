#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# pylint: disable=duplicate-code

"""Differential compatibility checks against CPython 3.12 behavior."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.imports import (
    disable_multilingual_imports,
    enable_multilingual_imports,
)


def _run_python_source(source):
    """Execute Python source with stdout capture."""
    stdout = io.StringIO()
    try:
        with redirect_stdout(stdout):
            exec(source, {})  # pylint: disable=exec-used
    except Exception as exc:  # pragma: no cover - exercised by tests
        return {
            "success": False,
            "output": stdout.getvalue(),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    return {
        "success": True,
        "output": stdout.getvalue(),
        "error_type": None,
        "error_message": None,
    }


def _run_multilingual_source(source, check_semantics=True):
    """Execute multilingual source in English mode with stdout capture."""
    result = ProgramExecutor(
        language="en",
        check_semantics=check_semantics,
    ).execute(source)
    error_type = None
    error_message = None
    if result.errors:
        parts = result.errors[0].split(":", 1)
        error_type = parts[0].strip()
        if len(parts) > 1:
            error_message = parts[1].strip()
    return {
        "success": result.success,
        "output": result.output,
        "error_type": error_type,
        "error_message": error_message,
    }


class DifferentialCompatibility312TestSuite(unittest.TestCase):
    """Compare multilingual execution against equivalent CPython programs."""

    def _assert_equivalent(
        self,
        *,
        multilingual_source,
        python_source,
        check_semantics=True,
    ):
        py = _run_python_source(python_source)
        ml = _run_multilingual_source(
            multilingual_source,
            check_semantics=check_semantics,
        )
        self.assertEqual(ml["success"], py["success"])
        self.assertEqual(ml["output"], py["output"])
        if not py["success"]:
            self.assertEqual(ml["error_type"], py["error_type"])

    def test_control_flow_class_and_import_parity(self):
        multilingual_source = """\
import math
from math import sqrt as root_fn

let acc_total = 0
let numbers = [1, 2, 3, 4]

for num_item in numbers:
    acc_total = acc_total + num_item

let idx_counter = 0
while idx_counter < 2:
    idx_counter = idx_counter + 1
    acc_total = acc_total + idx_counter

def adjust_val(value):
    if value > 5:
        return value - 1
    else:
        return value + 1

let adjusted = [adjust_val(v_item) for v_item in numbers if v_item > 2]
let flag_ok = True and not False
assert flag_ok

try:
    let root_value = root_fn(16)
except Exception as handled_error:
    let root_value = 0
finally:
    acc_total = acc_total + int(root_value)

class CounterBox:
    def __init__(self, start_value):
        self.value = start_value

    def bump(self):
        self.value = self.value + 1
        return self.value

let box = CounterBox(acc_total)
let bumped_value = box.bump()

print(acc_total)
print(len(adjusted))
print(bumped_value)
print(acc_total is None)
"""
        python_source = """\
import math
from math import sqrt as root_fn

acc_total = 0
numbers = [1, 2, 3, 4]

for num_item in numbers:
    acc_total = acc_total + num_item

idx_counter = 0
while idx_counter < 2:
    idx_counter = idx_counter + 1
    acc_total = acc_total + idx_counter

def adjust_val(value):
    if value > 5:
        return value - 1
    else:
        return value + 1

adjusted = [adjust_val(v_item) for v_item in numbers if v_item > 2]
flag_ok = True and not False
assert flag_ok

try:
    root_value = root_fn(16)
except Exception as handled_error:
    root_value = 0
finally:
    acc_total = acc_total + int(root_value)

class CounterBox:
    def __init__(self, start_value):
        self.value = start_value

    def bump(self):
        self.value = self.value + 1
        return self.value

box = CounterBox(acc_total)
bumped_value = box.bump()

print(acc_total)
print(len(adjusted))
print(bumped_value)
print(acc_total is None)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_try_except_finally_runtime_path_parity(self):
        multilingual_source = """\
let value = 0
try:
    value = 1 / 0
except ZeroDivisionError as err:
    print("caught")
finally:
    print("finally")
"""
        python_source = """\
value = 0
try:
    value = 1 / 0
except ZeroDivisionError as err:
    print("caught")
finally:
    print("finally")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_runtime_exception_type_parity(self):
        multilingual_source = """\
let x = 1 / 0
"""
        python_source = """\
x = 1 / 0
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
            check_semantics=False,
        )

    def test_async_execution_parity(self):
        multilingual_source = """\
import asyncio

class AsyncCtx:
    async def __aenter__(self):
        return 10
    async def __aexit__(self, exc_type, exc, tb):
        return False

async def agen():
    for i in range(4):
        yield i

async def main():
    let total = 0
    async with AsyncCtx() as base:
        async for i in agen():
            total = total + i + base
    return total

print(asyncio.run(main()))
"""
        python_source = """\
import asyncio

class AsyncCtx:
    async def __aenter__(self):
        return 10
    async def __aexit__(self, exc_type, exc, tb):
        return False

async def agen():
    for i in range(4):
        yield i

async def main():
    total = 0
    async with AsyncCtx() as base:
        async for i in agen():
            total = total + i + base
    return total

print(asyncio.run(main()))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_import_package_resolution_parity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg_dir = root / "pkg"
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / "__init__.ml").write_text(
                "let default_value = 5\n",
                encoding="utf-8",
            )
            (pkg_dir / "tools.ml").write_text(
                "def double(x):\n"
                "    return x * 2\n",
                encoding="utf-8",
            )

            source = """\
from pkg import default_value
from pkg import tools
print(tools.double(default_value))
"""

            original_path = list(sys.path)
            sys.path.insert(0, str(root))
            for module_name in ("pkg", "pkg.tools"):
                sys.modules.pop(module_name, None)
            try:
                enable_multilingual_imports()
                py = _run_python_source(source)
                for module_name in ("pkg", "pkg.tools"):
                    sys.modules.pop(module_name, None)
                ml = _run_multilingual_source(source)
            finally:
                disable_multilingual_imports()
                sys.path[:] = original_path
                for module_name in ("pkg", "pkg.tools"):
                    sys.modules.pop(module_name, None)

            self.assertEqual(ml["success"], py["success"])
            self.assertEqual(ml["output"], py["output"])

    def test_starred_unpacking_assignment_parity(self):
        """Test starred unpacking in various contexts."""
        multilingual_source = """\
a, *rest = [1, 2, 3, 4]
print(a, rest)

*init, last = [1, 2, 3, 4]
print(init, last)

first, *mid, last = [1, 2, 3, 4]
print(first, mid, last)
"""
        python_source = """\
a, *rest = [1, 2, 3, 4]
print(a, rest)

*init, last = [1, 2, 3, 4]
print(init, last)

first, *mid, last = [1, 2, 3, 4]
print(first, mid, last)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
            check_semantics=False,
        )

    def test_extended_builtins_parity(self):
        """Test newly added built-in functions and exceptions."""
        multilingual_source = """\
print(pow(2, 10))
print(divmod(17, 5))
print(isinstance(42, int))
try:
    raise BaseException("test")
except BaseException as e:
    print("caught")
"""
        python_source = """\
print(pow(2, 10))
print(divmod(17, 5))
print(isinstance(42, int))
try:
    raise BaseException("test")
except BaseException as e:
    print("caught")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_loop_else_parity(self):
        """Test for/while else control flow."""
        multilingual_source = """\
for i in range(3):
    pass
else:
    print("done")

let x = 0
while x < 2:
    x = x + 1
else:
    print(x)
"""
        python_source = """\
for i in range(3):
    pass
else:
    print("done")

x = 0
while x < 2:
    x = x + 1
else:
    print(x)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_match_statement_parity(self):
        """Test match/case structural pattern matching."""
        multilingual_source = """\
let x = 2
match x:
    case 1:
        print("one")
    case 2:
        print("two")
    case _:
        print("other")
"""
        python_source = """\
x = 2
match x:
    case 1:
        print("one")
    case 2:
        print("two")
    case _:
        print("other")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
            check_semantics=False,
        )

    def test_global_nonlocal_semantic_parity(self):
        """Test global and nonlocal scope declarations."""
        multilingual_source = """\
let x = 10
def modify_global():
    global x
    x = 20
modify_global()
print(x)

def outer():
    let y = 10
    def inner():
        nonlocal y
        y = 20
    inner()
    print(y)
outer()
"""
        python_source = """\
x = 10
def modify_global():
    global x
    x = 20
modify_global()
print(x)

def outer():
    y = 10
    def inner():
        nonlocal y
        y = 20
    inner()
    print(y)
outer()
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_fstring_format_spec_parity(self):
        """Test f-string format specs and conversions."""
        multilingual_source = """\
let x = 3.14159
print(f"{x:.2f}")

let s = "hello"
print(f"{s!r}")

let n = 42
print(f"{n!s}")
"""
        python_source = """\
x = 3.14159
print(f"{x:.2f}")

s = "hello"
print(f"{s!r}")

n = 42
print(f"{n!s}")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_set_comprehension_parity(self):
        """Test set comprehension syntax."""
        multilingual_source = """\
let s = {x * x for x in range(5)}
print(sorted(s))

let s2 = {x for x in range(10) if x % 2 == 0}
print(sorted(s2))
"""
        python_source = """\
s = {x * x for x in range(5)}
print(sorted(s))

s2 = {x for x in range(10) if x % 2 == 0}
print(sorted(s2))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_yield_from_parity(self):
        """Test yield from generator delegation."""
        multilingual_source = """\
def gen():
    yield from range(3)

let result = list(gen())
print(result)
"""
        python_source = """\
def gen():
    yield from range(3)

result = list(gen())
print(result)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_raise_from_parity(self):
        """Test raise X from Y exception chaining."""
        multilingual_source = """\
try:
    raise ValueError("a") from TypeError("b")
except ValueError as e:
    print(type(e.__cause__).__name__)
"""
        python_source = """\
try:
    raise ValueError("a") from TypeError("b")
except ValueError as e:
    print(type(e.__cause__).__name__)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    # M2.1 Expansion: Exception handling parity tests
    def test_exception_value_error_parity(self):
        """ValueError exception produces identical behavior."""
        multilingual_source = """\
try:
    raise ValueError("test error")
except ValueError as e:
    print(str(e))
"""
        python_source = """\
try:
    raise ValueError("test error")
except ValueError as e:
    print(str(e))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_exception_type_error_parity(self):
        """TypeError exception produces identical behavior."""
        multilingual_source = """\
try:
    let x = "string" + 5
except TypeError as e:
    print("caught TypeError")
"""
        python_source = """\
try:
    x = "string" + 5
except TypeError as e:
    print("caught TypeError")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_exception_attribute_error_parity(self):
        """AttributeError exception parity."""
        multilingual_source = """\
class A:
    pass
try:
    let x = A().nonexistent
except AttributeError:
    print("caught")
"""
        python_source = """\
class A:
    pass
try:
    x = A().nonexistent
except AttributeError:
    print("caught")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_exception_key_error_parity(self):
        """KeyError exception parity."""
        multilingual_source = """\
try:
    let x = {"a": 1}["b"]
except KeyError:
    print("caught")
"""
        python_source = """\
try:
    x = {"a": 1}["b"]
except KeyError:
    print("caught")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_exception_index_error_parity(self):
        """IndexError exception parity."""
        multilingual_source = """\
try:
    let x = [1, 2, 3][10]
except IndexError:
    print("caught")
"""
        python_source = """\
try:
    x = [1, 2, 3][10]
except IndexError:
    print("caught")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_multiple_except_execution_parity(self):
        """Multiple except handlers execute correct one."""
        multilingual_source = """\
try:
    raise TypeError("test")
except ValueError:
    print("wrong")
except TypeError:
    print("correct")
"""
        python_source = """\
try:
    raise TypeError("test")
except ValueError:
    print("wrong")
except TypeError:
    print("correct")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_except_else_execution_parity(self):
        """Else clause executes when no exception."""
        multilingual_source = """\
try:
    let x = 1
except ValueError:
    print("error")
else:
    print("no error")
"""
        python_source = """\
try:
    x = 1
except ValueError:
    print("error")
else:
    print("no error")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_except_finally_always_executes(self):
        """Finally block always executes."""
        multilingual_source = """\
try:
    let x = 1
except ValueError:
    pass
finally:
    print("finally")
"""
        python_source = """\
try:
    x = 1
except ValueError:
    pass
finally:
    print("finally")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    # M2.1 Expansion: Operator behavior parity
    def test_operator_short_circuit_and(self):
        """Short-circuit AND operator."""
        multilingual_source = """\
def side_effect():
    print("called")
    return True
let result = False and side_effect()
print("done")
"""
        python_source = """\
def side_effect():
    print("called")
    return True
result = False and side_effect()
print("done")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_operator_short_circuit_or(self):
        """Short-circuit OR operator."""
        multilingual_source = """\
def side_effect():
    print("called")
    return False
let result = True or side_effect()
print("done")
"""
        python_source = """\
def side_effect():
    print("called")
    return False
result = True or side_effect()
print("done")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_operator_comparison_chain(self):
        """Chained comparison operators."""
        multilingual_source = """\
let x = 5
let result = 1 < x < 10
print(result)
"""
        python_source = """\
x = 5
result = 1 < x < 10
print(result)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_operator_division_by_zero(self):
        """Division by zero raises ZeroDivisionError."""
        multilingual_source = """\
try:
    let x = 1 / 0
except ZeroDivisionError:
    print("caught")
"""
        python_source = """\
try:
    x = 1 / 0
except ZeroDivisionError:
    print("caught")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_operator_truthiness_empty_list(self):
        """Empty list is falsy."""
        multilingual_source = """\
let x = []
if x:
    print("truthy")
else:
    print("falsy")
"""
        python_source = """\
x = []
if x:
    print("truthy")
else:
    print("falsy")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_operator_truthiness_zero(self):
        """Zero is falsy."""
        multilingual_source = """\
let x = 0
if x:
    print("truthy")
else:
    print("falsy")
"""
        python_source = """\
x = 0
if x:
    print("truthy")
else:
    print("falsy")
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    # M2.1 Expansion: Scope and closure parity
    def test_scope_global_modification(self):
        """Global variable modification."""
        multilingual_source = """\
let x = 10
def modify():
    global x
    x = 20
modify()
print(x)
"""
        python_source = """\
x = 10
def modify():
    global x
    x = 20
modify()
print(x)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_scope_nonlocal_modification(self):
        """Nonlocal variable modification."""
        multilingual_source = """\
def outer():
    let x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    print(x)
outer()
"""
        python_source = """\
def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    print(x)
outer()
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_scope_closure_capture(self):
        """Closure captures variable."""
        multilingual_source = """\
def make_adder(n):
    def adder(x):
        return x + n
    return adder
let add5 = make_adder(5)
print(add5(3))
"""
        python_source = """\
def make_adder(n):
    def adder(x):
        return x + n
    return adder
add5 = make_adder(5)
print(add5(3))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    # M2.1 Expansion: Class and object model parity
    def test_class_inheritance_basic(self):
        """Basic inheritance."""
        multilingual_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    pass
let b = B()
print(b.method())
"""
        python_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    pass
b = B()
print(b.method())
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_class_method_override(self):
        """Method override in subclass."""
        multilingual_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    def method(self):
        return "B"
let b = B()
print(b.method())
"""
        python_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    def method(self):
        return "B"
b = B()
print(b.method())
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_class_super_call(self):
        """super() in subclass."""
        multilingual_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    def method(self):
        return super().method() + "B"
let b = B()
print(b.method())
"""
        python_source = """\
class A:
    def method(self):
        return "A"
class B(A):
    def method(self):
        return super().method() + "B"
b = B()
print(b.method())
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    # M2.1 Expansion: Advanced features parity
    def test_walrus_operator_assignment(self):
        """Walrus operator assignment in expression."""
        multilingual_source = """\
if (x := 10) > 5:
    print(x)
"""
        python_source = """\
if (x := 10) > 5:
    print(x)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_comprehension_scope_isolation(self):
        """Comprehension variable isolated from outer scope."""
        multilingual_source = """\
let x = 5
let result = [x * 2 for x in range(3)]
print(x)
print(result)
"""
        python_source = """\
x = 5
result = [x * 2 for x in range(3)]
print(x)
print(result)
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_dict_comprehension_parity(self):
        """Dictionary comprehension."""
        multilingual_source = """\
let result = {x: x*2 for x in range(3)}
print(sorted(result.items()))
"""
        python_source = """\
result = {x: x*2 for x in range(3)}
print(sorted(result.items()))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )

    def test_set_comprehension_even_filter_parity(self):
        """Set comprehension with filtering."""
        multilingual_source = """\
let result = {x*x for x in range(5) if x % 2 == 0}
print(sorted(result))
"""
        python_source = """\
result = {x*x for x in range(5) if x % 2 == 0}
print(sorted(result))
"""
        self._assert_equivalent(
            multilingual_source=multilingual_source,
            python_source=python_source,
        )
