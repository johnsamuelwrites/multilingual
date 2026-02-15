#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual datetime handling."""

import datetime as dt
from multilingualprogramming.datetime.mp_date import MPDate
from multilingualprogramming.datetime.mp_time import MPTime
from multilingualprogramming.datetime.date_parser import DateParser
from multilingualprogramming.exceptions import InvalidDateError


class MPDatetime:
    """
    A datetime object with multilingual formatting and parsing.

    Combines MPDate and MPTime. Internally stores as Python datetime.datetime.
    """

    def __init__(self, year=None, month=None, day=None,
                 hour=0, minute=0, second=0, datetime_obj=None):
        """
        Create an MPDatetime.

        Parameters:
            year (int): Year
            month (int): Month (1-12)
            day (int): Day (1-31)
            hour (int): Hour (0-23)
            minute (int): Minute (0-59)
            second (int): Second (0-59)
            datetime_obj (datetime.datetime): Python datetime object
        """
        if datetime_obj is not None:
            self._datetime = datetime_obj
        elif year is not None and month is not None and day is not None:
            try:
                self._datetime = dt.datetime(
                    year, month, day, hour, minute, second
                )
            except ValueError as e:
                raise InvalidDateError(str(e)) from e
        else:
            raise InvalidDateError(
                "MPDatetime requires year/month/day or a datetime object"
            )

    @classmethod
    def from_string(cls, datestr, language=None):
        """
        Parse a multilingual date string into an MPDatetime.

        Parameters:
            datestr (str): Date string in any supported language
            language (str): Optional language hint

        Returns:
            MPDatetime: Parsed datetime (time defaults to 00:00:00)
        """
        year, month, day, _ = DateParser.parse(datestr, language)
        return cls(year=year, month=month, day=day)

    @classmethod
    def now(cls):
        """Create an MPDatetime for the current date and time."""
        return cls(datetime_obj=dt.datetime.now())

    def to_datetime(self):
        """Convert to Python datetime.datetime."""
        return self._datetime

    def date(self):
        """Get the date part as MPDate."""
        return MPDate(date=self._datetime.date())

    def time(self):
        """Get the time part as MPTime."""
        return MPTime(time=self._datetime.time())

    @property
    def year(self):
        """Return the year."""
        return self._datetime.year

    @property
    def month(self):
        """Return the month."""
        return self._datetime.month

    @property
    def day(self):
        """Return the day."""
        return self._datetime.day

    @property
    def hour(self):
        """Return the hour."""
        return self._datetime.hour

    @property
    def minute(self):
        """Return the minute."""
        return self._datetime.minute

    @property
    def second(self):
        """Return the second."""
        return self._datetime.second

    def to_string(self, language="en", fmt=None):
        """
        Format datetime in a given language.

        Parameters:
            language (str): Language code
            fmt (str): Optional format override

        Returns:
            str: Formatted datetime string
        """
        date_part = self.date().to_string(language)
        time_part = self.time().to_string(language)
        return f"{date_part} {time_part}"

    def __eq__(self, other):
        if isinstance(other, MPDatetime):
            return self._datetime == other._datetime
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, MPDatetime):
            return self._datetime < other._datetime
        return NotImplemented

    def __hash__(self):
        return hash(self._datetime)

    def __str__(self):
        return self.to_string("en")

    def __repr__(self):
        return (
            f"MPDatetime({self._datetime.year}, {self._datetime.month}, "
            f"{self._datetime.day}, {self._datetime.hour}, "
            f"{self._datetime.minute}, {self._datetime.second})"
        )
