#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the Python code generator."""

import unittest

from multilingualprogramming.parser.ast_nodes import (
    Program, NumeralLiteral, StringLiteral, BooleanLiteral,
    NoneLiteral, ListLiteral, DictLiteral, DateLiteral,
    Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess, LambdaExpr,
    ConditionalExpr,
    VariableDeclaration, Assignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, GlobalStatement, LocalStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, CaseClause,
    WithStatement, ImportStatement, FromImportStatement,
)
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator


class PythonGeneratorExpressionTestSuite(unittest.TestCase):
    """Test expression code generation."""

    def setUp(self):
        self.gen = PythonCodeGenerator()

    def _gen_expr(self, node):
        """Generate code for a single expression wrapped in a program."""
        prog = Program([ExpressionStatement(node)])
        return self.gen.generate(prog).strip()

    def test_numeral_literal_ascii(self):
        result = self._gen_expr(NumeralLiteral("42"))
        self.assertEqual(result, "42")

    def test_numeral_literal_devanagari(self):
        result = self._gen_expr(NumeralLiteral("१२३"))
        self.assertEqual(result, "123")

    def test_numeral_literal_arabic_indic(self):
        result = self._gen_expr(NumeralLiteral("٤٥٦"))
        self.assertEqual(result, "456")

    def test_numeral_literal_roman(self):
        result = self._gen_expr(NumeralLiteral("XIV"))
        self.assertEqual(result, "14")

    def test_string_literal(self):
        result = self._gen_expr(StringLiteral("hello"))
        self.assertEqual(result, "'hello'")

    def test_boolean_true(self):
        result = self._gen_expr(BooleanLiteral(True))
        self.assertEqual(result, "True")

    def test_boolean_false(self):
        result = self._gen_expr(BooleanLiteral(False))
        self.assertEqual(result, "False")

    def test_none_literal(self):
        result = self._gen_expr(NoneLiteral())
        self.assertEqual(result, "None")

    def test_list_literal(self):
        result = self._gen_expr(
            ListLiteral([NumeralLiteral("1"), NumeralLiteral("2")])
        )
        self.assertEqual(result, "[1, 2]")

    def test_dict_literal(self):
        result = self._gen_expr(
            DictLiteral([
                (StringLiteral("a"), NumeralLiteral("1")),
            ])
        )
        self.assertEqual(result, "{'a': 1}")

    def test_date_literal(self):
        result = self._gen_expr(DateLiteral("2024-01-15"))
        self.assertEqual(result, "'2024-01-15'")

    def test_identifier(self):
        result = self._gen_expr(Identifier("x"))
        self.assertEqual(result, "x")

    def test_binary_op(self):
        result = self._gen_expr(
            BinaryOp(NumeralLiteral("1"), "+", NumeralLiteral("2"))
        )
        self.assertEqual(result, "(1 + 2)")

    def test_unary_op(self):
        result = self._gen_expr(
            UnaryOp("-", NumeralLiteral("5"))
        )
        self.assertEqual(result, "(-5)")

    def test_boolean_op_and(self):
        result = self._gen_expr(
            BooleanOp("AND", [Identifier("a"), Identifier("b")])
        )
        self.assertEqual(result, "(a and b)")

    def test_boolean_op_or(self):
        result = self._gen_expr(
            BooleanOp("OR", [Identifier("x"), Identifier("y")])
        )
        self.assertEqual(result, "(x or y)")

    def test_compare_op(self):
        result = self._gen_expr(
            CompareOp(Identifier("x"), [("<", NumeralLiteral("10"))])
        )
        self.assertEqual(result, "(x < 10)")

    def test_chained_comparison(self):
        result = self._gen_expr(
            CompareOp(
                NumeralLiteral("1"),
                [("<", Identifier("x")), ("<", NumeralLiteral("10"))]
            )
        )
        self.assertEqual(result, "(1 < x < 10)")

    def test_call_expr(self):
        result = self._gen_expr(
            CallExpr(Identifier("print"), [StringLiteral("hi")])
        )
        self.assertEqual(result, "print('hi')")

    def test_call_expr_kwargs(self):
        result = self._gen_expr(
            CallExpr(
                Identifier("f"),
                [NumeralLiteral("1")],
                [("key", StringLiteral("val"))]
            )
        )
        self.assertEqual(result, "f(1, key='val')")

    def test_attribute_access(self):
        result = self._gen_expr(
            AttributeAccess(Identifier("obj"), "method")
        )
        self.assertEqual(result, "obj.method")

    def test_index_access(self):
        result = self._gen_expr(
            IndexAccess(Identifier("arr"), NumeralLiteral("0"))
        )
        self.assertEqual(result, "arr[0]")

    def test_lambda_expr(self):
        result = self._gen_expr(
            LambdaExpr(["x"], BinaryOp(Identifier("x"), "*", NumeralLiteral("2")))
        )
        self.assertEqual(result, "(lambda x: (x * 2))")

    def test_conditional_expr(self):
        result = self._gen_expr(
            ConditionalExpr(
                Identifier("cond"),
                NumeralLiteral("1"),
                NumeralLiteral("0")
            )
        )
        self.assertEqual(result, "(1 if cond else 0)")

    def test_unary_bitwise_not(self):
        result = self._gen_expr(UnaryOp("~", Identifier("x")))
        self.assertEqual(result, "(~x)")


class PythonGeneratorStatementTestSuite(unittest.TestCase):
    """Test statement code generation."""

    def setUp(self):
        self.gen = PythonCodeGenerator()

    def _gen(self, *stmts):
        prog = Program(list(stmts))
        return self.gen.generate(prog).strip()

    def test_variable_declaration(self):
        result = self._gen(VariableDeclaration("x", NumeralLiteral("10")))
        self.assertEqual(result, "x = 10")

    def test_const_declaration(self):
        # const generates same Python as let (Python has no const)
        result = self._gen(
            VariableDeclaration("PI", NumeralLiteral("3.14"), is_const=True)
        )
        self.assertIn("PI = ", result)

    def test_assignment(self):
        result = self._gen(
            Assignment(Identifier("x"), NumeralLiteral("5"))
        )
        self.assertEqual(result, "x = 5")

    def test_augmented_assignment(self):
        result = self._gen(
            Assignment(Identifier("x"), NumeralLiteral("1"), op="+=")
        )
        self.assertEqual(result, "x += 1")

    def test_pass_statement(self):
        result = self._gen(PassStatement())
        self.assertEqual(result, "pass")

    def test_return_with_value(self):
        result = self._gen(ReturnStatement(NumeralLiteral("42")))
        self.assertEqual(result, "return 42")

    def test_return_bare(self):
        result = self._gen(ReturnStatement())
        self.assertEqual(result, "return")

    def test_break(self):
        result = self._gen(BreakStatement())
        self.assertEqual(result, "break")

    def test_continue(self):
        result = self._gen(ContinueStatement())
        self.assertEqual(result, "continue")

    def test_raise_with_value(self):
        result = self._gen(
            RaiseStatement(CallExpr(Identifier("ValueError"), [StringLiteral("bad")]))
        )
        self.assertEqual(result, "raise ValueError('bad')")

    def test_raise_bare(self):
        result = self._gen(RaiseStatement())
        self.assertEqual(result, "raise")

    def test_global_statement(self):
        result = self._gen(GlobalStatement(["x", "y"]))
        self.assertEqual(result, "global x, y")

    def test_local_statement(self):
        result = self._gen(LocalStatement(["count"]))
        self.assertEqual(result, "nonlocal count")

    def test_import_simple(self):
        result = self._gen(ImportStatement("math"))
        self.assertEqual(result, "import math")

    def test_import_alias(self):
        result = self._gen(ImportStatement("numpy", alias="np"))
        self.assertEqual(result, "import numpy as np")

    def test_from_import(self):
        result = self._gen(
            FromImportStatement("math", [("sqrt", None), ("pi", None)])
        )
        self.assertEqual(result, "from math import sqrt, pi")

    def test_from_import_alias(self):
        result = self._gen(
            FromImportStatement("os.path", [("join", "pjoin")])
        )
        self.assertEqual(result, "from os.path import join as pjoin")


class PythonGeneratorCompoundTestSuite(unittest.TestCase):
    """Test compound statement code generation."""

    def setUp(self):
        self.gen = PythonCodeGenerator()

    def _gen(self, *stmts):
        prog = Program(list(stmts))
        return self.gen.generate(prog)

    def test_if_statement(self):
        result = self._gen(
            IfStatement(
                Identifier("x"),
                [ExpressionStatement(
                    CallExpr(Identifier("print"), [StringLiteral("yes")])
                )]
            )
        )
        self.assertIn("if x:", result)
        self.assertIn("    print('yes')", result)

    def test_if_else(self):
        result = self._gen(
            IfStatement(
                Identifier("x"),
                [PassStatement()],
                else_body=[PassStatement()]
            )
        )
        self.assertIn("if x:", result)
        self.assertIn("else:", result)

    def test_if_elif_else(self):
        result = self._gen(
            IfStatement(
                CompareOp(Identifier("x"), [("==", NumeralLiteral("1"))]),
                [PassStatement()],
                elif_clauses=[
                    (CompareOp(Identifier("x"), [("==", NumeralLiteral("2"))]),
                     [PassStatement()])
                ],
                else_body=[PassStatement()]
            )
        )
        self.assertIn("if (x == 1):", result)
        self.assertIn("elif (x == 2):", result)
        self.assertIn("else:", result)

    def test_while_loop(self):
        result = self._gen(
            WhileLoop(
                BooleanLiteral(True),
                [BreakStatement()]
            )
        )
        self.assertIn("while True:", result)
        self.assertIn("    break", result)

    def test_for_loop(self):
        result = self._gen(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("range"), [NumeralLiteral("10")]),
                [ExpressionStatement(
                    CallExpr(Identifier("print"), [Identifier("i")])
                )]
            )
        )
        self.assertIn("for i in range(10):", result)
        self.assertIn("    print(i)", result)

    def test_function_def(self):
        result = self._gen(
            FunctionDef(
                "add",
                ["a", "b"],
                [ReturnStatement(
                    BinaryOp(Identifier("a"), "+", Identifier("b"))
                )]
            )
        )
        self.assertIn("def add(a, b):", result)
        self.assertIn("    return (a + b)", result)

    def test_class_def(self):
        result = self._gen(
            ClassDef(
                "Animal",
                [],
                [FunctionDef(
                    "__init__",
                    ["self", "name"],
                    [Assignment(
                        AttributeAccess(Identifier("self"), "name"),
                        Identifier("name")
                    )]
                )]
            )
        )
        self.assertIn("class Animal:", result)
        self.assertIn("    def __init__(self, name):", result)
        self.assertIn("        self.name = name", result)

    def test_class_with_base(self):
        result = self._gen(
            ClassDef("Dog", [Identifier("Animal")], [PassStatement()])
        )
        self.assertIn("class Dog(Animal):", result)

    def test_try_except(self):
        result = self._gen(
            TryStatement(
                [ExpressionStatement(
                    CallExpr(Identifier("risky"), [])
                )],
                handlers=[
                    ExceptHandler(
                        Identifier("ValueError"),
                        "e",
                        [ExpressionStatement(
                            CallExpr(Identifier("print"), [Identifier("e")])
                        )]
                    )
                ]
            )
        )
        self.assertIn("try:", result)
        self.assertIn("    risky()", result)
        self.assertIn("except ValueError as e:", result)
        self.assertIn("    print(e)", result)

    def test_try_except_finally(self):
        result = self._gen(
            TryStatement(
                [PassStatement()],
                handlers=[ExceptHandler(body=[PassStatement()])],
                finally_body=[
                    ExpressionStatement(
                        CallExpr(Identifier("cleanup"), [])
                    )
                ]
            )
        )
        self.assertIn("try:", result)
        self.assertIn("except:", result)
        self.assertIn("finally:", result)
        self.assertIn("    cleanup()", result)

    def test_match_statement(self):
        result = self._gen(
            MatchStatement(
                Identifier("cmd"),
                [
                    CaseClause(StringLiteral("start"), [PassStatement()]),
                    CaseClause(is_default=True, body=[PassStatement()]),
                ]
            )
        )
        self.assertIn("match cmd:", result)
        self.assertIn("    case 'start':", result)
        self.assertIn("    case _:", result)

    def test_with_statement(self):
        result = self._gen(
            WithStatement(
                CallExpr(Identifier("open"), [StringLiteral("f.txt")]),
                name="f",
                body=[ExpressionStatement(
                    CallExpr(
                        AttributeAccess(Identifier("f"), "read"), []
                    )
                )]
            )
        )
        self.assertIn("with open('f.txt') as f:", result)
        self.assertIn("    f.read()", result)

    def test_empty_body_gets_pass(self):
        result = self._gen(
            FunctionDef("noop", [], [])
        )
        self.assertIn("def noop():", result)
        self.assertIn("    pass", result)

    def test_nested_function(self):
        result = self._gen(
            FunctionDef(
                "outer",
                [],
                [FunctionDef(
                    "inner",
                    [],
                    [ReturnStatement(NumeralLiteral("1"))]
                ),
                 ReturnStatement(
                     CallExpr(Identifier("inner"), [])
                 )]
            )
        )
        self.assertIn("def outer():", result)
        self.assertIn("    def inner():", result)
        self.assertIn("        return 1", result)
        self.assertIn("    return inner()", result)


class PythonGeneratorMultilingualTestSuite(unittest.TestCase):
    """Test code generation with multilingual numerals."""

    def setUp(self):
        self.gen = PythonCodeGenerator()

    def _gen(self, *stmts):
        prog = Program(list(stmts))
        return self.gen.generate(prog)

    def test_devanagari_numeral_in_expression(self):
        """Hindi numerals should be converted to Python integers."""
        result = self._gen(
            VariableDeclaration(
                "x",
                BinaryOp(NumeralLiteral("१०"), "+", NumeralLiteral("२०"))
            )
        )
        self.assertIn("x = (10 + 20)", result)

    def test_arabic_indic_numeral(self):
        """Arabic-Indic numerals should be converted."""
        result = self._gen(
            VariableDeclaration("y", NumeralLiteral("٧٨٩"))
        )
        self.assertIn("y = 789", result)

    def test_bengali_numeral(self):
        """Bengali numerals should be converted."""
        result = self._gen(
            VariableDeclaration("z", NumeralLiteral("৪৫"))
        )
        self.assertIn("z = 45", result)

    def test_roman_numeral(self):
        """Roman numerals should be converted to integers."""
        result = self._gen(
            VariableDeclaration("r", NumeralLiteral("XLII"))
        )
        self.assertIn("r = 42", result)

    def test_factorial_program(self):
        """Generate a complete factorial program."""
        result = self._gen(
            FunctionDef(
                "factorial",
                ["n"],
                [
                    IfStatement(
                        CompareOp(Identifier("n"), [("<=", NumeralLiteral("1"))]),
                        [ReturnStatement(NumeralLiteral("1"))]
                    ),
                    ReturnStatement(
                        BinaryOp(
                            Identifier("n"), "*",
                            CallExpr(
                                Identifier("factorial"),
                                [BinaryOp(Identifier("n"), "-", NumeralLiteral("1"))]
                            )
                        )
                    )
                ]
            ),
            ExpressionStatement(
                CallExpr(Identifier("print"), [
                    CallExpr(Identifier("factorial"), [NumeralLiteral("5")])
                ])
            )
        )
        self.assertIn("def factorial(n):", result)
        self.assertIn("if (n <= 1):", result)
        self.assertIn("return 1", result)
        self.assertIn("return (n * factorial((n - 1)))", result)
        self.assertIn("print(factorial(5))", result)
