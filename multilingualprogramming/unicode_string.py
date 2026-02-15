#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to represent numbers in multiple languages
"""

import re
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

# Unicode vulgar fraction characters mapped to (numerator, denominator) tuples
UNICODE_FRACTION_MAP = {
    "\u00bd": (1, 2),    # ½
    "\u2153": (1, 3),    # ⅓
    "\u2154": (2, 3),    # ⅔
    "\u00bc": (1, 4),    # ¼
    "\u00be": (3, 4),    # ¾
    "\u2155": (1, 5),    # ⅕
    "\u2156": (2, 5),    # ⅖
    "\u2157": (3, 5),    # ⅗
    "\u2158": (4, 5),    # ⅘
    "\u2159": (1, 6),    # ⅙
    "\u215a": (5, 6),    # ⅚
    "\u2150": (1, 7),    # ⅐
    "\u215b": (1, 8),    # ⅛
    "\u215c": (3, 8),    # ⅜
    "\u215d": (5, 8),    # ⅝
    "\u215e": (7, 8),    # ⅞
    "\u2151": (1, 9),    # ⅑
    "\u2152": (1, 10),   # ⅒
}


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
        if character == "-":
            unicode_numstr = character
        elif character == ".":
            unicode_numstr = unicode_numstr + character
        else:
            unicode_character = unicodedata.lookup(
                lookup_language + " " + NUMBER_STRINGS[int(character)]
            )
            unicode_numstr = unicode_numstr + unicode_character
    return unicode_numstr


def get_language_from_character(char):
    """
    Detect the language name of a single Unicode digit character.

    Parameters:
        char (str): A single Unicode digit character

    Returns:
        str | None: The language name (e.g., "MALAYALAM", "ARABIC-INDIC")
            or None if not a decimal digit
    """
    if unicodedata.category(char) != "Nd":
        return None
    char_name = unicodedata.name(char)
    # Extract the language prefix (everything before " DIGIT ...")
    language_name = re.sub(r" .*$", "", char_name)
    return language_name


def convert_numeral_string(numstr, source_language, target_language):
    """
    Convert a numeral string from one script to another.

    Parameters:
        numstr (str): The numeral string to convert
        source_language (str): Source language name (e.g., "MALAYALAM")
        target_language (str): Target language name (e.g., "ARABIC-INDIC")

    Returns:
        str: The numeral string in the target script
    """
    source_digits = get_number_list(source_language)
    target_digits = get_number_list(target_language)
    digit_map = dict(zip(source_digits, target_digits))

    result = ""
    for char in numstr:
        if char in digit_map:
            result += digit_map[char]
        else:
            # Preserve non-digit characters (signs, separators)
            result += char
    return result
