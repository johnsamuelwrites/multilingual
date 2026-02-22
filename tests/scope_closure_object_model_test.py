#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for scope and variable binding behavior."""

import unittest
from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute_multilingual(source, language="en"):
    """Execute multilingual source and capture output."""
    result = ProgramExecutor(language=language, check_semantics=True).execute(source)
    return {
        "success": result.success,
        "output": result.output,
    }


class ScopeClosureObjectModelTestSuite(unittest.TestCase):
    """Tests for scope, closure, and variable binding behavior."""

    # Global variable modification
    def test_global_variable_modification_english(self):
        """Global variable can be modified in function."""
        source = """\
let x = 10
def modify():
    global x
    x = 20
modify()
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("20", result["output"])

    # Nonlocal variable modification
    def test_nonlocal_variable_modification_english(self):
        """Nonlocal variable in nested function."""
        source = """\
def outer():
    let x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    return x
print(outer())
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("20", result["output"])

    # Scope shadowing
    def test_local_scope_shadowing_english(self):
        """Local variable shadows global variable."""
        source = """\
let x = 1
def func():
    let x = 2
    return x
print(func())
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("2", result["output"])
        self.assertIn("1", result["output"])

    # Nested scope access
    def test_nested_scope_access_english(self):
        """Access outer scope from nested scope."""
        source = """\
let y = 5
def outer():
    let x = 10
    def inner():
        return x + y
    return inner()
print(outer())
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("15", result["output"])

    # Function parameters
    def test_function_parameter_shadowing_english(self):
        """Function parameter shadows global."""
        source = """\
let x = 1
def func(x):
    return x * 2
print(func(5))
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("10", result["output"])
        self.assertIn("1", result["output"])

    # Multiple assignments
    def test_multiple_assignment_unpacking_english(self):
        """Tuple unpacking in assignment."""
        source = """\
let a, b, c = 1, 2, 3
print(a)
print(b)
print(c)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("1", result["output"])
        self.assertIn("2", result["output"])
        self.assertIn("3", result["output"])

    def test_multiple_assignment_unpacking_french(self):
        """Tuple unpacking in French."""
        source = """\
soit a, b, c = 1, 2, 3
afficher(a)
afficher(b)
afficher(c)
"""
        result = _execute_multilingual(source, "fr")
        self.assertTrue(result["success"])
        self.assertIn("1", result["output"])
        self.assertIn("2", result["output"])
        self.assertIn("3", result["output"])

    # Comprehension variable scope
    def test_comprehension_variable_scope_english(self):
        """Comprehension variables don't affect outer scope."""
        source = """\
let items = [x * 2 for x in range(3)]
print(items)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("[0, 2, 4]", result["output"])

    # Constant redefinition
    def test_const_cannot_be_reassigned_english(self):
        """Const variable cannot be reassigned."""
        source = """\
const X = 5
X = 10
"""
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])


    # Empty scope doesn't cause error
    def test_empty_function_english(self):
        """Empty function with only pass."""
        source = """\
def func():
    pass
func()
print("done")
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("done", result["output"])

    # Simple variable lifetime
    def test_variable_lifetime_english(self):
        """Variable lifetime in nested blocks."""
        source = """\
let x = 1
if True:
    let y = 2
    print(x + y)
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("3", result["output"])
        self.assertIn("1", result["output"])

    # For loop variable scope
    def test_for_loop_variable_scope_english(self):
        """For loop variable scope."""
        source = """\
for i in range(3):
    pass
print(i)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("2", result["output"])

    # Multiple function definitions
    def test_multiple_function_definitions_english(self):
        """Multiple functions can be defined."""
        source = """\
def add(a, b):
    return a + b
def multiply(a, b):
    return a * b
print(add(2, 3))
print(multiply(2, 3))
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])
        self.assertIn("5", result["output"])
        self.assertIn("6", result["output"])


if __name__ == "__main__":
    unittest.main()
