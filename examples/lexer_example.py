#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Examples demonstrating the multilingual lexer."""

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.lexer.token_types import TokenType

# Tokenize English code
print("== Tokenizing English code ==")
SOURCE_EN = 'if x > 5:\n    print("hello")'
lexer = Lexer(SOURCE_EN, language="en")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Tokenize French code
print("\n== Tokenizing French code ==")
SOURCE_FR = 'si x > 5:\n    afficher("bonjour")'
lexer = Lexer(SOURCE_FR, language="fr")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Tokenize Hindi code with Devanagari numerals
print("\n== Tokenizing Hindi code ==")
SOURCE_HI = "अगर x > ५:\n    छापो(x)"
lexer = Lexer(SOURCE_HI, language="hi")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Auto-detect language
print("\n== Auto-detecting language ==")
SOURCE_AUTO = "si x > 5:\n    retour x"
lexer = Lexer(SOURCE_AUTO)
tokens = lexer.tokenize()
print(f"  Source: {SOURCE_AUTO!r}")
print(f"  Detected language: {lexer.language}")

# Unicode operators
print("\n== Unicode operators ==")
SOURCE_UNICODE = "x \u00d7 y \u2260 z"
lexer = Lexer(SOURCE_UNICODE)
tokens = lexer.tokenize()
for token in tokens:
    if token.type == TokenType.OPERATOR:
        print(f"  Operator: {token.value}")
