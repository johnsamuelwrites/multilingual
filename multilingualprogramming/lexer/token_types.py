#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Token type definitions for the multilingual lexer."""

from enum import Enum, auto


class TokenType(Enum):
    """Types of tokens recognized by the lexer."""

    # Keywords and identifiers
    KEYWORD = auto()
    IDENTIFIER = auto()

    # Literals
    NUMERAL = auto()
    STRING = auto()
    DATE_LITERAL = auto()

    # Operators
    OPERATOR = auto()

    # Delimiters
    DELIMITER = auto()

    # Whitespace-significant tokens
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    # Comments and end-of-file
    COMMENT = auto()
    EOF = auto()
