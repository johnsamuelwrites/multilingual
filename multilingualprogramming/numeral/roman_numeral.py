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
from multilingualprogramming.numeral.abstract_numeral import AbstractNumeral


class RomanNumeral(AbstractNumeral):
    """
    Handling Roman numerals
    """

    roman_numerals_list = [
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

    @classmethod
    def __verify_roman_characters__(cls, self, numstr: str):
        """
        Verify whether each character is a Roman character
        """
        for character in numstr:
            if character not in self.roman_numerals_list:
                raise InvalidNumeralCharacterError(
                    "Not a valid number, contains the character: " + character
                )

    @staticmethod
    def is_roman_numeral(numstr: str) -> bool:
        """
        Verify whether each character is a Roman character
        """
        for character in numstr:
            if character not in RomanNumeral.roman_numerals_list:
                return False
        return True

    def __init__(self, numstr: str):
        super().__init__(numstr)
        self.numstr = numstr
        self.__verify_roman_characters__(self, numstr)

    def to_decimal(self):
        """
        Returns the number associated with the number string (Roman numeral)
        given by the user

        return:
           number: number associated with the number string
        """
        return fromRoman(self.numstr)

    @staticmethod
    def get_roman_numerals() -> list:
        """
        Get list of Roman numerals
        """
        return RomanNumeral.roman_numerals_list

    def set_roman_numerals(self, numerals: list):
        """
        Set list of Roman numerals
        """
        self.roman_numerals_list = numerals

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

    def __add__(self, second):
        """
        Add a RomanNumeral with a numeral or another RomanNumeral

        return:
           RomanNumeral: returns the sum of a RomanNumeral
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() + second.to_decimal()))
        raise TypeError("Cannot substract a Roman numeral with a non-Roman numeral")

    def __mul__(self, second):
        """
        Multiply a RomanNumeral with a numeral or another RomanNumeral

        return:
           RomanNumeral: multiplication of the two RomanNumeral values
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() * second.to_decimal()))
        raise TypeError("Cannot multiply a Roman numeral with a non-Roman numeral")

    def __sub__(self, second):
        """
        Substraction of Roman Numerals

        return:
           AbstractNumeral: returns the difference
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() - second.to_decimal()))
        raise TypeError("Cannot substract a Roman numeral with a non-Roman numeral")

    def __lshift__(self, second):
        """
        Left-shifting of Roman Numerals

        return:
           AbstractNumeral: returns the left shifted value
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() << second.to_decimal()))
        raise TypeError("Cannot left-shift a Roman numeral with a non-Roman numeral")

    def __rshift__(self, second):
        """
        Right-shifting of Roman Numerals

        return:
           AbstractNumeral: returns the right shifted value
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() >> second.to_decimal()))
        raise TypeError("Cannot right-shift a Roman numeral with a non-Roman numeral")

    def __truediv__(self, second):
        """
        True division of Roman Numerals

        return:
           AbstractNumeral: returns the value after true division
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() / second.to_decimal()))
        raise TypeError("Cannot divide a Roman numeral with a non-Roman numeral")

    def __floordiv__(self, second):
        """
        Floor division of Roman Numerals

        return:
           AbstractNumeral: returns the value after floor division
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() // second.to_decimal()))
        raise TypeError("Cannot floor divide a Roman numeral with a non-Roman numeral")

    def __neg__(self):
        """
        Negation of Roman Numerals

        return:
           AbstractNumeral: returns the negation
        """
        return RomanNumeral(toRoman(neg(self.to_decimal())))

    def __pow__(self, second):
        """
        Power of Roman Numerals

        return:
           AbstractNumeral: returns the power
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() ** second.to_decimal()))
        raise TypeError(
            "Cannot compute power of a Roman numeral with a non-Roman numeral"
        )

    def __mod__(self, second):
        """
        Modulus of Roman Numerals

        return:
           AbstractNumeral: returns the modulus value
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() % second.to_decimal()))
        raise TypeError(
            "Cannot compute modulus of a Roman numeral with a non-Roman numeral"
        )

    def __xor__(self, second):
        """
        XOR value of Roman Numerals

        return:
           AbstractNumeral: returns the XOR value
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() ^ second.to_decimal()))
        raise TypeError(
            "Cannot compute XOR of a Roman numeral with a non-Roman numeral"
        )

    def __invert__(self):
        """
        Bitwise inversion value of Roman Numerals

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """
        return RomanNumeral(invert(toRoman(self.to_decimal())))

    def __or__(self, second):
        """
        OR value of Roman Numerals

        return:
           AbstractNumeral: returns the OR value
        """
        if isinstance(second, RomanNumeral):
            return RomanNumeral(toRoman(self.to_decimal() | second.to_decimal()))
        raise TypeError(
            "Cannot computer OR of a Roman numeral with a non-Roman numeral"
        )
