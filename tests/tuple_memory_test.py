#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for tuple out-param memory packing helpers."""

import unittest

from multilingualprogramming.wasm.tuple_memory import (
    pack_tuple_out_params,
    unpack_tuple_out_params,
)


class TupleMemoryTestSuite(unittest.TestCase):
    """Validate tuple memory binary layout helpers."""

    def test_pack_unpack_roundtrip(self):
        values = (1.5, -2.0, 42.25)
        packed = pack_tuple_out_params(values)
        restored = unpack_tuple_out_params(packed)
        self.assertEqual(restored, values)

    def test_unpack_rejects_short_header(self):
        with self.assertRaises(ValueError):
            unpack_tuple_out_params(b"\x00\x01")

    def test_unpack_rejects_short_payload(self):
        with self.assertRaises(ValueError):
            unpack_tuple_out_params(b"\x01\x00\x00\x00\x00")


if __name__ == "__main__":
    unittest.main()
