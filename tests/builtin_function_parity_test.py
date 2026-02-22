#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for builtin function parity across languages."""

import unittest
from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute(source, language="en"):
    """Execute and return output."""
    result = ProgramExecutor(language=language, check_semantics=True).execute(source)
    return result.output if result.success else ""


class BuiltinFunctionParityTestSuite(unittest.TestCase):
    """Tests for builtin function behavior."""

    # Length function
    def test_len_list_english(self):
        source = "print(len([1, 2, 3]))"
        output = _execute(source, "en")
        self.assertIn("3", output)

    def test_len_string_english(self):
        source = 'print(len("hello"))'
        output = _execute(source, "en")
        self.assertIn("5", output)

    def test_len_dict_english(self):
        source = 'print(len({"a": 1, "b": 2}))'
        output = _execute(source, "en")
        self.assertIn("2", output)

    # Range function
    def test_range_basic_english(self):
        source = "print(list(range(3)))"
        output = _execute(source, "en")
        self.assertIn("[0, 1, 2]", output)

    def test_range_with_start_stop_english(self):
        source = "print(list(range(1, 4)))"
        output = _execute(source, "en")
        self.assertIn("[1, 2, 3]", output)

    def test_range_with_step_english(self):
        source = "print(list(range(0, 10, 2)))"
        output = _execute(source, "en")
        self.assertIn("[0, 2, 4, 6, 8]", output)

    # Type function
    def test_type_int_english(self):
        source = "print(type(42).__name__)"
        output = _execute(source, "en")
        self.assertIn("int", output)

    def test_type_str_english(self):
        source = 'print(type("hello").__name__)'
        output = _execute(source, "en")
        self.assertIn("str", output)

    def test_type_list_english(self):
        source = "print(type([]).__name__)"
        output = _execute(source, "en")
        self.assertIn("list", output)

    # Abs function
    def test_abs_positive_english(self):
        source = "print(abs(42))"
        output = _execute(source, "en")
        self.assertIn("42", output)

    def test_abs_negative_english(self):
        source = "print(abs(-42))"
        output = _execute(source, "en")
        self.assertIn("42", output)

    # Min and max
    def test_min_english(self):
        source = "print(min(3, 1, 2))"
        output = _execute(source, "en")
        self.assertIn("1", output)

    def test_max_english(self):
        source = "print(max(3, 1, 2))"
        output = _execute(source, "en")
        self.assertIn("3", output)

    def test_min_list_english(self):
        source = "print(min([3, 1, 2]))"
        output = _execute(source, "en")
        self.assertIn("1", output)

    # Sum function
    def test_sum_list_english(self):
        source = "print(sum([1, 2, 3]))"
        output = _execute(source, "en")
        self.assertIn("6", output)

    def test_sum_with_start_english(self):
        source = "print(sum([1, 2, 3], 10))"
        output = _execute(source, "en")
        self.assertIn("16", output)

    # Sorted function
    def test_sorted_list_english(self):
        source = "print(sorted([3, 1, 2]))"
        output = _execute(source, "en")
        self.assertIn("[1, 2, 3]", output)

    def test_sorted_reverse_english(self):
        source = "print(sorted([3, 1, 2], reverse=True))"
        output = _execute(source, "en")
        self.assertIn("[3, 2, 1]", output)

    # Enumerate function
    def test_enumerate_english(self):
        source = "for i, x in enumerate(['a', 'b']):\n    print(i, x)\n"
        output = _execute(source, "en")
        self.assertIn("0 a", output)
        self.assertIn("1 b", output)

    # Zip function
    def test_zip_english(self):
        source = "for x, y in zip([1, 2], ['a', 'b']):\n    print(x, y)\n"
        output = _execute(source, "en")
        self.assertIn("1 a", output)
        self.assertIn("2 b", output)

    # Map function
    def test_map_english(self):
        source = "result = list(map(lambda x: x * 2, [1, 2, 3]))\nprint(result)\n"
        output = _execute(source, "en")
        self.assertIn("[2, 4, 6]", output)

    # Filter function
    def test_filter_english(self):
        source = "result = list(filter(lambda x: x > 1, [1, 2, 3]))\nprint(result)\n"
        output = _execute(source, "en")
        self.assertIn("[2, 3]", output)

    # Any and all
    def test_any_true_english(self):
        source = "print(any([False, True, False]))"
        output = _execute(source, "en")
        self.assertIn("True", output)

    def test_all_true_english(self):
        source = "print(all([True, True, True]))"
        output = _execute(source, "en")
        self.assertIn("True", output)

    def test_all_false_english(self):
        source = "print(all([True, False, True]))"
        output = _execute(source, "en")
        self.assertIn("False", output)

    # Int and str conversions
    def test_int_conversion_english(self):
        source = 'print(int("42"))'
        output = _execute(source, "en")
        self.assertIn("42", output)

    def test_str_conversion_english(self):
        source = "print(str(42))"
        output = _execute(source, "en")
        self.assertIn("42", output)

    # Pow function
    def test_pow_english(self):
        source = "print(pow(2, 3))"
        output = _execute(source, "en")
        self.assertIn("8", output)

    def test_pow_with_modulo_english(self):
        source = "print(pow(2, 3, 5))"
        output = _execute(source, "en")
        self.assertIn("3", output)

    # Divmod function
    def test_divmod_english(self):
        source = "q, r = divmod(17, 5)\nprint(q, r)\n"
        output = _execute(source, "en")
        self.assertIn("3 2", output)


if __name__ == "__main__":
    unittest.main()
