# pylint: disable=duplicate-code
#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Test suite for multilingual numerals and associated operations."""

import unittest
from multilingualprogramming.unicode_string import (
    get_number_list,
    get_unicode_character,
    get_unicode_character_string,
)


class UnicodeStringTestSuite(unittest.TestCase):
    """
    Test cases for handling unicode strings for numbers
    """

    def setUp(self):
        """
        Set up TestSuite
        """

    def test_get_number_list_malayalam(self):
        """
        Get numbers from a list (Malayalam)
        """
        desired_number_list = ["൦", "൧", "൨", "൩", "൪", "൫", "൬", "൭", "൮", "൯"]
        number_list = get_number_list("MALAYALAM")  # create a numeral
        # The length must be 10
        self.assertTrue(len(number_list) == 10)
        for i, j in zip(desired_number_list, number_list):
            self.assertTrue(i == j)

    def test_get_unicode_character_malayalam(self):
        """
        Get number in Malayalam
        """
        desired_number = "൧"
        character = get_unicode_character("MALAYALAM", "ONE")  # create a numeral
        self.assertTrue(desired_number == character)

    def test_get_number_list_bengali(self):
        """
        Get numbers from a list (Bengali)
        """
        desired_number_list = ["০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯"]
        number_list = get_number_list("BENGALI")  # create a numeral
        # The value must be 12
        self.assertTrue(len(number_list) == 10)
        for i, j in zip(desired_number_list, number_list):
            self.assertTrue(i == j)

    def test_get_unicode_character_string(self):
        """
        Get unicode number string (Malayalam)
        """
        unicode_string = get_unicode_character_string("MALAYALAM", 12345)
        self.assertTrue(len(unicode_string) == 5)
        self.assertTrue(unicode_string == "൧൨൩൪൫")
