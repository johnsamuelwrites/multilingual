#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle numbers of multiple languages
"""

import unicodedata
import re
from multilingualprogramming.exceptions import (
    InvalidNumeralCharacterError,
    MultipleLanguageCharacterMixError,
)
from multilingualprogramming.unicode_string import get_unicode_character_string
from multilingualprogramming.abstract_numeral import AbstractNumeral
import multilingualprogramming.roman_numeral as rn
import multilingualprogramming.unicode_numeral as un


class MPNumeral:
    """
    Handling numerals in unicode-supported languages and
    Roman numerals
    """

    def __init__(self, numstr: str):
        self.numstr = numstr
        self.language_name = None

    def to_numeral(self):
        """
        Returns the number associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """
        return int(self.numstr)

    def __str__(self):
        """
        Returns the original number string

        return:
           numstr: original number string
        """
        return self.numstr

    def __repr__(self):
        """
        Returns the representation of an instance

        return:
           reprstr: representation of an instance
        """
        return f'MPNumeral("{self.numstr}")'

    def __add__(self, numeral):
        """
        Add a MPNumeral with a numeral or another MPNumeral

        return:
           MPNumeral: returns the sum of a MPNumeral
        """

    def __mul__(self, numeral):
        """
        Multiply a MPNumeral with a numeral or another MPNumeral

        return:
           MPNumeral: multiplication of the two MPNumeral values
        """

    def __lshift__(self, numeral):
        """
        Left-shifting

        return:
           AbstractNumeral: returns the left shifted value
        """

    def __rshift__(self, numeral):
        """
        Right-shifting

        return:
           AbstractNumeral: returns the right shifted value
        """

    def __sub__(self, numeral):
        """
        Substraction

        return:
           AbstractNumeral: returns the difference
        """

    def __truediv__(self, numeral):
        """
        True division

        return:
           AbstractNumeral: returns the value after true division
        """

    def __floordiv__(self, numeral):
        """
        Floor division

        return:
           AbstractNumeral: returns the value after floor division
        """

    def __neg__(self):
        """
        Negation

        return:
           AbstractNumeral: returns the negation
        """

    def __pow__(self, numeral):
        """
        Power

        return:
           AbstractNumeral: returns the power
        """

    def __mod__(self, numeral):
        """
        Modulus

        return:
           AbstractNumeral: returns the modulus value
        """

    def __xor__(self, numeral):
        """
        XOR value

        return:
           AbstractNumeral: returns the XOR value
        """

    def __invert__(self):
        """
        Bitwise inversion value

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """

    def __or__(self, numeral):
        """
        OR value

        return:
           AbstractNumeral: returns the OR value
        """
