#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Token data class for the multilingual lexer."""

from multilingualprogramming.lexer.token_types import TokenType


class Token:
    """
    Represents a single token produced by the lexer.

    Attributes:
        type (TokenType): The type of this token
        value (str): The raw text of the token
        concept (str | None): USM concept ID (for KEYWORD tokens only)
        language (str | None): Detected language of the token
        line (int): Line number (1-based)
        column (int): Column number (1-based)
    """

    def __init__(self, token_type, value, line=1, column=1,
                 concept=None, language=None):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.concept = concept
        self.language = language

    def __repr__(self):
        parts = [f"Token({self.type.name}, {self.value!r}"]
        if self.concept:
            parts.append(f", concept={self.concept!r}")
        if self.language:
            parts.append(f", lang={self.language!r}")
        parts.append(f", {self.line}:{self.column})")
        return "".join(parts)

    def __eq__(self, other):
        if isinstance(other, Token):
            return (
                self.type == other.type
                and self.value == other.value
                and self.concept == other.concept
            )
        return NotImplemented

    def __hash__(self):
        return hash((self.type, self.value, self.concept))
