#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for complex numerals
"""

import unittest
from multilingualprogramming.numeral.complex_numeral import ComplexNumeral
from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral


class ComplexNumeralTestSuite(unittest.TestCase):
    """
    Test cases for complex number handling
    """

    def test_create_from_string(self):
        """Test creating a complex numeral from string."""
        c = ComplexNumeral("3+4i")
        self.assertEqual(c.to_complex(), complex(3, 4))

    def test_create_from_string_negative_imaginary(self):
        """Test creating with negative imaginary part."""
        c = ComplexNumeral("3-4i")
        self.assertEqual(c.to_complex(), complex(3, -4))

    def test_create_pure_imaginary(self):
        """Test creating a pure imaginary number."""
        c = ComplexNumeral("5i")
        self.assertEqual(c.to_complex(), complex(0, 5))

    def test_create_pure_real(self):
        """Test creating a pure real number (no imaginary)."""
        c = ComplexNumeral("7")
        self.assertEqual(c.to_complex(), complex(7, 0))

    def test_create_from_parts(self):
        """Test creating from UnicodeNumeral parts."""
        real = UnicodeNumeral("3")
        imag = UnicodeNumeral("4")
        c = ComplexNumeral(real=real, imaginary=imag)
        self.assertEqual(c.to_complex(), complex(3, 4))

    def test_addition(self):
        """Test adding two complex numerals."""
        c1 = ComplexNumeral("3+4i")
        c2 = ComplexNumeral("1+2i")
        result = c1 + c2
        self.assertEqual(result.to_complex(), complex(4, 6))

    def test_subtraction(self):
        """Test subtracting two complex numerals."""
        c1 = ComplexNumeral("5+3i")
        c2 = ComplexNumeral("2+1i")
        result = c1 - c2
        self.assertEqual(result.to_complex(), complex(3, 2))

    def test_multiplication(self):
        """Test multiplying two complex numerals."""
        c1 = ComplexNumeral("3+2i")
        c2 = ComplexNumeral("1+4i")
        result = c1 * c2
        # (3+2i)(1+4i) = 3+12i+2i+8i² = 3+14i-8 = -5+14i
        self.assertEqual(result.to_complex(), complex(-5, 14))

    def test_division(self):
        """Test dividing two complex numerals."""
        c1 = ComplexNumeral("4+2i")
        c2 = ComplexNumeral("2+0i")
        result = c1 / c2
        self.assertEqual(result.to_complex(), complex(2, 1))

    def test_absolute_value(self):
        """Test absolute value (magnitude)."""
        c = ComplexNumeral("3+4i")
        magnitude = abs(c)
        self.assertEqual(magnitude.to_decimal(), 5)

    def test_conjugate(self):
        """Test complex conjugate."""
        c = ComplexNumeral("3+4i")
        conj = c.conjugate()
        self.assertEqual(conj.to_complex(), complex(3, -4))

    def test_equality(self):
        """Test equality comparison."""
        c1 = ComplexNumeral("3+4i")
        c2 = ComplexNumeral("3+4i")
        self.assertEqual(c1, c2)

    def test_str_representation(self):
        """Test string output."""
        c = ComplexNumeral("3+4i")
        self.assertIn("3", str(c))
        self.assertIn("4", str(c))
        self.assertIn("i", str(c))

    def test_malayalam_complex(self):
        """Test complex numbers in Malayalam script."""
        c1 = ComplexNumeral("൩+൪i")
        self.assertEqual(c1.to_complex(), complex(3, 4))
        self.assertEqual(c1.language_name, "MALAYALAM")

    def test_language_preservation(self):
        """Test that operations preserve the language."""
        c1 = ComplexNumeral("൩+൪i")
        c2 = ComplexNumeral("൧+൨i")
        result = c1 + c2
        self.assertEqual(result.language_name, "MALAYALAM")
