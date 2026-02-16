#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Same program parsed in multiple languages produces identical ASTs."""

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_printer import ASTPrinter

# The same factorial function in 5 languages
PROGRAMS = {
    "en": """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
""",
    "fr": """\
d\u00e9f factorial(n):
    si n <= 1:
        retour 1
    retour n * factorial(n - 1)
""",
    "hi": """\
\u092a\u0930\u093f\u092d\u093e\u0937\u093e factorial(n):
    \u0905\u0917\u0930 n <= 1:
        \u0935\u093e\u092a\u0938\u0940 1
    \u0935\u093e\u092a\u0938\u0940 n * factorial(n - 1)
""",
    "zh": """\
\u51fd\u6570 factorial(n):
    \u5982\u679c n <= 1:
        \u8fd4\u56de 1
    \u8fd4\u56de n * factorial(n - 1)
""",
    "ar": """\
\u062f\u0627\u0644\u0629 factorial(n):
    \u0625\u0630\u0627 n <= 1:
        \u0625\u0631\u062c\u0627\u0639 1
    \u0625\u0631\u062c\u0627\u0639 n * factorial(n - 1)
""",
}

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
