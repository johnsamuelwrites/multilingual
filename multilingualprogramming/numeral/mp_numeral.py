#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle numbers of multiple languages
"""

from operator import invert, neg
from roman import toRoman
from multilingualprogramming.unicode_string import get_unicode_character_string
import multilingualprogramming.numeral.unicode_numeral as un
import multilingualprogramming.numeral.roman_numeral as rn
from multilingualprogramming.exceptions import (
    MultipleLanguageCharacterMixError,
    InvalidNumeralCharacterError,
    DifferentNumeralTypeError
)


class MPNumeral:
    """
    Handling numerals in unicode-supported languages and
    Roman numerals
    """

    def __init__(self, numstr: str):
        self.numstr = numstr
        self.num = None
        try:
            if rn.RomanNumeral.is_roman_numeral(numstr):
                self.num = rn.RomanNumeral(numstr)  # create a Roman numeral
                self.numeral_type = "Roman"
            else:
                self.num = un.UnicodeNumeral(numstr)  # create a Unicode numeral
                self.numeral_type = "Unicode"
        except (
            MultipleLanguageCharacterMixError,
            InvalidNumeralCharacterError,
        ) as exception:
            raise exception

    def to_decimal(self):
        """
        Returns the number (Multilingual Numeral) associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """
        if self.num:
            return self.num.to_decimal()
        return None

    def __str__(self):
        """
        Returns the original number string (Multilingual Numeral)

        return:
           numstr: original number string
        """
        return self.numstr

    def __repr__(self):
        """
        Returns the representation (Multilingual numeral) of an instance

        return:
           reprstr: representation of an instance
        """

    def to_mp_numeral(self, number):
        """
        Returns the number (Multilingual Numeral) associated with the number string
        given by the user

        return:
           mpnumeral: MPNumber associated with the number string
        """
        result = None
        if self.numeral_type == "Roman":
            result = toRoman(number)
        else:
            result = get_unicode_character_string(self.num.language_name, number)
        return MPNumeral(result)

    def _perform_operation(self, numeral, operation):
        """
        Helper function to perform arithmetic operations on MPNumeral objects.

        Parameters:
            numeral (MPNumeral): The numeral to operate with.
            operation (function): The arithmetic operation to apply.

        Returns:
            MPNumeral: The result of the arithmetic operation.
        """
        if isinstance(numeral, MPNumeral) and self.numeral_type == numeral.numeral_type:
            result = operation(self.to_decimal(), numeral.to_decimal())
            return self.to_mp_numeral(result)
        raise DifferentNumeralTypeError(operation.__name__)

    def __add__(self, numeral):
        """
        Add a MPNumeral with a numeral or another MPNumeral.

        Returns:
            MPNumeral: The sum of the MPNumeral values.
        """
        return self._perform_operation(numeral, lambda x, y: x + y)

    def __mul__(self, numeral):
        """
        Multiply a MPNumeral with a numeral or another MPNumeral.

        Returns:
            MPNumeral: The product of the MPNumeral values.
        """
        return self._perform_operation(numeral, lambda x, y: x * y)

    def __lshift__(self, numeral):
        """
        Left-shifting of Multilingual numerals

        return:
           MPNumeral: returns the left shifted value
        """
        return self._perform_operation(numeral, lambda x, y: x << y)

    def __rshift__(self, numeral):
        """
        Right-shifting of Multilingual numerals

        return:
           MPNumeral: returns the right shifted value
        """
        return self._perform_operation(numeral, lambda x, y: x >> y)

    def __sub__(self, numeral):
        """
        Substraction of Multilingual numerals

        return:
           MPNumeral: returns the difference
        """
        return self._perform_operation(numeral, lambda x, y: x - y)

    def __truediv__(self, numeral):
        """
        True division of Multilingual numerals

        return:
           MPNumeral: returns the value after true division
        """
        return self._perform_operation(numeral, lambda x, y: x / y)

    def __floordiv__(self, numeral):
        """
        Floor division of Multilingual numerals

        return:
           MPNumeral: returns the value after floor division
        """
        return self._perform_operation(numeral, lambda x, y: x // y)

    def __neg__(self):
        """
        Negation of Multilingual numerals

        return:
           MPNumeral: returns the negation
        """
        return MPNumeral(str(neg(self.to_decimal())))

    def __pow__(self, numeral):
        """
        Power of Multilingual numerals

        return:
           MPNumeral: returns the power
        """
        return self._perform_operation(numeral, lambda x, y: x**y)

    def __mod__(self, numeral):
        """
        Modulus of Multilingual numerals

        return:
           MPNumeral: returns the modulus value
        """
        return self._perform_operation(numeral, lambda x, y: x % y)

    def __xor__(self, numeral):
        """
        XOR value of Multilingual numerals

        return:
           MPNumeral: returns the XOR value
        """
        return self._perform_operation(numeral, lambda x, y: x ^ y)

    def __invert__(self):
        """
        Bitwise inversion value of Multilingual numerals

        return:
           MPNumeral: returns the bitwise-inverted value
        """
        result = invert(self.to_decimal())
        if self.numeral_type == "Roman":
            result = toRoman(result)
        else:
            result = get_unicode_character_string(self.num.language_name, result)
        return MPNumeral(result)

    def __or__(self, numeral):
        """
        OR value of Multilingual numerals

        return:
           MPNumeral: returns the OR value
        """
        return self._perform_operation(numeral, lambda x, y: x | y)
