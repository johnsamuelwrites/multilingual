"""
Pytest configuration and fixtures for WASM and fallback backend testing.

Provides fixtures for:
- Backend selection (WASM vs fallback)
- Backend availability detection
- Performance measurement
- Multilingual test parameterization
"""

import os
import sys
import pytest
from typing import Callable, Any, Optional


# Environment variable to force backend selection
WASM_BACKEND_PREFERENCE = os.environ.get("WASM_BACKEND", "auto").lower()


def pytest_configure(config):
    """Configure pytest with backend markers."""
    config.addinivalue_line(
        "markers", "wasm: Tests specific to WASM backend"
    )
    config.addinivalue_line(
        "markers", "fallback: Tests specific to Python fallback"
    )
    config.addinivalue_line(
        "markers", "correctness: Correctness validation tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance benchmark tests"
    )


@pytest.fixture(scope="session")
def backend_preference():
    """Get the backend preference from environment."""
    return WASM_BACKEND_PREFERENCE


@pytest.fixture(scope="session")
def is_wasm_available():
    """Check if WASM backend is available."""
    try:
        import wasmtime
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def backend_selector():
    """Provide a BackendSelector instance."""
    from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend

    if WASM_BACKEND_PREFERENCE == "wasm":
        return BackendSelector(prefer_backend=Backend.WASM)
    elif WASM_BACKEND_PREFERENCE == "fallback":
        return BackendSelector(prefer_backend=Backend.PYTHON)
    else:  # auto
        return BackendSelector(prefer_backend=Backend.AUTO)


@pytest.fixture
def wasm_backend_selector():
    """Provide a BackendSelector forced to WASM."""
    from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend
    return BackendSelector(prefer_backend=Backend.WASM)


@pytest.fixture
def fallback_backend_selector():
    """Provide a BackendSelector forced to Python fallback."""
    from multilingualprogramming.runtime.backend_selector import BackendSelector, Backend
    return BackendSelector(prefer_backend=Backend.PYTHON)


@pytest.fixture
def python_fallbacks():
    """Provide all Python fallback implementations."""
    from multilingualprogramming.runtime.python_fallbacks import (
        MatrixOperations,
        StringOperations,
        CryptoOperations,
        DataProcessing,
        NumericOperations,
        JSONOperations,
        SearchOperations,
        ImageOperations,
        FALLBACK_REGISTRY,
    )

    return {
        "matrix": MatrixOperations,
        "string": StringOperations,
        "crypto": CryptoOperations,
        "data": DataProcessing,
        "numeric": NumericOperations,
        "json": JSONOperations,
        "search": SearchOperations,
        "image": ImageOperations,
        "registry": FALLBACK_REGISTRY,
    }


@pytest.fixture(params=["en", "fr", "es", "de"])
def language_variants(request):
    """Parameterized fixture for multilingual testing."""
    return request.param


@pytest.fixture
def multilingual_sources():
    """Provide multilingual source code templates."""
    return {
        "en": {
            "for_loop": "for i in range(5): print(i)",
            "function": "def add(x, y): return x + y",
            "class": "class Point: def __init__(self, x, y): self.x = x; self.y = y",
        },
        "fr": {
            "for_loop": "pour i dans intervalle(5): afficher(i)",
            "function": "fonction ajouter(x, y): retourne x + y",
            "class": "classe Point: fonction __init__(soi, x, y): soi.x = x; soi.y = y",
        },
        "es": {
            "for_loop": "para i en rango(5): imprimir(i)",
            "function": "función sumar(x, y): devolver x + y",
            "class": "clase Punto: función __init__(yo, x, y): yo.x = x; yo.y = y",
        },
        "de": {
            "for_loop": "für i in bereich(5): ausgeben(i)",
            "function": "funktion addieren(x, y): zurück x + y",
            "class": "klasse Punkt: funktion __init__(selbst, x, y): selbst.x = x; selbst.y = y",
        },
    }


class PerformanceTimer:
    """Context manager for measuring operation performance."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.elapsed = 0.0
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        import time
        self.elapsed = time.perf_counter() - self.start_time

    def __str__(self):
        return f"{self.name}: {self.elapsed*1000:.2f}ms"


@pytest.fixture
def performance_timer():
    """Provide a performance timer."""
    return PerformanceTimer


@pytest.fixture
def assert_speedup():
    """Fixture for asserting WASM speedup over Python fallback."""
    def _assert_speedup(fallback_time: float, wasm_time: float, min_speedup: float = 1.5):
        """Assert that WASM is faster by at least min_speedup factor."""
        if wasm_time > 0:
            speedup = fallback_time / wasm_time
            assert speedup >= min_speedup, (
                f"WASM speedup {speedup:.1f}x < expected {min_speedup:.1f}x. "
                f"Fallback: {fallback_time*1000:.2f}ms, WASM: {wasm_time*1000:.2f}ms"
            )
            return speedup
        return 0

    return _assert_speedup


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on backend and type."""
    for item in items:
        # Mark correctness tests
        if "correctness" in item.nodeid.lower():
            item.add_marker(pytest.mark.correctness)

        # Mark performance tests
        if "performance" in item.nodeid.lower() or "benchmark" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

        # Mark corpus tests
        if "corpus" in item.nodeid.lower():
            item.add_marker(pytest.mark.corpus)
            item.add_marker(pytest.mark.slow)

        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)

        # Mark multilingual tests
        if "multilingual" in item.nodeid.lower():
            item.add_marker(pytest.mark.multilingual)
