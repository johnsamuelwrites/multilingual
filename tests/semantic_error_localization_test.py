#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for semantic error localization across languages."""

import unittest
from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute_multilingual(source, language="en"):
    """Execute multilingual source and return result."""
    result = ProgramExecutor(
        language=language,
        check_semantics=True,
    ).execute(source)
    return {
        "success": result.success,
        "errors": result.errors,
        "output": result.output,
    }


class SemanticErrorLocalizationTestSuite(unittest.TestCase):
    """Tests for semantic error detection across languages."""

    # Undefined variable errors
    def test_undefined_variable_english(self):
        """Undefined variable error in English."""
        source = "print(undefined_var)\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])
        self.assertTrue(any("not defined" in err.lower() for err in result["errors"]))

    def test_undefined_variable_french(self):
        """Undefined variable error in French."""
        source = "afficher(var_indefinie)\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    def test_undefined_variable_spanish(self):
        """Undefined variable error in Spanish."""
        source = "imprimir(var_indefinida)\n"
        result = _execute_multilingual(source, "es")
        self.assertFalse(result["success"])

    # Undefined function errors
    def test_undefined_function_english(self):
        """Undefined function error in English."""
        source = "undefined_func()\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_undefined_function_french(self):
        """Undefined function error in French."""
        source = "func_indefinie()\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Break outside loop
    def test_break_outside_loop_english(self):
        """Break statement outside loop."""
        source = "break\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_break_outside_loop_french(self):
        """Break statement outside loop in French."""
        source = "arrêter\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    def test_break_outside_loop_spanish(self):
        """Break statement outside loop in Spanish."""
        source = "romper\n"
        result = _execute_multilingual(source, "es")
        self.assertFalse(result["success"])

    # Continue outside loop
    def test_continue_outside_loop_english(self):
        """Continue statement outside loop."""
        source = "continue\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_continue_outside_loop_french(self):
        """Continue statement outside loop in French."""
        source = "continuer\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Return outside function
    def test_return_outside_function_english(self):
        """Return statement outside function."""
        source = "return 42\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_return_outside_function_french(self):
        """Return statement outside function in French."""
        source = "retour 42\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Yield outside function
    def test_yield_outside_function_english(self):
        """Yield statement outside function."""
        source = "yield 42\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_yield_outside_function_french(self):
        """Yield statement outside function in French."""
        source = "produire 42\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Duplicate constant definition
    def test_duplicate_const_english(self):
        """Cannot redefine constant."""
        source = """const X = 5
X = 10
"""
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_duplicate_const_french(self):
        """Cannot redefine constant in French."""
        source = """const X = 5
X = 10
"""
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Global statement for undefined variable
    def test_global_in_function_english(self):
        """Using global for undefined variable in function."""
        source = """def func():
    global x
    print(x)
func()
"""
        result = _execute_multilingual(source, "en")
        # Should fail because x is not defined globally
        self.assertFalse(result["success"])

    def test_global_in_function_french(self):
        """Using global for undefined variable in French function."""
        source = """def func():
    global x
    afficher(x)
func()
"""
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Nonlocal in module scope
    def test_nonlocal_in_module_scope_english(self):
        """Using nonlocal at module scope."""
        source = "nonlocal x\n"
        result = _execute_multilingual(source, "en")
        self.assertFalse(result["success"])

    def test_nonlocal_in_module_scope_french(self):
        """Using nonlocal at module scope in French."""
        source = "nonlocale x\n"
        result = _execute_multilingual(source, "fr")
        self.assertFalse(result["success"])

    # Valid code - control check
    def test_valid_code_english(self):
        """Valid code executes successfully."""
        source = """let x = 5
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])

    def test_valid_code_french(self):
        """Valid code executes successfully in French."""
        source = """soit x = 5
afficher(x)
"""
        result = _execute_multilingual(source, "fr")
        self.assertTrue(result["success"])

    def test_valid_code_spanish(self):
        """Valid code executes successfully in Spanish."""
        source = """sea x = 5
imprimir(x)
"""
        result = _execute_multilingual(source, "es")
        self.assertTrue(result["success"])

    # Scope shadowing - this should be valid
    def test_scope_shadowing_english(self):
        """Variable shadowing in nested scope."""
        source = """let x = 5
def func():
    let x = 10
    print(x)
func()
print(x)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])

    # Name binding in comprehension
    def test_comprehension_scope_english(self):
        """Comprehension creates isolated scope."""
        source = """let result = [x for x in range(3)]
print(x)
"""
        result = _execute_multilingual(source, "en")
        # Should fail because x is not in outer scope
        self.assertFalse(result["success"])

    # Function parameter shadowing
    def test_function_parameter_shadowing_english(self):
        """Function parameter can shadow outer variable."""
        source = """let x = 5
def func(x):
    print(x)
func(10)
"""
        result = _execute_multilingual(source, "en")
        self.assertTrue(result["success"])


if __name__ == "__main__":
    unittest.main()
