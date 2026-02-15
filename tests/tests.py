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
from tests.keyword_registry_test import KeywordRegistryTestSuite, KeywordValidatorTestSuite
from tests.complex_numeral_test import ComplexNumeralTestSuite
from tests.fraction_numeral_test import FractionNumeralTestSuite
from tests.numeral_converter_test import NumeralConverterTestSuite
from tests.mp_datetime_test import MPDateTestSuite, MPTimeTestSuite, MPDatetimeTestSuite
from tests.lexer_test import LexerTestSuite

if __name__ == "__main__":
    mp_numeral_tests = MPNumeralTestSuite()
    roman_numeral_tests = RomanNumeralTestSuite()
    unicode_numeral_tests = UnicodeNumeralTestSuite()
    unicode_string_tests = UnicodeStringTestSuite()
    keyword_registry_tests = KeywordRegistryTestSuite()
    keyword_validator_tests = KeywordValidatorTestSuite()
    complex_numeral_tests = ComplexNumeralTestSuite()
    fraction_numeral_tests = FractionNumeralTestSuite()
    numeral_converter_tests = NumeralConverterTestSuite()
    mp_date_tests = MPDateTestSuite()
    mp_time_tests = MPTimeTestSuite()
    mp_datetime_tests = MPDatetimeTestSuite()
    lexer_tests = LexerTestSuite()
    tests = unittest.TestSuite(
        [
            mp_numeral_tests,
            roman_numeral_tests,
            unicode_numeral_tests,
            unicode_string_tests,
            keyword_registry_tests,
            keyword_validator_tests,
            complex_numeral_tests,
            fraction_numeral_tests,
            numeral_converter_tests,
            mp_date_tests,
            mp_time_tests,
            mp_datetime_tests,
            lexer_tests,
        ]
    )
    unittest.main()
