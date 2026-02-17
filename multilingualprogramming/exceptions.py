#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Exceptions"""


class InvalidNumeralCharacterError(Exception):
    """
    Exception raised when a character is not a valid digit
    """

    def __init__(self, message):
        message = "Invalid numeral: " + message
        super().__init__(message)


class MultipleLanguageCharacterMixError(Exception):
    """
    Exception raised when a numeral string contains mix of characters
    from different languages
    """

    def __init__(self, message):
        message = "Mix of characters: " + message
        super().__init__(message)


class DifferentNumeralTypeError(Exception):
    """
    Exception raised when an operation is performed on different
    types of numeral type
    """

    def __init__(self, message):
        message = "Invalid operation (different numeral type): " + message
        super().__init__(message)


class UnknownKeywordError(Exception):
    """
    Exception raised when a keyword string is not found in any language
    """

    def __init__(self, message):
        message = "Unknown keyword: " + message
        super().__init__(message)


class AmbiguousKeywordError(Exception):
    """
    Exception raised when a keyword matches multiple concepts
    """

    def __init__(self, message):
        message = "Ambiguous keyword: " + message
        super().__init__(message)


class UnsupportedLanguageError(Exception):
    """
    Exception raised when a requested language is not in the registry
    """

    def __init__(self, message):
        message = "Unsupported language: " + message
        super().__init__(message)


class InvalidDateError(Exception):
    """
    Exception raised for malformed multilingual dates
    """

    def __init__(self, message):
        message = "Invalid date: " + message
        super().__init__(message)


class LexerError(Exception):
    """
    Base exception for lexer errors
    """

    def __init__(self, message, line=None, column=None):
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        message = "Lexer error" + location + ": " + message
        self.line = line
        self.column = column
        super().__init__(message)


class UnexpectedTokenError(LexerError):
    """
    Exception raised for unexpected tokens during lexing
    """

    def __init__(self, message, line=None, column=None):
        super().__init__("Unexpected token: " + message, line, column)


class ParseError(LexerError):
    """
    Base exception for parser errors
    """

    def __init__(self, message, line=None, column=None):
        super().__init__("Parse error: " + message, line, column)


class SemanticError(Exception):
    """
    Exception for semantic analysis errors
    """

    def __init__(self, message, line=None, column=None):
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        self.line = line
        self.column = column
        message = "Semantic error" + location + ": " + message
        super().__init__(message)


class CodeGenerationError(Exception):
    """
    Exception for code generation errors
    """

    def __init__(self, message, line=None, column=None):
        location = ""
        if line is not None:
            location = f" at line {line}"
            if column is not None:
                location += f", column {column}"
        self.line = line
        self.column = column
        message = "Code generation error" + location + ": " + message
        super().__init__(message)


class RuntimeExecutionError(Exception):
    """
    Exception for runtime execution errors
    """

    def __init__(self, message):
        message = "Runtime error: " + message
        super().__init__(message)
