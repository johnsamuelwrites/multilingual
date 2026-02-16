#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Full pipeline from source code to AST."""

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_printer import ASTPrinter

SOURCE = """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

let result = factorial(5)
print(result)
"""

print("=== Source Code ===")
print(SOURCE)

# Step 1: Tokenize
lexer = Lexer(SOURCE, language="en")
tokens = lexer.tokenize()
print("=== Tokens ===")
for token in tokens:
    print(f"  {token}")

# Step 2: Parse
parser = Parser(tokens, source_language="en")
program = parser.parse()

# Step 3: Pretty-print the AST
printer = ASTPrinter()
print("\n=== AST ===")
print(printer.print(program))
