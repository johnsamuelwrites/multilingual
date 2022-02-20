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


class MPNumeral:
    """
    Handling numerals in unicode-supported languages
    """

    def __verify_unicode_category__(self, numstr: str):
        running_character_name = None
        for character in numstr:
            if unicodedata.category(character) != "Nd":
                raise InvalidNumeralCharacterError(
                    "Not a valid number, contains the character: " + character
                )
            current_character_name = unicodedata.name(character)
            current_character_name = re.sub(r" .*$", "", current_character_name)
            if running_character_name is not None:
                if running_character_name != current_character_name:
                    raise MultipleLanguageCharacterMixError(
                        "Not a valid number, mix of characters from multiple scripts, found "
                        + character
                    )
            else:
                running_character_name = current_character_name

    def __init__(self, numstr: str):
        self.numstr = numstr
        self.__verify_unicode_category__(numstr)

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
