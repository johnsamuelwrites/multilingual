#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the recursive-descent parser."""

import unittest
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_nodes import (
    Program, NumeralLiteral, StringLiteral, DateLiteral,
    BooleanLiteral, NoneLiteral, ListLiteral, DictLiteral,
    Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess, LambdaExpr,
    VariableDeclaration, Assignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, GlobalStatement, LocalStatement, YieldStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, CaseClause,
    WithStatement, ImportStatement, FromImportStatement,
)
from multilingualprogramming.exceptions import ParseError


def _parse(source, language=None):
    """Helper: lex + parse source code."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    lang = language or lexer.language or "en"
    parser = Parser(tokens, source_language=lang)
    return parser.parse()


class ParserExpressionTestSuite(unittest.TestCase):
    """Tests for expression parsing."""

    def test_parse_numeral_literal(self):
        prog = _parse("42\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, NumeralLiteral)
        self.assertEqual(stmt.expression.value, "42")

    def test_parse_string_literal(self):
        prog = _parse('"hello"\n')
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, StringLiteral)
        self.assertEqual(stmt.expression.value, "hello")

    def test_parse_date_literal(self):
        prog = _parse('\u301415-January-2024\u3015\n')
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, DateLiteral)

    def test_parse_boolean_true(self):
        prog = _parse("True\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, BooleanLiteral)
        self.assertTrue(stmt.expression.value)

    def test_parse_boolean_false(self):
        prog = _parse("False\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, BooleanLiteral)
        self.assertFalse(stmt.expression.value)

    def test_parse_none_literal(self):
        prog = _parse("None\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, NoneLiteral)

    def test_parse_identifier(self):
        prog = _parse("x\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, Identifier)
        self.assertEqual(stmt.expression.name, "x")

    def test_parse_parenthesized(self):
        prog = _parse("(42)\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, NumeralLiteral)

    def test_parse_list_literal_empty(self):
        prog = _parse("[]\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, ListLiteral)
        self.assertEqual(len(stmt.expression.elements), 0)

    def test_parse_list_literal_elements(self):
        prog = _parse("[1, 2, 3]\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, ListLiteral)
        self.assertEqual(len(stmt.expression.elements), 3)

    def test_parse_dict_literal_empty(self):
        prog = _parse("{}\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, DictLiteral)
        self.assertEqual(len(stmt.expression.pairs), 0)

    def test_parse_dict_literal_pairs(self):
        prog = _parse('{"a": 1, "b": 2}\n')
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, DictLiteral)
        self.assertEqual(len(stmt.expression.pairs), 2)

    def test_parse_addition(self):
        prog = _parse("1 + 2\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "+")

    def test_parse_subtraction(self):
        prog = _parse("5 - 3\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "-")

    def test_parse_multiplication(self):
        prog = _parse("4 * 6\n")
        expr = prog.body[0].expression
        self.assertEqual(expr.op, "*")

    def test_parse_division(self):
        prog = _parse("10 / 2\n")
        expr = prog.body[0].expression
        self.assertEqual(expr.op, "/")

    def test_parse_floor_division(self):
        prog = _parse("10 // 3\n")
        expr = prog.body[0].expression
        self.assertEqual(expr.op, "//")

    def test_parse_modulus(self):
        prog = _parse("10 % 3\n")
        expr = prog.body[0].expression
        self.assertEqual(expr.op, "%")

    def test_parse_power(self):
        prog = _parse("2 ** 3\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "**")

    def test_parse_precedence_mul_over_add(self):
        prog = _parse("1 + 2 * 3\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "+")
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "*")

    def test_parse_unary_minus(self):
        prog = _parse("-5\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "-")

    def test_parse_unary_plus(self):
        prog = _parse("+5\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "+")

    def test_parse_equality(self):
        prog = _parse("x == 5\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CompareOp)
        self.assertEqual(expr.comparators[0][0], "==")

    def test_parse_inequality(self):
        prog = _parse("x != 5\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CompareOp)
        self.assertEqual(expr.comparators[0][0], "!=")

    def test_parse_less_than(self):
        prog = _parse("x < 5\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CompareOp)

    def test_parse_chained_comparison(self):
        prog = _parse("1 < x < 10\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CompareOp)
        self.assertEqual(len(expr.comparators), 2)

    def test_parse_and_expression(self):
        prog = _parse("x and y\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BooleanOp)
        self.assertEqual(expr.op, "AND")

    def test_parse_or_expression(self):
        prog = _parse("x or y\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BooleanOp)
        self.assertEqual(expr.op, "OR")

    def test_parse_not_expression(self):
        prog = _parse("not x\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "NOT")

    def test_parse_function_call(self):
        prog = _parse("f()\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)
        self.assertEqual(len(expr.args), 0)

    def test_parse_function_call_with_args(self):
        prog = _parse("f(1, 2)\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)
        self.assertEqual(len(expr.args), 2)

    def test_parse_index_access(self):
        prog = _parse("arr[0]\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, IndexAccess)

    def test_parse_attribute_access(self):
        prog = _parse("obj.method\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, AttributeAccess)
        self.assertEqual(expr.attr, "method")

    def test_parse_chained_calls(self):
        prog = _parse("a.b().c\n")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, AttributeAccess)
        self.assertEqual(expr.attr, "c")

    def test_parse_lambda(self):
        prog = _parse("lambda x: x + 1\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, LambdaExpr)
        self.assertEqual(expr.params, ["x"])

    def test_parse_print_as_identifier(self):
        prog = _parse('print("hello")\n', language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)
        self.assertIsInstance(expr.func, Identifier)
        self.assertEqual(expr.func.name, "print")


class ParserStatementTestSuite(unittest.TestCase):
    """Tests for simple statement parsing."""

    def test_parse_let_declaration(self):
        prog = _parse("let x = 5\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, VariableDeclaration)
        self.assertEqual(stmt.name, "x")
        self.assertFalse(stmt.is_const)

    def test_parse_const_declaration(self):
        prog = _parse("const PI = 3.14\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, VariableDeclaration)
        self.assertTrue(stmt.is_const)

    def test_parse_assignment(self):
        prog = _parse("x = 10\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.op, "=")

    def test_parse_augmented_assignment_add(self):
        prog = _parse("x += 1\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.op, "+=")

    def test_parse_augmented_assignment_sub(self):
        prog = _parse("x -= 1\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.op, "-=")

    def test_parse_expression_statement(self):
        prog = _parse("f()\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ExpressionStatement)

    def test_parse_return_with_value(self):
        prog = _parse("return 42\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ReturnStatement)
        self.assertIsNotNone(stmt.value)

    def test_parse_return_no_value(self):
        prog = _parse("return\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ReturnStatement)
        self.assertIsNone(stmt.value)

    def test_parse_break(self):
        prog = _parse("break\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, BreakStatement)

    def test_parse_continue(self):
        prog = _parse("continue\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ContinueStatement)

    def test_parse_pass(self):
        prog = _parse("pass\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, PassStatement)

    def test_parse_raise_with_value(self):
        prog = _parse("raise x\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, RaiseStatement)
        self.assertIsNotNone(stmt.value)

    def test_parse_raise_no_value(self):
        prog = _parse("raise\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, RaiseStatement)
        self.assertIsNone(stmt.value)

    def test_parse_global_statement(self):
        prog = _parse("global x, y\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, GlobalStatement)
        self.assertEqual(stmt.names, ["x", "y"])

    def test_parse_yield_statement(self):
        prog = _parse("yield 42\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, YieldStatement)


class ParserCompoundTestSuite(unittest.TestCase):
    """Tests for compound statement parsing."""

    def test_parse_if_simple(self):
        source = "if x:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsNone(stmt.else_body)

    def test_parse_if_else(self):
        source = "if x:\n    pass\nelse:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_body)

    def test_parse_if_elif_else(self):
        source = "if x:\n    pass\nelif y:\n    pass\nelse:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertEqual(len(stmt.elif_clauses), 1)
        self.assertIsNotNone(stmt.else_body)

    def test_parse_while_loop(self):
        source = "while True:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WhileLoop)

    def test_parse_for_loop(self):
        source = "for i in items:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

    def test_parse_function_def_no_params(self):
        source = "def f():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(stmt.name, "f")
        self.assertEqual(stmt.params, [])

    def test_parse_function_def_with_params(self):
        source = "def f(a, b):\n    return a + b\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(len(stmt.params), 2)
        self.assertEqual(stmt.params[0].name, "a")
        self.assertEqual(stmt.params[1].name, "b")

    def test_parse_class_def_no_bases(self):
        source = "class Foo:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)
        self.assertEqual(stmt.name, "Foo")
        self.assertEqual(len(stmt.bases), 0)

    def test_parse_class_def_with_bases(self):
        source = "class Foo(Bar):\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)
        self.assertEqual(len(stmt.bases), 1)

    def test_parse_try_except(self):
        source = "try:\n    pass\nexcept:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)
        self.assertEqual(len(stmt.handlers), 1)

    def test_parse_try_except_as(self):
        source = "try:\n    pass\nexcept Error as e:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        handler = stmt.handlers[0]
        self.assertIsInstance(handler, ExceptHandler)
        self.assertEqual(handler.name, "e")

    def test_parse_try_except_finally(self):
        source = "try:\n    pass\nexcept:\n    pass\nfinally:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsNotNone(stmt.finally_body)

    def test_parse_try_finally(self):
        source = "try:\n    pass\nfinally:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertEqual(len(stmt.handlers), 0)
        self.assertIsNotNone(stmt.finally_body)

    def test_parse_match_case(self):
        source = "match x:\n    case 1:\n        pass\n    case 2:\n        pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, MatchStatement)
        self.assertEqual(len(stmt.cases), 2)

    def test_parse_match_case_default(self):
        source = "match x:\n    case 1:\n        pass\n    default:\n        pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertTrue(stmt.cases[1].is_default)

    def test_parse_with_statement(self):
        source = "with f():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WithStatement)

    def test_parse_with_as(self):
        source = "with f() as x:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertEqual(stmt.name, "x")

    def test_parse_import_simple(self):
        source = "import os\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ImportStatement)
        self.assertEqual(stmt.module, "os")

    def test_parse_import_as(self):
        source = "import numpy as np\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertEqual(stmt.alias, "np")

    def test_parse_from_import(self):
        source = "from os import path\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FromImportStatement)
        self.assertEqual(stmt.module, "os")
        self.assertEqual(stmt.names, [("path", None)])

    def test_parse_from_import_multiple(self):
        source = "from os import path, getcwd\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertEqual(len(stmt.names), 2)

    def test_parse_nested_blocks(self):
        source = "if True:\n    if True:\n        pass\n"
        prog = _parse(source, language="en")
        outer = prog.body[0]
        self.assertIsInstance(outer, IfStatement)
        inner = outer.body[0]
        self.assertIsInstance(inner, IfStatement)

    def test_parse_function_with_nested_if(self):
        source = "def f(x):\n    if x:\n        return 1\n    return 0\n"
        prog = _parse(source, language="en")
        func = prog.body[0]
        self.assertIsInstance(func, FunctionDef)
        self.assertEqual(len(func.body), 2)


class ParserMultilingualTestSuite(unittest.TestCase):
    """Tests for parsing in multiple languages."""

    def test_parse_french_if_else(self):
        source = "si x:\n    passer\nsinon:\n    passer\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_body)

    def test_parse_hindi_while_loop(self):
        source = "\u091c\u092c\u0924\u0915 x:\n    \u0930\u094b\u0915\u094b\n"
        prog = _parse(source, language="hi")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WhileLoop)

    def test_parse_chinese_function_def(self):
        source = "\u51fd\u6570 f():\n    \u8fd4\u56de 1\n"
        prog = _parse(source, language="zh")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_parse_arabic_for_loop(self):
        source = "\u0644\u0643\u0644 i \u0641\u064a items:\n    \u0645\u0631\u0631\n"
        prog = _parse(source, language="ar")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)

    def test_parse_japanese_class_def(self):
        source = "\u30af\u30e9\u30b9 Foo:\n    \u30d1\u30b9\n"
        prog = _parse(source, language="ja")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)

    def test_parse_spanish_try_except(self):
        source = "intentar:\n    pasar\nexcepto:\n    pasar\n"
        prog = _parse(source, language="es")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)

    def test_parse_german_match_case(self):
        source = "zuordnen x:\n    fall 1:\n        weiter\n"
        prog = _parse(source, language="de")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, MatchStatement)

    def test_parse_bengali_import(self):
        source = "\u0986\u09ae\u09a6\u09be\u09a8\u09bf os\n"
        prog = _parse(source, language="bn")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ImportStatement)

    def test_parse_tamil_let_const(self):
        source = "\u0b87\u0bb0\u0bc1\u0b95\u0bcd\u0b95\u0b9f\u0bcd\u0b9f\u0bc1\u0bae\u0bcd x = 5\n"
        prog = _parse(source, language="ta")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, VariableDeclaration)

    def test_parse_same_ast_english_french(self):
        """Same program in English and French produces equivalent AST structure."""
        en_source = "if True:\n    pass\n"
        fr_source = "si Vrai:\n    passer\n"
        en_prog = _parse(en_source, language="en")
        fr_prog = _parse(fr_source, language="fr")
        self.assertIsInstance(en_prog.body[0], IfStatement)
        self.assertIsInstance(fr_prog.body[0], IfStatement)
        self.assertIsInstance(en_prog.body[0].condition, BooleanLiteral)
        self.assertIsInstance(fr_prog.body[0].condition, BooleanLiteral)


class ParserErrorTestSuite(unittest.TestCase):
    """Tests for parser error handling."""

    def test_error_missing_colon(self):
        with self.assertRaises(ParseError):
            _parse("if x\n    pass\n", language="en")

    def test_error_unexpected_token(self):
        with self.assertRaises(ParseError):
            _parse("if:\n    pass\n", language="en")

    def test_error_missing_closing_paren(self):
        with self.assertRaises(ParseError):
            _parse("f(1, 2\n", language="en")

    def test_error_missing_closing_bracket(self):
        with self.assertRaises(ParseError):
            _parse("[1, 2\n", language="en")

    def test_error_line_column_in_error(self):
        try:
            _parse("if x\n    pass\n", language="en")
            self.fail("Expected ParseError")
        except ParseError as e:
            self.assertIsNotNone(e.line)


if __name__ == "__main__":
    unittest.main()
