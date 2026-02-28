#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for numeric primitives used in fractal workloads."""

import unittest

from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.runtime.numeric_primitives import (
    Vec2,
    ComplexScalar,
    FastRNG,
    BoundedArray,
    MinDistanceAccumulator,
)


class NumericPrimitivesTestSuite(unittest.TestCase):
    """Validate correctness of low-level numeric helpers."""

    def test_vec2_operations(self):
        a = Vec2(1.0, 2.0)
        b = Vec2(3.0, 4.0)
        self.assertEqual(a.add(b), Vec2(4.0, 6.0))
        self.assertEqual(a.sub(b), Vec2(-2.0, -2.0))
        self.assertAlmostEqual(a.dot(b), 11.0)
        self.assertAlmostEqual(a.distance_sq(b), 8.0)

    def test_complex_scalar_mul(self):
        a = ComplexScalar(1.0, 2.0)
        b = ComplexScalar(3.0, 4.0)
        c = a.mul(b)
        self.assertAlmostEqual(c.re, -5.0)
        self.assertAlmostEqual(c.im, 10.0)
        self.assertAlmostEqual(c.abs_sq(), 125.0)

    def test_fast_rng_is_deterministic_for_seed(self):
        rng1 = FastRNG(42)
        rng2 = FastRNG(42)
        seq1 = [rng1.next_u64() for _ in range(5)]
        seq2 = [rng2.next_u64() for _ in range(5)]
        self.assertEqual(seq1, seq2)

    def test_bounded_array_capacity(self):
        arr = BoundedArray(2)
        self.assertTrue(arr.push(1))
        self.assertTrue(arr.push(2))
        self.assertFalse(arr.push(3))
        self.assertEqual(arr.to_list(), [1, 2])

    def test_min_distance_accumulator(self):
        acc = MinDistanceAccumulator()
        acc.add_point(0.0, 0.0)
        acc.add_point(2.0, 0.0)
        self.assertAlmostEqual(acc.min_distance_sq(1.0, 0.0), 1.0)

    def test_runtime_builtins_expose_numeric_primitives(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["Vec2"], Vec2)
        self.assertIs(ns["FastRNG"], FastRNG)


if __name__ == "__main__":
    unittest.main()
