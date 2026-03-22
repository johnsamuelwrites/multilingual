#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Placement annotation runtime for @local, @edge, and @cloud.

Placement annotations declare the *preferred deployment target* of a
function or agent without changing its calling convention.  On the Python
backend all three run locally; a future distributed backend can inspect
the ``__ml_placement__`` attribute to route calls appropriately.

Usage (from transpiled Python)
-------------------------------
    from multilingualprogramming.runtime.placement import local, edge, cloud

    @local
    def my_fn(): ...        # hint: run on the local machine

    @edge
    def preprocess(): ...   # hint: run at the network edge

    @cloud
    def heavy_model(): ...  # hint: run in the cloud
"""

from __future__ import annotations

import functools
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

_VALID_PLACEMENTS = frozenset({"local", "edge", "cloud"})


def _make_placement_decorator(placement: str) -> Callable[[F], F]:
    """Return a decorator that tags *fn* with ``__ml_placement__ = placement``."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        wrapper.__ml_placement__ = placement  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


# Public decorators
local = _make_placement_decorator("local")
edge  = _make_placement_decorator("edge")
cloud = _make_placement_decorator("cloud")


def get_placement(fn: Callable) -> str | None:
    """Return the placement hint attached to *fn*, or None."""
    return getattr(fn, "__ml_placement__", None)
