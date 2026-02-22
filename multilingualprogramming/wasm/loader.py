#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
WebAssembly Module Loader for Python integration.

Loads and manages WASM modules, providing seamless Python ↔ WASM interoperability.

WASM Bridge: Python ↔ WASM Bridge
"""

from pathlib import Path
from typing import Dict, Any, Callable, Optional, Union
import sys


class WasmModule:
    """
    Loads and manages WebAssembly modules.

    Provides transparent interface between Python and WASM code.

    Usage:
        module = WasmModule.load("module.wasm")
        result = module.call("function_name", arg1, arg2)
    """

    def __init__(self, module_path: Union[str, Path]):
        """
        Initialize WASM module loader.

        Args:
            module_path: Path to .wasm file
        """
        self.module_path = Path(module_path)
        self.engine = None
        self.module = None
        self.store = None
        self.instance = None
        self._functions: Dict[str, Callable] = {}
        self._load_wasm_runtime()

    def _load_wasm_runtime(self):
        """Load WASM runtime (wasmtime)."""
        try:
            import wasmtime
            self.wasmtime = wasmtime
            self.engine = wasmtime.Engine()
            self.store = wasmtime.Store(self.engine)
        except ImportError:
            self.wasmtime = None
            # Will use Python fallback

    @staticmethod
    def load(module_path: Union[str, Path]) -> 'WasmModule':
        """
        Load WASM module from file.

        Args:
            module_path: Path to .wasm file

        Returns:
            Loaded WasmModule
        """
        return WasmModule(module_path)

    def instantiate(self) -> bool:
        """
        Instantiate WASM module in runtime.

        Returns:
            True if successful, False if WASM unavailable
        """
        if not self.wasmtime or not self.engine:
            return False

        try:
            if not self.module_path.exists():
                return False

            with open(self.module_path, 'rb') as f:
                wasm_bytes = f.read()

            self.module = self.wasmtime.Module(self.engine, wasm_bytes)
            self.instance = self.wasmtime.Instance(self.store, self.module, [])

            self._extract_exports()
            return True
        except Exception as e:
            print(f"Failed to instantiate WASM module: {e}", file=sys.stderr)
            return False

    def _extract_exports(self):
        """Extract exported functions from WASM module."""
        if not self.instance:
            return

        try:
            exports = self.instance.exports(self.store)
            for name, obj in exports.items():
                if callable(obj):
                    self._functions[name] = obj
        except Exception as e:
            print(f"Failed to extract exports: {e}", file=sys.stderr)

    def call(self, function_name: str, *args: Any) -> Any:
        """
        Call WASM function from Python.

        Args:
            function_name: Name of exported WASM function
            *args: Arguments to pass to function

        Returns:
            Result from WASM function
        """
        if function_name not in self._functions:
            raise ValueError(f"Function '{function_name}' not found in WASM module")

        try:
            func = self._functions[function_name]
            # Call with store and arguments
            return func(self.store, *args)
        except Exception as e:
            raise RuntimeError(f"Error calling WASM function '{function_name}': {e}")

    def has_function(self, function_name: str) -> bool:
        """Check if function is exported from WASM module."""
        return function_name in self._functions

    def get_exported_functions(self) -> list:
        """Get list of exported function names."""
        return list(self._functions.keys())

    def get_memory_buffer(self, offset: int, length: int) -> bytes:
        """
        Read raw bytes from WASM linear memory.

        Args:
            offset: Byte offset in memory
            length: Number of bytes to read

        Returns:
            Raw bytes from WASM memory
        """
        if not self.instance:
            raise RuntimeError("WASM module not instantiated")

        try:
            # Get memory export from WASM
            memory = self.instance.exports(self.store).get('memory')
            if not memory:
                raise RuntimeError("WASM module has no exported memory")

            # Read from memory
            data = memory.data_ptr(self.store)
            buffer = bytes(data[offset:offset + length])
            return buffer
        except Exception as e:
            raise RuntimeError(f"Failed to read WASM memory: {e}")

    def write_memory(self, offset: int, data: bytes) -> None:
        """
        Write raw bytes to WASM linear memory.

        Args:
            offset: Byte offset in memory
            data: Bytes to write
        """
        if not self.instance:
            raise RuntimeError("WASM module not instantiated")

        try:
            memory = self.instance.exports(self.store).get('memory')
            if not memory:
                raise RuntimeError("WASM module has no exported memory")

            # Write to memory
            data_ptr = memory.data_ptr(self.store)
            for i, byte in enumerate(data):
                data_ptr[offset + i] = byte
        except Exception as e:
            raise RuntimeError(f"Failed to write WASM memory: {e}")


class WasmModuleCache:
    """
    Cache for loaded WASM modules to avoid reloading.

    Usage:
        cache = WasmModuleCache()
        module = cache.get_or_load("module.wasm")
    """

    def __init__(self):
        """Initialize WASM module cache."""
        self._cache: Dict[str, WasmModule] = {}

    def get_or_load(self, module_path: Union[str, Path]) -> Optional[WasmModule]:
        """
        Get WASM module from cache or load if not cached.

        Args:
            module_path: Path to .wasm file

        Returns:
            Loaded WasmModule, or None if WASM unavailable
        """
        path_str = str(module_path)

        if path_str not in self._cache:
            try:
                module = WasmModule.load(module_path)
                if module.instantiate():
                    self._cache[path_str] = module
                else:
                    return None
            except Exception as e:
                print(f"Failed to load WASM module: {e}", file=sys.stderr)
                return None

        return self._cache.get(path_str)

    def clear(self):
        """Clear cache of loaded modules."""
        self._cache.clear()


# Global cache instance
_wasm_cache = WasmModuleCache()


def get_wasm_module(module_path: Union[str, Path]) -> Optional[WasmModule]:
    """
    Get cached WASM module or load if not cached.

    Args:
        module_path: Path to .wasm file

    Returns:
        Loaded WasmModule, or None if WASM unavailable
    """
    return _wasm_cache.get_or_load(module_path)


def is_wasm_available() -> bool:
    """
    Check if WASM runtime (wasmtime) is available.

    Returns:
        True if wasmtime is installed
    """
    try:
        import wasmtime
        return True
    except ImportError:
        return False
