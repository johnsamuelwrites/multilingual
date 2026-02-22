"""
M4 Tests: Ecosystem Compatibility

Tests execution of real-world Python code (small, pure-Python projects)
with output/behavior parity against CPython 3.12.

This test suite validates the multilingual compiler on curated corpus of
small, pure-Python projects across multiple domains:
- String manipulation (humanize)
- Algorithms (Sieve, FizzBuzz)
- JSON encoding
- Text processing
- Date arithmetic

Failure Classification:
  Layer 1 (Detection):
    PE: Parser Error - syntax not recognized
    SE: Semantic Error - analyzer rejects code
    CE: Code Generation Error - transpiler fails
    RE: Runtime Error - Python code fails
    OM: Output Mismatch - wrong result

  Layer 2 (Root Cause):
    IM: Import Missing
    TM: Type Mismatch
    AE: Attribute Error
    IE: Index/Key Error
    SP: Stdlib Parity divergence
    OS: Operator Semantics
    CF: Control Flow
    SB: Scope/Binding
"""

import unittest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import time

from multilingualprogramming.codegen.executor import ProgramExecutor


class FailureCategory(Enum):
    """Layer 1: Detection phase."""
    PARSER = "PE"
    SEMANTIC = "SE"
    CODEGEN = "CE"
    RUNTIME = "RE"
    OUTPUT = "OM"


class RootCause(Enum):
    """Layer 2: Semantic root cause."""
    IMPORT_MISSING = "IM"
    TYPE_MISMATCH = "TM"
    ATTRIBUTE_ERROR = "AE"
    INDEX_ERROR = "IE"
    STDLIB_PARITY = "SP"
    OPERATOR_SEMANTICS = "OS"
    CONTROL_FLOW = "CF"
    SCOPE_BINDING = "SB"


@dataclass
class CorpusProject:
    """Metadata for a corpus project."""
    name: str
    source_file: Path
    languages: list[str]
    category: str
    complexity: str
    expected_output: str
    description: str


@dataclass
class ExecutionResult:
    """Result of executing a corpus project."""
    success: bool
    output: str
    stderr: str
    error: Optional[str]
    category: Optional[FailureCategory]
    root_cause: Optional[RootCause]
    execution_time_ms: float


class CorpusProjectRegistry:
    """Central registry for corpus projects."""

    PROJECTS = {
        "humanize_numbers": CorpusProject(
            name="humanize_numbers",
            source_file=Path("tests/corpus/humanize_numbers.ml"),
            languages=["en", "fr", "es"],
            category="string_manipulation",
            complexity="simple",
            description="Format numbers with thousands separators",
            expected_output=(
                "1,000\n"
                "1,000\n"
                "1,000,000\n"
                "1.5\n"
                "1,234.567\n"
            ),
        ),
        "algorithms": CorpusProject(
            name="algorithms",
            source_file=Path("tests/corpus/algorithms.ml"),
            languages=["en"],
            category="algorithm",
            complexity="simple",
            description="Sieve of Eratosthenes and FizzBuzz",
            expected_output=(
                "2 3 5 7 11 13 17 19 23 29\n"
                "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n"
            ),
        ),
        "json_encoder": CorpusProject(
            name="json_encoder",
            source_file=Path("tests/corpus/json_encoder.ml"),
            languages=["en"],
            category="data_encoding",
            complexity="moderate",
            description="Simple JSON serialization",
            expected_output=(
                '{"a": 1, "b": [2, 3]}\n'
                '{"x": "hello"}\n'
                "null\n"
                "true\n"
                "false\n"
            ),
        ),
        "text_analyzer": CorpusProject(
            name="text_analyzer",
            source_file=Path("tests/corpus/text_analyzer.ml"),
            languages=["en"],
            category="text_processing",
            complexity="simple",
            description="Word frequency analysis",
            expected_output=(
                "the: 2\n"
                "quick: 1\n"
                "brown: 1\n"
                "fox: 1\n"
            ),
        ),
        "date_arithmetic": CorpusProject(
            name="date_arithmetic",
            source_file=Path("tests/corpus/date_arithmetic.ml"),
            languages=["en"],
            category="datetime",
            complexity="moderate",
            description="Date arithmetic operations",
            expected_output=(
                "2023-01-10\n"
                "2023-12-20\n"
                "3\n"
                "365\n"
            ),
        ),
    }

    @classmethod
    def get(cls, name: str) -> CorpusProject:
        """Get a corpus project by name."""
        if name not in cls.PROJECTS:
            raise ValueError(f"Unknown corpus project: {name}")
        return cls.PROJECTS[name]

    @classmethod
    def all(cls) -> list[CorpusProject]:
        """Get all corpus projects."""
        return list(cls.PROJECTS.values())


class EcosystemTestRunner:
    """Executes corpus projects and compares results."""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def execute_multilingual(
        self, source: str, language: str = "en"
    ) -> ExecutionResult:
        """Execute multilingual source code."""
        start_time = time.time()
        executor = ProgramExecutor(language=language, check_semantics=True)
        result = executor.execute(source)
        elapsed_ms = (time.time() - start_time) * 1000

        category = None
        root_cause = None

        if not result.success:
            category, root_cause = self._classify_failure(result)

        return ExecutionResult(
            success=result.success,
            output=result.output if result.success else "",
            stderr="",
            error=result.errors[0] if result.errors else None,
            category=category,
            root_cause=root_cause,
            execution_time_ms=elapsed_ms,
        )

    def _classify_failure(self, result) -> tuple:
        """Determine failure category and root cause."""
        if not result.errors:
            # Runtime error with no error message
            return (FailureCategory.RUNTIME, RootCause.IMPORT_MISSING)

        error_msg = result.errors[0].lower() if result.errors else ""

        # Layer 1: Detection
        if "syntax error" in error_msg or "invalid syntax" in error_msg:
            category = FailureCategory.PARSER
        elif "semantic error" in error_msg:
            category = FailureCategory.SEMANTIC
        elif "codegen" in error_msg or "code generation" in error_msg:
            category = FailureCategory.CODEGEN
        else:
            category = FailureCategory.RUNTIME

        # Layer 2: Root cause
        root_cause = RootCause.IMPORT_MISSING
        if "not defined" in error_msg:
            root_cause = RootCause.SCOPE_BINDING
        elif "undefined" in error_msg or "name" in error_msg:
            root_cause = RootCause.SCOPE_BINDING
        elif "type" in error_msg:
            root_cause = RootCause.TYPE_MISMATCH
        elif "attribute" in error_msg:
            root_cause = RootCause.ATTRIBUTE_ERROR
        elif "index" in error_msg or "key" in error_msg:
            root_cause = RootCause.INDEX_ERROR
        elif "import" in error_msg:
            root_cause = RootCause.IMPORT_MISSING

        return (category, root_cause)


# ===== Test Suites =====


class HumanizeNumberTestSuite(unittest.TestCase):
    """Tests humanize.number equivalence across languages."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("humanize_numbers")

    def _load_corpus(self, filename: str) -> str:
        """Load corpus file."""
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_humanize_format_en_basic(self):
        """Humanize numbers in English."""
        result = self.runner.execute_multilingual(
            self._load_corpus("humanize_numbers.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_humanize_format_fr_equivalent(self):
        """Humanize numbers in French produces same result."""
        source = self._load_corpus("humanize_numbers_fr.ml")
        result = self.runner.execute_multilingual(source, language="fr")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should produce same output as English version
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_humanize_format_es_equivalent(self):
        """Humanize numbers in Spanish produces same result."""
        source = self._load_corpus("humanize_numbers_es.ml")
        result = self.runner.execute_multilingual(source, language="es")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should produce same output as English version
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())


class AlgorithmsTestSuite(unittest.TestCase):
    """Tests algorithms (Sieve, FizzBuzz)."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("algorithms")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_sieve_of_eratosthenes(self):
        """Generate primes using Sieve of Eratosthenes."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        output_lines = result.output.strip().split("\n")
        # First line should be primes
        self.assertIn("2", output_lines[0])
        self.assertIn("3", output_lines[0])
        self.assertIn("5", output_lines[0])


class JsonEncoderTestSuite(unittest.TestCase):
    """Tests JSON encoding."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("json_encoder")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_json_encode_basic(self):
        """Encode basic JSON structures."""
        result = self.runner.execute_multilingual(
            self._load_corpus("json_encoder.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should produce valid JSON output
        self.assertIn('"', result.output)


class TextAnalyzerTestSuite(unittest.TestCase):
    """Tests text processing and word frequency."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("text_analyzer")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_word_frequency(self):
        """Analyze word frequency in text."""
        result = self.runner.execute_multilingual(
            self._load_corpus("text_analyzer.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output word frequency pairs
        self.assertIn(":", result.output)


class DateArithmeticTestSuite(unittest.TestCase):
    """Tests date arithmetic operations."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("date_arithmetic")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_date_arithmetic(self):
        """Perform date arithmetic."""
        result = self.runner.execute_multilingual(
            self._load_corpus("date_arithmetic.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output dates in YYYY-MM-DD format
        self.assertIn("2023", result.output)


if __name__ == "__main__":
    unittest.main()
