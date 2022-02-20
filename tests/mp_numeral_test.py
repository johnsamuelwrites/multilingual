#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for multilingual numerals
"""

import unittest
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

    def test_mp_numeral(self):
        """
        Test to create a base 10 numeral
        """
        num = mpn.MPNumeral("12")  # create a numeral
        # The value must be 12
        self.assertTrue(num.to_numeral() == 12)

    def test_mp_numeral_repr(self):
        """
        Test to create a base 10 numeral
        """
        num = mpn.MPNumeral("12")  # create a numeral
        self.assertTrue(repr(num) == 'MPNumeral("12")')

    def test_invalid_mp_numeral(self):
        """
        Test to create a non-digit number
        """
        try:
            mpn.MPNumeral("ab")  # create a numeral
        except InvalidNumeralCharacterError as exception:
            self.assertTrue(isinstance(exception, InvalidNumeralCharacterError))

    def test_character_mix_mp_numeral(self):
        """
        Test to verify mix of digits from different languages
        """
        try:
            mpn.MPNumeral("1෫")  # create a numeral
        except MultipleLanguageCharacterMixError as exception:
            self.assertTrue(
                isinstance(
                    exception,
                    MultipleLanguageCharacterMixError,
                )
            )

    def test_mp_numeral_addition(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("12")  # create a numeral
        num2 = mpn.MPNumeral("14")  # create a numeral
        self.assertTrue(repr(num1) == 'MPNumeral("12")')
        num3 = num1 + num2
        self.assertTrue(str(num3) == "26")
        self.assertTrue(repr(num3) == 'MPNumeral("26")')

    def test_mp_numeral_malayalam_addition(self):
        """
        Test to create a base 10 numeral
        """
        num1 = mpn.MPNumeral("൧൩")  # create a numeral
        num2 = mpn.MPNumeral("൨൪")  # create a numeral
        self.assertTrue(repr(num1) == 'MPNumeral("൧൩")')
        num3 = num1 + num2
        self.assertTrue(str(num3) == "൩൭")
        self.assertTrue(repr(num3) == 'MPNumeral("൩൭")')
