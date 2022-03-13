#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle Roman numerals
"""

from operator import invert, neg
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
        Returns the number associated with the number string (Roman numeral)
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
        Returns the original number string (Roman numeral)

        return:
           numstr: original number string
        """
        return self.numstr

    def __repr__(self):
        """
        Returns the representation (Roman numeral) of an instance

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

    def __sub__(self, numeral):
        """
        Substraction of Roman Numerals

        return:
           AbstractNumeral: returns the difference
        """
        return RomanNumeral(toRoman(self.to_numeral() - numeral.to_numeral()))

    def __lshift__(self, numeral):
        """
        Left-shifting of Roman Numerals

        return:
           AbstractNumeral: returns the left shifted value
        """
        return RomanNumeral(toRoman(self.to_numeral() << numeral.to_numeral()))

    def __rshift__(self, numeral):
        """
        Right-shifting of Roman Numerals

        return:
           AbstractNumeral: returns the right shifted value
        """
        return RomanNumeral(toRoman(self.to_numeral() >> numeral.to_numeral()))

    def __truediv__(self, numeral):
        """
        True division of Roman Numerals

        return:
           AbstractNumeral: returns the value after true division
        """
        return RomanNumeral(toRoman(self.to_numeral() / numeral.to_numeral()))

    def __floordiv__(self, numeral):
        """
        Floor division of Roman Numerals

        return:
           AbstractNumeral: returns the value after floor division
        """
        return RomanNumeral(toRoman(self.to_numeral() // numeral.to_numeral()))

    def __neg__(self):
        """
        Negation of Roman Numerals

        return:
           AbstractNumeral: returns the negation
        """
        return RomanNumeral(toRoman(neg(self.to_numeral())))

    def __pow__(self, numeral):
        """
        Power of Roman Numerals

        return:
           AbstractNumeral: returns the power
        """
        return RomanNumeral(toRoman(self.to_numeral() ** numeral.to_numeral()))

    def __mod__(self, numeral):
        """
        Modulus of Roman Numerals

        return:
           AbstractNumeral: returns the modulus value
        """
        return RomanNumeral(toRoman(self.to_numeral() % numeral.to_numeral()))

    def __xor__(self, numeral):
        """
        XOR value of Roman Numerals

        return:
           AbstractNumeral: returns the XOR value
        """
        return RomanNumeral(toRoman(self.to_numeral() ^ numeral.to_numeral()))

    def __invert__(self):
        """
        Bitwise inversion value of Roman Numerals

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """
        return RomanNumeral(invert(toRoman(self.to_numeral())))

    def __or__(self, numeral):
        """
        OR value of Roman Numerals

        return:
           AbstractNumeral: returns the OR value
        """
        return RomanNumeral(toRoman(self.to_numeral() | numeral.to_numeral()))
