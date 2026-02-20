#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the AST pretty-printer."""

import unittest
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_printer import ASTPrinter


def _print_ast(source, language="en"):
    """Helper: lex + parse + pretty-print."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language)
    program = parser.parse()
    printer = ASTPrinter()
    return printer.print(program)


class ASTPrinterTestSuite(unittest.TestCase):
    """Tests for AST pretty-printing."""

    def test_print_numeral_literal(self):
        output = _print_ast("42\n")
        self.assertIn("NumeralLiteral", output)
        self.assertIn("42", output)

    def test_print_binary_op(self):
        output = _print_ast("1 + 2\n")
        self.assertIn("BinaryOp", output)
        self.assertIn("'+'", output)

    def test_print_function_def(self):
        output = _print_ast("def f(x):\n    return x\n")
        self.assertIn("FunctionDef", output)
        self.assertIn("'f'", output)
        self.assertIn("ReturnStatement", output)

    def test_print_if_statement(self):
        output = _print_ast("if x:\n    pass\nelse:\n    pass\n")
        self.assertIn("IfStatement", output)
        self.assertIn("else:", output)
        self.assertIn("PassStatement", output)

    def test_print_class_def(self):
        output = _print_ast("class Foo:\n    pass\n")
        self.assertIn("ClassDef", output)
        self.assertIn("'Foo'", output)

    def test_print_nested_structure(self):
        source = "def f(n):\n    if n:\n        return 1\n    return 0\n"
        output = _print_ast(source)
        self.assertIn("FunctionDef", output)
        self.assertIn("IfStatement", output)
        self.assertIn("ReturnStatement", output)

    def test_print_program(self):
        output = _print_ast("42\n")
        self.assertTrue(output.startswith("Program"))

    def test_print_empty_program(self):
        output = _print_ast("")
        self.assertIn("Program", output)

    def test_print_list_literal(self):
        output = _print_ast("[1, 2, 3]\n")
        self.assertIn("ListLiteral", output)

    def test_print_try_statement(self):
        source = "try:\n    pass\nexcept:\n    pass\nelse:\n    pass\n"
        output = _print_ast(source)
        self.assertIn("TryStatement", output)
        self.assertIn("ExceptHandler", output)
        self.assertIn("else:", output)

    def test_print_for_loop(self):
        source = "for i in items:\n    pass\n"
        output = _print_ast(source)
        self.assertIn("ForLoop", output)
        self.assertIn("target:", output)
        self.assertIn("iterable:", output)

    def test_print_indentation(self):
        output = _print_ast("def f():\n    pass\n")
        lines = output.split("\n")
        # FunctionDef should be indented under Program
        func_line = [l for l in lines if "FunctionDef" in l][0]
        self.assertTrue(func_line.startswith("  "))


if __name__ == "__main__":
    unittest.main()
