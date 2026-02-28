#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Encoding checks for generated compiler outputs."""

import json
import unittest

from multilingualprogramming.codegen.encoding_guard import assert_clean_text_encoding
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _parse(source: str, lang: str = "en"):
    lexer = Lexer(source, language=lang)
    parser = Parser(lexer.tokenize(), source_language=lang)
    return parser.parse()


class GeneratedOutputEncodingTestSuite(unittest.TestCase):
    """Fail fast when generated outputs contain encoding regressions."""

    def test_generated_python_wat_and_manifest_are_clean(self):
        source = (
            "def draw(x):\n"
            "    return x + 1\n"
            "print(draw(41))\n"
        )
        program = _parse(source, "en")
        wat_gen = WATCodeGenerator()
        py_source = PythonCodeGenerator().generate(program)
        wat_source = wat_gen.generate(program)
        abi_json = json.dumps(
            wat_gen.generate_abi_manifest(program), ensure_ascii=False, indent=2
        )

        assert_clean_text_encoding("generated_python", py_source)
        assert_clean_text_encoding("generated_wat", wat_source)
        assert_clean_text_encoding("generated_abi_json", abi_json)


if __name__ == "__main__":
    unittest.main()
