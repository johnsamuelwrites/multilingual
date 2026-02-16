#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual lexer that tokenizes mixed-script source code."""

import unicodedata
from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.lexer.token import Token
from multilingualprogramming.lexer.source_reader import SourceReader
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.exceptions import UnexpectedTokenError


# Operator characters and multi-character operators
SINGLE_OPERATORS = set("+-*/%<>=!&|^~")
MULTI_OPERATORS = {
    "**", "//", "==", "!=", "<=", ">=", "<<", ">>",
    "+=", "-=", "*=", "/=", "->",
}
# Unicode operator alternatives
UNICODE_OPERATORS = {
    "\u00d7": "*",   # ×
    "\u00f7": "/",   # ÷
    "\u2212": "-",   # −
    "\u2260": "!=",  # ≠
    "\u2264": "<=",  # ≤
    "\u2265": ">=",  # ≥
    "\u2192": "->",  # →
}

DELIMITERS = set("()[]{},:;.@")
# Unicode delimiter alternatives
UNICODE_DELIMITERS = {
    "\uff08": "(", "\uff09": ")",  # fullwidth parens
    "\uff3b": "[", "\uff3d": "]",  # fullwidth brackets
    "\uff5b": "{", "\uff5d": "}",  # fullwidth braces
    "\uff0c": ",", "\u060c": ",",  # fullwidth/Arabic comma
    "\uff1a": ":",                  # fullwidth colon
    "\uff1b": ";", "\u061b": ";",  # fullwidth/Arabic semicolon
}

# String delimiter pairs: (open, close)
STRING_PAIRS = {
    '"': '"',
    "'": "'",
    "\u300c": "\u300d",  # 「」 CJK corner brackets
    "\u00ab": "\u00bb",  # «» guillemets
    "\u201c": "\u201d",  # "" smart double quotes
    "\u2018": "\u2019",  # '' smart single quotes
}

# Date literal delimiters
DATE_OPEN = "\u3014"   # 〔
DATE_CLOSE = "\u3015"  # 〕


def _is_identifier_start(char):
    """Check if a character can start an identifier."""
    if not char:
        return False
    cat = unicodedata.category(char)
    # Lu=uppercase, Ll=lowercase, Lt=titlecase, Lm=modifier, Lo=other letter
    # Mn=nonspacing mark (e.g., Devanagari vowel signs that start conjuncts)
    return cat.startswith("L") or cat in ("Mn", "Mc") or char == "_"


def _is_identifier_part(char):
    """Check if a character can be part of an identifier."""
    if not char:
        return False
    cat = unicodedata.category(char)
    # Include combining marks (Mn=nonspacing, Mc=spacing combining)
    # needed for Devanagari, Arabic, and other complex scripts
    return (cat.startswith("L") or cat == "Nd"
            or cat in ("Mn", "Mc") or char == "_")


def _is_digit(char):
    """Check if a character is a Unicode decimal digit."""
    if not char:
        return False
    return unicodedata.category(char) == "Nd"


# pylint: disable=too-few-public-methods
class Lexer:
    """
    Tokenizes multilingual source code.

    Recognizes keywords in any of the 10 pilot languages,
    Unicode identifiers, multilingual numerals, multilingual
    string literals, and operators (including Unicode alternatives).
    """

    def __init__(self, source, language=None):
        """
        Initialize the lexer.

        Parameters:
            source (str): Source code to tokenize
            language (str): If given, only this language's keywords
                are recognized. If None, auto-detect.
        """
        self.reader = SourceReader(source)
        self.language = language
        self.registry = KeywordRegistry()
        self.tokens = []
        self._indent_stack = [0]
        self._at_line_start = True
        self._detected_keywords = []

    # pylint: disable=too-many-branches,too-many-statements
    def tokenize(self):
        """
        Tokenize the entire source string.

        Returns:
            list[Token]: List of tokens
        """
        while not self.reader.is_at_end():
            self._skip_spaces()
            if self.reader.is_at_end():
                break

            char = self.reader.peek()

            # Newline
            if char == "\n":
                self._read_newline()
                continue

            # Comment
            if char == "#":
                self._read_comment()
                continue

            # Handle indentation at start of line
            if self._at_line_start:
                self._handle_indentation()
                self._at_line_start = False
                if self.reader.is_at_end():
                    break
                char = self.reader.peek()
                if char in ("\n", "#"):
                    continue

            # F-string literals: f"..." or f'...'
            if char in ('f', 'F') and self.reader.peek_ahead(1) in ('"', "'"):
                self._read_fstring()
                continue

            # String literals (check triple-quoted first)
            if char in ('"', "'") and self.reader.peek_ahead(1) == char \
                    and self.reader.peek_ahead(2) == char:
                self._read_triple_string(char)
                continue

            # String literals
            if char in STRING_PAIRS:
                self._read_string(char)
                continue

            # Date literals
            if char == DATE_OPEN:
                self._read_date_literal()
                continue

            # Numerals (Unicode decimal digits or ASCII digits, or leading -)
            if _is_digit(char):
                self._read_numeral()
                continue

            # Identifiers and keywords
            if _is_identifier_start(char):
                self._read_identifier_or_keyword()
                continue

            # Operators (Unicode)
            if char in UNICODE_OPERATORS:
                line, col = self.reader.line, self.reader.column
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.OPERATOR, UNICODE_OPERATORS[char],
                    line, col
                ))
                continue

            # Operators (ASCII)
            if char in SINGLE_OPERATORS:
                self._read_operator()
                continue

            # Delimiters (Unicode)
            if char in UNICODE_DELIMITERS:
                line, col = self.reader.line, self.reader.column
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.DELIMITER, UNICODE_DELIMITERS[char],
                    line, col
                ))
                continue

            # Delimiters (ASCII)
            if char in DELIMITERS:
                line, col = self.reader.line, self.reader.column
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.DELIMITER, char, line, col
                ))
                continue

            # Whitespace (spaces/tabs already handled)
            if char in (" ", "\t", "\r"):
                self.reader.advance()
                continue

            # Unknown character
            raise UnexpectedTokenError(
                repr(char), self.reader.line, self.reader.column
            )

        # Emit remaining DEDENTs
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            self.tokens.append(Token(
                TokenType.DEDENT, "", self.reader.line, self.reader.column
            ))

        self.tokens.append(Token(
            TokenType.EOF, "", self.reader.line, self.reader.column
        ))

        # Auto-detect language if not set
        if self.language is None and self._detected_keywords:
            self.language = self.registry.detect_language(
                self._detected_keywords
            )

        return self.tokens

    def _skip_spaces(self):
        """Skip spaces and tabs (not newlines)."""
        while not self.reader.is_at_end() and self.reader.peek() in (" ", "\t"):
            if self._at_line_start:
                break  # Don't skip — indentation matters
            self.reader.advance()

    def _read_newline(self):
        """Read a newline and emit NEWLINE token."""
        line, col = self.reader.line, self.reader.column
        self.reader.advance()
        self.tokens.append(Token(TokenType.NEWLINE, "\\n", line, col))
        self._at_line_start = True

    def _read_comment(self):
        """Read a comment (# to end of line)."""
        line, col = self.reader.line, self.reader.column
        text = ""
        while not self.reader.is_at_end() and self.reader.peek() != "\n":
            text += self.reader.advance()
        self.tokens.append(Token(TokenType.COMMENT, text, line, col))

    def _handle_indentation(self):
        """Handle Python-style indentation."""
        line, col = self.reader.line, self.reader.column
        indent = 0
        while not self.reader.is_at_end() and self.reader.peek() in (" ", "\t"):
            char = self.reader.advance()
            if char == "\t":
                indent += 4  # Tab = 4 spaces
            else:
                indent += 1

        # Skip blank lines and comment-only lines
        if not self.reader.is_at_end() and self.reader.peek() in ("\n", "#"):
            return

        current = self._indent_stack[-1]
        if indent > current:
            self._indent_stack.append(indent)
            self.tokens.append(Token(TokenType.INDENT, "", line, col))
        elif indent < current:
            while self._indent_stack and self._indent_stack[-1] > indent:
                self._indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, "", line, col))

    def _read_numeral(self):
        """Read a numeral token (Unicode digits)."""
        line, col = self.reader.line, self.reader.column
        text = ""
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if _is_digit(char) or char == ".":
                text += self.reader.advance()
            else:
                break
        self.tokens.append(Token(TokenType.NUMERAL, text, line, col))

    def _read_identifier_or_keyword(self):
        """Read an identifier or keyword token."""
        line, col = self.reader.line, self.reader.column
        text = ""
        while not self.reader.is_at_end() and _is_identifier_part(self.reader.peek()):
            text += self.reader.advance()

        # Check if it's a keyword
        lang = self.language
        if lang is not None:
            if self.registry.is_keyword(text, lang):
                concept = self.registry.get_concept(text, lang)
                self._detected_keywords.append(text)
                self.tokens.append(Token(
                    TokenType.KEYWORD, text, line, col,
                    concept=concept, language=lang
                ))
                return
        else:
            # Try all languages
            for try_lang in self.registry.get_supported_languages():
                if self.registry.is_keyword(text, try_lang):
                    concept = self.registry.get_concept(text, try_lang)
                    self._detected_keywords.append(text)
                    self.tokens.append(Token(
                        TokenType.KEYWORD, text, line, col,
                        concept=concept, language=try_lang
                    ))
                    return

        self.tokens.append(Token(TokenType.IDENTIFIER, text, line, col))

    def _read_fstring(self):
        """Read an f-string literal: f"text {expr} text"."""
        line, col = self.reader.line, self.reader.column
        self.reader.advance()  # consume 'f'
        quote_char = self.reader.advance()  # consume opening quote
        text = ""
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if char == quote_char:
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.FSTRING, text, line, col
                ))
                return
            if char == "\\" and quote_char in ('"', "'"):
                self.reader.advance()
                next_char = self.reader.advance()
                text += "\\" + next_char
            else:
                text += self.reader.advance()

        raise UnexpectedTokenError(
            "Unterminated f-string literal",
            line, col
        )

    def _read_triple_string(self, quote_char):
        """Read a triple-quoted string literal (\"\"\"...\"\"\" or '''...''')."""
        line, col = self.reader.line, self.reader.column
        # Consume the three opening quotes
        self.reader.advance()
        self.reader.advance()
        self.reader.advance()
        text = ""
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if char == quote_char and self.reader.peek_ahead(1) == quote_char \
                    and self.reader.peek_ahead(2) == quote_char:
                # Consume the three closing quotes
                self.reader.advance()
                self.reader.advance()
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.STRING, text, line, col
                ))
                return
            if char == "\\" and quote_char in ('"', "'"):
                self.reader.advance()  # consume backslash
                next_char = self.reader.advance()
                text += "\\" + next_char
            else:
                text += self.reader.advance()

        raise UnexpectedTokenError(
            "Unterminated triple-quoted string literal",
            line, col
        )

    def _read_string(self, open_char):
        """Read a string literal."""
        line, col = self.reader.line, self.reader.column
        close_char = STRING_PAIRS[open_char]
        self.reader.advance()  # consume opening quote
        text = ""
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if char == close_char:
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.STRING, text, line, col
                ))
                return
            if char == "\\" and close_char in ('"', "'"):
                self.reader.advance()  # consume backslash
                next_char = self.reader.advance()
                text += "\\" + next_char
            else:
                text += self.reader.advance()

        # Unterminated string
        raise UnexpectedTokenError(
            "Unterminated string literal",
            line, col
        )

    def _read_date_literal(self):
        """Read a date literal enclosed in 〔 and 〕."""
        line, col = self.reader.line, self.reader.column
        self.reader.advance()  # consume 〔
        text = ""
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if char == DATE_CLOSE:
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.DATE_LITERAL, text, line, col
                ))
                return
            text += self.reader.advance()

        raise UnexpectedTokenError(
            "Unterminated date literal",
            line, col
        )

    def _read_operator(self):
        """Read an operator token, checking for multi-character operators."""
        line, col = self.reader.line, self.reader.column
        char = self.reader.advance()

        # Check for two-character operators
        if not self.reader.is_at_end():
            two_char = char + self.reader.peek()
            if two_char in MULTI_OPERATORS:
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.OPERATOR, two_char, line, col
                ))
                return

        self.tokens.append(Token(TokenType.OPERATOR, char, line, col))
