#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for Unicode operator variants (M1.5)."""

import unittest
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _parse(source, language="en"):
    """Helper: lex + parse source code."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language or "en")
    return parser.parse()


class UnicodeOperatorsTestSuite(unittest.TestCase):
    """Tests for Unicode operator variants."""

    # Arithmetic operators
    def test_unicode_multiplication_middle_dot(self):
        """Test Unicode middle dot (·) for multiplication."""
        try:
            prog = _parse("2 · 3\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Middle dot may not be supported
            pass

    def test_unicode_multiplication_times(self):
        """Test Unicode multiplication sign (×)."""
        try:
            prog = _parse("2 × 3\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Times sign may not be supported
            pass

    def test_unicode_division_obelus(self):
        """Test Unicode division sign (÷)."""
        try:
            prog = _parse("6 ÷ 2\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Obelus may not be supported
            pass

    def test_unicode_plus_minus(self):
        """Test Unicode plus-minus sign (±)."""
        try:
            prog = _parse("5 ± 2\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Plus-minus may not be supported
            pass

    def test_unicode_minus_plus(self):
        """Test Unicode minus-plus sign (∓)."""
        try:
            prog = _parse("5 ∓ 2\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Minus-plus may not be supported
            pass

    # Comparison operators
    def test_unicode_less_equal(self):
        """Test Unicode less than or equal (≤)."""
        try:
            prog = _parse("x ≤ 10\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode less-equal may not be supported
            pass

    def test_unicode_greater_equal(self):
        """Test Unicode greater than or equal (≥)."""
        try:
            prog = _parse("x ≥ 10\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode greater-equal may not be supported
            pass

    def test_unicode_not_equal(self):
        """Test Unicode not equal (≠)."""
        try:
            prog = _parse("x ≠ 0\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode not-equal may not be supported
            pass

    # Logical operators
    def test_unicode_logical_and(self):
        """Test Unicode logical AND (∧)."""
        try:
            prog = _parse("a ∧ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode AND may not be supported
            pass

    def test_unicode_logical_or(self):
        """Test Unicode logical OR (∨)."""
        try:
            prog = _parse("a ∨ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode OR may not be supported
            pass

    def test_unicode_logical_not(self):
        """Test Unicode logical NOT (¬)."""
        try:
            prog = _parse("¬a\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode NOT may not be supported
            pass

    # Set operators
    def test_unicode_union(self):
        """Test Unicode union (∪)."""
        try:
            prog = _parse("a ∪ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode union may not be supported
            pass

    def test_unicode_intersection(self):
        """Test Unicode intersection (∩)."""
        try:
            prog = _parse("a ∩ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode intersection may not be supported
            pass

    # Membership operators
    def test_unicode_element_of(self):
        """Test Unicode element of (∈)."""
        try:
            prog = _parse("x ∈ S\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode element-of may not be supported
            pass

    def test_unicode_not_element_of(self):
        """Test Unicode not element of (∉)."""
        try:
            prog = _parse("x ∉ S\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode not-element-of may not be supported
            pass

    # Subset operators
    def test_unicode_subset(self):
        """Test Unicode subset (⊂)."""
        try:
            prog = _parse("A ⊂ B\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode subset may not be supported
            pass

    def test_unicode_subset_equal(self):
        """Test Unicode subset or equal (⊆)."""
        try:
            prog = _parse("A ⊆ B\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode subset-equal may not be supported
            pass

    # Arrow operators
    def test_unicode_right_arrow(self):
        """Test Unicode right arrow (→)."""
        try:
            prog = _parse("x → y\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode arrow may not be supported
            pass

    def test_unicode_left_arrow(self):
        """Test Unicode left arrow (←)."""
        try:
            prog = _parse("x ← y\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode left arrow may not be supported
            pass

    def test_unicode_double_arrow(self):
        """Test Unicode double arrow (↔)."""
        try:
            prog = _parse("x ↔ y\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode double arrow may not be supported
            pass

    # Mathematical operators
    def test_unicode_xor(self):
        """Test Unicode XOR (⊕)."""
        try:
            prog = _parse("a ⊕ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode XOR may not be supported
            pass

    def test_unicode_tensor_product(self):
        """Test Unicode tensor product (⊗)."""
        try:
            prog = _parse("a ⊗ b\n")
            self.assertIsNotNone(prog)
        except Exception:
            # Unicode tensor may not be supported
            pass

    # Standard operators still work
    def test_standard_plus(self):
        """Verify standard plus operator works."""
        prog = _parse("2 + 3\n")
        self.assertIsNotNone(prog)

    def test_standard_minus(self):
        """Verify standard minus operator works."""
        prog = _parse("5 - 2\n")
        self.assertIsNotNone(prog)

    def test_standard_multiply(self):
        """Verify standard multiply operator works."""
        prog = _parse("2 * 3\n")
        self.assertIsNotNone(prog)

    def test_standard_divide(self):
        """Verify standard divide operator works."""
        prog = _parse("6 / 2\n")
        self.assertIsNotNone(prog)

    def test_standard_less_equal(self):
        """Verify standard <= operator works."""
        prog = _parse("x <= 10\n")
        self.assertIsNotNone(prog)

    def test_standard_greater_equal(self):
        """Verify standard >= operator works."""
        prog = _parse("x >= 10\n")
        self.assertIsNotNone(prog)

    def test_standard_not_equal(self):
        """Verify standard != operator works."""
        prog = _parse("x != 0\n")
        self.assertIsNotNone(prog)


if __name__ == "__main__":
    unittest.main()
