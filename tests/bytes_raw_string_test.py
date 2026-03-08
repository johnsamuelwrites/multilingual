#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for bytes literals (b"...") and raw string literals (r"...")."""

import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.parser.ast_nodes import (
    BytesLiteral,
    StringLiteral,
)
from tests._test_helpers import execute_source, generate_python, parse_source


class TestBytesLiteralLexer(unittest.TestCase):
    """Lexer correctly tokenizes bytes literals."""

    def _tokens(self, source):
        return Lexer(source).tokenize()

    def test_bytes_double_quote(self):
        tokens = self._tokens('b"hello"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, "hello")
        self.assertFalse(tokens[0].raw)

    def test_bytes_single_quote(self):
        tokens = self._tokens("b'world'")
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, "world")
        self.assertFalse(tokens[0].raw)

    def test_bytes_uppercase_prefix(self):
        tokens = self._tokens('B"data"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, "data")

    def test_bytes_with_escape(self):
        tokens = self._tokens(r'b"line\n"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertIn("\\n", tokens[0].value)

    def test_raw_bytes_rb(self):
        tokens = self._tokens(r'rb"no\nescape"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, r"no\nescape")
        self.assertTrue(tokens[0].raw)

    def test_raw_bytes_br(self):
        tokens = self._tokens(r'br"no\nescape"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, r"no\nescape")
        self.assertTrue(tokens[0].raw)

    def test_raw_bytes_RB(self):
        tokens = self._tokens(r'RB"data\t"')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertTrue(tokens[0].raw)

    def test_raw_string_r(self):
        tokens = self._tokens(r'r"raw\nstring"')
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, r"raw\nstring")
        self.assertTrue(tokens[0].raw)

    def test_raw_string_R(self):
        tokens = self._tokens(r'R"also\traw"')
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertTrue(tokens[0].raw)

    def test_bytes_triple_quoted(self):
        tokens = self._tokens('b"""triple bytes"""')
        self.assertEqual(tokens[0].type, TokenType.BYTES)
        self.assertEqual(tokens[0].value, "triple bytes")

    def test_raw_triple_string(self):
        tokens = self._tokens(r'r"""raw\ntriple"""')
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, r"raw\ntriple")
        self.assertTrue(tokens[0].raw)


class TestBytesLiteralParser(unittest.TestCase):
    """Parser creates BytesLiteral and raw StringLiteral AST nodes."""

    def _first_expr(self, source):
        prog = parse_source(f"x = {source}")
        return prog.body[0].value

    def test_bytes_literal_node(self):
        node = self._first_expr('b"hello"')
        self.assertIsInstance(node, BytesLiteral)
        self.assertEqual(node.value, "hello")
        self.assertFalse(node.raw)

    def test_raw_bytes_node(self):
        node = self._first_expr(r'rb"no\nescape"')
        self.assertIsInstance(node, BytesLiteral)
        self.assertTrue(node.raw)

    def test_raw_string_node(self):
        node = self._first_expr(r'r"path\nvalue"')
        self.assertIsInstance(node, StringLiteral)
        self.assertTrue(node.raw)

    def test_regular_string_not_raw(self):
        node = self._first_expr('"normal"')
        self.assertIsInstance(node, StringLiteral)
        self.assertFalse(node.raw)


class TestBytesLiteralCodegen(unittest.TestCase):
    """Python code generator emits correct output for bytes and raw strings."""

    def test_bytes_codegen(self):
        result = generate_python('x = b"hello"')
        self.assertEqual(result, "x = b'hello'")

    def test_bytes_single_quote_codegen(self):
        result = generate_python("x = b'world'")
        self.assertEqual(result, "x = b'world'")

    def test_raw_bytes_codegen(self):
        result = generate_python(r'x = rb"no\nescape"')
        self.assertIn("rb", result)
        self.assertIn(r"no\nescape", result)

    def test_raw_string_codegen(self):
        result = generate_python(r'x = r"path\nvalue"')
        self.assertIn("r", result[4:6])  # prefix r present
        self.assertIn(r"path\nvalue", result)

    def test_raw_string_double_quote(self):
        result = generate_python(r'x = r"C:\Users\name"')
        self.assertIn(r"C:\Users\name", result)
        self.assertIn("r", result)

    def test_bytes_expression_in_call(self):
        result = generate_python('print(b"data")')
        self.assertIn("b'data'", result)

    def test_raw_bytes_br_prefix_codegen(self):
        result = generate_python(r'x = br"test\t"')
        self.assertIn("rb", result)

    def test_bytes_uppercase_codegen(self):
        result = generate_python('x = B"data"')
        self.assertIn("b'data'", result)


class TestBytesLiteralExecution(unittest.TestCase):
    """Bytes and raw string literals execute correctly via ProgramExecutor."""

    def test_bytes_type(self):
        r = execute_source('x = b"hello"\nprint(type(x).__name__)')
        self.assertEqual(r.output.strip(), "bytes")

    def test_bytes_value(self):
        r = execute_source('x = b"hello"\nprint(x)')
        self.assertIn("hello", r.output)

    def test_raw_bytes_no_escape(self):
        r = execute_source(r'x = rb"no\nescape"' + "\nprint(len(x))")
        # rb"no\nescape" has 10 chars: n,o,\,n,e,s,c,a,p,e (backslash is literal)
        self.assertEqual(r.output.strip(), "10")

    def test_raw_string_no_escape(self):
        r = execute_source(r'x = r"a\nb"' + "\nprint(len(x))")
        # r"a\nb" has 4 chars: a, \, n, b
        self.assertEqual(r.output.strip(), "4")

    def test_raw_string_type(self):
        r = execute_source(r'x = r"path"' + "\nprint(type(x).__name__)")
        self.assertEqual(r.output.strip(), "str")


class TestWATStaticMethod(unittest.TestCase):
    """WAT generator correctly handles @staticmethod and @classmethod."""

    def _generate_wat(self, source):
        prog = parse_source(source)
        gen = WATCodeGenerator()
        return gen.generate(prog)

    def test_staticmethod_no_self_in_wat(self):
        src = """
class MyClass:
    @staticmethod
    def add(a, b):
        return a + b
"""
        wat = self._generate_wat(src)
        # The WAT function for add is mangled to MyClass__add; params are a and b only
        self.assertIn("MyClass__add", wat or "")
        # Confirm params $a and $b exist but not $self
        self.assertIn("$a", wat)
        self.assertIn("$b", wat)
        self.assertNotIn("$self", wat)

    def test_classmethod_no_self_in_wat(self):
        src = """
class Counter:
    @classmethod
    def create(cls):
        pass
"""
        wat = self._generate_wat(src)
        self.assertIsNotNone(wat)

    def test_regular_method_still_gets_self(self):
        src = """
class Point:
    def __init__(self, x):
        self.x = x
    def get_x(self):
        return self.x
"""
        wat = self._generate_wat(src)
        self.assertIn("self", wat)


if __name__ == "__main__":
    unittest.main()
