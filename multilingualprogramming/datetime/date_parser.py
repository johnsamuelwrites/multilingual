#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Parser for multilingual date strings."""

import unicodedata
from typing import Any, cast
from multilingualprogramming.datetime.resource_loader import load_datetime_resource
from multilingualprogramming.exceptions import InvalidDateError
from multilingualprogramming.unicode_string import get_language_from_character


# pylint: disable=too-few-public-methods
class DateParser:
    """
    Parses multilingual date strings into (year, month, day) tuples.

    Supports date strings with:
    - Month names in any of the 10 pilot languages
    - Numerals in any Unicode script
    - Various separator characters (-, /, .)
    """

    _months_data: dict[str, Any] | None = None
    _month_lookup: dict[str, dict[str, int]] | None = None

    @classmethod
    def _load(cls):
        """Load month names from JSON."""
        if cls._months_data is not None and cls._month_lookup is not None:
            return

        months_data = load_datetime_resource("months.json")
        if not isinstance(months_data, dict):
            raise InvalidDateError("Invalid months data format")

        # Build lookup: {lang: {month_name_lower: month_number}}
        month_lookup: dict[str, dict[str, int]] = {}
        month_names = list(months_data["months"].keys())
        for idx, month_key in enumerate(month_names, 1):
            month_data = months_data["months"][month_key]
            for lang, names in month_data.items():
                if lang not in month_lookup:
                    month_lookup[lang] = {}
                month_lookup[lang][names["full"].lower()] = idx
                month_lookup[lang][names["abbr"].lower()] = idx

        cls._months_data = months_data
        cls._month_lookup = month_lookup

    @classmethod
    def _extract_number(cls, token):
        """
        Extract a numeric value from a token that may contain Unicode digits.

        Returns:
            int | None: The numeric value, or None if not a number
        """
        if not token:
            return None
        try:
            return int(token)
        except ValueError:
            pass

        result = 0
        for char in token:
            if unicodedata.category(char) == "Nd":
                result = result * 10 + unicodedata.decimal(char)
            else:
                return None
        return result

    @classmethod
    def _find_month(cls, token):
        """
        Find a month number from a token string.

        Returns:
            tuple(int, str) | None: (month_number, language) or None
        """
        if cls._month_lookup is None:
            return None

        token_lower = token.lower()
        for lang, months in cls._month_lookup.items():
            if token_lower in months:
                return (months[token_lower], lang)
        return None

    @classmethod
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
    def parse(cls, datestr, language=None):
        """
        Parse a multilingual date string.

        Parameters:
            datestr (str): Date string (e.g., "15-January-2024")
            language (str): Optional language hint

        Returns:
            tuple(int, int, int, str): (year, month, day, detected_language)

        Raises:
            InvalidDateError: If the date cannot be parsed
        """
        cls._load()
        datestr = datestr.strip()

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

        numbers = []
        month_info = None
        detected_lang = language

        for token in tokens:
            num = cls._extract_number(token)
            if num is not None:
                numbers.append(num)
                if detected_lang is None:
                    for char in token:
                        lang_name = get_language_from_character(char)
                        if lang_name and lang_name != "DIGIT":
                            detected_lang = lang_name
                            break
                continue

            result = cls._find_month(token)
            if result is None:
                raise InvalidDateError(f"Cannot identify token: {token}")

            month_num = result[0]
            lang = result[1]
            month_info = month_num
            if detected_lang is None:
                detected_lang = lang

        if detected_lang is None:
            detected_lang = "en"

        if month_info is not None:
            if len(numbers) == 2:
                first = numbers[0]
                second = numbers[1]
                if first > 31:
                    year, day = first, second
                elif second > 31:
                    day, year = first, second
                elif first > 12:
                    day, year = first, second
                else:
                    day, year = first, second
                return (year, month_info, day, detected_lang)

            if len(numbers) == 1:
                value = cast(int, numbers[0])
                if value > 31:
                    return (value, month_info, 1, detected_lang)
                return (2024, month_info, value, detected_lang)

        if len(numbers) == 3:
            a = numbers[0]
            b = numbers[1]
            c = numbers[2]
            if a > 31:
                return (a, b, c, detected_lang)
            if c > 31:
                if a > 12:
                    return (c, b, a, detected_lang)
                return (c, a, b, detected_lang)
            return (c, b, a, detected_lang)

        raise InvalidDateError(f"Cannot determine date components: {datestr}")
