#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""String and lambda-specific WAT generator tests."""

import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    BinaryOp,
    CallExpr,
    ExpressionStatement,
    Identifier,
    LambdaExpr,
    NumeralLiteral,
    Parameter,
    Program,
    SliceExpr,
    StringLiteral,
    VariableDeclaration,
    IndexAccess,
)


def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _gen(*stmts):
    """Generate WAT for the given top-level statements."""
    return WATCodeGenerator().generate(_prog(*stmts))


class WATStringOpsTestSuite(unittest.TestCase):
    """WAT lowering for string concatenation, indexing, and slicing."""

    def test_compile_time_string_concat(self):
        stmt = VariableDeclaration(
            Identifier("s"),
            BinaryOp(StringLiteral("hello"), "+", StringLiteral(" world")),
        )
        wat = _gen(stmt)
        self.assertIn("str concat (compile-time)", wat)
        self.assertNotIn("call $__str_concat", wat)

    def test_runtime_string_concat_calls_helper(self):
        stmts = [
            VariableDeclaration(Identifier("a"), StringLiteral("hi")),
            VariableDeclaration(
                Identifier("b"),
                BinaryOp(Identifier("a"), "+", StringLiteral("!")),
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_concat", wat)
        self.assertIn("str concat (runtime)", wat)

    def test_string_index_calls_slice_helper(self):
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(IndexAccess(Identifier("s"), NumeralLiteral("0"))),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_slice", wat)
        self.assertIn("single-character string", wat)

    def test_string_slice_calls_helper(self):
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(
                IndexAccess(Identifier("s"), SliceExpr(NumeralLiteral("1"), NumeralLiteral("3")))
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_slice", wat)
        self.assertIn("string slice", wat)

    def test_string_slice_no_start_uses_zero(self):
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(
                IndexAccess(Identifier("s"), SliceExpr(stop=NumeralLiteral("3")))
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_slice", wat)
        self.assertIn("f64.const 0", wat)


class WATLambdaTableTestSuite(unittest.TestCase):
    """WAT lambda function pointers via WAT table + call_indirect."""

    def test_lambda_emits_table_and_index(self):
        stmt = VariableDeclaration(
            Identifier("f"),
            LambdaExpr(
                params=[Parameter(Identifier("x"))],
                body=Identifier("x"),
            ),
        )
        wat = _gen(stmt)
        self.assertIn("(table", wat)
        self.assertIn("(elem", wat)
        self.assertIn("f64.const 0.0", wat)

    def test_lambda_call_emits_call_indirect(self):
        stmts = [
            VariableDeclaration(
                Identifier("f"),
                LambdaExpr(
                    params=[Parameter(Identifier("x"))],
                    body=Identifier("x"),
                ),
            ),
            ExpressionStatement(CallExpr(Identifier("f"), [NumeralLiteral("42")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("call_indirect", wat)
        self.assertIn("(table", wat)

    def test_two_lambdas_get_distinct_table_indices(self):
        stmts = [
            VariableDeclaration(
                Identifier("f"),
                LambdaExpr(params=[Parameter(Identifier("x"))], body=Identifier("x")),
            ),
            VariableDeclaration(
                Identifier("g"),
                LambdaExpr(params=[Parameter(Identifier("y"))], body=Identifier("y")),
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.const 0.0", wat)
        self.assertIn("f64.const 1.0", wat)


if __name__ == "__main__":
    unittest.main()
