#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""channel<T> runtime for the Multilingual structured-concurrency model.

A Channel is a typed async FIFO pipe between concurrent tasks.  It wraps
``asyncio.Queue`` so that Multilingual's ``channel<T>()``, ``send``, and
``receive`` constructs map directly to awaitable operations.

Usage (from transpiled Python)
-------------------------------
    from multilingualprogramming.runtime.channel import Channel

    ch = Channel()                   # channel<T>() — unbounded
    ch_bounded = Channel(capacity=8) # channel<T>(8) — bounded buffer

    await ch.send(value)             # channel.send(value)
    item = await ch.receive()        # channel.receive()
    await ch.close()                 # signal no more items
"""

from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")


class Channel(Generic[T]):
    """Typed async FIFO channel backed by asyncio.Queue.

    Parameters
    ----------
    capacity:
        Maximum number of buffered items.  0 (default) means unbounded.
    """

    _SENTINEL = object()

    def __init__(self, capacity: int = 0) -> None:
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=capacity)
        self._closed = False

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    async def send(self, value: T) -> None:
        """Send *value* into the channel.  Blocks if the buffer is full."""
        if self._closed:
            raise RuntimeError("Cannot send on a closed channel")
        await self._queue.put(value)

    async def receive(self) -> T:
        """Receive the next value.  Blocks until one is available.

        Raises StopAsyncIteration when the channel is closed and empty.
        """
        item = await self._queue.get()
        if item is self._SENTINEL:
            # Put the sentinel back so other receivers also unblock
            self._queue.put_nowait(self._SENTINEL)
            raise StopAsyncIteration
        return item  # type: ignore[return-value]

    async def close(self) -> None:
        """Signal that no more values will be sent."""
        self._closed = True
        await self._queue.put(self._SENTINEL)

    # ------------------------------------------------------------------
    # Convenience: async iteration
    # ------------------------------------------------------------------

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        try:
            return await self.receive()
        except StopAsyncIteration:
            raise StopAsyncIteration from None

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def empty(self) -> bool:
        """Return ``True`` when no buffered items are waiting."""
        return self._queue.empty()

    @property
    def size(self) -> int:
        """Return the current number of buffered items."""
        return self._queue.qsize()

    def __repr__(self) -> str:
        status = "closed" if self._closed else f"size={self.size}"
        return f"Channel({status})"
