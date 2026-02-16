#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for AST node classes."""

import unittest
from multilingualprogramming.parser.ast_nodes import (
    ASTNode, Program, NumeralLiteral, StringLiteral, DateLiteral,
    BooleanLiteral, NoneLiteral, ListLiteral, DictLiteral,
    Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess, LambdaExpr, YieldExpr,
    VariableDeclaration, Assignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, GlobalStatement, LocalStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, CaseClause,
    WithStatement, ImportStatement, FromImportStatement,
)


class ASTNodeConstructionTestSuite(unittest.TestCase):
    """Tests for constructing AST nodes."""

    def test_numeral_literal(self):
        node = NumeralLiteral("42", line=1, column=1)
        self.assertEqual(node.value, "42")
        self.assertEqual(node.line, 1)

    def test_string_literal(self):
        node = StringLiteral("hello", line=2, column=5)
        self.assertEqual(node.value, "hello")
        self.assertEqual(node.column, 5)

    def test_date_literal(self):
        node = DateLiteral("15-January-2024")
        self.assertEqual(node.value, "15-January-2024")

    def test_boolean_literal_true(self):
        node = BooleanLiteral(True, line=1, column=1)
        self.assertTrue(node.value)

    def test_boolean_literal_false(self):
        node = BooleanLiteral(False)
        self.assertFalse(node.value)

    def test_none_literal(self):
        node = NoneLiteral(line=3, column=1)
        self.assertEqual(node.line, 3)

    def test_list_literal(self):
        elems = [NumeralLiteral("1"), NumeralLiteral("2")]
        node = ListLiteral(elems)
        self.assertEqual(len(node.elements), 2)

    def test_dict_literal(self):
        pairs = [(StringLiteral("a"), NumeralLiteral("1"))]
        node = DictLiteral(pairs)
        self.assertEqual(len(node.pairs), 1)

    def test_identifier(self):
        node = Identifier("x", line=1, column=4)
        self.assertEqual(node.name, "x")

    def test_binary_op(self):
        left = NumeralLiteral("1")
        right = NumeralLiteral("2")
        node = BinaryOp(left, "+", right)
        self.assertEqual(node.op, "+")
        self.assertIs(node.left, left)
        self.assertIs(node.right, right)

    def test_unary_op(self):
        operand = NumeralLiteral("5")
        node = UnaryOp("-", operand)
        self.assertEqual(node.op, "-")

    def test_boolean_op(self):
        a = Identifier("a")
        b = Identifier("b")
        node = BooleanOp("AND", [a, b])
        self.assertEqual(node.op, "AND")
        self.assertEqual(len(node.values), 2)

    def test_compare_op(self):
        left = Identifier("x")
        node = CompareOp(left, [("<", NumeralLiteral("5"))])
        self.assertEqual(len(node.comparators), 1)

    def test_call_expr(self):
        func = Identifier("print")
        args = [StringLiteral("hello")]
        node = CallExpr(func, args)
        self.assertEqual(len(node.args), 1)
        self.assertEqual(len(node.keywords), 0)

    def test_attribute_access(self):
        obj = Identifier("obj")
        node = AttributeAccess(obj, "method")
        self.assertEqual(node.attr, "method")

    def test_index_access(self):
        obj = Identifier("arr")
        idx = NumeralLiteral("0")
        node = IndexAccess(obj, idx)
        self.assertIs(node.index, idx)

    def test_lambda_expr(self):
        body = BinaryOp(Identifier("x"), "+", NumeralLiteral("1"))
        node = LambdaExpr(["x"], body)
        self.assertEqual(node.params, ["x"])

    def test_variable_declaration(self):
        node = VariableDeclaration("x", NumeralLiteral("5"), is_const=False)
        self.assertEqual(node.name, "x")
        self.assertFalse(node.is_const)

    def test_const_declaration(self):
        node = VariableDeclaration("PI", NumeralLiteral("3.14"), is_const=True)
        self.assertTrue(node.is_const)

    def test_assignment(self):
        target = Identifier("x")
        value = NumeralLiteral("10")
        node = Assignment(target, value, op="+=")
        self.assertEqual(node.op, "+=")

    def test_if_statement(self):
        cond = BooleanLiteral(True)
        body = [PassStatement()]
        node = IfStatement(cond, body, else_body=[PassStatement()])
        self.assertIsNotNone(node.else_body)
        self.assertEqual(len(node.elif_clauses), 0)

    def test_while_loop(self):
        cond = BooleanLiteral(True)
        body = [BreakStatement()]
        node = WhileLoop(cond, body)
        self.assertEqual(len(node.body), 1)

    def test_for_loop(self):
        target = Identifier("i")
        iterable = Identifier("items")
        body = [PassStatement()]
        node = ForLoop(target, iterable, body)
        self.assertEqual(node.target.name, "i")

    def test_function_def(self):
        body = [ReturnStatement(NumeralLiteral("1"))]
        node = FunctionDef("fact", ["n"], body)
        self.assertEqual(node.name, "fact")
        self.assertEqual(node.params, ["n"])

    def test_class_def(self):
        body = [PassStatement()]
        node = ClassDef("MyClass", [Identifier("Base")], body)
        self.assertEqual(node.name, "MyClass")
        self.assertEqual(len(node.bases), 1)

    def test_try_statement(self):
        body = [PassStatement()]
        handler = ExceptHandler(Identifier("Error"), "e", [PassStatement()])
        node = TryStatement(body, [handler], finally_body=[PassStatement()])
        self.assertEqual(len(node.handlers), 1)
        self.assertIsNotNone(node.finally_body)

    def test_match_statement(self):
        subject = Identifier("x")
        case1 = CaseClause(NumeralLiteral("1"), [PassStatement()])
        case2 = CaseClause(None, [PassStatement()], is_default=True)
        node = MatchStatement(subject, [case1, case2])
        self.assertEqual(len(node.cases), 2)
        self.assertTrue(node.cases[1].is_default)

    def test_with_statement(self):
        ctx = CallExpr(Identifier("open"), [StringLiteral("f.txt")])
        node = WithStatement(ctx, name="f", body=[PassStatement()])
        self.assertEqual(node.name, "f")

    def test_import_statement(self):
        node = ImportStatement("os", alias="operating_system")
        self.assertEqual(node.module, "os")
        self.assertEqual(node.alias, "operating_system")

    def test_from_import_statement(self):
        node = FromImportStatement("os.path", [("join", None), ("exists", "ex")])
        self.assertEqual(node.module, "os.path")
        self.assertEqual(len(node.names), 2)

    def test_program(self):
        body = [ExpressionStatement(NumeralLiteral("1"))]
        node = Program(body, line=1, column=1)
        self.assertEqual(len(node.body), 1)

    def test_line_column_preserved(self):
        node = Identifier("test", line=42, column=13)
        self.assertEqual(node.line, 42)
        self.assertEqual(node.column, 13)

    def test_visitor_dispatch(self):
        """Test that accept() dispatches to the correct visitor method."""

        class TestVisitor:
            def __init__(self):
                self.visited = None

            def visit_Identifier(self, node):
                self.visited = node.name

            def generic_visit(self, _node):
                self.visited = "generic"

        visitor = TestVisitor()
        node = Identifier("x")
        node.accept(visitor)
        self.assertEqual(visitor.visited, "x")

    def test_visitor_generic_fallback(self):
        """Test that accept() falls back to generic_visit."""

        class TestVisitor:
            def __init__(self):
                self.visited = None

            def generic_visit(self, _node):
                self.visited = "generic"

        visitor = TestVisitor()
        node = NumeralLiteral("42")
        node.accept(visitor)
        self.assertEqual(visitor.visited, "generic")


if __name__ == "__main__":
    unittest.main()
