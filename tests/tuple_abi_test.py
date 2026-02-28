#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for tuple ABI lowering and restoration."""

import unittest

from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend
from multilingualprogramming.wasm.tuple_abi import (
    TupleLoweringMode,
    lower_tuple_value,
    restore_tuple_value,
)


class TupleABITestSuite(unittest.TestCase):
    """Validate tuple lowering modes."""

    def test_out_params_lower_and_restore_roundtrip(self):
        value = (1, 2, (3, 4))
        lowered = lower_tuple_value(value, TupleLoweringMode.OUT_PARAMS)
        self.assertIsInstance(lowered, dict)
        restored = restore_tuple_value(lowered, TupleLoweringMode.OUT_PARAMS)
        self.assertEqual(restored, value)

    def test_multi_value_keeps_tuple_shape(self):
        value = (1, 2, 3)
        lowered = lower_tuple_value(value, TupleLoweringMode.MULTI_VALUE)
        self.assertEqual(lowered, value)
        restored = restore_tuple_value(lowered, TupleLoweringMode.MULTI_VALUE)
        self.assertEqual(restored, value)

    def test_backend_selector_uses_tuple_mode_for_argument_lowering(self):
        selector = BackendSelector(prefer_backend=Backend.PYTHON)
        selector.set_tuple_lowering_mode(TupleLoweringMode.OUT_PARAMS)
        lowered = selector._convert_to_wasm((1, 2), 3)  # pylint: disable=protected-access
        self.assertIsInstance(lowered[0], dict)

        selector.set_tuple_lowering_mode(TupleLoweringMode.MULTI_VALUE)
        lowered_mv = selector._convert_to_wasm((1, 2), 3)  # pylint: disable=protected-access
        self.assertIsInstance(lowered_mv[0], tuple)


if __name__ == "__main__":
    unittest.main()
