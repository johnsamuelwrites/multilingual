#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle numbers of multiple languages
"""

import unicodedata
import re
import locale
from operator import invert, neg
from multilingualprogramming.exceptions import (
    InvalidNumeralCharacterError,
    MultipleLanguageCharacterMixError,
)
from multilingualprogramming.unicode_string import get_unicode_character_string
from multilingualprogramming.abstract_numeral import AbstractNumeral


class UnicodeNumeral(AbstractNumeral):
    """
    Handling numerals in unicode-supported languages
    """

    @classmethod
    def __verify_unicode_category__(cls, self, numstr: str):
        """
        Verify the unicode category of each character
        """
        running_character_name = None
        for character in numstr:
            if unicodedata.category(character) != "Nd":
                # Handle decimal separators of all locales
                decimal_separator = locale.localeconv()["decimal_point"]
                if character == decimal_separator:
                    continue

                raise InvalidNumeralCharacterError(
                    "Not a valid number, contains the character: " + character
                )
            current_character_name = unicodedata.name(character)
            current_character_name = re.sub(r" .*$", "", current_character_name)

            if running_character_name is not None:
                if running_character_name != current_character_name:
                    self.language_name = None
                    raise MultipleLanguageCharacterMixError(
                        "Not a valid number, mix of characters from multiple scripts, found "
                        + character
                    )
            else:
                self.language_name = current_character_name
                running_character_name = current_character_name

    def __init__(self, numstr: str):
        super().__init__(numstr)
        self.numstr = numstr
        self.language_name = None
        self.__verify_unicode_category__(self, numstr)

    def to_numeral(self):
        """
        Returns the number associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """
        decimal_separator = locale.localeconv()["decimal_point"]
        self.numstr = self.numstr.replace(decimal_separator, ".")
        try:
            if "." in self.numstr:
                return float(self.numstr)
            return int(self.numstr)
        except ValueError:
            return None

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
        return f'UnicodeNumeral("{self.numstr}")'

    def __add__(self, numeral):
        """
        Add a UnicodeNumeral with a numeral or another UnicodeNumeral

        return:
           UnicodeNumeral: returns the sum of a UnicodeNumeral
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() + numeral.to_numeral()
            )
        )

    def __mul__(self, numeral):
        """
        Multiply a UnicodeNumeral with a numeral or another UnicodeNumeral

        return:
           UnicodeNumeral: multiplication of the two UnicodeNumeral values
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() * numeral.to_numeral()
            )
        )

    def __lshift__(self, numeral):
        """
        Left-shifting of Unicode Numerals

        return:
           AbstractNumeral: returns the left shifted value
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() << numeral.to_numeral()
            )
        )

    def __rshift__(self, numeral):
        """
        Right-shifting of Unicode Numerals

        return:
           AbstractNumeral: returns the right shifted value
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() >> numeral.to_numeral()
            )
        )

    def __sub__(self, numeral):
        """
        Substraction of Unicode Numerals

        return:
           AbstractNumeral: returns the difference
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() - numeral.to_numeral()
            )
        )

    def __truediv__(self, numeral):
        """
        True division of Unicode Numerals

        return:
           AbstractNumeral: returns the value after true division
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() / numeral.to_numeral()
            )
        )

    def __floordiv__(self, numeral):
        """
        Floor division of Unicode Numerals

        return:
           AbstractNumeral: returns the value after floor division
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() // numeral.to_numeral()
            )
        )

    def __neg__(self):
        """
        Negation of Unicode Numerals

        return:
           AbstractNumeral: returns the negation
        """
        return UnicodeNumeral(
            get_unicode_character_string(self.language_name, neg(self.to_numeral()))
        )

    def __pow__(self, numeral):
        """
        Power of Unicode Numerals

        return:
           AbstractNumeral: returns the power
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() ** numeral.to_numeral()
            )
        )

    def __mod__(self, numeral):
        """
        Modulus of Unicode Numerals

        return:
           AbstractNumeral: returns the modulus value
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() % numeral.to_numeral()
            )
        )

    def __xor__(self, numeral):
        """
        XOR value of Unicode Numerals

        return:
           AbstractNumeral: returns the XOR value
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() ^ numeral.to_numeral()
            )
        )

    def __invert__(self):
        """
        Bitwise inversion value of Unicode Numerals

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """
        return UnicodeNumeral(
            get_unicode_character_string(self.language_name, invert(self.to_numeral()))
        )

    def __or__(self, numeral):
        """
        OR value of Unicode Numerals

        return:
           AbstractNumeral: returns the OR value
        """
        return UnicodeNumeral(
            get_unicode_character_string(
                self.language_name, self.to_numeral() | numeral.to_numeral()
            )
        )
