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
source_en = 'if x > 5:\n    print("hello")'
lexer = Lexer(source_en, language="en")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Tokenize French code
print("\n== Tokenizing French code ==")
source_fr = 'si x > 5:\n    afficher("bonjour")'
lexer = Lexer(source_fr, language="fr")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Tokenize Hindi code with Devanagari numerals
print("\n== Tokenizing Hindi code ==")
source_hi = "अगर x > ५:\n    छापो(x)"
lexer = Lexer(source_hi, language="hi")
tokens = lexer.tokenize()
for token in tokens:
    if token.type != TokenType.EOF:
        print(f"  {token}")
print(f"  Detected language: {lexer.language}")

# Auto-detect language
print("\n== Auto-detecting language ==")
source_auto = "si x > 5:\n    retour x"
lexer = Lexer(source_auto)
tokens = lexer.tokenize()
print(f"  Source: {source_auto!r}")
print(f"  Detected language: {lexer.language}")

# Unicode operators
print("\n== Unicode operators ==")
source_unicode = "x \u00d7 y \u2260 z"
lexer = Lexer(source_unicode)
tokens = lexer.tokenize()
for token in tokens:
    if token.type == TokenType.OPERATOR:
        print(f"  Operator: {token.value}")
