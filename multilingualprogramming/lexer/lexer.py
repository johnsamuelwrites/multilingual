#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Multilingual lexer that tokenizes mixed-script source code."""
import json
import unicodedata
from pathlib import Path
from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.lexer.token import Token
from multilingualprogramming.lexer.source_reader import SourceReader
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.exceptions import UnexpectedTokenError
# Operator characters and multi-character operators
_DEFAULT_SINGLE_OPERATORS = set("+-*/%<>=!&|^~")
_DEFAULT_MULTI_OPERATORS = {
    "**", "//", "==", "!=", "<=", ">=", "<<", ">>",
    "+=", "-=", "*=", "/=", "->", ":=",
    "**=", "//=", "%=", "&=", "|=", "^=", "<<=", ">>=",
}
# Unicode operator alternatives
_DEFAULT_UNICODE_OPERATORS = {
    "\u00d7": "*",   # ×
    "\u00f7": "/",   # ÷
    "\u2212": "-",   # −
    "\u2260": "!=",  # ≠
    "\u2264": "<=",  # ≤
    "\u2265": ">=",  # ≥
    "\u2192": "->",  # →
}
_DEFAULT_DELIMITERS = set("()[]{},:;.@")
# Unicode delimiter alternatives
_DEFAULT_UNICODE_DELIMITERS = {
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
def _load_operator_config():
    """Load operator and delimiter tables from operators.json."""
    single_ops = set(_DEFAULT_SINGLE_OPERATORS)
    multi_ops = set(_DEFAULT_MULTI_OPERATORS)
    unicode_ops = dict(_DEFAULT_UNICODE_OPERATORS)
    delimiters = set(_DEFAULT_DELIMITERS)
    unicode_delims = dict(_DEFAULT_UNICODE_DELIMITERS)
    date_open = DATE_OPEN
    date_close = DATE_CLOSE
    config_path = (
        Path(__file__).resolve().parent.parent
        / "resources" / "usm" / "operators.json"
    )
    try:
        with open(config_path, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except Exception:
        return (
            single_ops, multi_ops, unicode_ops,
            delimiters, unicode_delims, date_open, date_close,
        )
    for section in ("arithmetic", "comparison", "assignment", "bitwise"):
        entries = data.get(section, {})
        for meta in entries.values():
            symbols = meta.get("symbols", [])
            if not symbols:
                continue
            canonical = symbols[0]
            for symbol in symbols:
                if len(symbol) > 1:
                    multi_ops.add(symbol)
                else:
                    single_ops.add(symbol)
            for alt in meta.get("unicode_alt", []):
                unicode_ops[alt] = canonical
    for name, meta in data.get("delimiters", {}).items():
        symbols = meta.get("symbols", [])
        if not symbols:
            continue
        canonical = symbols[0]
        if name == "ARROW":
            multi_ops.add(canonical)
            for alt in meta.get("unicode_alt", []):
                unicode_ops[alt] = canonical
            continue
        if name == "DATE_OPEN":
            date_open = canonical
            continue
        if name == "DATE_CLOSE":
            date_close = canonical
            continue
        delimiters.add(canonical)
        for alt in meta.get("unicode_alt", []):
            unicode_delims[alt] = canonical
    return (
        single_ops, multi_ops, unicode_ops,
        delimiters, unicode_delims, date_open, date_close,
    )
(SINGLE_OPERATORS, MULTI_OPERATORS, UNICODE_OPERATORS, DELIMITERS,
 UNICODE_DELIMITERS, DATE_OPEN, DATE_CLOSE) = _load_operator_config()
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
def _is_hex_digit(char):
    """Check if a character is an ASCII hexadecimal digit."""
    return char.isdigit() or char.lower() in "abcdef"
# pylint: disable=too-few-public-methods
class Lexer:
    """
    Tokenizes multilingual source code.
    Recognizes keywords in any of the 10 pilot languages,
    Unicode identifiers, multilingual numerals, multilingual
    string literals, and operators (including Unicode alternatives).
    """
    _MAX_KEYWORD_WORDS = 3

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

    def _reader_state(self):
        """Snapshot current reader state."""
        return (self.reader.pos, self.reader.line, self.reader.column)

    def _restore_reader_state(self, state):
        """Restore a previously saved reader state."""
        self.reader.pos, self.reader.line, self.reader.column = state

    def _match_keyword(self, text):
        """Return (concept, language) if text is a keyword, else None."""
        if self.language is not None:
            if self.registry.is_keyword(text, self.language):
                return (self.registry.get_concept(text, self.language), self.language)
            return None

        for try_lang in self.registry.get_supported_languages():
            if self.registry.is_keyword(text, try_lang):
                return (self.registry.get_concept(text, try_lang), try_lang)
        return None
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
            # Walrus operator uses ':' prefix, which is also a delimiter.
            if char == ":" and self.reader.peek_ahead(1) == "=":
                line, col = self.reader.line, self.reader.column
                self.reader.advance()
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.OPERATOR, ":=", line, col
                ))
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
        """Read numeral token (decimal, base-prefixed, scientific)."""
        line, col = self.reader.line, self.reader.column
        text = self.reader.advance()  # first digit already confirmed
        # Base-prefixed numerals: 0x..., 0o..., 0b...
        if text == "0" and not self.reader.is_at_end():
            prefix = self.reader.peek()
            if prefix.lower() in ("x", "o", "b"):
                text += self.reader.advance()
                while not self.reader.is_at_end():
                    char = self.reader.peek()
                    valid = False
                    if prefix.lower() == "x":
                        valid = _is_hex_digit(char) or char == "_"
                    elif prefix.lower() == "o":
                        valid = char in "01234567_"
                    elif prefix.lower() == "b":
                        valid = char in "01_"
                    if not valid:
                        break
                    text += self.reader.advance()
                self.tokens.append(Token(TokenType.NUMERAL, text, line, col))
                return
        # Decimal and float part
        while not self.reader.is_at_end():
            char = self.reader.peek()
            if _is_digit(char) or char == "_":
                text += self.reader.advance()
            else:
                break
        # Fractional part
        if not self.reader.is_at_end() and self.reader.peek() == ".":
            text += self.reader.advance()
            while not self.reader.is_at_end():
                char = self.reader.peek()
                if _is_digit(char) or char == "_":
                    text += self.reader.advance()
                else:
                    break
        # Scientific notation (ASCII e/E)
        if not self.reader.is_at_end() and self.reader.peek() in ("e", "E"):
            sign = self.reader.peek_ahead(1)
            first_digit = self.reader.peek_ahead(2) if sign in ("+", "-") \
                else sign
            if first_digit and _is_digit(first_digit):
                text += self.reader.advance()  # e/E
                if sign in ("+", "-"):
                    text += self.reader.advance()
                while not self.reader.is_at_end():
                    char = self.reader.peek()
                    if _is_digit(char) or char == "_":
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

        first_word_end = self._reader_state()
        words = [text]
        best_match = None

        initial_match = self._match_keyword(text)
        if initial_match is not None:
            best_match = (text, initial_match[0], initial_match[1], first_word_end)

        for _ in range(self._MAX_KEYWORD_WORDS - 1):
            before_gap = self._reader_state()
            saw_gap = False
            while not self.reader.is_at_end() and self.reader.peek() in (" ", "\t"):
                saw_gap = True
                self.reader.advance()
            if (not saw_gap) or self.reader.is_at_end():
                self._restore_reader_state(before_gap)
                break
            if not _is_identifier_start(self.reader.peek()):
                self._restore_reader_state(before_gap)
                break

            next_word = ""
            while (not self.reader.is_at_end()
                   and _is_identifier_part(self.reader.peek())):
                next_word += self.reader.advance()

            words.append(next_word)
            phrase = " ".join(words)
            phrase_match = self._match_keyword(phrase)
            if phrase_match is not None:
                best_match = (
                    phrase,
                    phrase_match[0],
                    phrase_match[1],
                    self._reader_state(),
                )

        if best_match is not None:
            phrase, concept, language, end_state = best_match
            self._restore_reader_state(end_state)
            self._detected_keywords.append(phrase)
            self.tokens.append(Token(
                TokenType.KEYWORD, phrase, line, col,
                concept=concept, language=language
            ))
            return

        self._restore_reader_state(first_word_end)
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
        # Check for three-character operators first (e.g., **=, //=, <<=, >>=)
        if not self.reader.is_at_end():
            two_char = char + self.reader.peek()
            if two_char in MULTI_OPERATORS:
                peek2 = self.reader.peek_ahead(1)
                three_char = two_char + peek2 if peek2 else ""
                if len(three_char) == 3 and three_char in MULTI_OPERATORS:
                    self.reader.advance()  # consume second char
                    self.reader.advance()  # consume third char
                    self.tokens.append(Token(
                        TokenType.OPERATOR, three_char, line, col
                    ))
                    return
                self.reader.advance()
                self.tokens.append(Token(
                    TokenType.OPERATOR, two_char, line, col
                ))
                return
        self.tokens.append(Token(TokenType.OPERATOR, char, line, col))
