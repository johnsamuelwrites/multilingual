#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tuple memory packing helpers for out-params WASM interop."""

from struct import pack, unpack_from


def pack_tuple_out_params(values: tuple[float, ...]) -> bytes:
    """Pack tuple as [len:i32 little-endian][f64...]."""
    header = pack("<i", len(values))
    payload = b"".join(pack("<d", float(v)) for v in values)
    return header + payload


def unpack_tuple_out_params(buffer: bytes) -> tuple[float, ...]:
    """Unpack tuple from [len:i32 little-endian][f64...]."""
    if len(buffer) < 4:
        raise ValueError("buffer too small for tuple header")
    count = unpack_from("<i", buffer, 0)[0]
    needed = 4 + count * 8
    if len(buffer) < needed:
        raise ValueError("buffer too small for tuple payload")
    return tuple(unpack_from("<d", buffer, 4 + i * 8)[0] for i in range(count))
