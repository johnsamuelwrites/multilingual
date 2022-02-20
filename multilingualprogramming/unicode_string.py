#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to represent numbers in multiple languages
"""

import unicodedata

NUMBER_STRINGS = [
    "ZERO",
    "ONE",
    "TWO",
    "THREE",
    "FOUR",
    "FIVE",
    "SIX",
    "SEVEN",
    "EIGHT",
    "NINE",
]

DIGIT_STRING = "DIGIT"


def get_number_list(language: str):
    """
    Get the unicode characters for the numbers in a given language
    """
    number_list = []
    for number in NUMBER_STRINGS:
        number = unicodedata.lookup(language + " " + DIGIT_STRING + " " + number)
        number_list.append(number)
    return number_list
