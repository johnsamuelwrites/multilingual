#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual time handling."""

import datetime as dt
from multilingualprogramming.exceptions import InvalidDateError
from multilingualprogramming.unicode_string import get_unicode_character_string


class MPTime:
    """
    A time object with multilingual formatting.

    Internally stores as Python datetime.time.
    """

    # Script mapping for numeral conversion
    SCRIPT_MAP = {
        "hi": "DEVANAGARI",
        "ar": "ARABIC-INDIC",
        "bn": "BENGALI",
        "ta": "TAMIL",
    }

    def __init__(self, hour=0, minute=0, second=0, time=None):
        """
        Create an MPTime.

        Parameters:
            hour (int): Hour (0-23)
            minute (int): Minute (0-59)
            second (int): Second (0-59)
            time (datetime.time): Python time object
        """
        if time is not None:
            self._time = time
        else:
            try:
                self._time = dt.time(hour, minute, second)
            except ValueError as e:
                raise InvalidDateError(str(e)) from e

    def to_time(self):
        """Convert to Python datetime.time."""
        return self._time

    @property
    def hour(self):
        """Return the hour."""
        return self._time.hour

    @property
    def minute(self):
        """Return the minute."""
        return self._time.minute

    @property
    def second(self):
        """Return the second."""
        return self._time.second

    def _format_number(self, number, language, pad=True):
        """Format a number in the given script, zero-padded to 2 digits."""
        unicode_script = self.SCRIPT_MAP.get(language)
        if unicode_script:
            numstr = get_unicode_character_string(unicode_script, number)
            if pad and number < 10:
                zero = get_unicode_character_string(unicode_script, 0)
                numstr = zero + numstr
            return numstr
        if pad:
            return f"{number:02d}"
        return str(number)

    def to_string(self, language="en", use_24h=True):
        """
        Format time in a given language.

        Parameters:
            language (str): Language code
            use_24h (bool): Use 24-hour format (default True)

        Returns:
            str: Formatted time string
        """
        if use_24h:
            h = self._format_number(self._time.hour, language)
            m = self._format_number(self._time.minute, language)
            s = self._format_number(self._time.second, language)
            return f"{h}:{m}:{s}"

        # 12-hour format
        hour_12 = self._time.hour % 12
        if hour_12 == 0:
            hour_12 = 12
        is_pm = self._time.hour >= 12

        h = self._format_number(hour_12, language)
        m = self._format_number(self._time.minute, language)
        s = self._format_number(self._time.second, language)
        time_str = f"{h}:{m}:{s}"

        am_pm_map = {
            "en": ("AM", "PM"),
            "fr": ("", ""),
            "es": ("a.m.", "p.m."),
            "de": ("", ""),
            "hi": ("पूर्वाह्न", "अपराह्न"),
            "ar": ("ص", "م"),
            "bn": ("পূর্বাহ্ন", "অপরাহ্ন"),
            "ta": ("முற்பகல்", "பிற்பகல்"),
            "zh": ("上午", "下午"),
            "ja": ("午前", "午後"),
        }
        am, pm = am_pm_map.get(language, ("AM", "PM"))
        suffix = pm if is_pm else am

        if language in ("zh", "ja"):
            return f"{suffix} {time_str}"
        if suffix:
            return f"{time_str} {suffix}"
        return time_str

    def __eq__(self, other):
        if isinstance(other, MPTime):
            return self._time == other._time
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, MPTime):
            return self._time < other._time
        return NotImplemented

    def __hash__(self):
        return hash(self._time)

    def __str__(self):
        return self.to_string("en")

    def __repr__(self):
        return (
            f"MPTime({self._time.hour}, {self._time.minute}, {self._time.second})"
        )
