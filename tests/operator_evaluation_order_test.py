#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for operator evaluation order parity with Python."""

import unittest
from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute(source):
    """Execute multilingual source and return output."""
    result = ProgramExecutor(language="en", check_semantics=True).execute(source)
    return result.output if result.success else ""


class OperatorEvaluationOrderTestSuite(unittest.TestCase):
    """Tests for operator evaluation order and side effects."""

    def test_short_circuit_and_no_side_effect(self):
        """AND short-circuits, not evaluating right side."""
        source = """\
def side_effect():
    print("called")
    return True
let result = False and side_effect()
print("done")
"""
        output = _execute(source)
        self.assertNotIn("called", output)
        self.assertIn("done", output)

    def test_short_circuit_or_no_side_effect(self):
        """OR short-circuits when left is True."""
        source = """\
def side_effect():
    print("called")
    return False
let result = True or side_effect()
print("done")
"""
        output = _execute(source)
        self.assertNotIn("called", output)
        self.assertIn("done", output)

    def test_and_evaluates_both_when_needed(self):
        """AND evaluates both when left is True."""
        source = """\
def track():
    print("evaluated")
    return True
let result = True and track()
"""
        output = _execute(source)
        self.assertIn("evaluated", output)

    def test_or_evaluates_both_when_needed(self):
        """OR evaluates right when left is False."""
        source = """\
def track():
    print("evaluated")
    return False
let result = False or track()
"""
        output = _execute(source)
        self.assertIn("evaluated", output)

    def test_comparison_chain_evaluation(self):
        """Comparison chains evaluate all expressions."""
        source = """\
let a = 1
let b = 2
let c = 3
let result = a < b < c
print(result)
"""
        output = _execute(source)
        self.assertIn("True", output)

    def test_function_arguments_left_to_right(self):
        """Function arguments evaluated left to right."""
        source = """\
let order = []
def track(x):
    order.append(x)
    return x
def f(a, b, c):
    return a + b + c
let result = f(track(1), track(2), track(3))
print(len(order))
"""
        output = _execute(source)
        self.assertIn("3", output)

    def test_operator_precedence_mult_before_add(self):
        """Multiplication has higher precedence than addition."""
        source = """\
let result = 2 + 3 * 4
print(result)
"""
        output = _execute(source)
        self.assertIn("14", output)

    def test_operator_precedence_power_highest(self):
        """Power has highest precedence."""
        source = """\
let result = 2 ** 3 ** 2
print(result)
"""
        output = _execute(source)
        self.assertIn("512", output)

    def test_unary_minus_precedence(self):
        """Unary minus has high precedence."""
        source = """\
let result = -2 ** 2
print(result)
"""
        output = _execute(source)
        self.assertIn("-4", output)

    def test_truthiness_evaluation(self):
        """Truthiness determines boolean outcomes."""
        source = """\
let result = [] and "truthy"
print(result)
"""
        output = _execute(source)
        self.assertIn("[]", output)

    def test_boolean_return_values(self):
        """Boolean operators return actual values."""
        source = """\
let x = 0 or 5
print(x)
"""
        output = _execute(source)
        self.assertIn("5", output)

    def test_nested_boolean_precedence(self):
        """AND has higher precedence than OR."""
        source = """\
let result = True or False and False
print(result)
"""
        output = _execute(source)
        self.assertIn("True", output)

    def test_comparison_returns_boolean(self):
        """Comparisons return boolean values."""
        source = """\
let result = 5 > 3
print(result)
print(type(result).__name__)
"""
        output = _execute(source)
        self.assertIn("True", output)

    def test_membership_operator_precedence(self):
        """Membership operators work with other comparisons."""
        source = """\
let result = 1 < 2 < 3
print(result)
"""
        output = _execute(source)
        self.assertIn("True", output)


if __name__ == "__main__":
    unittest.main()
