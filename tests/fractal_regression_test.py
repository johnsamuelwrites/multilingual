#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Golden semantic regression tests for fractal-like workloads."""

import hashlib
import unittest

from multilingualprogramming.runtime.numeric_primitives import ComplexScalar, FastRNG


def _escape_time_grid(
    width: int = 48,
    height: int = 36,
    cx: float = -0.75,
    cy: float = 0.0,
    scale: float = 2.8,
    max_iter: int = 64,
) -> list[int]:
    values = []
    for j in range(height):
        y = cy + (j / (height - 1) - 0.5) * scale
        for i in range(width):
            x = cx + (i / (width - 1) - 0.5) * scale
            c = ComplexScalar(x, y)
            z = ComplexScalar(0.0, 0.0)
            it = 0
            while it < max_iter and z.abs_sq() <= 4.0:
                z = z.mul(z).add(c)
                it += 1
            values.append(it)
    return values


def _quantiles(values: list[int]) -> tuple[float, float, float]:
    arr = sorted(values)
    n = len(arr)
    q25 = arr[int(0.25 * (n - 1))]
    q50 = arr[int(0.50 * (n - 1))]
    q75 = arr[int(0.75 * (n - 1))]
    return float(q25), float(q50), float(q75)


def _ascii_snapshot(values: list[int], width: int, charset: str = " .:-=+*#%@") -> str:
    max_v = max(values) or 1
    rows = []
    for row_start in range(0, len(values), width):
        row = values[row_start:row_start + width]
        chars = []
        for v in row:
            idx = int((v / max_v) * (len(charset) - 1))
            chars.append(charset[idx])
        rows.append("".join(chars))
    return "\n".join(rows)


def _pgm_bytes(values: list[int], width: int, height: int) -> bytes:
    max_v = max(values) or 1
    pixels = bytearray()
    for v in values:
        gray = int((v / max_v) * 255)
        pixels.append(gray & 0xFF)
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    return header + bytes(pixels)


class FractalRegressionTestSuite(unittest.TestCase):
    """Golden numeric and image-like regression checks."""

    def test_escape_grid_quantiles_and_center_checkpoint(self):
        width, height = 48, 36
        values = _escape_time_grid(width=width, height=height)
        q25, q50, q75 = _quantiles(values)
        self.assertGreaterEqual(q25, 2.0)
        self.assertGreaterEqual(q50, 3.0)
        self.assertGreaterEqual(q75, 6.0)
        self.assertLessEqual(q75, 64.0)

        center_idx = (height // 2) * width + (width // 2)
        self.assertGreaterEqual(values[center_idx], 20)

    def test_escape_grid_low_res_snapshot_hash(self):
        width, height = 48, 36
        values = _escape_time_grid(width=width, height=height)
        snapshot = _ascii_snapshot(values, width=width)
        digest = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
        self.assertEqual(
            digest,
            "971c80c149dce40781642d609d5849feb7e508c2408978b14603480a63ba30d3",
        )

    def test_ifs_point_distribution_range(self):
        rng = FastRNG(123456)
        x, y = 0.0, 0.0
        points = []
        for _ in range(2000):
            r = rng.next_f64()
            if r < 0.01:
                x, y = 0.0, 0.16 * y
            elif r < 0.86:
                x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
            elif r < 0.93:
                x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
            else:
                x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
            points.append((x, y))

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self.assertGreaterEqual(min(xs), -3.0)
        self.assertLessEqual(max(xs), 3.0)
        self.assertGreaterEqual(min(ys), -1.0)
        self.assertLessEqual(max(ys), 12.0)

    def test_escape_grid_pgm_snapshot_hash(self):
        width, height = 48, 36
        values = _escape_time_grid(width=width, height=height)
        pgm = _pgm_bytes(values, width=width, height=height)
        digest = hashlib.sha256(pgm).hexdigest()
        self.assertEqual(
            digest,
            "2abc6fa019693453b76d7c774ec50649c8d1576cff0f2e23763c144c817fd95c",
        )


if __name__ == "__main__":
    unittest.main()
