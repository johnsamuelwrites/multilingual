#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions for converting numerals between scripts and notations"""

from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral
from multilingualprogramming.unicode_string import (
    convert_numeral_string,
    get_unicode_character_string,
    get_language_from_character,
)


class NumeralConverter:
    """
    Utility class for converting numerals between scripts and formats.
    """

    # Unicode superscript digits for scientific notation
    SUPERSCRIPT_MAP = {
        "0": "\u2070",
        "1": "\u00b9",
        "2": "\u00b2",
        "3": "\u00b3",
        "4": "\u2074",
        "5": "\u2075",
        "6": "\u2076",
        "7": "\u2077",
        "8": "\u2078",
        "9": "\u2079",
        "-": "\u207b",
    }

    SUPERSCRIPT_REVERSE = {v: k for k, v in SUPERSCRIPT_MAP.items()}

    @staticmethod
    def convert(numeral, target_language):
        """
        Convert a UnicodeNumeral to a different script.

        Parameters:
            numeral (UnicodeNumeral): The numeral to convert
            target_language (str): Target language name (e.g., "ARABIC-INDIC")

        Returns:
            UnicodeNumeral: A new numeral in the target script
        """
        return numeral.convert_to(target_language)

    @staticmethod
    def to_scientific(numeral, language=None):
        """
        Convert a numeral to scientific notation string.

        Parameters:
            numeral (UnicodeNumeral): The numeral to convert
            language (str): Target language for output (default: same as input)

        Returns:
            str: Scientific notation string (e.g., "1.23×10³")
        """
        value = numeral.to_decimal()
        lang = language or numeral.language_name or "DIGIT"

        if value == 0:
            zero = get_unicode_character_string(lang, 0)
            return zero

        # Calculate mantissa and exponent
        negative = value < 0
        abs_value = abs(value)

        exponent = 0
        mantissa = abs_value
        if mantissa >= 10:
            while mantissa >= 10:
                mantissa /= 10
                exponent += 1
        elif mantissa < 1 and mantissa > 0:
            while mantissa < 1:
                mantissa *= 10
                exponent -= 1

        # Format mantissa
        if mantissa == int(mantissa):
            mantissa = int(mantissa)

        # Build the string
        mantissa_val = -mantissa if negative else mantissa
        if isinstance(mantissa_val, float):
            # Round to avoid floating point artifacts
            mantissa_val = round(mantissa_val, 10)

        if exponent == 0:
            return get_unicode_character_string(lang, mantissa_val)

        mantissa_str = get_unicode_character_string(lang, mantissa_val)
        ten_str = get_unicode_character_string(lang, 10)

        # Build superscript exponent
        exp_str = ""
        for char in str(exponent):
            exp_str += NumeralConverter.SUPERSCRIPT_MAP.get(char, char)

        return f"{mantissa_str}\u00d7{ten_str}{exp_str}"

    @staticmethod
    def from_scientific(sci_str):
        """
        Parse a scientific notation string into a UnicodeNumeral.

        Parameters:
            sci_str (str): Scientific notation string (e.g., "1.23×10³")

        Returns:
            UnicodeNumeral: The parsed numeral
        """
        # Split on multiplication sign
        if "\u00d7" in sci_str:
            parts = sci_str.split("\u00d7", 1)
            mantissa_str = parts[0]
            base_exp_str = parts[1]
        else:
            # No scientific notation, just a plain number
            return UnicodeNumeral(sci_str)

        # Parse mantissa
        mantissa_numeral = UnicodeNumeral(mantissa_str)
        mantissa = mantissa_numeral.to_decimal()
        lang = mantissa_numeral.language_name

        # Parse exponent from superscript digits after the base
        # Find where superscripts start
        exp_chars = ""
        base_chars = ""
        for char in base_exp_str:
            if char in NumeralConverter.SUPERSCRIPT_REVERSE:
                exp_chars += NumeralConverter.SUPERSCRIPT_REVERSE[char]
            else:
                base_chars += char

        exponent = int(exp_chars) if exp_chars else 0

        # Calculate final value, rounding to avoid floating point artifacts
        result = mantissa * (10 ** exponent)
        result = round(result, 10)
        if result == int(result):
            result = int(result)

        return UnicodeNumeral(get_unicode_character_string(lang, result))
