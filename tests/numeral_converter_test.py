#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for numeral converter
"""

import unittest
from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral
from multilingualprogramming.numeral.numeral_converter import NumeralConverter


class NumeralConverterTestSuite(unittest.TestCase):
    """
    Test cases for numeral conversion between scripts
    """

    def test_convert_digit_to_malayalam(self):
        """Test converting ASCII digits to Malayalam."""
        num = UnicodeNumeral("123")
        result = NumeralConverter.convert(num, "MALAYALAM")
        self.assertEqual(str(result), "൧൨൩")
        self.assertEqual(result.to_decimal(), 123)

    def test_convert_malayalam_to_arabic_indic(self):
        """Test converting Malayalam to Arabic-Indic."""
        num = UnicodeNumeral("൧൨൩")
        result = NumeralConverter.convert(num, "ARABIC-INDIC")
        self.assertEqual(str(result), "١٢٣")
        self.assertEqual(result.to_decimal(), 123)

    def test_convert_arabic_indic_to_bengali(self):
        """Test converting Arabic-Indic to Bengali."""
        num = UnicodeNumeral("١٢٣")
        result = NumeralConverter.convert(num, "BENGALI")
        self.assertEqual(str(result), "১২৩")
        self.assertEqual(result.to_decimal(), 123)

    def test_convert_round_trip(self):
        """Test round-trip conversion preserves value."""
        num = UnicodeNumeral("12345")
        converted = NumeralConverter.convert(num, "MALAYALAM")
        back = NumeralConverter.convert(converted, "DIGIT")
        self.assertEqual(back.to_decimal(), 12345)

    def test_scientific_notation_simple(self):
        """Test scientific notation for a simple number."""
        num = UnicodeNumeral("12300")
        result = NumeralConverter.to_scientific(num)
        self.assertIn("\u00d7", result)  # Contains multiplication sign

    def test_scientific_notation_zero(self):
        """Test scientific notation for zero."""
        num = UnicodeNumeral("0")
        result = NumeralConverter.to_scientific(num)
        self.assertEqual(result, "0")

    def test_from_scientific_notation(self):
        """Test parsing scientific notation."""
        num = UnicodeNumeral("12300")
        sci = NumeralConverter.to_scientific(num)
        parsed = NumeralConverter.from_scientific(sci)
        self.assertEqual(parsed.to_decimal(), 12300)

    def test_scientific_round_trip(self):
        """Test round-trip scientific notation conversion."""
        num = UnicodeNumeral("45600")
        sci = NumeralConverter.to_scientific(num)
        parsed = NumeralConverter.from_scientific(sci)
        self.assertEqual(parsed.to_decimal(), num.to_decimal())

    def test_scientific_notation_malayalam(self):
        """Test scientific notation in Malayalam script."""
        num = UnicodeNumeral("൧൨൩൦൦")
        result = NumeralConverter.to_scientific(num, "MALAYALAM")
        self.assertIn("\u00d7", result)
