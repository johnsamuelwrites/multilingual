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
    def __init__(self, message, errors):            
        super().__init__(message)
        self.errors = errors

class MultiplaLanguageCharacterMixError(Exception):
    """
    Exception raised when a numeral string contains mix of characters
    from different languages
    """
    def __init__(self, message, errors):            
        super().__init__(message)
        self.errors = errors