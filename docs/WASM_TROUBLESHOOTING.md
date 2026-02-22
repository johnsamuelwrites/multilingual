# Troubleshooting Guide

## Quick Diagnostics

### Is WASM Working?

```python
from multilingualprogramming.runtime.backend_selector import BackendSelector

selector = BackendSelector()
print(f"WASM Available: {selector.is_wasm_available()}")
print(f"Current Backend: {selector.backend}")
```

If `WASM Available: False` → See [WASM Not Available](#issue-2-wasm-not-available)
If `WASM Available: True` → WASM is working ✓

---

## Common Issues & Solutions

### Issue 1: ModuleNotFoundError - No module named 'wasmtime'

**Symptom**:
```
ModuleNotFoundError: No module named 'wasmtime'
```

**Cause**: wasmtime runtime not installed

**Solutions**:

```bash
# Option 1: Install WASM package
pip install multilingualprogramming[wasm]

# Option 2: Install wasmtime directly
pip install wasmtime

# Option 3: Use Python fallback (no WASM)
pip install multilingualprogramming
```

**Code Workaround**:
```python
from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

# Force Python (will always work)
selector = BackendSelector(prefer_backend=Backend.PYTHON)
result = selector.call_function("fibonacci", 10)
```

---

### Issue 2: WASM Not Available

**Symptom**:
```
WASM Available: False
Performance not improved
```

**Diagnosis**:
```python
from multilingualprogramming.runtime.backend_selector import BackendSelector
import sys
import platform

selector = BackendSelector()
print(f"WASM: {selector.is_wasm_available()}")
print(f"Python: {sys.version}")
print(f"Platform: {platform.system()} {platform.machine()}")
```

**Possible Causes**:

1. **Wasmtime not installed**
   ```bash
   pip install wasmtime>=1.0.0
   ```

2. **WASM binaries missing from package**
   ```bash
   # Check installation
   python -c "import multilingualprogramming; import os; print(os.listdir(os.path.dirname(multilingualprogramming.__file__) + '/wasm'))"
   ```
   - If empty → Reinstall: `pip install --force-reinstall multilingualprogramming[wasm]`

3. **Platform not supported**
   - Linux ARM64: Use Python fallback
   - Windows ARM64: Use Python fallback
   - Solution: Use Python backend

   ```python
   from multilingualprogramming.runtime.backend_selector import Backend
   selector = BackendSelector(prefer_backend=Backend.PYTHON)
   ```

4. **WASM module corruption**
   ```bash
   # Reinstall clean
   pip uninstall multilingualprogramming
   pip install multilingualprogramming[wasm]
   ```

---

### Issue 3: Performance Not Improved

**Symptom**:
```
Operation not faster, overhead > benefit
```

**Diagnosis**:

```python
import time
from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

def benchmark(func_name, *args):
    # Python
    sel_py = BackendSelector(prefer_backend=Backend.PYTHON)
    start = time.perf_counter()
    result = sel_py.call_function(func_name, *args)
    py_time = time.perf_counter() - start

    # WASM
    sel_wasm = BackendSelector(prefer_backend=Backend.WASM)
    start = time.perf_counter()
    result = sel_wasm.call_function(func_name, *args)
    wasm_time = time.perf_counter() - start

    speedup = py_time / wasm_time if wasm_time > 0 else 1
    print(f"Python: {py_time*1000:.2f}ms, WASM: {wasm_time*1000:.2f}ms, Speedup: {speedup:.1f}x")

# Test
benchmark("fibonacci", 25)
benchmark("matrix_multiply", [[1,2],[3,4]], [[5,6],[7,8]])
```

**Possible Causes**:

1. **Operation too small** (< 1ms)
   - WASM overhead dominates
   - **Solution**: Batch operations
   ```python
   # Bad
   for i in range(100):
       result = fibonacci(5)  # 100 slow calls

   # Good
   result = fibonacci(500)  # Single fast call
   ```

2. **WASM not actually being used**
   - **Check**: `selector.is_wasm_available()`
   - **Solution**: See [WASM Not Available](#issue-2-wasm-not-available)

3. **Incorrect operation**
   - Not all operations have WASM acceleration
   - **Solution**: Check FALLBACK_REGISTRY
   ```python
   from multilingualprogramming.runtime.python_fallbacks import FALLBACK_REGISTRY
   print("fibonacci" in FALLBACK_REGISTRY)  # True if supported
   ```

4. **Timing interference**
   - First call loads module (10-50ms overhead)
   - **Solution**: Warm up before timing
   ```python
   selector.call_function("fibonacci", 5)  # Warm up
   # Now measure...
   ```

---

### Issue 4: OutOfMemory Error with WASM

**Symptom**:
```
RuntimeError: Out of memory
Exception: Memory access out of bounds
```

**Cause**: WASM memory (1GB) exceeded

**Diagnosis**:
```python
import sys

# Check data size
matrix = [[1.0 for _ in range(10000)] for _ in range(10000)]
size_mb = sys.getsizeof(matrix) / 1024 / 1024
print(f"Matrix size: {size_mb:.1f} MB")

if size_mb > 64:
    print("TOO LARGE for WASM! Max ~64MB")
```

**Solutions**:

1. **Use smaller data**
   ```python
   # Bad: 100×100 = 10,000 elements, 80KB (OK)
   # Worse: 1000×1000 = 1M elements, 8MB (OK)
   # Too much: 10000×10000 = 100M elements, 800MB (TOO LARGE)

   # Use Python fallback for large data
   from multilingualprogramming.runtime.backend_selector import Backend
   selector = BackendSelector(prefer_backend=Backend.PYTHON)
   ```

2. **Stream processing**
   ```python
   def process_large_matrix(matrix, chunk_size=100):
       """Process in chunks to avoid memory issues."""
       for i in range(0, len(matrix), chunk_size):
           chunk = matrix[i:i+chunk_size]
           yield process_chunk(chunk)
   ```

3. **Use Python directly**
   ```python
   from multilingualprogramming.runtime.python_fallbacks import MatrixOperations

   # Direct fallback (no memory issues)
   result = MatrixOperations.multiply(large_a, large_b)
   ```

---

### Issue 5: ImportError on Windows

**Symptom**:
```
ImportError: DLL load failed
ImportError: cannot import name 'wasmtime'
```

**Cause**: Visual C++ Redistributables missing

**Solutions**:

1. **Install Visual C++ Redistributables**
   - Download: [Microsoft Visual C++ Redistributable](https://support.microsoft.com/en-us/help/2977003)
   - Install for your Python architecture (32-bit or 64-bit)

2. **Use vcpkg** (Advanced)
   ```bash
   vcpkg install wasmtime:x64-windows
   ```

3. **Update pip & setuptools**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   pip install multilingualprogramming[wasm]
   ```

4. **Use Python fallback**
   ```python
   from multilingualprogramming.runtime.backend_selector import Backend
   selector = BackendSelector(prefer_backend=Backend.PYTHON)
   ```

---

### Issue 6: TypeError - Type Conversion Failed

**Symptom**:
```
TypeError: Cannot convert type X to WASM
ValueError: Unsupported argument type
```

**Cause**: Invalid data type passed to WASM function

**Diagnosis**:
```python
from multilingualprogramming.runtime.backend_selector import BackendSelector

# WASM supports: int, float, str, list, dict
# WASM doesn't support: custom objects, functions

# Good
result = selector.call_function("fibonacci", 10)  # int ✓

# Bad
result = selector.call_function("fibonacci", lambda: 10)  # function ✗
```

**Solutions**:

1. **Convert to supported type**
   ```python
   # Bad
   result = fibonacci(numpy_array)

   # Good
   result = fibonacci(int(numpy_array))
   # Or
   result = fibonacci(numpy_array.tolist())
   ```

2. **Use Python for custom types**
   ```python
   from multilingualprogramming.runtime.python_fallbacks import NumericOperations

   # Use Python directly
   result = NumericOperations.fibonacci(10)
   ```

---

### Issue 7: Assertion Error - Operation Produces Different Results

**Symptom**:
```
AssertionError: WASM result differs from Python
Expected: 120
Got: 121
```

**Cause**: Bug in WASM code or type conversion

**Diagnosis**:
```python
from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

func_name = "factorial"
args = (5,)

# Compare results
sel_py = BackendSelector(prefer_backend=Backend.PYTHON)
sel_wasm = BackendSelector(prefer_backend=Backend.WASM)

result_py = sel_py.call_function(func_name, *args)
result_wasm = sel_wasm.call_function(func_name, *args)

print(f"Python: {result_py}")
print(f"WASM: {result_wasm}")
print(f"Match: {result_py == result_wasm}")
```

**Solutions**:

1. **Report bug**
   - File issue on [GitHub Issues](https://github.com/johnsamuelwrites/multilingual/issues)
   - Include: Python version, platform, input args, actual vs expected

2. **Use Python fallback**
   ```python
   from multilingualprogramming.runtime.backend_selector import Backend
   selector = BackendSelector(prefer_backend=Backend.PYTHON)
   ```

3. **Use Python directly**
   ```python
   from multilingualprogramming.runtime.python_fallbacks import NumericOperations
   result = NumericOperations.factorial(5)
   ```

---

### Issue 8: FileNotFoundError - WASM Binary Not Found

**Symptom**:
```
FileNotFoundError: WASM module not found: matrix_operations.wasm
```

**Cause**: WASM binary missing or incorrect path

**Diagnosis**:
```bash
# Check installation
python -c "import multilingualprogramming; print(multilingualprogramming.__file__)"
# Navigate to directory, check for 'wasm' folder with .wasm files

# List WASM modules
find /path/to/multilingualprogramming -name "*.wasm" -type f
```

**Solutions**:

1. **Reinstall**
   ```bash
   pip uninstall multilingualprogramming
   pip install multilingualprogramming[wasm]
   ```

2. **Verify installation**
   ```python
   from multilingualprogramming.wasm.loader import WasmModule
   import os

   # Check if modules exist
   wasm_dir = os.path.join(os.path.dirname(__file__), 'wasm')
   print(os.listdir(wasm_dir))
   ```

3. **Use Python fallback**
   ```python
   from multilingualprogramming.runtime.backend_selector import Backend
   selector = BackendSelector(prefer_backend=Backend.PYTHON)
   ```

---

## Debugging Techniques

### Enable Verbose Logging

```bash
export MULTILINGUAL_DEBUG=1
python your_script.py
```

Or in code:
```python
import os
os.environ['MULTILINGUAL_DEBUG'] = '1'

# Then run...
from multilingualprogramming.runtime.backend_selector import BackendSelector
selector = BackendSelector()
result = selector.call_function("fibonacci", 10)
# Will print debug info
```

### Inspect Backend Selection

```python
from multilingualprogramming.runtime.backend_selector import BackendSelector

selector = BackendSelector()

# Check availability
print(f"WASM available: {selector.is_wasm_available()}")
print(f"Current backend: {selector.backend}")
print(f"Python 3.7+: {selector._check_python_version()}")

# Check module loading
try:
    from multilingualprogramming.wasm.loader import WasmModule
    module = WasmModule.load("matrix_operations.wasm")
    print(f"Module loaded: {module is not None}")
except Exception as e:
    print(f"Module load failed: {e}")
```

### Manual Function Testing

```python
from multilingualprogramming.runtime.python_fallbacks import (
    NumericOperations,
    MatrixOperations,
)

# Test fallbacks directly
fib = NumericOperations.fibonacci(10)
print(f"Fibonacci(10): {fib}")

a = [[1, 2], [3, 4]]
b = [[5, 6], [7, 8]]
result = MatrixOperations.multiply(a, b)
print(f"Matrix multiply: {result}")
```

### Performance Profiling

```python
import cProfile
import pstats
from multilingualprogramming.runtime.backend_selector import BackendSelector

selector = BackendSelector()

# Profile with cProfile
cProfile.run('selector.call_function("fibonacci", 30)', 'fibonacci.prof')

# Print stats
stats = pstats.Stats('fibonacci.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## Getting Help

### Before Reporting an Issue

1. **Verify Python version**: `python --version` (should be 3.7+)
2. **Check installation**: `pip show multilingualprogramming`
3. **Test fallback**: Force Python backend, see if it works
4. **Try diagnostics**: Run scripts in [Diagnostics](#quick-diagnostics)

### When Reporting

Include:
- Python version: `python --version`
- Platform: `python -c "import platform; print(platform.platform())"`
- WASM status: `python -c "from multilingualprogramming.runtime.backend_selector import BackendSelector; print(BackendSelector().is_wasm_available())"`
- Minimal reproducible example
- Full error traceback

### Support Channels

- 🐛 [GitHub Issues](https://github.com/johnsamuelwrites/multilingual/issues)
- 💬 [GitHub Discussions](https://github.com/johnsamuelwrites/multilingual/discussions)
- 📧 Email: johnsamuelwrites@gmail.com

---

## FAQ Quick Links

See [WASM_FAQ.md](./WASM_FAQ.md) for answers to common questions

---

**Version**: Documentation Suite Final
**Last Updated**: February 22, 2026
**Status**: ✅ Complete
