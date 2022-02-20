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
    get the unicode characters for the numbers in a given language
    """
    number_list = []
    lookup_language = language
    if language != DIGIT_STRING:
        lookup_language = language + " " + DIGIT_STRING
    for number in NUMBER_STRINGS:
        number = unicodedata.lookup(lookup_language + " " + number)
        number_list.append(number)
    return number_list


def get_unicode_character(language: str, numstr: str):
    """
    get the unicode characters for the numbers in a given language
    """
    lookup_language = language
    if language != DIGIT_STRING:
        lookup_language = language + " " + DIGIT_STRING
    character = unicodedata.lookup(lookup_language + " " + numstr)
    return character


def get_unicode_character_string(language: str, number: int):
    """
    get the unicode characters for the numbers in a given language
    """
    numstr = str(number)
    lookup_language = language
    if language != DIGIT_STRING:
        lookup_language = language + " " + DIGIT_STRING
    unicode_numstr = ""
    for character in numstr:
        unicode_character = unicodedata.lookup(
            lookup_language + " " + NUMBER_STRINGS[int(character)]
        )
        unicode_numstr = unicode_numstr + unicode_character
    return unicode_numstr
