#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for fraction numerals
"""

import unittest
from fractions import Fraction
from multilingualprogramming.numeral.fraction_numeral import FractionNumeral
from multilingualprogramming.exceptions import InvalidNumeralCharacterError


class FractionNumeralTestSuite(unittest.TestCase):
    """
    Test cases for fraction handling
    """

    def test_create_from_unicode_half(self):
        """Test creating from Unicode vulgar fraction ½."""
        f = FractionNumeral("½")
        self.assertEqual(f.to_fraction(), Fraction(1, 2))

    def test_create_from_unicode_third(self):
        """Test creating from Unicode vulgar fraction ⅓."""
        f = FractionNumeral("⅓")
        self.assertEqual(f.to_fraction(), Fraction(1, 3))

    def test_create_from_unicode_quarter(self):
        """Test creating from Unicode vulgar fraction ¼."""
        f = FractionNumeral("¼")
        self.assertEqual(f.to_fraction(), Fraction(1, 4))

    def test_create_from_unicode_three_quarters(self):
        """Test creating from Unicode vulgar fraction ¾."""
        f = FractionNumeral("¾")
        self.assertEqual(f.to_fraction(), Fraction(3, 4))

    def test_create_from_slash_notation(self):
        """Test creating from slash notation."""
        f = FractionNumeral("3/4")
        self.assertEqual(f.to_fraction(), Fraction(3, 4))

    def test_create_from_slash_notation_large(self):
        """Test creating from slash notation with larger numbers."""
        f = FractionNumeral("7/12")
        self.assertEqual(f.to_fraction(), Fraction(7, 12))

    def test_create_from_malayalam(self):
        """Test creating from Malayalam numerals."""
        f = FractionNumeral("൩/൪")
        self.assertEqual(f.to_fraction(), Fraction(3, 4))
        self.assertEqual(f.language_name, "MALAYALAM")

    def test_to_decimal(self):
        """Test conversion to decimal."""
        f = FractionNumeral("½")
        self.assertAlmostEqual(f.to_decimal(), 0.5)

    def test_addition(self):
        """Test adding two fractions."""
        f1 = FractionNumeral("1/4")
        f2 = FractionNumeral("1/4")
        result = f1 + f2
        self.assertEqual(result.to_fraction(), Fraction(1, 2))

    def test_subtraction(self):
        """Test subtracting two fractions."""
        f1 = FractionNumeral("3/4")
        f2 = FractionNumeral("1/4")
        result = f1 - f2
        self.assertEqual(result.to_fraction(), Fraction(1, 2))

    def test_multiplication(self):
        """Test multiplying two fractions."""
        f1 = FractionNumeral("2/3")
        f2 = FractionNumeral("3/4")
        result = f1 * f2
        self.assertEqual(result.to_fraction(), Fraction(1, 2))

    def test_division(self):
        """Test dividing two fractions."""
        f1 = FractionNumeral("1/2")
        f2 = FractionNumeral("1/4")
        result = f1 / f2
        self.assertEqual(result.to_fraction(), Fraction(2, 1))

    def test_simplify(self):
        """Test fraction simplification."""
        f = FractionNumeral("4/8")
        simplified = f.simplify()
        self.assertEqual(simplified.to_fraction(), Fraction(1, 2))

    def test_comparison(self):
        """Test comparison operators."""
        f1 = FractionNumeral("1/4")
        f2 = FractionNumeral("1/2")
        self.assertTrue(f1 < f2)
        self.assertTrue(f2 > f1)
        self.assertTrue(f1 <= f2)
        self.assertTrue(f2 >= f1)

    def test_equality(self):
        """Test equality."""
        f1 = FractionNumeral("2/4")
        f2 = FractionNumeral("1/2")
        self.assertEqual(f1, f2)

    def test_invalid_fraction(self):
        """Test invalid fraction string raises error."""
        with self.assertRaises(InvalidNumeralCharacterError):
            FractionNumeral("abc")

    def test_division_by_zero(self):
        """Test division by zero raises error."""
        with self.assertRaises(InvalidNumeralCharacterError):
            FractionNumeral("3/0")
