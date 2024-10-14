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
