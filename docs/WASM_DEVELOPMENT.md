# WASM Development Guide

## Overview

This guide explains how the WASM backend works and how to develop with it.

---

## Architecture

### Backend Selection Flow

```
Application Code
    ↓
BackendSelector
    ├→ Backend.WASM: Use WebAssembly (performance gain depends on workload)
    ├→ Backend.PYTHON: Use Python fallback (always works)
    └→ Backend.AUTO: Auto-detect (smart default)
        ├→ WASM available? → Use WASM
        └→ Else → Use Python fallback
```

### Component Stack

```
PyPI Distribution: PyPI Distribution (THIS LEVEL)
    ├─ Wheel file (.whl) containing:
    │  ├─ Python source code
    │  ├─ WASM binaries (.wasm)
    │  └─ Fallback implementations
    │
Comprehensive Testing: Comprehensive Testing
    ├─ Correctness validation
    ├─ Performance benchmarking
    └─ Platform compatibility
    │
WASM Corpus: Corpus Projects (Real-world examples)
    ├─ Matrix operations
    ├─ Cryptography
    ├─ Image processing
    ├─ JSON parsing
    └─ Scientific computing
    │
Backend Selection: Smart Backend Selector
    ├─ Auto-detection logic
    ├─ Fallback routing
    └─ Performance stats
    │
WASM Bridge: Python ↔ WASM Bridge
    ├─ Type conversion
    ├─ Memory management
    └─ Module caching
    │
WASM Code Generation: WASM Codegen
    ├─ Rust code generation
    ├─ Cranelift compilation
    └─ Binary optimization
```

---

## Key Components

### 1. WasmCodeGenerator (WASM Code Generation)

**Location**: `multilingualprogramming/codegen/wasm_generator.py`

Generates Rust intermediate code from AST:

```python
from multilingualprogramming.codegen.wasm_generator import WasmCodeGenerator
from multilingualprogramming.parser import Parser

# Parse program
program = Parser(...).parse()

# Generate Rust code for WASM
generator = WasmCodeGenerator()
rust_code = generator.generate(program)
print(rust_code)  # Ready for cranelift compilation
```

**Output**: Rust code that compiles to WASM binary

---

### 2. WasmModule Loader (WASM Bridge)

**Location**: `multilingualprogramming/wasm/loader.py`

Loads and executes WASM modules:

```python
from multilingualprogramming.wasm.loader import WasmModule, WasmModuleCache

# Load WASM module
module = WasmModule.load("path/to/module.wasm")
module.instantiate()

# Call functions
result = module.call("fibonacci", 10)

# Cache for performance
cache = WasmModuleCache()
cached = cache.get_or_load("path/to/module.wasm")
```

**Features**:
- Lazy loading (load when first used)
- Module caching (avoid reloading)
- Type conversion (Python ↔ WASM)
- Memory management (linear memory access)

---

### 3. Smart Backend Selector (Backend Selection)

**Location**: `multilingualprogramming/runtime/backend_selector.py`

Intelligent backend selection:

```python
from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

# Auto-detection (recommended)
selector = BackendSelector()
result = selector.call_function("fibonacci", 10)

# Force Python
selector_py = BackendSelector(prefer_backend=Backend.PYTHON)
result = selector_py.call_function("fibonacci", 10)

# Force WASM
selector_wasm = BackendSelector(prefer_backend=Backend.WASM)
result = selector_wasm.call_function("fibonacci", 10)
```

**Detection Logic**:
1. Check if wasmtime installed
2. Check if WASM binary available
3. Check platform compatibility
4. Fall back to Python if any check fails

---

### 4. Python Fallback (Python Fallbacks)

**Location**: `multilingualprogramming/runtime/python_fallbacks.py`

Pure Python implementations:

```python
from multilingualprogramming.runtime.python_fallbacks import (
    MatrixOperations,
    NumericOperations,
    FALLBACK_REGISTRY,
)

# Direct usage
result = MatrixOperations.multiply(a, b)
fib = NumericOperations.fibonacci(10)

# Via registry
func = FALLBACK_REGISTRY.get("matrix_multiply")
result = func(a, b)
```

**Advantages**:
- Always works (no external dependencies)
- No binary distribution issues
- NumPy-optimizable
- Easy debugging

---

## Performance Characteristics

### Overhead Costs

| Operation | Overhead | When Worth It |
|-----------|----------|---------------|
| WASM module load | 10-50ms | Once, cached |
| WASM function call | 0.1-1ms | Operations > 1ms |
| Type conversion | 0.01-0.1ms | Depends on data |
| Python call | <0.001ms | Very fast |

### Break-even Points

```
Matrix 10x10:     Python 0.1ms  WASM 1ms  (overhead > benefit)
Matrix 100x100:   Python 10ms   WASM 1ms  (10x benefit)
Matrix 1000x1000: Python 5000ms WASM 50ms (100x benefit)

Crypto 1KB:    Python 0.1ms   WASM 0.01ms (overhead dominates)
Crypto 1MB:    Python 100ms   WASM 1ms    (100x benefit)

JSON 1KB:      Python 0.1ms   WASM 0.1ms  (parity)
JSON 10MB:     Python 200ms   WASM 20ms   (10x benefit)
```

---

## Developing Custom WASM Functions

### Step-by-Step Guide

#### 1. Write Multilingual Code

```python
# myfunction.ml
def expensive_operation(n: integer) -> integer:
    result = 0
    pour i dans intervalle(n * n):
        result = result + (i * i) // (i + 1)
    retourne result

expensive_operation(1000000)
```

#### 2. Prepare for WASM

Update `multilingualprogramming/runtime/python_fallbacks.py`:

```python
class CustomOperations:
    @staticmethod
    def expensive_operation(n: int) -> int:
        """Pure Python fallback."""
        result = 0
        for i in range(n * n):
            result = result + (i * i) // (i + 1)
        return result

# Register in FALLBACK_REGISTRY
FALLBACK_REGISTRY["expensive_operation"] = CustomOperations.expensive_operation
```

#### 3. Register in Backend Selector

Update `multilingualprogramming/runtime/backend_selector.py`:

```python
# In BackendRegistry class
def register_expensive_operation(self, wasm_path: str):
    self.register_wasm("expensive_operation", wasm_path)

# Usage
registry = BackendRegistry()
registry.register_wasm("expensive_operation", "path/to/expensive_operation.wasm")
```

#### 4. Test Both Backends

```python
# Test fallback
result_py = CustomOperations.expensive_operation(1000)

# Test WASM (when available)
selector = BackendSelector()
result_wasm = selector.call_function("expensive_operation", 1000)

# Verify identical results
assert result_py == result_wasm
```

---

## Build System

### Compilation Pipeline

```
Multilingual Source Code (.ml)
    ↓
Lexer & Parser
    ↓
AST (Abstract Syntax Tree)
    ↓
WasmCodeGenerator
    ↓
Rust Code (intermediate)
    ↓
Cranelift Compiler
    ↓
WebAssembly Binary (.wasm)
    ↓
Wheel Package (.whl)
    ↓
PyPI Distribution
```

### Building WASM Binaries

```bash
# Install development dependencies (includes WASM runtime)
pip install -e ".[dev,wasm]"

# Validate WASM codegen and backend integration
pytest tests/wasm_codegen_poc_test.py -v
pytest tests/wasm_comprehensive_test.py -v
```

At this time, the repository does not provide a top-level `build_wasm.sh` helper.
WASM assets are generated/validated through the codegen pipeline and tests.

---

## Memory Management

### WASM Memory Layout

```
┌─────────────────────────────────────────┐
│  WebAssembly Linear Memory (1GB)       │
├─────────────────────────────────────────┤
│  Stack (grows upward)   ↑               │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  Heap (grows downward)  ↓               │
├─────────────────────────────────────────┤
│  Reserved                               │
└─────────────────────────────────────────┘
```

### Type Conversion

Python → WASM:
```python
# Python int → WASM i32/i64
# Python float → WASM f32/f64
# Python list → WASM array (pointer to memory)
# Python dict → WASM struct (packed in memory)
```

WASM → Python:
```python
# WASM i32/i64 → Python int
# WASM f32/f64 → Python float
# WASM pointer → Python list/bytes
```

---

## Debugging

### Enable Logging

```python
import os
os.environ['MULTILINGUAL_DEBUG'] = '1'

from multilingualprogramming.runtime.backend_selector import BackendSelector
selector = BackendSelector()
result = selector.call_function("fibonacci", 10)
# Will print debug info
```

### Manual Testing

```python
from multilingualprogramming.wasm.loader import WasmModule

# Load and inspect module
module = WasmModule.load("path/to/module.wasm")
print(module.get_wasm_functions())  # List exported functions

# Test function directly
result = module.call("test_function", arg1, arg2)
print(f"Result: {result}")

# Memory inspection
mem = module.get_memory_buffer(0, 100)
print(f"Memory: {mem.hex()}")
```

### Performance Profiling

```python
import time
from multilingualprogramming.runtime.backend_selector import BackendSelector

# Profile Python fallback
selector_py = BackendSelector(prefer_backend=Backend.PYTHON)
start = time.perf_counter()
result = selector_py.call_function("fibonacci", 30)
py_time = time.perf_counter() - start

# Profile WASM
selector_wasm = BackendSelector(prefer_backend=Backend.WASM)
start = time.perf_counter()
result = selector_wasm.call_function("fibonacci", 30)
wasm_time = time.perf_counter() - start

print(f"Python: {py_time*1000:.2f}ms")
print(f"WASM: {wasm_time*1000:.2f}ms")
print(f"Speedup: {py_time/wasm_time:.1f}x")
```

---

## Best Practices

### DO:
- ✅ Use WASM for compute-intensive operations (> 1ms)
- ✅ Batch operations to amortize WASM call overhead
- ✅ Cache WASM modules (WasmModuleCache does this)
- ✅ Test both Python and WASM paths
- ✅ Provide Python fallback for all WASM functions
- ✅ Use auto-detection (Backend.AUTO) in production

### DON'T:
- ❌ Use WASM for simple operations (< 1ms)
- ❌ Create new WASM module per call
- ❌ Assume WASM available (always test fallback)
- ❌ Pass very large data structures to WASM
- ❌ Use WASM for I/O operations
- ❌ Ignore type conversion errors

---

## Future Enhancements

### Documentation Suite (Next)

- 📝 [x] Installation guide
- 📝 [x] Development guide
- 📝 [ ] Performance tuning
- 📝 [ ] Troubleshooting
- 🎓 [ ] Tutorials

### Advanced Features (Beyond)

- 🔧 JIT compilation (compile multilingual → WASM at runtime)
- 🔧 Parallel execution (multiple WASM modules)
- 🔧 GPU acceleration (for image processing)
- 🔧 Distributed computing (WASM on workers)

---

## Resources

- 📚 [WebAssembly Specification](https://webassembly.org/specs/)
- 📚 [Cranelift Compiler](https://docs.rs/cranelift/0.91.1/cranelift/)
- 📚 [Wasmtime Documentation](https://docs.wasmtime.dev/)
- 🔗 [Multilingual Repo](https://github.com/johnsamuelwrites/multilingual)

---

**Version**: PyPI Distribution Final
**Status**: Stable; benchmark and validate in your deployment environment.
