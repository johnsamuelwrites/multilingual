#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for roman numerals
"""

import unittest
import multilingualprogramming.roman_numeral as rn

class RomanNumeralTestSuite(unittest.TestCase):
    """
    Test cases for Roman numbers
    """

    def setUp(self):
        """
        Set up TestSuite
        """

    def test_roman_numeral(self):
        """
        Test to create a Roman numeral
        """
        num = rn.RomanNumeral("X")  # create a numeral
        # The value must be 10
        self.assertTrue(num.to_numeral() == 10)
        num = rn.RomanNumeral("CLVIII")  # create a numeral
        # The value must be 10
        self.assertTrue(num.to_numeral() == 158)
