#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Abstract Numeral class and methods
"""

from abc import ABC, abstractmethod


class AbstractNumeral(ABC):
    """
    Methods related to numerals
    """

    def __init__(self, numstr: str):
        pass

    @abstractmethod
    def to_decimal(self):
        """
        Returns the decimal number associated with the number string
        given by the user

        return:
           number: number associated with the number string
        """

    def __str__(self):
        """
        Returns the original number string

        return:
           numstr: original number string
        """

    def __repr__(self):
        """
        Returns the representation of an instance

        return:
           reprstr: representation of an instance
        """

    @abstractmethod
    def __lshift__(self, numeral):
        """
        Left-shifting

        return:
           AbstractNumeral: returns the left shifted value
        """

    @abstractmethod
    def __rshift__(self, numeral):
        """
        Right-shifting

        return:
           AbstractNumeral: returns the right shifted value
        """

    @abstractmethod
    def __add__(self, numeral):
        """
        Add a AbstractNumeral with a numeral or another AbstractNumeral

        return:
           AbstractNumeral: returns the sum of a AbstractNumeral
        """

    @abstractmethod
    def __mul__(self, numeral):
        """
        Multiplication

        return:
           AbstractNumeral: returns the product
        """

    @abstractmethod
    def __sub__(self, numeral):
        """
        Substraction

        return:
           AbstractNumeral: returns the difference
        """

    @abstractmethod
    def __truediv__(self, numeral):
        """
        True division

        return:
           AbstractNumeral: returns the value after true division
        """

    @abstractmethod
    def __floordiv__(self, numeral):
        """
        Floor division

        return:
           AbstractNumeral: returns the value after floor division
        """

    @abstractmethod
    def __neg__(self):
        """
        Negation

        return:
           AbstractNumeral: returns the negation
        """

    @abstractmethod
    def __pow__(self, numeral):
        """
        Power

        return:
           AbstractNumeral: returns the power
        """

    @abstractmethod
    def __mod__(self, numeral):
        """
        Modulus

        return:
           AbstractNumeral: returns the modulus value
        """

    @abstractmethod
    def __xor__(self, numeral):
        """
        XOR value

        return:
           AbstractNumeral: returns the XOR value
        """

    @abstractmethod
    def __invert__(self):
        """
        Bitwise inversion value

        return:
           AbstractNumeral: returns the bitwise-inverted value
        """

    @abstractmethod
    def __or__(self, numeral):
        """
        OR value

        return:
           AbstractNumeral: returns the OR value
        """

    def __eq__(self, other):
        """
        Equality comparison

        return:
           bool: True if both numerals have equal decimal values
        """
        if isinstance(other, AbstractNumeral):
            return self.to_decimal() == other.to_decimal()
        return NotImplemented

    def __lt__(self, other):
        """
        Less-than comparison

        return:
           bool: True if this numeral is less than the other
        """
        if isinstance(other, AbstractNumeral):
            return self.to_decimal() < other.to_decimal()
        return NotImplemented

    def __le__(self, other):
        """
        Less-than-or-equal comparison

        return:
           bool: True if this numeral is less than or equal to the other
        """
        if isinstance(other, AbstractNumeral):
            return self.to_decimal() <= other.to_decimal()
        return NotImplemented

    def __gt__(self, other):
        """
        Greater-than comparison

        return:
           bool: True if this numeral is greater than the other
        """
        if isinstance(other, AbstractNumeral):
            return self.to_decimal() > other.to_decimal()
        return NotImplemented

    def __ge__(self, other):
        """
        Greater-than-or-equal comparison

        return:
           bool: True if this numeral is greater than or equal to the other
        """
        if isinstance(other, AbstractNumeral):
            return self.to_decimal() >= other.to_decimal()
        return NotImplemented

    def __hash__(self):
        """
        Hash based on decimal value for consistency with __eq__
        """
        return hash(self.to_decimal())

    def __abs__(self):
        """
        Absolute value

        return:
           AbstractNumeral: returns the absolute value
        """
        raise NotImplementedError("Subclasses must implement __abs__")
