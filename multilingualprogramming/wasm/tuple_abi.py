#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Canonical tuple lowering helpers for JS/WASM interoperability."""

from enum import Enum


class TupleLoweringMode(Enum):
    """Tuple lowering strategies used at the host/WASM boundary."""

    MULTI_VALUE = "multi_value"
    OUT_PARAMS = "out_params"


def lower_tuple_value(value, mode: TupleLoweringMode):
    """Lower Python tuple values for the selected ABI mode."""
    if not isinstance(value, tuple):
        return value
    if mode == TupleLoweringMode.MULTI_VALUE:
        return value
    return {
        "__tuple_out__": True,
        "length": len(value),
        "values": [lower_tuple_value(item, mode) for item in value],
    }


def restore_tuple_value(value, mode: TupleLoweringMode):
    """Restore lowered tuple values from host/WASM boundary representation."""
    if mode == TupleLoweringMode.MULTI_VALUE:
        return value
    if isinstance(value, dict) and value.get("__tuple_out__") is True:
        return tuple(restore_tuple_value(item, mode) for item in value["values"])
    return value
