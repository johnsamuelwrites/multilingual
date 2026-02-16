#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Programmatic AST construction and printing."""

from multilingualprogramming.parser.ast_nodes import (
    Program, FunctionDef, IfStatement, ReturnStatement,
    BinaryOp, CompareOp, CallExpr, Identifier, NumeralLiteral,
)
from multilingualprogramming.parser.ast_printer import ASTPrinter

# Build a factorial function AST by hand:
#   def factorial(n):
#       if n <= 1:
#           return 1
#       return n * factorial(n - 1)

FACTORIAL = FunctionDef(
    name="factorial",
    params=["n"],
    body=[
        IfStatement(
            condition=CompareOp(
                left=Identifier("n"),
                comparators=[("<=", NumeralLiteral("1"))],
            ),
            body=[
                ReturnStatement(value=NumeralLiteral("1")),
            ],
        ),
        ReturnStatement(
            value=BinaryOp(
                left=Identifier("n"),
                op="*",
                right=CallExpr(
                    func=Identifier("factorial"),
                    args=[
                        BinaryOp(
                            left=Identifier("n"),
                            op="-",
                            right=NumeralLiteral("1"),
                        ),
                    ],
                ),
            ),
        ),
    ],
    line=1, column=1,
)

PROGRAM = Program(body=[FACTORIAL], line=1, column=1)

printer = ASTPrinter()
print("=== Programmatic AST ===")
print(printer.print(PROGRAM))
