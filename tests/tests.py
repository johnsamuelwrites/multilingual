#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Main file to run all the test suites
"""

import unittest

from tests.mp_numeral_test import MPNumeralTestSuite
from tests.roman_numerals_test import RomanNumeralTestSuite
from tests.unicode_numerals_test import UnicodeNumeralTestSuite
from tests.unicode_string_test import UnicodeStringTestSuite

if __name__ == "__main__":
    mp_numeral_tests = MPNumeralTestSuite()
    roman_numeral_tests = RomanNumeralTestSuite()
    unicode_numeral_tests = UnicodeNumeralTestSuite()
    unicode_string_tests = UnicodeStringTestSuite()
    tests = unittest.TestSuite(
        [
            mp_numeral_tests,
            roman_numeral_tests,
            unicode_numeral_tests,
            unicode_string_tests,
        ]
    )
    unittest.main()
