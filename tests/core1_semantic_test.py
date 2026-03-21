#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Focused tests for early Core 1.0 parsing and semantic lowering."""

import unittest

from multilingualprogramming.core import IRBinding, IRFunction, lower_to_semantic_ir
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _parse(source: str):
    lexer = Lexer(source, language="en")
    tokens = lexer.tokenize()
    return Parser(tokens, source_language="en").parse()


class Core1SemanticTestSuite(unittest.TestCase):
    """Validate the initial fn/var Core 1.0 bridge."""

    def test_var_parses_as_mutable_declaration(self):
        program = _parse("var counter = 1\n")
        stmt = program.body[0]
        self.assertEqual(stmt.declaration_kind, "var")
        self.assertTrue(stmt.is_mutable)

    def test_fn_parses_as_function_keyword(self):
        program = _parse("fn greet(name):\n    pass\n")
        stmt = program.body[0]
        self.assertEqual(stmt.syntax_keyword, "fn")
        self.assertEqual(stmt.name, "greet")

    def test_semantic_lowering_marks_mutable_binding(self):
        program = _parse("var counter = 1\n")
        ir = lower_to_semantic_ir(program, "en")
        self.assertIsInstance(ir.body[0], IRBinding)
        self.assertTrue(ir.body[0].is_mutable)

    def test_semantic_lowering_preserves_fn_keyword(self):
        program = _parse("fn greet(name):\n    pass\n")
        ir = lower_to_semantic_ir(program, "en")
        self.assertIsInstance(ir.body[0], IRFunction)
        self.assertEqual(ir.body[0].syntax_keyword, "fn")
        self.assertEqual(ir.body[0].parameters, ["name"])
