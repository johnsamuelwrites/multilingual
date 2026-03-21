#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 reactive runtime.

Provides the Signal/ReactiveEngine infrastructure that backs `observe var`
bindings and `on <signal>.change` event handlers.

Design
------
- Signal[T]          — an observable value cell.  Writing a new value
                       notifies all registered handlers synchronously.
- ReactiveEngine     — manages a registry of named signals and their
                       change handlers.
- stream_to_view     — connects an AI stream (Iterator[StreamChunk]) to
                       a Signal[str], appending chunks as they arrive.
- CanvasNode         — lightweight in-memory representation of a declared
                       canvas block, used before the JS/HTML code-gen step.

Usage
-----
    from multilingualprogramming.runtime.reactive import ReactiveEngine, Signal

    engine = ReactiveEngine()
    count = engine.declare("count", initial=0)

    @engine.on_change("count")
    def log_count(new_val):
        print(f"count changed to {new_val}")

    count.set(1)   # prints "count changed to 1"
    count.set(2)   # prints "count changed to 2"
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------------

class Signal(Generic[T]):
    """An observable value cell.

    Handlers registered via ``on_change`` are called synchronously every time
    the value changes.  The handler receives the new value as its sole
    argument.
    """

    def __init__(self, name: str, value: T) -> None:
        self._name = name
        self._value = value
        self._handlers: list[Callable[[T], None]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the declared signal name."""
        return self._name

    def get(self) -> T:
        """Return the current value."""
        return self._value

    def set(self, value: T) -> None:
        """Update the value and notify all registered handlers."""
        self._value = value
        for handler in self._handlers:
            handler(value)

    def on_change(self, handler: Callable[[T], None]) -> Callable[[T], None]:
        """Register a change handler.  Returns the handler for convenience."""
        self._handlers.append(handler)
        return handler

    def remove_handler(self, handler: Callable[[T], None]) -> None:
        """Remove a previously registered handler."""
        self._handlers = [h for h in self._handlers if h is not handler]

    def __repr__(self) -> str:
        return f"Signal({self._name!r}, value={self._value!r})"


# ---------------------------------------------------------------------------
# ReactiveEngine
# ---------------------------------------------------------------------------

class ReactiveEngine:
    """Manages named signals and wires `on <signal>.change` handlers.

    This is the per-program (or per-module) reactive context.
    """

    def __init__(self) -> None:
        self._signals: dict[str, Signal[Any]] = {}

    # ------------------------------------------------------------------
    # Signal management
    # ------------------------------------------------------------------

    def declare(self, name: str, initial: Any = None) -> Signal[Any]:
        """Declare a new signal with an initial value.

        If a signal with the same name already exists, returns it unchanged.
        """
        if name not in self._signals:
            self._signals[name] = Signal(name, initial)
        return self._signals[name]

    def get(self, name: str) -> Signal[Any]:
        """Return the signal registered under *name*.  Raises KeyError if absent."""
        return self._signals[name]

    def names(self) -> list[str]:
        """Return all declared signal names."""
        return list(self._signals.keys())

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def on_change(self, signal_name: str) -> Callable[[Callable[..., None]], Callable[..., None]]:
        """Decorator that registers a handler for the named signal.

        Usage::

            @engine.on_change("count")
            def handle(new_value):
                ...
        """
        def decorator(fn: Callable[..., None]) -> Callable[..., None]:
            sig = self.declare(signal_name)
            sig.on_change(fn)
            return fn
        return decorator

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Return a dict mapping signal names to their current values."""
        return {name: sig.get() for name, sig in self._signals.items()}


# ---------------------------------------------------------------------------
# Stream-to-view binding
# ---------------------------------------------------------------------------

def stream_to_view(
    stream: Iterator[Any],
    signal: Signal[str],
    *,
    append: bool = True,
    transform: Callable[[Any], str] | None = None,
) -> None:
    """Drive *signal* with chunks from *stream*.

    Parameters
    ----------
    stream:
        Any iterable that yields chunk objects (e.g. ``StreamChunk`` from
        ``ai_types``) or plain strings.
    signal:
        The ``Signal[str]`` to update.  If *append* is True each chunk is
        concatenated onto the previous value; otherwise the signal is replaced.
    append:
        When True (default) chunks are appended to the current value.
    transform:
        Optional callable applied to each raw chunk before it is used.
        Defaults to ``str(chunk.text)`` for objects with a ``.text`` attribute,
        ``str(chunk.content)`` for objects with a ``.content`` attribute,
        or ``str(chunk)`` for everything else.
    """
    for chunk in stream:
        if transform is not None:
            text = transform(chunk)
        elif hasattr(chunk, "text"):
            text = str(chunk.text)
        elif hasattr(chunk, "content"):
            text = str(chunk.content)
        else:
            text = str(chunk)

        if append:
            signal.set(signal.get() + text)
        else:
            signal.set(text)


# ---------------------------------------------------------------------------
# Canvas node (in-memory representation)
# ---------------------------------------------------------------------------

class CanvasNode:
    """In-memory representation of a `canvas` block.

    The UI lowering pass converts an ``IRCanvasBlock`` into a ``CanvasNode``
    tree before emitting HTML/JS.

    ``children`` is a list of ``CanvasNode`` or plain values.
    ``bindings`` maps slot names to ``Signal`` objects that drive live updates.
    """

    def __init__(
        self,
        name: str = "",
        children: list["CanvasNode | Any"] | None = None,
        bindings: dict[str, Signal[Any]] | None = None,
    ) -> None:
        self.name = name
        self.children: list[CanvasNode | Any] = children or []
        self.bindings: dict[str, Signal[Any]] = bindings or {}

    def bind(self, slot: str, signal: Signal[Any]) -> None:
        """Attach *signal* to the named slot in this canvas node."""
        self.bindings[slot] = signal
        signal.on_change(lambda val: self._on_slot_change(slot, val))

    def _on_slot_change(self, slot: str, value: Any) -> None:
        """Called whenever a bound signal changes.  Override in subclasses."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict (useful for testing and JS codegen)."""
        return {
            "name": self.name,
            "bindings": {k: v.get() for k, v in self.bindings.items()},
            "children": [
                c.to_dict() if isinstance(c, CanvasNode) else c
                for c in self.children
            ],
        }

    def __repr__(self) -> str:
        return f"CanvasNode({self.name!r}, bindings={list(self.bindings)!r})"
