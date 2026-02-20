#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for many-frontends-to-one-core equivalence claims."""

import unittest

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_printer import ASTPrinter
from multilingualprogramming.codegen.executor import ProgramExecutor


def _parse_and_print(source, language):
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=lexer.language or language)
    program = parser.parse()
    printer = ASTPrinter()
    return printer.print(program)


class FrontendEquivalenceTestSuite(unittest.TestCase):
    """Ensure language-specific surfaces map to identical core AST shape."""

    def test_english_and_french_map_to_same_ast(self):
        english = """\
let total = 0
for i in range(4):
    total = total + i
print(total)
"""
        french = """\
soit total = 0
pour i dans range(4):
    total = total + i
print(total)
"""
        self.assertEqual(
            _parse_and_print(english, "en"),
            _parse_and_print(french, "fr"),
        )

    def test_japanese_surface_and_canonical_map_to_same_ast(self):
        surface = (
            "\u5909\u6570 total = 0\n"
            "\u7bc4\u56f2(4) \u5185\u306e \u5404 i \u306b\u5bfe\u3057\u3066:\n"
            "    total = total + i\n"
            "print(total)\n"
        )
        canonical = (
            "\u5909\u6570 total = 0\n"
            "\u6bce i \u4e2d \u7bc4\u56f2(4):\n"
            "    total = total + i\n"
            "print(total)\n"
        )
        self.assertEqual(
            _parse_and_print(surface, "ja"),
            _parse_and_print(canonical, "ja"),
        )

    def test_frontend_variants_execute_same_result(self):
        english = """\
let x = 2
let y = 3
print(x + y)
"""
        french = """\
soit x = 2
soit y = 3
print(x + y)
"""
        en_result = ProgramExecutor(language="en").execute(english)
        fr_result = ProgramExecutor(language="fr").execute(french)
        self.assertTrue(en_result.success, en_result.errors)
        self.assertTrue(fr_result.success, fr_result.errors)
        self.assertEqual(en_result.output, fr_result.output)
