#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle numbers of multiple languages
"""

import multilingualprogramming.unicode_numeral as un
import multilingualprogramming.roman_numeral as rn
from multilingualprogramming.exceptions import (
    MultipleLanguageCharacterMixError,
    InvalidNumeralCharacterError,
)


class MPNumeral:
    """
    Handling numerals in unicode-supported languages and
    Roman numerals
    """

    def __init__(self, numstr: str):
        self.numstr = numstr
        self.num = None
        self.language_name = None
        try:
            self.num = un.UnicodeNumeral(numstr)  # create a numeral
        except (MultipleLanguageCharacterMixError,) as exception:
            raise exception
        except (InvalidNumeralCharacterError,) as exception:
            try:
                self.num = rn.RomanNumeral(numstr)  # create a numeral
            except (
                MultipleLanguageCharacterMixError,
                InvalidNumeralCharacterError,
            ) as exception:
                raise exception

    def to_numeral(self):
        """
        Returns the number (Multilingual Numeral) associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """
        if self.num:
            return self.num.to_numeral()
        return None

    def __str__(self):
        """
        Returns the original number string (Multilingual Numeral)

        return:
           numstr: original number string
        """

    def __repr__(self):
        """
        Returns the representation (Multilingual numeral) of an instance

        return:
           reprstr: representation of an instance
        """

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
        Left-shifting of Multilingual numerals

        return:
           AbstractNumeral: returns the left shifted value
        """

    def __rshift__(self, numeral):
        """
        Right-shifting of Multilingual numerals

        return:
           AbstractNumeral: returns the right shifted value
        """

    def __sub__(self, numeral):
        """
        Substraction of Multilingual numerals

        return:
           AbstractNumeral: returns the difference
        """

    def __truediv__(self, numeral):
        """
        True division of Multilingual numerals

        return:
           AbstractNumeral: returns the value after true division
        """

    def __floordiv__(self, numeral):
        """
        Floor division of Multilingual numerals

        return:
           AbstractNumeral: returns the value after floor division
        """

    def __neg__(self):
        """
        Negation of Multilingual numerals

        return:
           AbstractNumeral: returns the negation
        """

    def __pow__(self, numeral):
        """
        Power of Multilingual numerals

        return:
           AbstractNumeral: returns the power
        """

    def __mod__(self, numeral):
        """
        Modulus of Multilingual numerals

        return:
           AbstractNumeral: returns the modulus value
        """

    def __xor__(self, numeral):
        """
        XOR value of Multilingual numerals

        return:
           AbstractNumeral: returns the XOR value
        """

    def __invert__(self):
        """
        Bitwise inversion value of Multilingual numerals

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """

    def __or__(self, numeral):
        """
        OR value of Multilingual numerals

        return:
           AbstractNumeral: returns the OR value
        """
