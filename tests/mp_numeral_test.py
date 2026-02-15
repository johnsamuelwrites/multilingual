#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for multilingual numerals
"""

import unittest
import locale
import multilingualprogramming.numeral.mp_numeral as mpn
from multilingualprogramming.exceptions import (
    MultipleLanguageCharacterMixError,
    InvalidNumeralCharacterError,
)


class MPNumeralTestSuite(unittest.TestCase):
    """
    Test cases for multilingual numbers
    """

    def setUp(self):
        """
        Set up TestSuite
        """

    def test_mp_numeral_with_roman_numeral(self):
        """
        Test to create a Roman numeral
        """
        num = mpn.MPNumeral("X")  # create a numeral
        self.assertTrue(num.to_decimal() == 10)
        num = mpn.MPNumeral("CLVIII")  # create a numeral
        # The value must be 158
        self.assertTrue(num.to_decimal() == 158)

    def test_mp_numeral_with_un_numeral(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("12")  # create a numeral
        # The value must be 12
        self.assertTrue(num1.to_decimal() == 12)
        num2 = mpn.MPNumeral("൧൩")  # create a numeral
        self.assertTrue(num2.to_decimal() == 13)
        num3 = mpn.MPNumeral("١٢٣٤٥")  # Arabic-Indic numerals
        self.assertTrue(num3.to_decimal() == 12345)

    def test_mp_numeral_with_invalid_un_numeral(self):
        """
        Test to create a non-digit number
        """
        try:
            mpn.MPNumeral("ab")  # create a numeral
        except InvalidNumeralCharacterError as exception:
            self.assertTrue(isinstance(exception, InvalidNumeralCharacterError))

    def test_mp_numeral_with_character_mix_un_numeral(self):
        """
        Test to verify mix of digits from different languages
        """
        try:
            mpn.MPNumeral("1෫")  # create a numeral
        except (
            InvalidNumeralCharacterError,
            MultipleLanguageCharacterMixError,
        ) as exception:
            self.assertTrue(
                isinstance(
                    exception,
                    MultipleLanguageCharacterMixError,
                )
            )

    def test_mp_numeral_with_real_numerals(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("12.34")  # create a numeral
        # The value must be 12.34
        self.assertTrue(num1.to_decimal() == 12.34)

        original_locale = locale.setlocale(locale.LC_NUMERIC)
        locale_candidates = [
            "fr_FR.UTF-8",
            "fr_FR.utf8",
            "fr_FR",
            "French_France.1252",
        ]
        selected_locale = None

        try:
            for locale_code in locale_candidates:
                try:
                    selected_locale = locale.setlocale(
                        locale.LC_NUMERIC, locale_code
                    )
                    break
                except locale.Error:
                    continue

            if selected_locale is None:
                self.skipTest("No French locale with comma decimal separator is installed")

            num1 = mpn.MPNumeral("12,34")  # create a numeral

            # The value must be 12.34
            self.assertTrue(num1.to_decimal() == 12.34)
        finally:
            locale.setlocale(locale.LC_NUMERIC, original_locale)

    def test_mp_numeral_operations(self):
        """
        Test for operations on MPNumeral
        """
        num1 = mpn.MPNumeral("12")  # create a numeral
        num2 = mpn.MPNumeral("15")  # create a numeral
        result = num1 + num2
        self.assertTrue(result.to_decimal() == 27)

        num1 = mpn.MPNumeral("V")  # create a numeral
        num2 = mpn.MPNumeral("IV")  # create a numeral
        result = num1 + num2
        self.assertTrue(result.to_decimal() == 9)

    def test_negative_mp_numeral(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("-12")  # create a numeral
        self.assertTrue(num1.to_decimal() == -12)
        num2 = mpn.MPNumeral("15")  # create a numeral
        result = num1 + num2
        self.assertTrue(result.to_decimal() == 3)

        num1 = mpn.MPNumeral("-12")  # create a numeral
        num2 = mpn.MPNumeral("5")  # create a numeral
        result = num1 + num2
        self.assertTrue(result.to_decimal() == -7)
