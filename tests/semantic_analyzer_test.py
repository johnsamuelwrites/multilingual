#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the semantic analyzer."""

import unittest
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import (
    Symbol, Scope, SymbolTable, SemanticAnalyzer,
)


def _analyze(source, language="en"):
    """Helper: lex + parse + analyze."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language)
    program = parser.parse()
    analyzer = SemanticAnalyzer(source_language=language)
    errors = analyzer.analyze(program)
    return errors, analyzer


class SemanticScopeTestSuite(unittest.TestCase):
    """Tests for scope resolution."""

    def test_variable_definition_and_lookup(self):
        errors, _ = _analyze("let x = 5\nx\n")
        # x is defined then used -- no errors expected
        self.assertEqual(len(errors), 0)

    def test_undefined_variable_error(self):
        errors, _ = _analyze("y\n")
        self.assertTrue(any("y" in str(e) for e in errors))

    def test_variable_in_nested_scope(self):
        source = "let x = 1\ndef f():\n    x\n"
        errors, _ = _analyze(source)
        # x is in outer scope, accessible from function
        self.assertEqual(len(errors), 0)

    def test_function_scope_isolation(self):
        source = "def f():\n    let y = 1\ny\n"
        errors, _ = _analyze(source)
        # y defined inside function, not accessible outside
        self.assertTrue(any("y" in str(e) for e in errors))

    def test_function_adds_symbol(self):
        source = "def f():\n    pass\nf()\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_class_adds_symbol(self):
        source = "class Foo:\n    pass\nFoo()\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_function_params_in_scope(self):
        source = "def f(a, b):\n    a + b\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)


class SemanticConstTestSuite(unittest.TestCase):
    """Tests for constant handling."""

    def test_const_declaration(self):
        errors, _ = _analyze("const PI = 3.14\nPI\n")
        self.assertEqual(len(errors), 0)

    def test_const_reassignment_error(self):
        errors, _ = _analyze("const PI = 3.14\nPI = 3.15\n")
        self.assertTrue(any("PI" in str(e) for e in errors))

    def test_let_reassignment_allowed(self):
        errors, _ = _analyze("let x = 1\nx = 2\n")
        self.assertEqual(len(errors), 0)


class SemanticControlFlowTestSuite(unittest.TestCase):
    """Tests for control flow validation."""

    def test_break_inside_loop(self):
        source = "while True:\n    break\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_break_outside_loop_error(self):
        source = "break\n"
        errors, _ = _analyze(source)
        self.assertTrue(any("break" in str(e).lower() for e in errors))

    def test_continue_inside_loop(self):
        source = "while True:\n    continue\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_continue_outside_loop_error(self):
        source = "continue\n"
        errors, _ = _analyze(source)
        self.assertTrue(any("continue" in str(e).lower() for e in errors))

    def test_return_inside_function(self):
        source = "def f():\n    return 1\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_return_outside_function_error(self):
        source = "return 1\n"
        errors, _ = _analyze(source)
        self.assertTrue(any("return" in str(e).lower() for e in errors))

    def test_yield_inside_function(self):
        source = "def f():\n    yield 1\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_yield_outside_function_error(self):
        source = "yield 1\n"
        errors, _ = _analyze(source)
        self.assertTrue(any("yield" in str(e).lower() for e in errors))

    def test_nested_loop_break(self):
        source = "while True:\n    while True:\n        break\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)


class SemanticDefinitionTestSuite(unittest.TestCase):
    """Tests for definition handling."""

    def test_duplicate_definition(self):
        source = "let x = 1\nlet x = 2\n"
        errors, _ = _analyze(source)
        self.assertTrue(any("x" in str(e) for e in errors))

    def test_import_adds_symbol(self):
        source = "import os\nos\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_from_import_adds_symbols(self):
        source = "from os import path\npath\n"
        errors, _ = _analyze(source)
        self.assertEqual(len(errors), 0)

    def test_for_loop_defines_variable(self):
        source = "for i in items:\n    i\n"
        errors, _ = _analyze(source)
        # 'items' is undefined, but 'i' should be defined in loop body
        items_errors = [e for e in errors if "items" in str(e)]
        i_errors = [e for e in errors if str(e).endswith("'i'") or "'i'" in str(e)]
        self.assertTrue(len(items_errors) > 0)  # items not defined
        self.assertEqual(len(i_errors), 0)  # i is defined by for loop


class SemanticMultilingualErrorTestSuite(unittest.TestCase):
    """Tests for multilingual error messages."""

    def test_error_message_english(self):
        errors, _ = _analyze("break\n", language="en")
        self.assertTrue(len(errors) > 0)
        self.assertIn("break", str(errors[0]).lower())

    def test_error_message_french(self):
        errors, _ = _analyze("arr\u00eater\n", language="fr")
        # 'arrêter' is the French for 'break'
        self.assertTrue(len(errors) > 0)
        self.assertIn("boucle", str(errors[0]).lower())

    def test_error_message_chinese(self):
        errors, _ = _analyze("\u7ec8\u6b62\n", language="zh")
        # '终止' is Chinese for 'break'
        self.assertTrue(len(errors) > 0)


class SymbolTableTestSuite(unittest.TestCase):
    """Tests for the SymbolTable class directly."""

    def test_define_and_lookup(self):
        st = SymbolTable()
        st.define("x", "variable")
        sym = st.lookup("x")
        self.assertIsNotNone(sym)
        self.assertEqual(sym.name, "x")

    def test_lookup_not_found(self):
        st = SymbolTable()
        self.assertIsNone(st.lookup("missing"))

    def test_nested_scope_lookup(self):
        st = SymbolTable()
        st.define("x", "variable")
        st.enter_scope("func", "function")
        sym = st.lookup("x")
        self.assertIsNotNone(sym)

    def test_local_lookup(self):
        st = SymbolTable()
        st.define("x", "variable")
        st.enter_scope("func", "function")
        self.assertIsNone(st.lookup_local("x"))

    def test_exit_scope(self):
        st = SymbolTable()
        st.enter_scope("func", "function")
        st.define("y", "variable")
        st.exit_scope()
        self.assertIsNone(st.lookup("y"))

    def test_symbol_repr(self):
        sym = Symbol("x", "variable", is_const=True, data_type="int")
        self.assertIn("x", repr(sym))
        self.assertIn("const=True", repr(sym))


if __name__ == "__main__":
    unittest.main()
