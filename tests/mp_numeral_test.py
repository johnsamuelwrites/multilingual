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


class MP_Numeral_TestSuite(unittest.TestCase):
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
        num = mpn.mp_numeral("12")  # create a numeral
        # The length must be greater than 0
        self.assertTrue(num.to_numeral() == 12)
