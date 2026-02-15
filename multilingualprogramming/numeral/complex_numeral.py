#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Functions to handle complex numbers in multiple languages"""

import re
from multilingualprogramming.numeral.unicode_numeral import UnicodeNumeral
from multilingualprogramming.exceptions import (
    InvalidNumeralCharacterError,
    MultipleLanguageCharacterMixError,
)
from multilingualprogramming.unicode_string import get_unicode_character_string


class ComplexNumeral:
    """
    Handling complex numbers with multilingual numeral support.

    Stores real and imaginary parts as UnicodeNumeral instances.
    Format: "real+imaginaryi" or "real-imaginaryi" in any supported script.
    """

    IMAGINARY_MARKERS = ["i", "ⅈ", "ⅉ"]

    def __init__(self, numstr=None, real=None, imaginary=None):
        """
        Create a ComplexNumeral.

        Parameters:
            numstr (str): A complex number string like "3+4i" or "൩+൪i"
            real (UnicodeNumeral): The real part
            imaginary (UnicodeNumeral): The imaginary part
        """
        if real is not None and imaginary is not None:
            self.real = real
            self.imaginary = imaginary
            self.language_name = real.language_name
        elif numstr is not None:
            self._parse(numstr)
        else:
            raise InvalidNumeralCharacterError(
                "ComplexNumeral requires either numstr or both real and imaginary"
            )

    def _parse(self, numstr):
        """Parse a complex number string."""
        # Remove spaces
        numstr = numstr.strip()

        # Check for imaginary marker at end
        has_imaginary = False
        for marker in self.IMAGINARY_MARKERS:
            if numstr.endswith(marker):
                numstr = numstr[: -len(marker)]
                has_imaginary = True
                break

        if not has_imaginary:
            # Pure real number
            self.real = UnicodeNumeral(numstr)
            self.imaginary = UnicodeNumeral("0")
            self.language_name = self.real.language_name
            return

        # Find the split between real and imaginary parts
        # Look for + or - that is not at the start
        split_pos = None
        for i in range(len(numstr) - 1, 0, -1):
            if numstr[i] in ("+", "-"):
                split_pos = i
                break

        if split_pos is not None:
            real_str = numstr[:split_pos]
            imag_str = numstr[split_pos:]
            # Strip leading '+' since UnicodeNumeral only accepts '-' as sign
            if imag_str.startswith("+"):
                imag_str = imag_str[1:]
            self.real = UnicodeNumeral(real_str)
            self.imaginary = UnicodeNumeral(imag_str)
        else:
            # Pure imaginary (e.g., "4i")
            self.real = UnicodeNumeral("0")
            self.imaginary = UnicodeNumeral(numstr)

        # Determine language from whichever part has a non-DIGIT language
        self.language_name = self.real.language_name
        if self.language_name == "DIGIT" and self.imaginary.language_name != "DIGIT":
            self.language_name = self.imaginary.language_name
        elif self.imaginary.language_name is not None:
            if (
                self.real.language_name is not None
                and self.real.language_name != "DIGIT"
                and self.imaginary.language_name != "DIGIT"
                and self.real.language_name != self.imaginary.language_name
            ):
                raise MultipleLanguageCharacterMixError(
                    "Real and imaginary parts use different scripts"
                )
            if self.imaginary.language_name != "DIGIT":
                self.language_name = self.imaginary.language_name

    def to_complex(self):
        """
        Convert to Python complex number.

        Returns:
            complex: Python complex number
        """
        return complex(self.real.to_decimal(), self.imaginary.to_decimal())

    def _make_result(self, result_complex):
        """Create a new ComplexNumeral from a Python complex result."""
        lang = self.language_name or "DIGIT"
        real_val = result_complex.real
        imag_val = result_complex.imag

        # Convert to int if possible
        if real_val == int(real_val):
            real_val = int(real_val)
        if imag_val == int(imag_val):
            imag_val = int(imag_val)

        real_str = get_unicode_character_string(lang, real_val)
        imag_str = get_unicode_character_string(lang, imag_val)

        return ComplexNumeral(
            real=UnicodeNumeral(real_str),
            imaginary=UnicodeNumeral(imag_str),
        )

    def __add__(self, other):
        """Add two ComplexNumerals."""
        result = self.to_complex() + other.to_complex()
        return self._make_result(result)

    def __sub__(self, other):
        """Subtract two ComplexNumerals."""
        result = self.to_complex() - other.to_complex()
        return self._make_result(result)

    def __mul__(self, other):
        """Multiply two ComplexNumerals."""
        result = self.to_complex() * other.to_complex()
        return self._make_result(result)

    def __truediv__(self, other):
        """Divide two ComplexNumerals."""
        result = self.to_complex() / other.to_complex()
        return self._make_result(result)

    def __abs__(self):
        """Return the magnitude as a UnicodeNumeral."""
        magnitude = abs(self.to_complex())
        if magnitude == int(magnitude):
            magnitude = int(magnitude)
        lang = self.language_name or "DIGIT"
        return UnicodeNumeral(get_unicode_character_string(lang, magnitude))

    def conjugate(self):
        """Return the complex conjugate."""
        result = self.to_complex().conjugate()
        return self._make_result(result)

    def __eq__(self, other):
        if isinstance(other, ComplexNumeral):
            return self.to_complex() == other.to_complex()
        return NotImplemented

    def __hash__(self):
        return hash(self.to_complex())

    def __str__(self):
        """Return string representation in the original script."""
        real_str = str(self.real)
        imag_str = str(self.imaginary)
        imag_val = self.imaginary.to_decimal()

        if imag_val == 0:
            return real_str
        if self.real.to_decimal() == 0:
            return f"{imag_str}i"

        if imag_val >= 0:
            return f"{real_str}+{imag_str}i"
        return f"{real_str}{imag_str}i"

    def __repr__(self):
        return f'ComplexNumeral("{self}")'
