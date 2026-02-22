#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Tests for Python Fallback Implementations.

Python Fallback Implementations
Validates that pure Python versions work correctly.
"""

import unittest
import math
from multilingualprogramming.runtime.python_fallbacks import (
    MatrixOperations,
    StringOperations,
    CryptoOperations,
    DataProcessing,
    NumericOperations,
    JSONOperations,
    SearchOperations,
    ImageOperations,
    get_fallback,
    has_fallback,
    list_fallbacks,
)


class MatrixOperationsFallbackTestSuite(unittest.TestCase):
    """Test matrix operation fallbacks."""

    def test_matrix_multiply_identity(self):
        """Verify matrix multiplication with identity."""
        identity = [[1, 0], [0, 1]]
        a = [[1, 2], [3, 4]]

        result = MatrixOperations.multiply(a, identity)

        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 2)
        self.assertEqual(result[1][0], 3)
        self.assertEqual(result[1][1], 4)

    def test_matrix_multiply_2x2(self):
        """Verify 2×2 matrix multiplication."""
        a = [[1, 2], [3, 4]]
        b = [[5, 6], [7, 8]]

        result = MatrixOperations.multiply(a, b)

        # [1*5+2*7, 1*6+2*8] = [19, 22]
        # [3*5+4*7, 3*6+4*8] = [43, 50]
        self.assertEqual(result[0][0], 19)
        self.assertEqual(result[0][1], 22)
        self.assertEqual(result[1][0], 43)
        self.assertEqual(result[1][1], 50)

    def test_matrix_transpose(self):
        """Verify matrix transpose."""
        a = [[1, 2, 3], [4, 5, 6]]
        result = MatrixOperations.transpose(a)

        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(result[0], [1, 4])
        self.assertEqual(result[1], [2, 5])
        self.assertEqual(result[2], [3, 6])

    def test_matrix_determinant_2x2(self):
        """Verify 2×2 determinant."""
        a = [[1, 2], [3, 4]]
        det = MatrixOperations.determinant(a)

        # det = 1*4 - 2*3 = -2
        self.assertEqual(det, -2)

    def test_matrix_determinant_identity(self):
        """Verify identity matrix determinant is 1."""
        identity = [[1, 0], [0, 1]]
        det = MatrixOperations.determinant(identity)
        self.assertEqual(det, 1)


class StringOperationsFallbackTestSuite(unittest.TestCase):
    """Test string operation fallbacks."""

    def test_string_reverse(self):
        """Verify string reversal."""
        result = StringOperations.reverse("hello")
        self.assertEqual(result, "olleh")

    def test_string_reverse_empty(self):
        """Verify empty string reversal."""
        result = StringOperations.reverse("")
        self.assertEqual(result, "")

    def test_is_palindrome_true(self):
        """Verify palindrome detection (true case)."""
        self.assertTrue(StringOperations.is_palindrome("racecar"))
        self.assertTrue(StringOperations.is_palindrome("A man, a plan, a canal: Panama"))

    def test_is_palindrome_false(self):
        """Verify palindrome detection (false case)."""
        self.assertFalse(StringOperations.is_palindrome("hello"))
        self.assertFalse(StringOperations.is_palindrome("python"))

    def test_character_frequency(self):
        """Verify character frequency counting."""
        result = StringOperations.character_frequency("aabbcc")
        self.assertEqual(result['a'], 2)
        self.assertEqual(result['b'], 2)
        self.assertEqual(result['c'], 2)

    def test_longest_substring(self):
        """Verify longest substring finding."""
        result = StringOperations.longest_substring("abc123def456ghi", "0123456789")
        self.assertEqual(result, 3)  # "123" is longest


class CryptoOperationsFallbackTestSuite(unittest.TestCase):
    """Test crypto operation fallbacks."""

    def test_simple_hash_consistency(self):
        """Verify hash function is consistent."""
        text = "test"
        hash1 = CryptoOperations.simple_hash(text)
        hash2 = CryptoOperations.simple_hash(text)
        self.assertEqual(hash1, hash2)

    def test_xor_cipher_roundtrip(self):
        """Verify XOR cipher encryption/decryption."""
        plaintext = "hello"
        key = "secret"

        encrypted = CryptoOperations.xor_cipher(plaintext, key)
        decrypted = CryptoOperations.xor_decipher(encrypted, key)

        self.assertEqual(decrypted, plaintext)

    def test_xor_cipher_different_with_different_key(self):
        """Verify different keys produce different ciphertexts."""
        plaintext = "hello"
        key1 = "secret"
        key2 = "other"

        encrypted1 = CryptoOperations.xor_cipher(plaintext, key1)
        encrypted2 = CryptoOperations.xor_cipher(plaintext, key2)

        self.assertNotEqual(encrypted1, encrypted2)


class DataProcessingFallbackTestSuite(unittest.TestCase):
    """Test data processing fallbacks."""

    def test_filter_data(self):
        """Verify data filtering."""
        data = [1, 2, 3, 4, 5]
        result = DataProcessing.filter_data(data, lambda x: x > 2)
        self.assertEqual(result, [3, 4, 5])

    def test_map_data(self):
        """Verify data mapping."""
        data = [1, 2, 3]
        result = DataProcessing.map_data(data, lambda x: x * 2)
        self.assertEqual(result, [2, 4, 6])

    def test_reduce_data(self):
        """Verify data reduction."""
        data = [1, 2, 3, 4]
        result = DataProcessing.reduce_data(data, lambda a, b: a + b)
        self.assertEqual(result, 10)

    def test_group_by(self):
        """Verify data grouping."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 25},
        ]
        result = DataProcessing.group_by(data, "age")
        self.assertEqual(len(result[30]), 2)
        self.assertEqual(len(result[25]), 1)

    def test_sort_data(self):
        """Verify data sorting."""
        data = [3, 1, 4, 1, 5]
        result = DataProcessing.sort_data(data)
        self.assertEqual(result, [1, 1, 3, 4, 5])


class NumericOperationsFallbackTestSuite(unittest.TestCase):
    """Test numeric operation fallbacks."""

    def test_fibonacci(self):
        """Verify Fibonacci sequence generation."""
        result = NumericOperations.fibonacci(7)
        self.assertEqual(result, [0, 1, 1, 2, 3, 5, 8])

    def test_fibonacci_empty(self):
        """Verify Fibonacci with n=0."""
        result = NumericOperations.fibonacci(0)
        self.assertEqual(result, [])

    def test_prime_factors(self):
        """Verify prime factorization."""
        result = NumericOperations.prime_factors(12)
        self.assertEqual(result, [2, 2, 3])

    def test_gcd(self):
        """Verify GCD calculation."""
        result = NumericOperations.gcd(48, 18)
        self.assertEqual(result, 6)

    def test_lcm(self):
        """Verify LCM calculation."""
        result = NumericOperations.lcm(12, 18)
        self.assertEqual(result, 36)

    def test_factorial(self):
        """Verify factorial calculation."""
        self.assertEqual(NumericOperations.factorial(0), 1)
        self.assertEqual(NumericOperations.factorial(5), 120)
        self.assertEqual(NumericOperations.factorial(10), 3628800)

    def test_factorial_negative_error(self):
        """Verify factorial raises error for negative input."""
        with self.assertRaises(ValueError):
            NumericOperations.factorial(-1)


class JSONOperationsFallbackTestSuite(unittest.TestCase):
    """Test JSON operation fallbacks."""

    def test_parse_json_object(self):
        """Verify JSON object parsing."""
        json_str = '{"name": "Alice", "age": 30}'
        result = JSONOperations.parse_json_simple(json_str)
        self.assertEqual(result["name"], "Alice")
        self.assertEqual(result["age"], 30)

    def test_parse_json_array(self):
        """Verify JSON array parsing."""
        json_str = '[1, 2, 3]'
        result = JSONOperations.parse_json_simple(json_str)
        self.assertEqual(result, [1, 2, 3])

    def test_stringify_json(self):
        """Verify JSON stringification."""
        obj = {"name": "Alice", "age": 30}
        result = JSONOperations.stringify_json(obj)
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        self.assertEqual(parsed["name"], "Alice")

    def test_json_roundtrip(self):
        """Verify JSON parse/stringify roundtrip."""
        original = {"a": 1, "b": [2, 3], "c": {"d": 4}}
        stringified = JSONOperations.stringify_json(original)
        parsed = JSONOperations.parse_json_simple(stringified)
        self.assertEqual(parsed, original)


class SearchOperationsFallbackTestSuite(unittest.TestCase):
    """Test search operation fallbacks."""

    def test_binary_search_found(self):
        """Verify binary search finds element."""
        arr = [1, 3, 5, 7, 9]
        result = SearchOperations.binary_search(arr, 5)
        self.assertEqual(result, 2)

    def test_binary_search_not_found(self):
        """Verify binary search returns -1 for missing element."""
        arr = [1, 3, 5, 7, 9]
        result = SearchOperations.binary_search(arr, 4)
        self.assertEqual(result, -1)

    def test_linear_search(self):
        """Verify linear search."""
        arr = [5, 3, 1, 9, 7]
        result = SearchOperations.linear_search(arr, 9)
        self.assertEqual(result, 3)

    def test_contains_substring(self):
        """Verify substring search."""
        self.assertTrue(SearchOperations.contains_substring("hello world", "world"))
        self.assertFalse(SearchOperations.contains_substring("hello world", "xyz"))


class ImageOperationsFallbackTestSuite(unittest.TestCase):
    """Test image operation fallbacks."""

    def test_blur_simple(self):
        """Verify simple blur operation."""
        # 3×3 image with uniform values
        pixels = [[100, 100, 100], [100, 100, 100], [100, 100, 100]]
        result = ImageOperations.blur_simple(pixels)

        # Result should still be 3×3
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 3)

    def test_blur_preserves_dimensions(self):
        """Verify blur preserves image dimensions."""
        pixels = [[i + j for j in range(5)] for i in range(5)]
        result = ImageOperations.blur_simple(pixels)

        self.assertEqual(len(result), 5)
        self.assertEqual(len(result[0]), 5)


class FallbackRegistryTestSuite(unittest.TestCase):
    """Test fallback registry functionality."""

    def test_get_fallback_exists(self):
        """Verify getting existing fallback."""
        fallback = get_fallback("matrix_multiply")
        self.assertIsNotNone(fallback)
        self.assertTrue(callable(fallback))

    def test_get_fallback_not_found(self):
        """Verify getting non-existent fallback."""
        fallback = get_fallback("nonexistent_function")
        self.assertIsNone(fallback)

    def test_has_fallback(self):
        """Verify fallback existence check."""
        self.assertTrue(has_fallback("matrix_multiply"))
        self.assertTrue(has_fallback("fibonacci"))
        self.assertFalse(has_fallback("nonexistent"))

    def test_list_fallbacks(self):
        """Verify listing all fallbacks."""
        fallbacks = list_fallbacks()
        self.assertGreater(len(fallbacks), 20)
        self.assertIn("matrix_multiply", fallbacks)
        self.assertIn("numeric_fibonacci", fallbacks)


if __name__ == "__main__":
    unittest.main()
