#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Code generation from AST to Python source."""

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator

registry = KeywordRegistry()


def safe_text(text):
    """Render Unicode text safely on non-UTF-8 consoles."""
    return text.encode("ascii", "backslashreplace").decode("ascii")


# --- Example 1: English source ---
print("=== English Source -> Python ===\n")

en_source = """\
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

for i in range(10):
    print(fibonacci(i))
"""

print("Input (English):")
print(en_source)

tokens = Lexer(en_source, language="en").tokenize()
tree = Parser(tokens, source_language="en").parse()
python = PythonCodeGenerator().generate(tree)

print("Generated Python:")
print(python)

# --- Example 2: French source (using correct keywords from registry) ---
print("=== French Source -> Python ===\n")

kw = {c: registry.get_keyword(c, "fr") for c in
      ["FUNC_DEF", "COND_IF", "RETURN", "LET", "PRINT"]}

fr_source = (
    f"{kw['FUNC_DEF']} factoriel(n):\n"
    f"    {kw['COND_IF']} n <= 1:\n"
    f"        {kw['RETURN']} 1\n"
    f"    {kw['RETURN']} n * factoriel(n - 1)\n"
    "\n"
    f"{kw['LET']} resultat = factoriel(5)\n"
    f"{kw['PRINT']}(resultat)\n"
)

print("Input (French):")
print(safe_text(fr_source))

tokens = Lexer(fr_source, language="fr").tokenize()
tree = Parser(tokens, source_language="fr").parse()
python = PythonCodeGenerator().generate(tree)

print("Generated Python:")
print(python)

# --- Example 3: Hindi with Devanagari numerals ---
print("=== Devanagari Numerals -> Python Integers ===\n")

kw_hi = {c: registry.get_keyword(c, "hi") for c in ["LET", "PRINT"]}

hi_source = (
    f"{kw_hi['LET']} x = \u0967\u0968\u0969\n"
    f"{kw_hi['LET']} y = \u096a\u096b\u096c\n"
    f"{kw_hi['PRINT']}(x + y)\n"
)

print("Input (Hindi with Devanagari numerals):")
print(safe_text(hi_source))

tokens = Lexer(hi_source, language="hi").tokenize()
tree = Parser(tokens, source_language="hi").parse()
python = PythonCodeGenerator().generate(tree)

print("Generated Python:")
print(safe_text(python))
print("Note: Devanagari numerals converted to Python integers (123, 456)")
