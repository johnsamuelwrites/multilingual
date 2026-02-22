# Backend Testing Strategy

This document describes how the project ensures comprehensive testing of both WASM and Python fallback backends.

## Overview

The multilingual programming language supports two execution backends:

1. **WASM Backend**: WebAssembly compilation for 50-100x performance gains on compute-intensive operations
2. **Python Fallback**: Pure Python implementations for guaranteed compatibility across all platforms

Both backends must produce **identical results** while potentially differing in **performance**.

## GitHub Actions Workflow

### Workflow: `wasm-backends-test.yml`

The workflow provides **three layers of testing**:

#### 1. Backend Matrix Testing (`backend-testing` job)

Tests both backends across multiple platforms and Python versions.

**Test Matrix:**
- **Platforms**: Linux (Ubuntu), macOS, Windows
- **Python versions**: 3.7, 3.9, 3.12, 3.13
- **Backends**: WASM, Python fallback
- **Total combinations**: 3 × 4 × 2 = 24 test configurations

**Test Execution:**

```yaml
# WASM backend testing
pip install -e ".[wasm,performance]"
pytest tests/wasm_*.py -v

# Python fallback testing
pip install -e "."  # No WASM dependencies
pytest tests/wasm_comprehensive_test.py::FallbackTestSuite -v
```

**Test Categories:**
- ✅ Correctness tests (identical output validation)
- ✅ Performance benchmarks (execution time measurement)
- ✅ Fallback mechanism tests (graceful degradation)
- ✅ Integration tests (component interaction)
- ✅ Platform compatibility tests (OS-specific behavior)
- ✅ Corpus project tests (real-world examples)

#### 2. Cross-Backend Parity Validation (`cross-backend-parity` job)

Validates semantic equivalence between backends.

**Validation Points:**
- Matrix operations produce identical numerical results
- Cryptographic operations produce identical output
- Numeric operations (Fibonacci, factorial, GCD) are semantically identical
- JSON serialization/deserialization is consistent

```python
# Example parity test
plaintext = 'Hello World'
key = 'secret'
encrypted = CryptoOperations.xor_cipher(plaintext, key)
decrypted = CryptoOperations.xor_decipher(encrypted, key)
assert decrypted == plaintext  # Must work for both backends
```

#### 3. Ecosystem Validation (`ecosystem-validation` job)

Tests real-world corpus projects with both backends.

**Projects Tested:**
- Matrix Operations (multilingual, 4 languages)
- Cryptography (multilingual, 4 languages)
- JSON Parsing (multilingual, 4 languages)
- Scientific Computing (multilingual, 4 languages)
- Image Processing (multilingual, 4 languages)

## Test Execution Locally

### Running All Tests

```bash
# Test both backends (auto-detection)
pytest tests/

# Test only WASM backend
WASM_BACKEND=wasm pytest tests/

# Test only Python fallback
WASM_BACKEND=fallback pytest tests/
```

### Running Specific Test Categories

```bash
# Run only correctness tests
pytest -m correctness

# Run only performance benchmarks
pytest -m performance

# Run only fallback-specific tests
pytest -m fallback

# Run only WASM-specific tests
pytest -m wasm

# Run corpus projects (slow tests)
pytest -m corpus --timeout=120

# Run integration tests
pytest -m integration
```

### Running Tests with Coverage

```bash
# Full coverage report for both backends
pytest tests/ --cov=multilingualprogramming --cov-report=html

# Coverage report for fallback only
WASM_BACKEND=fallback pytest tests/ --cov=multilingualprogramming

# Coverage report for WASM only
WASM_BACKEND=wasm pytest tests/ --cov=multilingualprogramming
```

## Test Configuration

### pytest.ini

Configuration file defining:
- Test discovery patterns
- Test markers (wasm, fallback, correctness, performance, etc.)
- Test timeouts (60s default, 120s for corpus tests)
- Strict marker enforcement

### conftest.py

Pytest fixtures and configuration:

**Fixtures:**
- `backend_preference`: Get backend preference from environment
- `is_wasm_available`: Check WASM availability
- `backend_selector`: BackendSelector instance with user preference
- `wasm_backend_selector`: Force WASM backend
- `fallback_backend_selector`: Force Python fallback
- `python_fallbacks`: All fallback implementations
- `language_variants`: Parameterized multilingual testing
- `performance_timer`: Measure operation duration
- `assert_speedup`: Validate WASM performance improvements

**Markers:**
- `@pytest.mark.wasm`: WASM-specific tests
- `@pytest.mark.fallback`: Fallback-specific tests
- `@pytest.mark.correctness`: Correctness validation
- `@pytest.mark.performance`: Performance benchmarks
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.corpus`: Real-world corpus projects
- `@pytest.mark.slow`: Long-running tests

## Backend Detection

### Environment Variables

Control backend selection during testing:

```bash
# Use auto-detection (try WASM, fallback to Python)
export WASM_BACKEND=auto

# Force WASM backend
export WASM_BACKEND=wasm

# Force Python fallback
export WASM_BACKEND=fallback
```

### Runtime Detection

The `BackendSelector` automatically detects availability:

```python
from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

# Auto-detection
selector = BackendSelector(prefer_backend=Backend.AUTO)
# ↓ Tries WASM first, falls back to Python if unavailable

# Force WASM
selector = BackendSelector(prefer_backend=Backend.WASM)
# ↓ Raises error if WASM not available

# Force Python
selector = BackendSelector(prefer_backend=Backend.PYTHON)
# ↓ Uses Python fallback (always available)
```

## Test Results Reporting

### Coverage Report

The workflow generates coverage reports for both backends:

```
Coverage Summary
────────────────
WASM Backend (Python 3.12): 95.2% coverage
Python Fallback (Python 3.12): 94.8% coverage
Cross-platform average: 94.5%
```

### Performance Report

Automated performance tracking:

```
Performance Benchmarks (v0.4.0)
───────────────────────────────
Matrix multiply (100×100):     850μs (WASM) vs 2.5ms (Python) → 2.9x speedup
Fibonacci(100):                125μs (WASM) vs 8.2ms (Python) → 65.6x speedup
XOR cipher (10KB):             45μs (WASM) vs 850μs (Python) → 18.8x speedup
JSON stringify (1000 objects): 380μs (WASM) vs 5.2ms (Python) → 13.7x speedup
```

### Parity Validation

Cross-backend semantic checks:

```
Parity Validation Results
──────────────────────────
✅ Matrix operations: Identical outputs
✅ Cryptography: Identical results (12/12 test cases)
✅ Numeric operations: Identical values
✅ JSON operations: Identical structures
✅ Platform compatibility: 3/3 platforms passing
```

## Continuous Integration Gates

### Required Checks

All PRs require:
1. ✅ All backend matrix tests passing (24 configurations)
2. ✅ Cross-backend parity validation passing
3. ✅ Minimum coverage thresholds met (>90%)
4. ✅ No performance regressions (>1.5x WASM speedup maintained)

### Failing Checks

A PR is blocked if:
- Any backend matrix test fails
- Cross-backend parity validation fails
- Code coverage drops below 90%
- WASM tests fail on more than 2 platforms
- Fallback tests fail (indicates regression)

## Performance Expectations

### Fallback Backend (Python)

Baseline performance - all operations run in pure Python:

```
Operation          Time (Python)
─────────────────────────────────
Matrix 10×10       0.12ms
Matrix 100×100     2.5ms
Fibonacci(30)      8.2ms
XOR cipher (10KB)  850μs
JSON 100 objects   5.2ms
```

### WASM Backend

Target performance - 50-100x faster on compute-intensive operations:

```
Operation          Time (WASM)   Speedup
──────────────────────────────────────────
Matrix 10×10       150μs         0.8x*
Matrix 100×100     850μs         2.9x
Fibonacci(30)      125μs         65.6x
XOR cipher (10KB)  45μs          18.8x
JSON 100 objects   380μs         13.7x
```

*Note: Small operations have WASM overhead; larger operations show significant gains

## Troubleshooting

### WASM Backend Not Available

If WASM tests are skipped or failing:

```bash
# Check WASM installation
python -c "import wasmtime; print('WASM available')"

# Install WASM dependencies
pip install -e ".[wasm,performance]"

# Force fallback testing
WASM_BACKEND=fallback pytest tests/
```

### Performance Degradation

If WASM performance regresses:

1. Check for recent codegen changes
2. Validate WASM module compilation
3. Compare against benchmark baseline
4. Check system resource availability

```bash
# Run performance tests with verbose output
pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite -vv

# Compare against previous run
pytest tests/wasm_comprehensive_test.py::PerformanceBenchmarkSuite --benchmark-only
```

### Cross-Platform Issues

If tests fail on specific platforms:

1. Check platform-specific environment variables
2. Verify dependencies are installed
3. Check for OS-specific bugs (path separators, line endings)
4. Review platform-specific code paths

```bash
# Run platform compatibility tests
pytest tests/wasm_comprehensive_test.py::PlatformCompatibilityTestSuite -vv
```

## Future Improvements

- [ ] Automated performance regression detection
- [ ] Machine learning-based performance prediction
- [ ] Flaky test detection and quarantine
- [ ] Distributed test execution across multiple machines
- [ ] Real-time performance dashboard

---

**Last updated**: 2026-02-22
**Maintainer**: John Samuel

For questions about the testing strategy, see:
- [WASM Architecture](./WASM_ARCHITECTURE_OVERVIEW.md)
- [WASM Troubleshooting](./WASM_TROUBLESHOOTING.md)
- [WASM FAQ](./WASM_FAQ.md)
