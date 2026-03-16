#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Focused tests for WAT string helper emission and lowering."""

import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    AttributeAccess,
    CallExpr,
    ExpressionStatement,
    Identifier,
    PassStatement,
    Program,
    StringLiteral,
    VariableDeclaration,
)


class WATStringHelpersTestSuite(unittest.TestCase):
    """Verify WAT string helper emission and lowering."""

    def _gen(self, prog):
        gen = WATCodeGenerator()
        return gen.generate(prog)

    def test_str_strip_helper_emitted(self):
        """$__str_strip is always emitted as part of the WASI runtime."""
        wat = self._gen(Program([PassStatement()]))
        self.assertIn("$__str_strip", wat)

    def test_str_find_helper_emitted(self):
        """$__str_find is always emitted as part of the WASI runtime."""
        wat = self._gen(Program([PassStatement()]))
        self.assertIn("$__str_find", wat)

    def test_strip_call_lowered(self):
        """s.strip() on a string variable lowers to call $__str_strip."""
        prog = Program([
            VariableDeclaration("s", StringLiteral("  hello  ")),
            ExpressionStatement(
                CallExpr(AttributeAccess(Identifier("s"), "strip"), [])
            ),
        ])
        wat = self._gen(prog)
        self.assertIn("call $__str_strip", wat)

    def test_find_call_lowered(self):
        """s.find(needle) on a string variable lowers to call $__str_find."""
        prog = Program([
            VariableDeclaration("s", StringLiteral("hello world")),
            VariableDeclaration(
                "idx",
                CallExpr(
                    AttributeAccess(Identifier("s"), "find"),
                    [StringLiteral("world")],
                ),
            ),
        ])
        wat = self._gen(prog)
        self.assertIn("call $__str_find", wat)


if __name__ == "__main__":
    unittest.main()
