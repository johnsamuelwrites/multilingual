#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle Roman numerals
"""

from roman import fromRoman, toRoman
from multilingualprogramming.exceptions import (
    InvalidNumeralCharacterError,
)
from multilingualprogramming.abstract_numeral import AbstractNumeral


class RomanNumeral(AbstractNumeral):
    """
    Handling Roman numerals
    """

    @classmethod
    def __verify_roman_characters__(cls, self, numstr: str):
        """
        Verify whether each character is a Roman character
        """
        roman_numerals_list = self.get_roman_numerals()
        for character in numstr:
            if character not in roman_numerals_list:
                raise InvalidNumeralCharacterError(
                    "Not a valid number, contains the character: " + character
                )

    def __init__(self, numstr: str):
        super().__init__(numstr)
        self.set_roman_numerals()
        self.numstr = numstr
        self.__verify_roman_characters__(self, numstr)

    def to_numeral(self):
        """
        Returns the number associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """
        return fromRoman(self.numstr)

    def get_roman_numerals(self):
        """
        Get list of Roman numerals
        """
        return self.roman_numerals_list

    def set_roman_numerals(self):
        """
        Set list of Roman numerals
        """
        self.roman_numerals_list = [
            "X",
            "V",
            "I",
            "L",
            "C",
            "D",
            "M",
            "x",
            "v",
            "i",
            "l",
            "c",
            "d",
            "m",
            "Ⅰ",
            "Ⅱ",
            "Ⅲ",
            "Ⅳ",
            "Ⅴ",
            "Ⅵ",
            "Ⅶ",
            "Ⅷ",
            "Ⅸ",
            "Ⅹ",
            "Ⅺ",
            "Ⅻ,Ⅼ",
            "Ⅽ",
            "Ⅾ",
            "Ⅿ",
            "ↀ",
            "ↁ",
            "ↂ",
            "ↇ",
            "ↈ",
            "ⅰ",
            "ⅱ",
            "ⅲ",
            "ⅳ",
            "ⅴ",
            "ⅵ",
            "ⅶ",
            "ⅷ",
            "ⅷ",
            "ⅸ",
            "ⅹ",
            "ⅺ",
            "ⅻ",
            "ⅼ",
            "ⅽ",
            "ⅾ",
            "ⅿ",
            "ↅ",
            "ↆ",
            "Ↄ",
        ]

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
        return f'RomanNumeral("{self.numstr}")'

    def __add__(self, numeral):
        """
        Add a RomanNumeral with a numeral or another RomanNumeral

        return:
           RomanNumeral: returns the sum of a RomanNumeral
        """
        return RomanNumeral(toRoman(self.to_numeral() + numeral.to_numeral()))

    def __mul__(self, numeral):
        """
        Multiply a RomanNumeral with a numeral or another RomanNumeral

        return:
           RomanNumeral: multiplication of the two RomanNumeral values
        """
        return RomanNumeral(toRoman(self.to_numeral() * numeral.to_numeral()))

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
