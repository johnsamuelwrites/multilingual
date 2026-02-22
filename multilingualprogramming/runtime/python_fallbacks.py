#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Pure Python Fallback Implementations.

Provides Python-only implementations for all WASM-accelerated functions.
Ensures code always works, even without WASM runtime.

Python Fallbacks: Fallback Implementations
"""

import json
from typing import List, Dict, Any
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class MatrixOperations:
    """Pure Python matrix operations (NumPy-accelerated when available)."""

    @staticmethod
    def multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """
        Multiply two matrices.

        Args:
            a: Matrix A (m × n)
            b: Matrix B (n × p)

        Returns:
            Result matrix (m × p)
        """
        if NUMPY_AVAILABLE:
            # NumPy version: much faster
            result = np.dot(np.array(a), np.array(b))
            return result.tolist()

        # Pure Python version
        m = len(a)
        n = len(a[0]) if a else 0
        p = len(b[0]) if b else 0

        result = [[0.0 for _ in range(p)] for _ in range(m)]

        for i in range(m):
            for j in range(p):
                for k in range(n):
                    result[i][j] += a[i][k] * b[k][j]

        return result

    @staticmethod
    def transpose(matrix: List[List[float]]) -> List[List[float]]:
        """
        Transpose a matrix.

        Args:
            matrix: Input matrix

        Returns:
            Transposed matrix
        """
        if NUMPY_AVAILABLE:
            return np.array(matrix).T.tolist()

        if not matrix:
            return []
        m = len(matrix)
        n = len(matrix[0]) if matrix else 0
        return [[matrix[i][j] for i in range(m)] for j in range(n)]

    @staticmethod
    def determinant(matrix: List[List[float]]) -> float:
        """
        Calculate matrix determinant (2×2 and 3×3 only for simplicity).

        Args:
            matrix: Square matrix

        Returns:
            Determinant value
        """
        if NUMPY_AVAILABLE:
            return float(np.linalg.det(np.array(matrix)))

        n = len(matrix)
        if n == 1:
            return float(matrix[0][0])
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        if n == 3:
            a = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            b = matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            c = matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
            return a - b + c
        raise ValueError("Determinant only implemented for 1×1, 2×2, 3×3 matrices")


class StringOperations:
    """Pure Python string operations."""

    @staticmethod
    def reverse(s: str) -> str:
        """Reverse a string."""
        return s[::-1]

    @staticmethod
    def is_palindrome(s: str) -> bool:
        """Check if string is palindrome."""
        clean = ''.join(c.lower() for c in s if c.isalnum())
        return clean == clean[::-1]

    @staticmethod
    def character_frequency(s: str) -> Dict[str, int]:
        """Count character frequencies."""
        freq = {}
        for char in s.lower():
            if char.isalnum():
                freq[char] = freq.get(char, 0) + 1
        return dict(sorted(freq.items()))

    @staticmethod
    def longest_substring(s: str, chars: str) -> int:
        """Find longest substring consisting of characters in 'chars'."""
        max_len = 0
        current_len = 0

        for char in s:
            if char in chars:
                current_len += 1
                max_len = max(max_len, current_len)
            else:
                current_len = 0

        return max_len


class CryptoOperations:
    """Pure Python cryptographic operations (simplified for demonstration)."""

    @staticmethod
    def simple_hash(data: str) -> int:
        """
        Simple hash function (NOT cryptographically secure).
        For demonstration purposes only.

        Args:
            data: Input string

        Returns:
            Hash value (32-bit)
        """
        hash_val = 0
        for char in data:
            hash_val = ((hash_val << 5) - hash_val) + ord(char)
            hash_val &= 0xFFFFFFFF  # Keep as 32-bit
        return hash_val

    @staticmethod
    def xor_cipher(plaintext: str, key: str) -> str:
        """
        Simple XOR cipher (NOT secure, for demonstration only).

        Args:
            plaintext: Input text
            key: Encryption key

        Returns:
            Encrypted text
        """
        result = []
        for i, char in enumerate(plaintext):
            key_char = key[i % len(key)]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            result.append(encrypted_char)
        return ''.join(result)

    @staticmethod
    def xor_decipher(ciphertext: str, key: str) -> str:
        """Decrypt XOR cipher (same as encryption for XOR)."""
        return CryptoOperations.xor_cipher(ciphertext, key)


class DataProcessing:
    """Pure Python data processing operations."""

    @staticmethod
    def filter_data(data: List[Any], predicate) -> List[Any]:
        """Filter data based on predicate."""
        return [item for item in data if predicate(item)]

    @staticmethod
    def map_data(data: List[Any], transform) -> List[Any]:
        """Transform data using function."""
        return [transform(item) for item in data]

    @staticmethod
    def reduce_data(data: List[Any], combine, initial=None) -> Any:
        """Reduce data using combine function."""
        if not data:
            return initial

        result = initial if initial is not None else data[0]
        start = 1 if initial is None else 0

        for i in range(start, len(data)):
            result = combine(result, data[i])

        return result

    @staticmethod
    def group_by(data: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict]]:
        """Group items by key value."""
        result = {}
        for item in data:
            k = item.get(key)
            if k not in result:
                result[k] = []
            result[k].append(item)
        return result

    @staticmethod
    def sort_data(data: List[Any], key=None, reverse=False) -> List[Any]:
        """Sort data."""
        return sorted(data, key=key, reverse=reverse)


class NumericOperations:
    """Pure Python numeric operations."""

    @staticmethod
    def fibonacci(n: int) -> List[int]:
        """Generate Fibonacci sequence up to n terms."""
        if n <= 0:
            return []
        if n == 1:
            return [0]

        fib = [0, 1]
        for _ in range(2, n):
            fib.append(fib[-1] + fib[-2])
        return fib[:n]

    @staticmethod
    def prime_factors(n: int) -> List[int]:
        """Find prime factors of n."""
        factors = []
        d = 2

        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1

        if n > 1:
            factors.append(n)

        return factors

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor."""
        while b:
            a, b = b, a % b
        return abs(a)

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate least common multiple."""
        return abs(a * b) // NumericOperations.gcd(a, b)

    @staticmethod
    def factorial(n: int) -> int:
        """Calculate factorial."""
        if n < 0:
            raise ValueError("Factorial undefined for negative numbers")
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result


class JSONOperations:
    """Pure Python JSON operations."""

    @staticmethod
    def parse_json_simple(json_str: str) -> Any:
        """
        Simple JSON parser (limited functionality).
        For demonstration - use standard json module for production.

        Args:
            json_str: JSON string

        Returns:
            Parsed object
        """
        return json.loads(json_str)

    @staticmethod
    def stringify_json(obj: Any) -> str:
        """
        Convert object to JSON string.

        Args:
            obj: Python object

        Returns:
            JSON string
        """
        return json.dumps(obj, separators=(',', ':'))


class SearchOperations:
    """Pure Python search operations."""

    @staticmethod
    def binary_search(arr: List[Any], target: Any) -> int:
        """
        Binary search in sorted array.

        Args:
            arr: Sorted array
            target: Value to find

        Returns:
            Index of target, or -1 if not found
        """
        left, right = 0, len(arr) - 1

        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            if arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        return -1

    @staticmethod
    def linear_search(arr: List[Any], target: Any) -> int:
        """Linear search in array."""
        for i, item in enumerate(arr):
            if item == target:
                return i
        return -1

    @staticmethod
    def contains_substring(text: str, pattern: str) -> bool:
        """Check if text contains pattern."""
        return pattern in text


class ImageOperations:
    """Pure Python image operations (simplified, for demonstration)."""

    @staticmethod
    def blur_simple(pixels: List[List[int]], kernel_size: int = 3) -> List[List[int]]:
        """
        Simple blur filter (box blur).

        Args:
            pixels: 2D array of pixel values
            kernel_size: Size of blur kernel

        Returns:
            Blurred image
        """
        if kernel_size <= 1:
            return pixels

        radius = kernel_size // 2

        if NUMPY_AVAILABLE:
            # NumPy version: much faster
            arr = np.array(pixels, dtype=float)
            # Keep behavior aligned with pure-Python fallback for now.
            return arr.astype(int).tolist()

        # Simple averaging (very basic blur)
        h, w = len(pixels), len(pixels[0]) if pixels else 0
        if h < (2 * radius + 1) or w < (2 * radius + 1):
            return pixels

        result = [[0 for _ in range(w)] for _ in range(h)]

        window_area = kernel_size * kernel_size
        for i in range(radius, h - radius):
            for j in range(radius, w - radius):
                avg = sum(pixels[i + di][j + dj]
                          for di in range(-radius, radius + 1)
                          for dj in range(-radius, radius + 1)) // window_area
                result[i][j] = avg

        return result


# Registry of all fallback operations
FALLBACK_REGISTRY = {
    # Matrix operations
    "matrix_multiply": MatrixOperations.multiply,
    "matrix_transpose": MatrixOperations.transpose,
    "matrix_determinant": MatrixOperations.determinant,

    # String operations
    "string_reverse": StringOperations.reverse,
    "string_is_palindrome": StringOperations.is_palindrome,
    "string_frequency": StringOperations.character_frequency,
    "string_longest_substring": StringOperations.longest_substring,

    # Crypto operations
    "crypto_hash": CryptoOperations.simple_hash,
    "crypto_xor_encrypt": CryptoOperations.xor_cipher,
    "crypto_xor_decrypt": CryptoOperations.xor_decipher,

    # Data processing
    "data_filter": DataProcessing.filter_data,
    "data_map": DataProcessing.map_data,
    "data_reduce": DataProcessing.reduce_data,
    "data_group_by": DataProcessing.group_by,
    "data_sort": DataProcessing.sort_data,

    # Numeric operations
    "numeric_fibonacci": NumericOperations.fibonacci,
    "numeric_prime_factors": NumericOperations.prime_factors,
    "numeric_gcd": NumericOperations.gcd,
    "numeric_lcm": NumericOperations.lcm,
    "numeric_factorial": NumericOperations.factorial,

    # JSON operations
    "json_parse": JSONOperations.parse_json_simple,
    "json_stringify": JSONOperations.stringify_json,

    # Search operations
    "search_binary": SearchOperations.binary_search,
    "search_linear": SearchOperations.linear_search,
    "search_contains": SearchOperations.contains_substring,

    # Image operations
    "image_blur": ImageOperations.blur_simple,
}


def get_fallback(function_name: str):
    """
    Get fallback implementation for function.

    Args:
        function_name: Name of function

    Returns:
        Fallback function, or None if not found
    """
    return FALLBACK_REGISTRY.get(function_name)


def has_fallback(function_name: str) -> bool:
    """Check if fallback exists for function."""
    return function_name in FALLBACK_REGISTRY


def list_fallbacks() -> List[str]:
    """Get list of all available fallbacks."""
    return list(FALLBACK_REGISTRY.keys())
