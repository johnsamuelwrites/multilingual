#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle fractions in multiple languages"""

from fractions import Fraction
from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral
from multilingualprogramming.exceptions import InvalidNumeralCharacterError
from multilingualprogramming.unicode_string import (
    UNICODE_FRACTION_MAP,
    get_unicode_character_string,
)


class FractionNumeral:
    """
    Handling fractions with multilingual numeral support.

    Supports:
    - Unicode vulgar fractions: ½, ⅓, ¼, etc.
    - Constructed fractions: "3/4", "൩/൪" (in any script)
    """

    def __init__(self, numstr):
        """
        Create a FractionNumeral.

        Parameters:
            numstr (str): A fraction string like "½", "3/4", or "൩/൪"
        """
        self.numstr = numstr
        self.language_name = None
        self._fraction = None
        self._parse(numstr)

    def _parse(self, numstr):
        """Parse a fraction string into a Fraction object."""
        numstr = numstr.strip()

        # Check for Unicode vulgar fraction characters
        if len(numstr) == 1 and numstr in UNICODE_FRACTION_MAP:
            numerator, denominator = UNICODE_FRACTION_MAP[numstr]
            self._fraction = Fraction(numerator, denominator)
            self.language_name = "DIGIT"
            return

        # Check for "numerator/denominator" format
        if "/" in numstr:
            parts = numstr.split("/", 1)
            if len(parts) == 2:
                num_part = UnicodeNumeral(parts[0].strip())
                den_part = UnicodeNumeral(parts[1].strip())
                self.language_name = num_part.language_name
                numerator = num_part.to_decimal()
                denominator = den_part.to_decimal()
                if denominator == 0:
                    raise InvalidNumeralCharacterError(
                        "Division by zero in fraction"
                    )
                self._fraction = Fraction(numerator, denominator)
                return

        raise InvalidNumeralCharacterError(
            f"Cannot parse fraction: {numstr}"
        )

    def to_fraction(self):
        """
        Convert to Python Fraction.

        Returns:
            Fraction: Python Fraction object
        """
        return self._fraction

    def to_decimal(self):
        """
        Convert to decimal float.

        Returns:
            float: The decimal value
        """
        return float(self._fraction)

    def simplify(self):
        """
        Return a simplified version of this fraction.

        Returns:
            FractionNumeral: Simplified fraction
        """
        simplified = Fraction(
            self._fraction.numerator, self._fraction.denominator
        )
        lang = self.language_name or "DIGIT"
        num_str = get_unicode_character_string(lang, simplified.numerator)
        den_str = get_unicode_character_string(lang, simplified.denominator)
        return FractionNumeral(f"{num_str}/{den_str}")

    def _make_result(self, result_fraction):
        """Create a new FractionNumeral from a Python Fraction."""
        lang = self.language_name or "DIGIT"
        num_str = get_unicode_character_string(lang, result_fraction.numerator)
        den_str = get_unicode_character_string(
            lang, result_fraction.denominator
        )
        return FractionNumeral(f"{num_str}/{den_str}")

    def __add__(self, other):
        """Add two FractionNumerals."""
        result = self._fraction + other._fraction
        return self._make_result(result)

    def __sub__(self, other):
        """Subtract two FractionNumerals."""
        result = self._fraction - other._fraction
        return self._make_result(result)

    def __mul__(self, other):
        """Multiply two FractionNumerals."""
        result = self._fraction * other._fraction
        return self._make_result(result)

    def __truediv__(self, other):
        """Divide two FractionNumerals."""
        result = self._fraction / other._fraction
        return self._make_result(result)

    def __eq__(self, other):
        if isinstance(other, FractionNumeral):
            return self._fraction == other._fraction
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, FractionNumeral):
            return self._fraction < other._fraction
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, FractionNumeral):
            return self._fraction <= other._fraction
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, FractionNumeral):
            return self._fraction > other._fraction
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, FractionNumeral):
            return self._fraction >= other._fraction
        return NotImplemented

    def __hash__(self):
        return hash(self._fraction)

    def __str__(self):
        """Return string representation."""
        return self.numstr

    def __repr__(self):
        return f'FractionNumeral("{self.numstr}")'
