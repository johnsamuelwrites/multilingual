#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

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
