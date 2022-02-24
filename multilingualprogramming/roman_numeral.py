#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle Roman numerals
"""

from roman import fromRoman, toRoman
from roman_numerals import convert_to_integer

class RomanNumeral:
    """
    Handling Roman numerals
    """

    @classmethod
    def __verify_roman_characters__(cls, self, numstr: str):
        pass

    def __init__(self, numstr: str):
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
        return RomanNumeral(
            toRoman(
                self.to_numeral() + numeral.to_numeral()
            )
        )

    def __mul__(self, numeral):
        """
        Multiply a RomanNumeral with a numeral or another RomanNumeral

        return:
           RomanNumeral: multiplication of the two RomanNumeral values
        """
        return RomanNumeral(
            toRoman(
                self.to_numeral() * numeral.to_numeral()
            )
        )
