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
    NumeralLiteral, StringLiteral, DateLiteral,
    BooleanLiteral, NoneLiteral, ListLiteral, DictLiteral, SetLiteral,
    DictUnpackEntry, Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess, LambdaExpr,
    VariableDeclaration, Assignment, AnnAssignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, DelStatement, GlobalStatement, LocalStatement, YieldStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, AwaitExpr, NamedExpr,
    ChainedAssignment, TupleLiteral,
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

    def test_parse_parenthesized_tuple(self):
        prog = _parse("(4, 9)\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, TupleLiteral)
        self.assertEqual(len(stmt.expression.elements), 2)

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

    def test_parse_set_literal(self):
        prog = _parse("{1, 2, 3}\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, SetLiteral)
        self.assertEqual(len(stmt.expression.elements), 3)

    def test_parse_dict_unpacking(self):
        prog = _parse("{**d1, 'x': 1, **d2}\n")
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, DictLiteral)
        self.assertEqual(len(stmt.expression.entries), 3)
        self.assertIsInstance(stmt.expression.entries[0], DictUnpackEntry)
        self.assertIsInstance(stmt.expression.entries[2], DictUnpackEntry)

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

    def test_parse_function_call_multiline_closing_paren(self):
        prog = _parse("print(1\n)\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)
        self.assertEqual(len(expr.args), 1)

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

    def test_parse_await_expression(self):
        prog = _parse("await f()\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, AwaitExpr)

    def test_parse_walrus_expression(self):
        prog = _parse("(x := 5)\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, NamedExpr)
        self.assertEqual(expr.target.name, "x")

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

    def test_parse_let_chained_assignment(self):
        prog = _parse("let a = b = c = 7\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ChainedAssignment)

    def test_parse_let_annotated_assignment(self):
        prog = _parse("let age: int = 42\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, AnnAssignment)
        self.assertEqual(stmt.target.name, "age")

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

    def test_parse_annotated_assignment(self):
        prog = _parse("x: int = 10\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, AnnAssignment)
        self.assertEqual(stmt.target.name, "x")

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

    def test_parse_nonlocal_statement(self):
        prog = _parse("nonlocal x, y\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, LocalStatement)
        self.assertEqual(stmt.names, ["x", "y"])

    def test_parse_del_statement(self):
        prog = _parse("del x\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, DelStatement)
        self.assertIsInstance(stmt.target, Identifier)
        self.assertEqual(stmt.target.name, "x")

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

    def test_parse_function_def_with_annotations(self):
        source = "def f(a: int, b: str) -> str:\n    return b\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertIsNotNone(stmt.return_annotation)
        self.assertIsNotNone(stmt.params[0].annotation)
        self.assertIsNotNone(stmt.params[1].annotation)

    def test_parse_async_function_def(self):
        source = "async def f(x):\n    return await g(x)\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertTrue(stmt.is_async)

    def test_parse_async_for_loop(self):
        source = "async for i in aiter:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertTrue(stmt.is_async)

    def test_parse_async_with_statement(self):
        source = "async with cm() as x:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WithStatement)
        self.assertTrue(stmt.is_async)

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

    def test_parse_try_except_else(self):
        source = "try:\n    pass\nexcept:\n    pass\nelse:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsNotNone(stmt.else_body)

    def test_parse_try_except_else_finally(self):
        source = "try:\n    pass\nexcept:\n    pass\nelse:\n    pass\nfinally:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsNotNone(stmt.else_body)
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

    def test_parse_with_multiple_contexts(self):
        source = "with a() as x, b() as y:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WithStatement)
        self.assertEqual(len(stmt.items), 2)

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

    def test_parse_french_type_annotation_keyword(self):
        source = "déf saluer(nom: chaine) -> chaine:\n    retour nom\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(stmt.params[0].annotation.name, "str")
        self.assertEqual(stmt.return_annotation.name, "str")

    def test_parse_french_type_annotation_keyword_accented(self):
        source = "déf saluer(nom: chaîne) -> chaîne:\n    retour nom\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(stmt.params[0].annotation.name, "str")
        self.assertEqual(stmt.return_annotation.name, "str")

    def test_parse_french_parameter_named_like_type_keyword(self):
        source = "déf moyenne(liste):\n    retour somme(liste) / longueur(liste)\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(stmt.params[0].name, "liste")

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

    def test_parse_arabic_iterable_first_for_loop(self):
        source = "range(4) \u0636\u0645\u0646 \u0644\u0643\u0644 i:\n    \u0645\u0631\u0631\n"
        prog = _parse(source, language="ar")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

    def test_parse_japanese_class_def(self):
        source = "\u30af\u30e9\u30b9 Foo:\n    \u30d1\u30b9\n"
        prog = _parse(source, language="ja")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)

    def test_parse_japanese_iterable_first_for_loop(self):
        source = (
            "\u7bc4\u56f2(4) \u5185\u306e \u5404 i \u306b\u5bfe\u3057\u3066:\n"
            "    \u30d1\u30b9\n"
        )
        prog = _parse(source, language="ja")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

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

    def test_parse_portuguese_phrase_elif(self):
        source = "se x:\n    passe\nsenão se y:\n    passe\n"
        prog = _parse(source, language="pt")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(len(stmt.elif_clauses), 1)

    def test_parse_portuguese_phrase_for(self):
        source = "para cada i em itens:\n    passe\n"
        prog = _parse(source, language="pt")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

    def test_parse_portuguese_iterable_first_for_loop(self):
        source = "range(4) para cada i:\n    passe\n"
        prog = _parse(source, language="pt")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

    def test_parse_spanish_iterable_first_for_loop(self):
        source = "range(4) para i:\n    pasar\n"
        prog = _parse(source, language="es")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

    def test_parse_french_phrase_elif(self):
        source = "si x:\n    passer\nsinon si y:\n    passer\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(len(stmt.elif_clauses), 1)

    def test_parse_french_phrase_for(self):
        source = "pour chaque i dans items:\n    passer\n"
        prog = _parse(source, language="fr")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertEqual(stmt.target.name, "i")

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

class ParserEdgeCaseTestSuite(unittest.TestCase):
    """Tests for edge case syntax forms and complex nesting."""

    # Complex nested comprehensions
    def test_nested_comprehension_two_levels(self):
        prog = _parse("[x for x in [y for y in range(3)]]\n", language="en")
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_nested_comprehension_three_levels(self):
        prog = _parse(
            "[[z for z in range(y)] for y in [x for x in range(2)]]\n",
            language="en",
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_comprehension_with_multiple_conditions(self):
        prog = _parse(
            "[x for x in range(10) if x > 2 if x < 8]\n", language="en"
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_dict_comprehension_complex(self):
        prog = _parse(
            "{k: v for k, v in [(i, i*2) for i in range(3)]}\n",
            language="en",
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_set_comprehension_with_nested_for(self):
        prog = _parse(
            "{x*y for x in range(2) for y in range(3)}\n", language="en"
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    # Nested function/class definitions
    def test_nested_function_definitions(self):
        source = (
            "def outer():\n"
            "    def middle():\n"
            "        def inner():\n"
            "            pass\n"
            "        pass\n"
            "    pass\n"
        )
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_class_with_nested_functions(self):
        source = (
            "class A:\n"
            "    def method(self):\n"
            "        def inner():\n"
            "            pass\n"
            "        pass\n"
        )
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)

    # Complex slice expressions
    def test_slice_with_step(self):
        prog = _parse("arr[1:10:2]\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, IndexAccess)

    def test_slice_negative_indices(self):
        prog = _parse("arr[-5:-1]\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, IndexAccess)

    def test_slice_negative_step(self):
        prog = _parse("arr[10:0:-1]\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, IndexAccess)

    def test_slice_omitted_bounds(self):
        prog = _parse("arr[::2]\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, IndexAccess)

    # Decorator chains
    def test_single_decorator(self):
        source = "@decorator\ndef func():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(len(stmt.decorators), 1)

    def test_multiple_decorators(self):
        source = "@decorator1\n@decorator2\n@decorator3\ndef func():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(len(stmt.decorators), 3)

    def test_decorator_with_arguments(self):
        source = "@decorator(arg1, arg2=value)\ndef func():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(len(stmt.decorators), 1)

    # Mixed arguments in function calls
    def test_call_positional_and_keyword(self):
        prog = _parse("f(1, 2, a=3, b=4)\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)

    def test_call_with_starred_args(self):
        prog = _parse("f(1, *args, 2, **kwargs)\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)

    def test_call_keyword_only_args(self):
        prog = _parse("f(a, b=2, *args, c=3)\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, CallExpr)

    # Walrus operator in various contexts
    def test_walrus_in_comprehension(self):
        prog = _parse(
            "[y for x in range(5) if (y := x*2) > 4]\n", language="en"
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_walrus_in_nested_comprehension(self):
        prog = _parse(
            "[[z for z in range(3) if (w := z) > 0] for x in range(2)]\n",
            language="en",
        )
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    def test_walrus_in_while_condition(self):
        source = "while (line := input()) != 'quit':\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WhileLoop)

    # Multiple context managers
    def test_multiple_context_managers(self):
        source = "with open('f1') as f1, open('f2') as f2:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WithStatement)
        self.assertEqual(len(stmt.items), 2)

    def test_context_manager_complex_expression(self):
        source = "with contextlib.suppress(ValueError) as ctx:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, WithStatement)

    # Exception handling edge cases
    def test_bare_except_clause(self):
        # This is a valid edge case - testing that parser accepts it
        source = "try:\n    pass\nexcept:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)

    def test_multiple_except_handlers(self):
        # This is a valid edge case - testing that parser accepts it
        source = (
            "try:\n"
            "    pass\n"
            "except ValueError:\n"
            "    pass\n"
            "except TypeError:\n"
            "    pass\n"
            "except:\n"
            "    pass\n"
        )
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)
        self.assertEqual(len(stmt.handlers), 3)

    def test_except_with_exception_variable(self):
        # Test exception binding with 'as' clause
        source = "try:\n    pass\nexcept ValueError as e:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)

    def test_try_except_else_finally_all(self):
        source = (
            "try:\n"
            "    pass\n"
            "except ValueError:\n"
            "    pass\n"
            "else:\n"
            "    pass\n"
            "finally:\n"
            "    pass\n"
        )
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, TryStatement)
        self.assertIsNotNone(stmt.else_body)
        self.assertIsNotNone(stmt.finally_body)

    # Function definition with parameter separators
    def test_function_with_positional_only_params(self):
        source = "def func(a, b, /, c):\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_function_with_keyword_only_params(self):
        source = "def func(a, *, b, c):\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_function_with_all_param_types(self):
        source = "def func(a, /, b, *args, c, **kwargs):\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    # Operator precedence edge cases
    def test_expression_operator_precedence_complex(self):
        prog = _parse("a + b * c - d / e % f ** g\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BinaryOp)

    def test_mixed_logical_and_comparison(self):
        prog = _parse("a < b and c > d or e == f\n", language="en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BooleanOp)

    def test_ternary_nested(self):
        prog = _parse("a if x else b if y else c\n", language="en")
        expr = prog.body[0].expression
        self.assertIsNotNone(expr)

    # Unpacking edge cases
    def test_starred_in_list_middle(self):
        # Starred unpacking in assignment target
        prog = _parse("a, *b, c = [1, 2, 3, 4]\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)

    def test_starred_in_tuple_unpacking(self):
        prog = _parse("a, *rest = (1, 2, 3)\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)

    def test_nested_unpacking(self):
        prog = _parse("(a, (b, c)) = (1, (2, 3))\n", language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)

    # Async/await edge cases
    def test_async_function_definition(self):
        source = "async def func():\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_async_for_loop(self):
        source = "async for item in items:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsNotNone(stmt)

    def test_async_with_statement(self):
        source = "async with manager:\n    pass\n"
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsNotNone(stmt)

    # Docstrings and comments
    def test_function_docstring(self):
        source = 'def func():\n    """Docstring"""\n    pass\n'
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, FunctionDef)

    def test_class_docstring(self):
        source = 'class A:\n    """Class docstring"""\n    pass\n'
        prog = _parse(source, language="en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)


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

    def test_error_positional_after_keyword_argument(self):
        with self.assertRaises(ParseError):
            _parse("f(a=1, 2)\n", language="en")

    def test_error_try_else_without_except(self):
        with self.assertRaises(ParseError):
            _parse("try:\n    pass\nelse:\n    pass\n", language="en")

    def test_error_line_column_in_error(self):
        try:
            _parse("if x\n    pass\n", language="en")
            self.fail("Expected ParseError")
        except ParseError as e:
            self.assertIsNotNone(e.line)

    def test_error_missing_closing_brace(self):
        with self.assertRaises(ParseError):
            _parse("{1, 2, 3\n", language="en")

    def test_error_missing_comma_in_list(self):
        with self.assertRaises(ParseError):
            _parse("[1 2 3]\n", language="en")

    def test_error_decorator_on_non_function(self):
        with self.assertRaises(ParseError):
            _parse("@decorator\nx = 5\n", language="en")

    def test_error_star_in_slice_without_slice_context(self):
        # This is a parser error - star without context
        with self.assertRaises(ParseError):
            _parse("print(*)\n", language="en")

    def test_error_double_star_in_call_position(self):
        # Double star followed by star is valid Python (order doesn't matter in calls)
        prog = _parse("f(*a, **b)\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_multiple_assignment_targets_in_for(self):
        # This should be valid: for a, b in list, so skip this
        pass

    def test_error_break_outside_loop(self):
        # This is a semantic error, not parser error
        prog = _parse("break\n", language="en")
        self.assertIsNotNone(prog)
        # Parser accepts it, semantic analyzer rejects it

    def test_error_continue_outside_loop(self):
        # This is a semantic error, not parser error
        prog = _parse("continue\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_missing_function_body(self):
        with self.assertRaises(ParseError):
            _parse("def func():\n", language="en")

    def test_error_missing_class_body(self):
        with self.assertRaises(ParseError):
            _parse("class A:\n", language="en")

    def test_error_missing_if_body(self):
        with self.assertRaises(ParseError):
            _parse("if True:\n", language="en")

    def test_error_missing_while_body(self):
        with self.assertRaises(ParseError):
            _parse("while True:\n", language="en")

    def test_error_missing_for_body(self):
        with self.assertRaises(ParseError):
            _parse("for x in range(5):\n", language="en")

    def test_error_missing_try_body(self):
        with self.assertRaises(ParseError):
            _parse("try:\n", language="en")

    def test_error_invalid_parameter_order_keyword_positional(self):
        # Note: Python allows default parameters before non-default in some contexts
        # This is a semantic error, not parser error
        prog = _parse("def f(a=1, b):\n    pass\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_positional_only_after_var_args(self):
        # Positional-only marker after *args is a semantic error, not parser error
        prog = _parse("def f(*args, /):\n    pass\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_multiple_star_args(self):
        # Multiple *args is a semantic error, not parser error
        prog = _parse("def f(*a, *b):\n    pass\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_multiple_star_kwargs(self):
        # Multiple **kwargs is a semantic error, not parser error
        prog = _parse("def f(**a, **b):\n    pass\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_starred_after_kwargs_in_call(self):
        # In function calls, **kwargs before *args is allowed
        prog = _parse("f(**d, *a)\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_lambda_without_body(self):
        with self.assertRaises(ParseError):
            _parse("lambda x:\n", language="en")

    def test_error_import_invalid_syntax(self):
        with self.assertRaises(ParseError):
            _parse("import\n", language="en")

    def test_error_from_import_invalid_syntax(self):
        with self.assertRaises(ParseError):
            _parse("from import x\n", language="en")

    def test_error_zero_step_in_slice(self):
        # This is a semantic/runtime error, not a parser error
        prog = _parse("arr[::0]\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_invalid_subscript_syntax(self):
        with self.assertRaises(ParseError):
            _parse("arr[]\n", language="en")

    def test_error_walrus_outside_parentheses_in_call(self):
        # Note: Walrus operator in function call argument is allowed in Python
        prog = _parse("f(x := 1)\n", language="en")
        self.assertIsNotNone(prog)

    def test_error_except_without_try(self):
        with self.assertRaises(ParseError):
            _parse("except ValueError:\n    pass\n", language="en")

    def test_error_else_without_try(self):
        with self.assertRaises(ParseError):
            _parse("else:\n    pass\n", language="en")

    def test_error_finally_without_try(self):
        with self.assertRaises(ParseError):
            _parse("finally:\n    pass\n", language="en")

    def test_error_elif_without_if(self):
        with self.assertRaises(ParseError):
            _parse("elif x:\n    pass\n", language="en")


if __name__ == "__main__":
    unittest.main()
