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
import multilingualprogramming.mp_numeral as mpn
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
        self.assertTrue(num.to_numeral() == 10)
        num = mpn.MPNumeral("CLVIII")  # create a numeral
        # The value must be 158
        self.assertTrue(num.to_numeral() == 158)

    def test_mp_numeral_with_un_numeral(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("12")  # create a numeral
        # The value must be 12
        self.assertTrue(num1.to_numeral() == 12)
        num2 = mpn.MPNumeral("൧൩")  # create a numeral
        self.assertTrue(num2.to_numeral() == 13)
        num3 = mpn.MPNumeral("١٢٣٤٥")  # Arabic-Indic numerals
        self.assertTrue(num3.to_numeral() == 12345)

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
        print(num1.to_numeral())
        # The value must be 12.34
        self.assertTrue(num1.to_numeral() == 12.34)

        locale_code = "fr_FR.UTF-8"  # Specify the desired locale code

        try:
            original_locale = locale.setlocale(locale.LC_ALL)
            locale.setlocale(locale.LC_ALL, locale_code)
            num1 = mpn.MPNumeral("12,34")  # create a numeral
            print(num1.to_numeral())
            # The value must be 12.34
            self.assertTrue(num1.to_numeral() == 12.34)
        finally:
            locale.setlocale(locale.LC_ALL, original_locale)
