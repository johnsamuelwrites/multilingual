#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for multilingual date/time
"""

import unittest
import datetime as dt
from multilingualprogramming.datetime.mp_date import MPDate
from multilingualprogramming.datetime.mp_time import MPTime
from multilingualprogramming.datetime.mp_datetime import MPDatetime
from multilingualprogramming.exceptions import InvalidDateError


class MPDateTestSuite(unittest.TestCase):
    """
    Test cases for MPDate
    """

    def test_create_from_components(self):
        """Test creating a date from year/month/day."""
        d = MPDate(2024, 1, 15)
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_create_from_python_date(self):
        """Test creating from Python date object."""
        py_date = dt.date(2024, 6, 20)
        d = MPDate(date=py_date)
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 6)
        self.assertEqual(d.day, 20)

    def test_to_date(self):
        """Test conversion to Python date."""
        d = MPDate(2024, 1, 15)
        py_date = d.to_date()
        self.assertEqual(py_date, dt.date(2024, 1, 15))

    def test_parse_english(self):
        """Test parsing English date string."""
        d = MPDate.from_string("15-January-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_french(self):
        """Test parsing French date string."""
        d = MPDate.from_string("15-Janvier-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_spanish(self):
        """Test parsing Spanish date string."""
        d = MPDate.from_string("15-Enero-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_hindi(self):
        """Test parsing Hindi date string."""
        d = MPDate.from_string("15-जनवरी-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_arabic(self):
        """Test parsing Arabic date string."""
        d = MPDate.from_string("15-يناير-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_german(self):
        """Test parsing German date string."""
        d = MPDate.from_string("15-Januar-2024")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_parse_numeric_iso(self):
        """Test parsing ISO-like numeric date."""
        d = MPDate.from_string("2024-01-15")
        self.assertEqual(d.year, 2024)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)

    def test_format_english(self):
        """Test formatting in English."""
        d = MPDate(2024, 1, 15)
        result = d.to_string("en")
        self.assertIn("January", result)
        self.assertIn("15", result)
        self.assertIn("2024", result)

    def test_format_french(self):
        """Test formatting in French."""
        d = MPDate(2024, 1, 15)
        result = d.to_string("fr")
        self.assertIn("Janvier", result)

    def test_format_hindi(self):
        """Test formatting in Hindi."""
        d = MPDate(2024, 1, 15)
        result = d.to_string("hi")
        self.assertIn("जनवरी", result)
        # Should contain Devanagari numerals
        self.assertIn("१५", result)

    def test_format_chinese(self):
        """Test formatting in Chinese."""
        d = MPDate(2024, 1, 15)
        result = d.to_string("zh")
        self.assertIn("年", result)
        self.assertIn("月", result)
        self.assertIn("日", result)

    def test_format_japanese(self):
        """Test formatting in Japanese."""
        d = MPDate(2024, 1, 15)
        result = d.to_string("ja")
        self.assertIn("年", result)
        self.assertIn("月", result)
        self.assertIn("日", result)

    def test_round_trip_english(self):
        """Test parse -> format -> parse gives same date."""
        d1 = MPDate(2024, 3, 20)
        formatted = d1.to_string("en")
        d2 = MPDate.from_string(formatted)
        self.assertEqual(d1, d2)

    def test_round_trip_french(self):
        """Test parse -> format -> parse gives same date for French."""
        d1 = MPDate(2024, 6, 10)
        formatted = d1.to_string("fr")
        d2 = MPDate.from_string(formatted)
        self.assertEqual(d1, d2)

    def test_add_days(self):
        """Test adding days to a date."""
        d = MPDate(2024, 1, 15)
        result = d + 10
        self.assertEqual(result, MPDate(2024, 1, 25))

    def test_subtract_dates(self):
        """Test difference between dates."""
        d1 = MPDate(2024, 1, 20)
        d2 = MPDate(2024, 1, 15)
        self.assertEqual(d1 - d2, 5)

    def test_subtract_days(self):
        """Test subtracting days from a date."""
        d = MPDate(2024, 1, 15)
        result = d - 5
        self.assertEqual(result, MPDate(2024, 1, 10))

    def test_comparison(self):
        """Test comparison operators."""
        d1 = MPDate(2024, 1, 15)
        d2 = MPDate(2024, 6, 20)
        self.assertTrue(d1 < d2)
        self.assertTrue(d2 > d1)
        self.assertTrue(d1 <= d2)
        self.assertTrue(d2 >= d1)

    def test_equality(self):
        """Test equality."""
        d1 = MPDate(2024, 1, 15)
        d2 = MPDate(2024, 1, 15)
        self.assertEqual(d1, d2)

    def test_invalid_date_error(self):
        """Test that invalid dates raise errors."""
        with self.assertRaises(InvalidDateError):
            MPDate(2024, 13, 1)

    def test_invalid_parse_error(self):
        """Test that unparseable strings raise errors."""
        with self.assertRaises(InvalidDateError):
            MPDate.from_string("not-a-date")


class MPTimeTestSuite(unittest.TestCase):
    """
    Test cases for MPTime
    """

    def test_create_time(self):
        """Test creating a time."""
        t = MPTime(14, 30, 0)
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 30)
        self.assertEqual(t.second, 0)

    def test_format_24h_english(self):
        """Test 24-hour format in English."""
        t = MPTime(14, 30, 45)
        result = t.to_string("en", use_24h=True)
        self.assertEqual(result, "14:30:45")

    def test_format_12h_english(self):
        """Test 12-hour format in English."""
        t = MPTime(14, 30, 0)
        result = t.to_string("en", use_24h=False)
        self.assertIn("PM", result)
        self.assertIn("02", result)

    def test_format_hindi(self):
        """Test formatting in Hindi (Devanagari numerals)."""
        t = MPTime(14, 30, 0)
        result = t.to_string("hi", use_24h=True)
        self.assertIn("१४", result)
        self.assertIn("३०", result)

    def test_format_arabic(self):
        """Test formatting in Arabic (Arabic-Indic numerals)."""
        t = MPTime(14, 30, 0)
        result = t.to_string("ar", use_24h=True)
        self.assertIn("١٤", result)

    def test_format_12h_hindi(self):
        """Test 12-hour format in Hindi."""
        t = MPTime(14, 30, 0)
        result = t.to_string("hi", use_24h=False)
        self.assertIn("अपराह्न", result)

    def test_format_12h_japanese(self):
        """Test 12-hour format in Japanese."""
        t = MPTime(9, 0, 0)
        result = t.to_string("ja", use_24h=False)
        self.assertIn("午前", result)

    def test_equality(self):
        """Test time equality."""
        t1 = MPTime(14, 30, 0)
        t2 = MPTime(14, 30, 0)
        self.assertEqual(t1, t2)

    def test_comparison(self):
        """Test time comparison."""
        t1 = MPTime(9, 0, 0)
        t2 = MPTime(14, 30, 0)
        self.assertTrue(t1 < t2)


class MPDatetimeTestSuite(unittest.TestCase):
    """
    Test cases for MPDatetime
    """

    def test_create_from_components(self):
        """Test creating datetime from components."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        self.assertEqual(mdt.year, 2024)
        self.assertEqual(mdt.month, 1)
        self.assertEqual(mdt.day, 15)
        self.assertEqual(mdt.hour, 14)
        self.assertEqual(mdt.minute, 30)

    def test_create_from_python_datetime(self):
        """Test creating from Python datetime."""
        py_dt = dt.datetime(2024, 6, 20, 10, 0, 0)
        mdt = MPDatetime(datetime_obj=py_dt)
        self.assertEqual(mdt.year, 2024)
        self.assertEqual(mdt.hour, 10)

    def test_from_string(self):
        """Test parsing date string into MPDatetime."""
        mdt = MPDatetime.from_string("15-January-2024")
        self.assertEqual(mdt.year, 2024)
        self.assertEqual(mdt.month, 1)
        self.assertEqual(mdt.day, 15)

    def test_to_datetime(self):
        """Test conversion to Python datetime."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        py_dt = mdt.to_datetime()
        self.assertEqual(py_dt, dt.datetime(2024, 1, 15, 14, 30, 0))

    def test_date_part(self):
        """Test extracting date part."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        d = mdt.date()
        self.assertIsInstance(d, MPDate)
        self.assertEqual(d.year, 2024)

    def test_time_part(self):
        """Test extracting time part."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        t = mdt.time()
        self.assertIsInstance(t, MPTime)
        self.assertEqual(t.hour, 14)

    def test_to_string_english(self):
        """Test formatting in English."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        result = mdt.to_string("en")
        self.assertIn("January", result)
        self.assertIn("14:30", result)

    def test_to_string_french(self):
        """Test formatting in French."""
        mdt = MPDatetime(2024, 1, 15, 14, 30, 0)
        result = mdt.to_string("fr")
        self.assertIn("Janvier", result)

    def test_now(self):
        """Test creating current datetime."""
        mdt = MPDatetime.now()
        self.assertIsNotNone(mdt.year)
        self.assertIsNotNone(mdt.hour)

    def test_equality(self):
        """Test datetime equality."""
        mdt1 = MPDatetime(2024, 1, 15, 14, 30, 0)
        mdt2 = MPDatetime(2024, 1, 15, 14, 30, 0)
        self.assertEqual(mdt1, mdt2)
