#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Same program parsed in all pilot languages."""

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.ast_printer import ASTPrinter
from multilingualprogramming.parser.parser import Parser


def build_factorial_source(registry, language):
    """Build the same factorial program using keywords of one language."""
    func_def = registry.get_keyword("FUNC_DEF", language)
    cond_if = registry.get_keyword("COND_IF", language)
    kw_return = registry.get_keyword("RETURN", language)
    return (
        f"{func_def} factorial(n):\n"
        f"    {cond_if} n <= 1:\n"
        f"        {kw_return} 1\n"
        f"    {kw_return} n * factorial(n - 1)\n"
    )


registry = KeywordRegistry()
LANGUAGES = registry.get_supported_languages()
PROGRAMS = {lang: build_factorial_source(registry, lang) for lang in LANGUAGES}

printer = ASTPrinter()

for lang, source in PROGRAMS.items():
    print(f"=== {lang.upper()} ===")
    lexer = Lexer(source, language=lang)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=lang)
    program = parser.parse()
    ast_text = printer.print(program)
    print(ast_text)
    print()
