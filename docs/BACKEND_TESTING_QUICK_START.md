# Backend Testing - Quick Start Guide

Fast reference for running WASM and fallback backend tests locally.

## Installation

```bash
# Install with WASM support
pip install -e ".[wasm,performance]"

# Install with fallback only (no WASM)
pip install -e "."
```

## Quick Test Commands

### Run All Tests

```bash
# Both backends (auto-detect)
pytest tests/

# WASM backend only
WASM_BACKEND=wasm pytest tests/

# Fallback only (no WASM)
WASM_BACKEND=fallback pytest tests/
```

### Test Specific Areas

```bash
# Correctness tests (must pass for both backends)
pytest -m correctness

# Performance benchmarks
pytest -m performance

# Fallback-specific functionality
pytest -m fallback

# WASM-specific functionality
pytest -m wasm

# Integration tests
pytest -m integration

# Real-world corpus projects
pytest -m corpus --timeout=120

# Skip slow tests
pytest -m "not slow"
```

### Test with Coverage

```bash
# Full coverage report
pytest --cov=multilingualprogramming tests/

# HTML coverage report
pytest --cov=multilingualprogramming --cov-report=html tests/
# Open htmlcov/index.html in browser
```

## Common Testing Scenarios

### Before Committing Code

```bash
# Quick smoke test (both backends, skip slow tests)
pytest -m "not slow" -v

# If that passes, run full suite
pytest tests/ --timeout=120
```

### Testing a Specific Component

```bash
# Test matrix operations across all languages
pytest tests/wasm_corpus_test.py::MatrixOperationsCorpusTest -v

# Test cryptography
pytest tests/wasm_corpus_test.py::CryptographyCorpusTest -v

# Test JSON parsing
pytest tests/wasm_corpus_test.py::JSONParsingCorpusTest -v
```

### Performance Comparison

```bash
# Run benchmarks with WASM
WASM_BACKEND=wasm pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite -v

# Run benchmarks with fallback
WASM_BACKEND=fallback pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite -v

# Compare outputs manually
```

### Testing a Single Language

```bash
# Test French language variants
pytest tests/ -k "fr" -v

# Test Spanish language variants
pytest tests/ -k "es" -v

# Test German language variants
pytest tests/ -k "de" -v
```

## Environment Variables

```bash
# Backend selection
export WASM_BACKEND=auto      # Try WASM, fallback to Python (default)
export WASM_BACKEND=wasm      # Force WASM only
export WASM_BACKEND=fallback  # Force Python fallback

# Pytest options
export PYTEST_TIMEOUT=120     # 2-minute timeout for slow tests
export PYTEST_VERBOSE=1       # Verbose output
```

## Troubleshooting

### "WASM not available" but I installed it

```bash
# Verify WASM installation
python -c "import wasmtime; print('WASM OK')"

# Reinstall WASM
pip install --force-reinstall wasmtime

# Force fallback for now
WASM_BACKEND=fallback pytest tests/
```

### Tests hanging or timing out

```bash
# Run with explicit timeout
pytest --timeout=30 tests/

# Skip slow/corpus tests
pytest -m "not slow" tests/

# Run only quick tests
pytest -m "not (slow or corpus)" tests/
```

### Performance seems slow

```bash
# Check if WASM backend is being used
python -c "
from multilingualprogramming.runtime.backend_selector import BackendSelector
s = BackendSelector()
print(f'WASM available: {s.wasm_module is not None}')
"

# Run benchmarks to check
WASM_BACKEND=wasm pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite -v
WASM_BACKEND=fallback pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite -v
```

## Test Files Structure

```
tests/
├── conftest.py                    # Pytest configuration & fixtures
├── wasm_comprehensive_test.py     # Core backend tests
│   ├── CorrectnessTestSuite       # Must pass for both backends
│   ├── PerformanceBenchmarkSuite  # Performance validation
│   ├── FallbackTestSuite          # Fallback-specific
│   ├── IntegrationTestSuite       # Component interaction
│   └── PlatformCompatibilityTestSuite
├── wasm_corpus_test.py            # Real-world corpus projects
│   ├── MatrixOperationsCorpusTest
│   ├── CryptographyCorpusTest
│   ├── ImageProcessingCorpusTest
│   ├── JSONParsingCorpusTest
│   └── ScientificComputingCorpusTest
├── corpus/                        # Corpus project files
│   ├── en/                        # English variants
│   ├── fr/                        # French variants
│   ├── es/                        # Spanish variants
│   └── de/                        # German variants
└── ... (other test files)
```

## Expected Results

### Correctness Tests (Both Backends)

```
CorrectnessTestSuite (12 tests)
  ✓ test_matrix_multiply_correctness
  ✓ test_matrix_transpose_correctness
  ✓ test_string_reverse_correctness
  ✓ test_crypto_hash_consistency
  ✓ test_crypto_xor_roundtrip
  ✓ test_numeric_fibonacci_correctness
  ✓ test_json_roundtrip_correctness
  ✓ test_search_binary_search_correctness
  ✓ ... (more tests)
```

### Performance (WASM should be faster)

```
Performance Benchmarks
  Matrix multiply (10x10):  150μs (WASM) vs 0.12ms (Python)
  Fibonacci(30):           125μs (WASM) vs 8.2ms (Python) → 65x faster
  XOR cipher (10KB):        45μs (WASM) vs 850μs (Python) → 18x faster
  JSON stringify (100):    380μs (WASM) vs 5.2ms (Python) → 13x faster
```

### All Tests Passing

```
collected 118 items
wasm_comprehensive_test.py::CorrectnessTestSuite::test_matrix_multiply_correctness PASSED
wasm_comprehensive_test.py::CorrectnessTestSuite::test_matrix_transpose_correctness PASSED
... (116 more tests)

========================= 118 passed in 45.23s ==========================
```

## Getting Help

- Run tests with `-v` (verbose) for detailed output
- Use `-vv` for even more detail
- Check `conftest.py` for available fixtures
- See `BACKEND_TESTING_STRATEGY.md` for comprehensive documentation
- Open an issue on GitHub with test output

---

**Quick Links:**
- [Backend Testing Strategy](./BACKEND_TESTING_STRATEGY.md) - Deep dive
- [WASM Architecture](./WASM_ARCHITECTURE_OVERVIEW.md) - Technical details
- [WASM Troubleshooting](./WASM_TROUBLESHOOTING.md) - Common issues
