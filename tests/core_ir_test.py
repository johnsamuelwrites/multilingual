#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for core IR typing and lowering boundaries."""

import unittest

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.core.lowering import lower_to_core_ir
from multilingualprogramming.parser.ast_nodes import (
    Program,
    VariableDeclaration,
    NumeralLiteral,
)


class CoreIRTestSuite(unittest.TestCase):
    """Validate the typed Core IR interface."""

    def test_lower_to_core_ir_wraps_program(self):
        ast = Program([VariableDeclaration("x", NumeralLiteral("1"))])
        core = lower_to_core_ir(ast, "en", frontend_name="test")
        self.assertIs(core.ast, ast)
        self.assertEqual(core.source_language, "en")
        self.assertEqual(core.frontend_metadata["frontend_name"], "test")

    def test_core_ir_rejects_invalid_ast(self):
        core = CoreIRProgram(ast="not_ast", source_language="en")
        with self.assertRaises(TypeError):
            core.validate()

    def test_lower_to_core_ir_requires_program_root(self):
        with self.assertRaises(TypeError):
            lower_to_core_ir("bad", "en")
