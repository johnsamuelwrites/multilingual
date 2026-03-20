#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Smart Backend Selector for transparent Python/WASM execution.

Automatically detects and selects the best execution backend:
- WASM for performance-critical code
- Python fallback when WASM unavailable

Backend Selection: Smart Backend Loader
"""

from typing import Dict, Any, Callable, Optional
from enum import Enum
import sys
from multilingualprogramming.wasm.loader import WasmModule
from multilingualprogramming.wasm.tuple_abi import (
    TupleLoweringMode,
    lower_tuple_value,
    restore_tuple_value,
)
from multilingualprogramming.runtime.python_fallbacks import FALLBACK_REGISTRY

try:
    import wasmtime
except ImportError:
    wasmtime = None

class Backend(Enum):
    """Execution backend selection."""
    PYTHON = "python"
    WASM = "wasm"
    AUTO = "auto"


class BackendSelector:  # pylint: disable=too-many-instance-attributes
    """
    Intelligently selects between Python and WASM execution.

    Features:
    - Automatic backend detection
    - Manual backend override
    - Performance monitoring
    - Fallback handling
    """

    def __init__(self, prefer_backend: Backend = Backend.AUTO):
        """
        Initialize backend selector.

        Args:
            prefer_backend: Preferred execution backend
        """
        self._backend = prefer_backend
        self._wasm_available = self._check_wasm_available()
        self._python_fallback = None
        self._wasm_module = None
        self._performance_stats: Dict[str, Dict[str, float]] = {}
        self._tuple_lowering_mode = TupleLoweringMode.OUT_PARAMS
        self._status_reason = "not-initialized"
        self._last_call_report: Dict[str, Any] = {}
        self._use_wasm = self._determine_backend()

        # Set up default Python fallback using FALLBACK_REGISTRY
        self._setup_default_fallback()

    def _check_wasm_available(self) -> bool:
        """Check if WASM runtime is available."""
        return wasmtime is not None

    def _determine_backend(self) -> bool:
        """
        Determine which backend to use.

        Returns:
            True if WASM should be used, False for Python
        """
        if self._backend == Backend.PYTHON:
            self._status_reason = "forced-python"
            return False
        if self._backend == Backend.WASM:
            if not self._wasm_available:
                self._status_reason = "wasmtime-not-installed"
                print("Warning: WASM requested but not available. Using Python.",
                      file=sys.stderr)
            else:
                self._status_reason = "forced-wasm"
            return self._wasm_available
        # AUTO
        # Use WASM if available and on supported platform
        if not self._wasm_available:
            self._status_reason = "wasmtime-not-installed"
            return False

        # Check platform support
        if sys.platform not in ["win32", "linux", "darwin"]:
            self._status_reason = f"unsupported-platform:{sys.platform}"
            return False

        # Check Python version
        if sys.version_info < (3, 7):
            self._status_reason = "unsupported-python-version"
            return False

        self._status_reason = "auto-wasm-available"
        return True

    def set_backend(self, backend: Backend) -> None:
        """
        Override backend selection.

        Args:
            backend: Backend to use
        """
        self._backend = backend
        self._use_wasm = self._determine_backend()

    def set_tuple_lowering_mode(self, mode: TupleLoweringMode) -> None:
        """Set tuple ABI lowering mode."""
        self._tuple_lowering_mode = mode

    def is_wasm_available(self) -> bool:
        """Check if WASM is available and being used."""
        return self._use_wasm

    def current_backend_name(self) -> str:
        """Return the currently selected backend name."""
        return "wasm" if self._use_wasm else "python"

    def get_status(self) -> Dict[str, Any]:
        """Return structured backend selection status."""
        return {
            "backend": self.current_backend_name(),
            "reason": self._status_reason,
            "requested": self._backend.value,
            "wasm_runtime_available": self._wasm_available,
            "module_loaded": self._wasm_module is not None,
        }

    def get_last_call_report(self) -> Dict[str, Any]:
        """Return the latest function-call backend report."""
        return dict(self._last_call_report)

    def set_python_fallback(self, func: Callable) -> None:
        """
        Set Python fallback implementation.

        Args:
            func: Python function to use as fallback
        """
        self._python_fallback = func

    def _setup_default_fallback(self) -> None:
        """
        Set up default Python fallback using FALLBACK_REGISTRY.

        This provides a default implementation that looks up functions
        in the FALLBACK_REGISTRY dictionary.
        """
        def default_fallback(func_name: str, *args, **kwargs):
            """Default fallback that looks up function in registry."""
            # Try exact match first
            if func_name in FALLBACK_REGISTRY:
                return FALLBACK_REGISTRY[func_name](*args, **kwargs)

            # Try with common prefixes (for backwards compatibility)
            prefixes = ["numeric_", "matrix_", "string_", "crypto_", "data_",
                       "json_", "search_", "image_"]
            for prefix in prefixes:
                full_name = f"{prefix}{func_name}"
                if full_name in FALLBACK_REGISTRY:
                    return FALLBACK_REGISTRY[full_name](*args, **kwargs)

            raise KeyError(f"Function '{func_name}' not found in FALLBACK_REGISTRY")

        self._python_fallback = default_fallback

    def set_wasm_module(self, wasm_path: str) -> bool:
        """
        Load WASM module.

        Args:
            wasm_path: Path to .wasm file

        Returns:
            True if WASM module loaded successfully
        """
        if not self._use_wasm:
            self._status_reason = f"module-load-skipped:{self.current_backend_name()}"
            return False

        try:
            self._wasm_module = WasmModule.load(wasm_path)
            instantiated = self._wasm_module.instantiate()
            if instantiated:
                self._status_reason = "wasm-module-loaded"
            else:
                self._status_reason = "wasm-module-instantiation-failed"
                self._use_wasm = False
            return instantiated
        except Exception as exc:
            print(f"Failed to load WASM module: {exc}", file=sys.stderr)
            self._status_reason = f"wasm-module-load-failed:{type(exc).__name__}"
            self._use_wasm = False
            return False

    def call_function(self, function_name: str, *args, **kwargs) -> Any:
        """
        Call function with automatic backend selection.

        Args:
            function_name: Name of function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        if self._use_wasm and self._wasm_module:
            try:
                # Convert Python args to WASM types
                wasm_args = self._convert_to_wasm(*args)
                result = self._wasm_module.call(function_name, *wasm_args)
                # Convert result back to Python
                self._last_call_report = {
                    "function": function_name,
                    "backend": "wasm",
                    "reason": "wasm-call-succeeded",
                    "fallback": False,
                }
                return self._convert_from_wasm(result)
            except Exception as exc:
                print(f"WASM execution failed: {exc}. Falling back to Python.",
                      file=sys.stderr)
                # Fall through to Python fallback
                self._status_reason = f"wasm-call-failed:{type(exc).__name__}"
                self._last_call_report = {
                    "function": function_name,
                    "backend": "python",
                    "reason": f"wasm-call-failed:{type(exc).__name__}",
                    "fallback": True,
                }
                self._use_wasm = False

        # Use Python fallback
        if self._python_fallback:
            if not self._last_call_report:
                self._last_call_report = {
                    "function": function_name,
                    "backend": "python",
                    "reason": self._status_reason,
                    "fallback": self._backend != Backend.PYTHON,
                }
            return self._python_fallback(function_name, *args, **kwargs)
        raise RuntimeError(f"No implementation for {function_name}")

    def _convert_to_wasm(self, *args) -> tuple:
        """
        Convert Python arguments to WASM types.

        Args:
            *args: Python arguments

        Returns:
            WASM-compatible arguments
        """
        # WASM Bridge will implement full type conversion
        # For now, pass through integers
        wasm_args = []
        for arg in args:
            if isinstance(arg, int):
                wasm_args.append(arg)
            elif isinstance(arg, float):
                wasm_args.append(int(arg))
            elif isinstance(arg, (list, tuple)):
                # Handle arrays - WASM Bridge
                wasm_args.append(lower_tuple_value(arg, self._tuple_lowering_mode))
            else:
                wasm_args.append(arg)
        return tuple(wasm_args)

    def _convert_from_wasm(self, result: Any) -> Any:
        """
        Convert WASM result to Python type.

        Args:
            result: WASM result

        Returns:
            Python-compatible result
        """
        # WASM Bridge will implement full type conversion
        return restore_tuple_value(result, self._tuple_lowering_mode)

    def get_performance_stats(self, function_name: str) -> Optional[Dict[str, float]]:
        """
        Get performance statistics for a function.

        Args:
            function_name: Name of function

        Returns:
            Performance stats (timing, speedup, etc.)
        """
        return self._performance_stats.get(function_name)

    def __repr__(self) -> str:
        backend_name = "WASM" if self._use_wasm else "Python"
        return f"BackendSelector(backend={backend_name})"


class BackendRegistry:
    """
    Registry of available backends for different functions.

    Allows mapping functions to specific backends.
    """

    def __init__(self):
        """Initialize backend registry."""
        self._backends: Dict[str, Dict[str, Callable]] = {}

    def register_python(self, func_name: str, func: Callable) -> None:
        """
        Register Python implementation.

        Args:
            func_name: Function name
            func: Python function
        """
        if func_name not in self._backends:
            self._backends[func_name] = {}
        self._backends[func_name]["python"] = func

    def register_wasm(self, func_name: str, wasm_path: str) -> None:
        """
        Register WASM implementation.

        Args:
            func_name: Function name
            wasm_path: Path to WASM module
        """
        if func_name not in self._backends:
            self._backends[func_name] = {}
        self._backends[func_name]["wasm"] = wasm_path

    def get_backend(self, func_name: str, backend: Backend) -> Optional[Any]:
        """
        Get backend implementation for function.

        Args:
            func_name: Function name
            backend: Requested backend

        Returns:
            Implementation, or None if not found
        """
        if func_name not in self._backends:
            return None

        if backend == Backend.PYTHON:
            return self._backends[func_name].get("python")
        if backend == Backend.WASM:
            return self._backends[func_name].get("wasm")
        # Return whichever is available
        if "wasm" in self._backends[func_name]:
            return self._backends[func_name]["wasm"]
        return self._backends[func_name].get("python")


# Global backend selector
_global_selector = BackendSelector()


def get_backend_selector() -> BackendSelector:
    """Get global backend selector instance."""
    return _global_selector


def set_backend(backend: Backend) -> None:
    """
    Set global backend preference.

    Args:
        backend: Backend to use
    """
    _global_selector.set_backend(backend)


def is_wasm_available() -> bool:
    """Check if WASM is available and enabled."""
    return _global_selector.is_wasm_available()


def get_current_backend() -> str:
    """Get name of current backend."""
    return _global_selector.current_backend_name().upper()
