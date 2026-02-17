#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Generate Python code from all pilot languages."""

from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def safe_text(text):
    """Render Unicode text safely on non-UTF-8 consoles."""
    return text.encode("ascii", "backslashreplace").decode("ascii")


def build_source(registry, language):
    """Build one equivalent source program in a given language."""
    kw_def = registry.get_keyword("FUNC_DEF", language)
    kw_if = registry.get_keyword("COND_IF", language)
    kw_return = registry.get_keyword("RETURN", language)
    kw_print = registry.get_keyword("PRINT", language)
    return (
        f"{kw_def} add(a, b):\n"
        f"    {kw_if} a < 0:\n"
        f"        {kw_return} 0\n"
        f"    {kw_return} a + b\n"
        "\n"
        f"{kw_print}(add(2, 3))\n"
    )


keyword_registry = KeywordRegistry()
generator = PythonCodeGenerator()

print("=== Code generation in all 10 pilot languages ===")
for lang in keyword_registry.get_supported_languages():
    source = build_source(keyword_registry, lang)
    tokens = Lexer(source, language=lang).tokenize()
    tree = Parser(tokens, source_language=lang).parse()
    python_code = generator.generate(tree)
    print(f"\n=== {lang.upper()} ===")
    print(safe_text(python_code))
