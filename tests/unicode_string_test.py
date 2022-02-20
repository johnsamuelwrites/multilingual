#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for multilingual numerals
"""

import unittest
from multilingualprogramming.unicode_string import get_number_list


class UnicodeStringTestSuite(unittest.TestCase):
    """
    Test cases for handling unicode strings for numbers
    """

    def setUp(self):
        """
        Set up TestSuite
        """

    def test_get_number_list_Malayalam(self):
        """
        Get numbers from a list
        """
        desired_number_list = ["൦", "൧", "൨", "൩", "൪", "൫", "൬", "൭", "൮", "൯"]
        number_list = get_number_list("MALAYALAM")  # create a numeral
        # The value must be 12
        self.assertTrue(len(number_list) == 10)
        for i, j in zip(desired_number_list, number_list):
            self.assertTrue(i==j)

    def test_get_number_list_Bengali(self):
        """
        Get numbers from a list
        """
        desired_number_list = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"]
        number_list = get_number_list("BENGALI")  # create a numeral
        # The value must be 12
        self.assertTrue(len(number_list) == 10)
        for i, j in zip(desired_number_list, number_list):
            self.assertTrue(i==j)
