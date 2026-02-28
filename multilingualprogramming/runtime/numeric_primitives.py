#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Numeric primitives for geometry-heavy workloads."""

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Vec2:
    """2D vector with small, allocation-light helpers."""

    x: float
    y: float

    def add(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def sub(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    def norm_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def distance_sq(self, other: "Vec2") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy


@dataclass(frozen=True)
class ComplexScalar:
    """Small complex-number helper with explicit fields."""

    re: float
    im: float

    def add(self, other: "ComplexScalar") -> "ComplexScalar":
        return ComplexScalar(self.re + other.re, self.im + other.im)

    def mul(self, other: "ComplexScalar") -> "ComplexScalar":
        return ComplexScalar(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def abs_sq(self) -> float:
        return self.re * self.re + self.im * self.im


class FastRNG:
    """Fast deterministic xorshift64* RNG for sampling-heavy loops."""

    def __init__(self, seed: int = 1):
        state = int(seed) & 0xFFFFFFFFFFFFFFFF
        self._state = state if state != 0 else 0x9E3779B97F4A7C15

    def next_u64(self) -> int:
        x = self._state
        x ^= (x >> 12) & 0xFFFFFFFFFFFFFFFF
        x ^= (x << 25) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 27) & 0xFFFFFFFFFFFFFFFF
        self._state = x & 0xFFFFFFFFFFFFFFFF
        return (self._state * 0x2545F4914F6CDD1D) & 0xFFFFFFFFFFFFFFFF

    def next_f64(self) -> float:
        return self.next_u64() / float(0xFFFFFFFFFFFFFFFF)

    def randint(self, low: int, high: int) -> int:
        if high < low:
            raise ValueError("high must be >= low")
        span = (high - low) + 1
        return low + (self.next_u64() % span)


class BoundedArray:
    """Fixed-capacity array for tight loops where list growth is unwanted."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = int(capacity)
        self._data = [None] * self._capacity
        self._size = 0

    def push(self, value) -> bool:
        if self._size >= self._capacity:
            return False
        self._data[self._size] = value
        self._size += 1
        return True

    def clear(self):
        self._size = 0

    def __len__(self):
        return self._size

    def to_list(self):
        return self._data[:self._size]


class MinDistanceAccumulator:
    """Tracks minimum distance to an observed point set."""

    def __init__(self):
        self._points: list[Vec2] = []

    def add_point(self, x: float, y: float):
        self._points.append(Vec2(float(x), float(y)))

    def min_distance_sq(self, x: float, y: float) -> float:
        if not self._points:
            return float("inf")
        probe = Vec2(float(x), float(y))
        return min(p.distance_sq(probe) for p in self._points)

    def min_distance(self, x: float, y: float) -> float:
        return sqrt(self.min_distance_sq(x, y))
