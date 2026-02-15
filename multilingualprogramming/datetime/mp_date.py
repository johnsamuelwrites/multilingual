#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual date handling."""

import datetime as dt
from multilingualprogramming.datetime.date_parser import DateParser
from multilingualprogramming.datetime.resource_loader import load_datetime_resource
from multilingualprogramming.exceptions import InvalidDateError
from multilingualprogramming.unicode_string import get_unicode_character_string


class MPDate:
    """
    A date object with multilingual formatting and parsing.

    Internally stores as Python datetime.date (Gregorian).
    """

    _months_data = None

    @classmethod
    def _load_months(cls):
        """Load month names from JSON."""
        if cls._months_data is not None:
            return
        cls._months_data = load_datetime_resource("months.json")

    def __init__(self, year=None, month=None, day=None, date=None):
        """
        Create an MPDate.

        Parameters:
            year (int): Year
            month (int): Month (1-12)
            day (int): Day (1-31)
            date (datetime.date): Python date object
        """
        if date is not None:
            self._date = date
        elif year is not None and month is not None and day is not None:
            try:
                self._date = dt.date(year, month, day)
            except ValueError as e:
                raise InvalidDateError(str(e)) from e
        else:
            raise InvalidDateError(
                "MPDate requires year/month/day or a date object"
            )

    @classmethod
    def from_string(cls, datestr, language=None):
        """
        Parse a multilingual date string.

        Parameters:
            datestr (str): Date string in any supported language
            language (str): Optional language hint

        Returns:
            MPDate: Parsed date
        """
        year, month, day, _ = DateParser.parse(datestr, language)
        return cls(year=year, month=month, day=day)

    def to_date(self):
        """
        Convert to Python datetime.date.

        Returns:
            datetime.date: Python date object
        """
        return self._date

    @property
    def year(self):
        """Return the year."""
        return self._date.year

    @property
    def month(self):
        """Return the month."""
        return self._date.month

    @property
    def day(self):
        """Return the day."""
        return self._date.day

    def _get_month_name(self, language, abbreviated=False):
        """Get the month name in a given language."""
        self._load_months()
        month_keys = list(self._months_data["months"].keys())
        month_key = month_keys[self._date.month - 1]
        month_data = self._months_data["months"][month_key]
        if language in month_data:
            form = "abbr" if abbreviated else "full"
            return month_data[language][form]
        return month_data["en"]["full" if not abbreviated else "abbr"]

    def _format_number(self, number, script=None):
        """Format a number in the given script."""
        if script and script not in ("en", "DIGIT"):
            # Map language codes to Unicode script names
            script_map = {
                "hi": "DEVANAGARI",
                "ar": "ARABIC-INDIC",
                "bn": "BENGALI",
                "ta": "TAMIL",
            }
            unicode_script = script_map.get(script)
            if unicode_script:
                return get_unicode_character_string(unicode_script, number)
        return str(number)

    def to_string(self, language="en", fmt=None):
        """
        Format date in a given language.

        Parameters:
            language (str): Language code (e.g., "en", "fr", "hi")
            fmt (str): Optional format override

        Returns:
            str: Formatted date string
        """
        month_name = self._get_month_name(language)
        day_str = self._format_number(self._date.day, language)
        year_str = self._format_number(self._date.year, language)

        if language in ("zh", "ja"):
            return f"{year_str}年{self._format_number(self._date.month, language)}月{day_str}日"

        return f"{day_str}-{month_name}-{year_str}"

    def __add__(self, days):
        """
        Add days to the date.

        Parameters:
            days (int): Number of days to add

        Returns:
            MPDate: New date
        """
        if isinstance(days, int):
            new_date = self._date + dt.timedelta(days=days)
            return MPDate(date=new_date)
        return NotImplemented

    def __sub__(self, other):
        """
        Subtract another MPDate or days.

        Returns:
            int: Difference in days (if MPDate)
            MPDate: New date (if int)
        """
        if isinstance(other, MPDate):
            delta = self._date - other._date
            return delta.days
        if isinstance(other, int):
            new_date = self._date - dt.timedelta(days=other)
            return MPDate(date=new_date)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, MPDate):
            return self._date == other._date
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, MPDate):
            return self._date < other._date
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, MPDate):
            return self._date <= other._date
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, MPDate):
            return self._date > other._date
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, MPDate):
            return self._date >= other._date
        return NotImplemented

    def __hash__(self):
        return hash(self._date)

    def __str__(self):
        return self.to_string("en")

    def __repr__(self):
        return f"MPDate({self._date.year}, {self._date.month}, {self._date.day})"
