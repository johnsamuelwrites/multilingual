#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Shared helpers for parser/codegen/executor tests."""

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def parse_source(source, language="en"):
    """Tokenize and parse source code."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language)
    return parser.parse()


def generate_python(source, language="en"):
    """Parse and generate Python source."""
    prog = parse_source(source, language)
    gen = PythonCodeGenerator()
    return gen.generate(prog).strip()


def execute_source(source, language="en", check_semantics=False):
    """Run the full execution pipeline."""
    executor = ProgramExecutor(language=language, check_semantics=check_semantics)
    return executor.execute(source)
