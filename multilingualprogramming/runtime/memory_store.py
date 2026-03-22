#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Named persistent memory stores for the Multilingual agent memory model.

Provides the runtime backing for the ``memory(name)`` language construct.
Scopes:

* ``session``    — in-process dict; lost when the program exits (default)
* ``persistent`` — JSON-backed file store in the current working directory
* ``shared``     — in-process shared store accessible by all agents in a swarm

Usage (from transpiled Python)
-------------------------------
    from multilingualprogramming.runtime.memory_store import ml_memory

    store = ml_memory("facts")          # session scope by default
    store["capital"] = "Paris"
    print(store["capital"])             # "Paris"

    hist = ml_memory("history", scope="persistent")
    hist["last_query"] = "What is AI?"
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterator


# ---------------------------------------------------------------------------
# Scoped backing stores
# ---------------------------------------------------------------------------

_SESSION_STORES: dict[str, dict[str, Any]] = {}
_SHARED_STORE:   dict[str, Any] = {}   # single shared namespace for swarm


class MemoryStore:
    """A dict-like named memory store.

    Parameters
    ----------
    name:
        Logical name for the store (used as the filename for persistent scope).
    scope:
        ``"session"``, ``"persistent"``, or ``"shared"``.
    """

    def __init__(self, name: str, scope: str = "session") -> None:
        self._name = name
        self._scope = scope
        if scope == "session":
            if name not in _SESSION_STORES:
                _SESSION_STORES[name] = {}
            self._data = _SESSION_STORES[name]
        elif scope == "shared":
            self._data = _SHARED_STORE
        elif scope == "persistent":
            self._data = self._load_persistent(name)
        else:
            raise ValueError(f"Unknown memory scope {scope!r}")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _persistent_path(name: str) -> str:
        return os.path.join(os.getcwd(), f".ml_memory_{name}.json")

    @classmethod
    def _load_persistent(cls, name: str) -> dict[str, Any]:
        path = cls._persistent_path(name)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_persistent(self) -> None:
        if self._scope != "persistent":
            return
        path = self._persistent_path(self._name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # dict-like interface
    # ------------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save_persistent()

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self._save_persistent()

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def update(self, other: dict) -> None:
        self._data.update(other)
        self._save_persistent()

    def clear(self) -> None:
        self._data.clear()
        self._save_persistent()

    def __repr__(self) -> str:
        return f"MemoryStore({self._name!r}, scope={self._scope!r}, {self._data!r})"


def ml_memory(name: str, scope: str = "session") -> MemoryStore:
    """Return the named MemoryStore, creating it if necessary."""
    return MemoryStore(name, scope=scope)
