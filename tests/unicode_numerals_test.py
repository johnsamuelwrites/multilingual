#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for multilingual numerals
"""

import unittest
import multilingualprogramming.numeral.unicode_numeral as un
from multilingualprogramming.exceptions import (
    MultipleLanguageCharacterMixError,
    InvalidNumeralCharacterError,
)


class UnicodeNumeralTestSuite(unittest.TestCase):
    """
    Test cases for multilingual numbers
    """

    def setUp(self):
        """
        Set up TestSuite
        """

    def test_un_numeral(self):
        """
        Test to create a base 10 numeral
        """
        num = un.UnicodeNumeral("12")  # create a numeral
        # The value must be 12
        self.assertTrue(num.to_decimal() == 12)

    def test_un_numeral_repr(self):
        """
        Test to create a base 10 numeral
        """
        num = un.UnicodeNumeral("12")  # create a numeral
        self.assertTrue(repr(num) == 'UnicodeNumeral("12")')

    def test_invalid_un_numeral(self):
        """
        Test to create a non-digit number
        """
        try:
            un.UnicodeNumeral("ab")  # create a numeral
        except InvalidNumeralCharacterError as exception:
            self.assertTrue(isinstance(exception, InvalidNumeralCharacterError))

    def test_character_mix_un_numeral(self):
        """
        Test to verify mix of digits from different languages
        """
        try:
            un.UnicodeNumeral("1෫")  # create a numeral
        except MultipleLanguageCharacterMixError as exception:
            self.assertTrue(
                isinstance(
                    exception,
                    MultipleLanguageCharacterMixError,
                )
            )

    def test_un_numeral_addition(self):
        """
        Test to create a base 10 numeral
        """
        num1 = un.UnicodeNumeral("12")  # create a numeral
        num2 = un.UnicodeNumeral("14")  # create a numeral
        self.assertTrue(repr(num1) == 'UnicodeNumeral("12")')
        num3 = num1 + num2
        self.assertTrue(str(num3) == "26")
        self.assertTrue(repr(num3) == 'UnicodeNumeral("26")')

    def test_un_numeral_multiplication(self):
        """
        Test to create a base 10 numeral
        """
        num1 = un.UnicodeNumeral("12")  # create a numeral
        num2 = un.UnicodeNumeral("14")  # create a numeral
        self.assertTrue(repr(num1) == 'UnicodeNumeral("12")')
        num3 = num1 * num2
        self.assertTrue(str(num3) == "168")
        self.assertTrue(repr(num3) == 'UnicodeNumeral("168")')

    def test_un_numeral_malayalam_addition(self):
        """
        Test to create a base 10 numeral
        """
        num1 = un.UnicodeNumeral("൧൩")  # create a numeral
        num2 = un.UnicodeNumeral("൨൪")  # create a numeral
        self.assertTrue(repr(num1) == 'UnicodeNumeral("൧൩")')
        num3 = num1 + num2
        self.assertTrue(str(num3) == "൩൭")
        self.assertTrue(repr(num3) == 'UnicodeNumeral("൩൭")')

    def test_un_numeral_malayalam_multiplication(self):
        """
        Test to create a base 10 numeral
        """
        num1 = un.UnicodeNumeral("൧൩")  # create a numeral
        num2 = un.UnicodeNumeral("൨൪")  # create a numeral
        self.assertTrue(repr(num1) == 'UnicodeNumeral("൧൩")')
        num3 = num1 * num2
        self.assertTrue(str(num3) == "൩൧൨")
        self.assertTrue(repr(num3) == 'UnicodeNumeral("൩൧൨")')
