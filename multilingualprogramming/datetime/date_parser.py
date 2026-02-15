#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Parser for multilingual date strings."""

import unicodedata
from multilingualprogramming.exceptions import InvalidDateError
from multilingualprogramming.unicode_string import get_language_from_character
from multilingualprogramming.datetime.resource_loader import load_datetime_resource


class DateParser:
    """
    Parses multilingual date strings into (year, month, day) tuples.

    Supports date strings with:
    - Month names in any of the 10 pilot languages
    - Numerals in any Unicode script
    - Various separator characters (-, /, .)
    """

    _months_data = None
    _month_lookup = None  # {language: {month_name_lower: month_number}}

    @classmethod
    def _load(cls):
        """Load month names from JSON."""
        if cls._months_data is not None:
            return
        cls._months_data = load_datetime_resource("months.json")

        # Build lookup: {lang: {month_name_lower: month_number}}
        cls._month_lookup = {}
        month_names = list(cls._months_data["months"].keys())
        for idx, month_key in enumerate(month_names, 1):
            month_data = cls._months_data["months"][month_key]
            for lang, names in month_data.items():
                if lang not in cls._month_lookup:
                    cls._month_lookup[lang] = {}
                cls._month_lookup[lang][names["full"].lower()] = idx
                cls._month_lookup[lang][names["abbr"].lower()] = idx

    @classmethod
    def _extract_number(cls, token):
        """
        Extract a numeric value from a token that may contain Unicode digits.

        Returns:
            int | None: The numeric value, or None if not a number
        """
        if not token:
            return None
        # Try direct int conversion first (ASCII digits)
        try:
            return int(token)
        except ValueError:
            pass
        # Try Unicode digit conversion
        result = 0
        for char in token:
            if unicodedata.category(char) == "Nd":
                result = result * 10 + unicodedata.decimal(char)
            else:
                return None
        return result if token else None

    @classmethod
    def _find_month(cls, token):
        """
        Find a month number from a token string.

        Returns:
            tuple(int, str) | None: (month_number, language) or None
        """
        token_lower = token.lower()
        for lang, months in cls._month_lookup.items():
            if token_lower in months:
                return (months[token_lower], lang)
        return None

    @classmethod
    def parse(cls, datestr, language=None):
        """
        Parse a multilingual date string.

        Parameters:
            datestr (str): Date string (e.g., "15-January-2024", "१५-जनवरी-२०२४")
            language (str): Optional language hint

        Returns:
            tuple(int, int, int, str): (year, month, day, detected_language)

        Raises:
            InvalidDateError: If the date cannot be parsed
        """
        cls._load()
        datestr = datestr.strip()

        # Split on common separators
        separators = ["-", "/", ".", " ", "年", "月", "日"]
        tokens = []
        current = ""
        for char in datestr:
            if char in separators:
                if current:
                    tokens.append(current)
                current = ""
            else:
                current += char
        if current:
            tokens.append(current)

        if len(tokens) < 2:
            raise InvalidDateError(f"Cannot parse date: {datestr}")

        # Classify each token as number or month name
        numbers = []
        month_info = None
        detected_lang = language

        for token in tokens:
            num = cls._extract_number(token)
            if num is not None:
                numbers.append(num)
                # Detect language from Unicode digits
                if detected_lang is None:
                    for char in token:
                        lang_name = get_language_from_character(char)
                        if lang_name and lang_name != "DIGIT":
                            detected_lang = lang_name
                            break
            else:
                # Try as month name
                result = cls._find_month(token)
                if result is not None:
                    month_num, lang = result
                    month_info = month_num
                    if detected_lang is None:
                        detected_lang = lang
                else:
                    raise InvalidDateError(
                        f"Cannot identify token: {token}"
                    )

        if detected_lang is None:
            detected_lang = "en"

        # Determine year, month, day from parsed values
        if month_info is not None:
            # We have a named month
            if len(numbers) == 2:
                # Determine which is day and which is year
                if numbers[0] > 31:
                    year, day = numbers[0], numbers[1]
                elif numbers[1] > 31:
                    day, year = numbers[0], numbers[1]
                elif numbers[0] > 12:
                    day, year = numbers[0], numbers[1]
                else:
                    day, year = numbers[0], numbers[1]
                return (year, month_info, day, detected_lang)
            if len(numbers) == 1:
                # Assume year if > 31, else day
                if numbers[0] > 31:
                    return (numbers[0], month_info, 1, detected_lang)
                return (2024, month_info, numbers[0], detected_lang)
        elif len(numbers) == 3:
            # All numeric: try to determine order
            a, b, c = numbers
            # If first number > 31, assume YYYY-MM-DD
            if a > 31:
                return (a, b, c, detected_lang)
            # If third number > 31, assume DD-MM-YYYY or MM-DD-YYYY
            if c > 31:
                if a > 12:
                    return (c, b, a, detected_lang)  # DD-MM-YYYY
                return (c, a, b, detected_lang)  # MM-DD-YYYY or DD-MM-YYYY
            # Ambiguous — default to DD-MM-YYYY
            return (c, b, a, detected_lang)

        raise InvalidDateError(f"Cannot determine date components: {datestr}")
