"""
Ecosystem Compatibility Tests

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
        "statistics": CorpusProject(
            name="statistics",
            source_file=Path("tests/corpus/statistics.ml"),
            languages=["en"],
            category="data_analysis",
            complexity="simple",
            description="Basic statistics (mean, median, mode)",
            expected_output=(
                "4.8\n"
                "5\n"
                "3\n"
            ),
        ),
        "list_utilities": CorpusProject(
            name="list_utilities",
            source_file=Path("tests/corpus/list_utilities.ml"),
            languages=["en"],
            category="data_manipulation",
            complexity="simple",
            description="List operations (flatten, unique, chunk)",
            expected_output=(
                "[1, 2, 3, 4, 5, 6]\n"
                "[1, 2, 3]\n"
                "[[1, 2], [3, 4], [5]]\n"
            ),
        ),
        "string_utilities": CorpusProject(
            name="string_utilities",
            source_file=Path("tests/corpus/string_utilities.ml"),
            languages=["en"],
            category="string_manipulation",
            complexity="simple",
            description="String operations (reverse, palindrome, count)",
            expected_output=(
                "dlrow olleh\n"
                "True\n"
                "3\n"
            ),
        ),
        "fibonacci": CorpusProject(
            name="fibonacci",
            source_file=Path("tests/corpus/fibonacci.ml"),
            languages=["en"],
            category="algorithm",
            complexity="moderate",
            description="Fibonacci sequence generator",
            expected_output=(
                "0\n1\n1\n2\n3\n5\n8\n13\n"
            ),
        ),
        "simple_calculator": CorpusProject(
            name="simple_calculator",
            source_file=Path("tests/corpus/simple_calculator.ml"),
            languages=["en"],
            category="utility",
            complexity="simple",
            description="Basic calculator operations",
            expected_output=(
                "15\n"
                "5\n"
                "50\n"
                "2.0\n"
            ),
        ),
        "recursive_factorial": CorpusProject(
            name="recursive_factorial",
            source_file=Path("tests/corpus/recursive_factorial.ml"),
            languages=["en"],
            category="algorithm",
            complexity="moderate",
            description="Recursive factorial calculation",
            expected_output=(
                "120\n"
                "720\n"
                "5040\n"
            ),
        ),
        "lambda_functions": CorpusProject(
            name="lambda_functions",
            source_file=Path("tests/corpus/lambda_functions.ml"),
            languages=["en"],
            category="functional",
            complexity="moderate",
            description="Lambda functions and functional programming",
            expected_output=(
                "[2, 4, 6, 8, 10]\n"
                "[2, 4]\n"
                "15\n"
            ),
        ),
        "exception_handling": CorpusProject(
            name="exception_handling",
            source_file=Path("tests/corpus/exception_handling.ml"),
            languages=["en"],
            category="control_flow",
            complexity="moderate",
            description="Try/except/finally exception handling",
            expected_output=(
                "Error caught\n"
                "Cleanup\n"
                "Success\n"
            ),
        ),
        "comprehensions": CorpusProject(
            name="comprehensions",
            source_file=Path("tests/corpus/comprehensions.ml"),
            languages=["en"],
            category="advanced",
            complexity="moderate",
            description="List/dict/set comprehensions",
            expected_output=(
                "[1, 4, 9, 16, 25]\n"
                "{1: 1, 2: 4, 3: 9}\n"
                "{1, 4, 9}\n"
            ),
        ),
        "edge_cases": CorpusProject(
            name="edge_cases",
            source_file=Path("tests/corpus/edge_cases.ml"),
            languages=["en"],
            category="robustness",
            complexity="moderate",
            description="Edge cases: empty collections, negative numbers, boundaries",
            expected_output=(
                "0\n"
                "True\n"
                "-5\n"
                "[]\n"
            ),
        ),
        "performance": CorpusProject(
            name="performance",
            source_file=Path("tests/corpus/performance.ml"),
            languages=["en"],
            category="performance",
            complexity="moderate",
            description="Performance testing with large data structures",
            expected_output=(
                "1000\n"
                "999\n"
                "4950\n"
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

    def _load_corpus_for_language(self, filename: str, language: str) -> str:
        """Load corpus file from language-specific folder when available."""
        lang_path = Path("tests/corpus") / language / filename
        if lang_path.exists():
            return lang_path.read_text(encoding="utf-8")
        return self._load_corpus(filename)

    def test_humanize_format_en_basic(self):
        """Humanize numbers in English."""
        result = self.runner.execute_multilingual(
            self._load_corpus("humanize_numbers.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_humanize_format_en_contains_separator(self):
        """English output contains comma separators."""
        result = self.runner.execute_multilingual(
            self._load_corpus("humanize_numbers.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn(",", result.output)

    def test_humanize_format_en_handles_thousands(self):
        """English handles thousands correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("humanize_numbers.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("1,000", result.output)
        self.assertIn("1,000,000", result.output)

    def test_humanize_format_fr_equivalent(self):
        """Humanize numbers in French produces same result."""
        source = self._load_corpus_for_language("humanize_numbers.ml", "fr")
        result = self.runner.execute_multilingual(source, language="fr")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should produce same output as English version
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_humanize_format_fr_execution_time(self):
        """French execution completes in reasonable time."""
        source = self._load_corpus_for_language("humanize_numbers.ml", "fr")
        result = self.runner.execute_multilingual(source, language="fr")
        self.assertTrue(result.success)
        self.assertLess(result.execution_time_ms, 5000)

    def test_humanize_format_es_equivalent(self):
        """Humanize numbers in Spanish produces same result."""
        source = self._load_corpus_for_language("humanize_numbers.ml", "es")
        result = self.runner.execute_multilingual(source, language="es")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should produce same output as English version
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_humanize_format_es_output_lines(self):
        """Spanish output has correct number of lines."""
        source = self._load_corpus_for_language("humanize_numbers.ml", "es")
        result = self.runner.execute_multilingual(source, language="es")
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 5)


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

    def test_sieve_includes_29(self):
        """Prime generation includes 29."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertIn("29", output_lines[0])

    def test_sieve_no_composites(self):
        """Prime generation excludes composite numbers."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        # Should not contain 4, 6, 8, 9, 10, etc.
        primes_str = output_lines[0]
        self.assertNotIn("4", primes_str.split())
        self.assertNotIn("6", primes_str.split())

    def test_fizzbuzz_has_fizz(self):
        """FizzBuzz output contains Fizz."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("Fizz", result.output)

    def test_fizzbuzz_has_buzz(self):
        """FizzBuzz output contains Buzz."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("Buzz", result.output)

    def test_algorithms_execution_time(self):
        """Algorithm execution completes quickly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("algorithms.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertLess(result.execution_time_ms, 5000)


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

    def test_json_encode_dict(self):
        """JSON encodes dictionaries."""
        result = self.runner.execute_multilingual(
            self._load_corpus("json_encoder.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn('{"a"', result.output)

    def test_json_encode_lists(self):
        """JSON encodes lists."""
        result = self.runner.execute_multilingual(
            self._load_corpus("json_encoder.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[", result.output)
        self.assertIn("]", result.output)

    def test_json_encode_null(self):
        """JSON encodes null values."""
        result = self.runner.execute_multilingual(
            self._load_corpus("json_encoder.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("null", result.output)

    def test_json_encode_booleans(self):
        """JSON encodes boolean values."""
        result = self.runner.execute_multilingual(
            self._load_corpus("json_encoder.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("true", result.output)
        self.assertIn("false", result.output)


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

    def test_word_frequency_format(self):
        """Word frequency output has correct format."""
        result = self.runner.execute_multilingual(
            self._load_corpus("text_analyzer.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        # Each line should have word: count format
        for line in output_lines:
            self.assertIn(":", line)

    def test_word_frequency_the_count(self):
        """Text analyzer counts 'the' correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("text_analyzer.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("the: 2", result.output)

    def test_word_frequency_uses_counter(self):
        """Word frequency analysis uses Counter."""
        result = self.runner.execute_multilingual(
            self._load_corpus("text_analyzer.ml"), language="en"
        )
        self.assertTrue(result.success)
        # Counter should produce frequency output
        self.assertGreater(len(result.output.strip()), 0)


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

    def test_date_addition(self):
        """Date addition with timedelta."""
        result = self.runner.execute_multilingual(
            self._load_corpus("date_arithmetic.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("2023-01-10", result.output)

    def test_date_subtraction(self):
        """Date arithmetic produces correct results."""
        result = self.runner.execute_multilingual(
            self._load_corpus("date_arithmetic.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        # Should have date operations results
        self.assertGreaterEqual(len(output_lines), 4)

    def test_date_difference(self):
        """Date difference calculation."""
        result = self.runner.execute_multilingual(
            self._load_corpus("date_arithmetic.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("365", result.output)


class StatisticsTestSuite(unittest.TestCase):
    """Tests basic statistics operations."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("statistics")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_statistics_basic(self):
        """Calculate mean, median, and mode."""
        result = self.runner.execute_multilingual(
            self._load_corpus("statistics.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output mean, median, mode
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 3)
        self.assertIn("4.8", output_lines[0])  # mean
        self.assertIn("5", output_lines[1])  # median
        self.assertIn("3", output_lines[2])  # mode

    def test_statistics_mean_calculation(self):
        """Mean is calculated correctly from dataset."""
        result = self.runner.execute_multilingual(
            self._load_corpus("statistics.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("4.8", result.output)

    def test_statistics_median_calculation(self):
        """Median is calculated correctly from dataset."""
        result = self.runner.execute_multilingual(
            self._load_corpus("statistics.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[1].strip(), "5")

    def test_statistics_mode_calculation(self):
        """Mode is calculated correctly from dataset."""
        result = self.runner.execute_multilingual(
            self._load_corpus("statistics.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("3", result.output)


class ListUtilitiesTestSuite(unittest.TestCase):
    """Tests list utility operations."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("list_utilities")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_list_utilities(self):
        """Test list flatten, unique, and chunk operations."""
        result = self.runner.execute_multilingual(
            self._load_corpus("list_utilities.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output flattened list, unique list, chunks
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 3)
        self.assertIn("[1, 2, 3, 4, 5, 6]", output_lines[0])

    def test_list_flatten(self):
        """List flattening produces flat result."""
        result = self.runner.execute_multilingual(
            self._load_corpus("list_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[0], "[1, 2, 3, 4, 5, 6]")

    def test_list_unique(self):
        """List deduplication preserves order."""
        result = self.runner.execute_multilingual(
            self._load_corpus("list_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[1], "[1, 2, 3]")

    def test_list_chunk(self):
        """List chunking groups elements correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("list_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[[1, 2], [3, 4], [5]]", result.output)


class StringUtilitiesTestSuite(unittest.TestCase):
    """Tests string utility operations."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("string_utilities")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_string_utilities(self):
        """Test string reverse, palindrome, and count operations."""
        result = self.runner.execute_multilingual(
            self._load_corpus("string_utilities.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output reversed string, palindrome result, character count
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 3)
        self.assertIn("dlrow olleh", output_lines[0])

    def test_string_reverse(self):
        """String reversal produces correct output."""
        result = self.runner.execute_multilingual(
            self._load_corpus("string_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("dlrow olleh", result.output)

    def test_string_palindrome(self):
        """Palindrome detection works correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("string_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("True", result.output)

    def test_string_character_count(self):
        """Character counting produces correct count."""
        result = self.runner.execute_multilingual(
            self._load_corpus("string_utilities.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("4", result.output)


class FibonacciTestSuite(unittest.TestCase):
    """Tests Fibonacci sequence generation."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("fibonacci")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_fibonacci_sequence(self):
        """Generate Fibonacci sequence."""
        result = self.runner.execute_multilingual(
            self._load_corpus("fibonacci.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output Fibonacci numbers
        self.assertIn("0", result.output)
        self.assertIn("1", result.output)
        self.assertIn("13", result.output)

    def test_fibonacci_starts_with_zero(self):
        """Fibonacci sequence starts with 0."""
        result = self.runner.execute_multilingual(
            self._load_corpus("fibonacci.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[0], "0")

    def test_fibonacci_correct_length(self):
        """Fibonacci sequence generates correct number of terms."""
        result = self.runner.execute_multilingual(
            self._load_corpus("fibonacci.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 8)

    def test_fibonacci_includes_13(self):
        """Fibonacci sequence includes 13."""
        result = self.runner.execute_multilingual(
            self._load_corpus("fibonacci.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("13", result.output)


class SimpleCalculatorTestSuite(unittest.TestCase):
    """Tests basic arithmetic operations."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("simple_calculator")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def _load_corpus_for_language(self, filename: str, language: str) -> str:
        lang_path = Path("tests/corpus") / language / filename
        if lang_path.exists():
            return lang_path.read_text(encoding="utf-8")
        return self._load_corpus(filename)

    def test_calculator_operations(self):
        """Perform basic calculator operations."""
        result = self.runner.execute_multilingual(
            self._load_corpus("simple_calculator.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        # Should output results of add, subtract, multiply, divide
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 4)
        self.assertIn("15", output_lines[0])  # add
        self.assertIn("5", output_lines[1])   # subtract

    def test_calculator_addition(self):
        """Calculator performs addition correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("simple_calculator.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[0], "15")

    def test_calculator_subtraction(self):
        """Calculator performs subtraction correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("simple_calculator.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[1], "5")

    def test_calculator_multiplication(self):
        """Calculator performs multiplication correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("simple_calculator.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[2], "50")

    def test_calculator_division(self):
        """Calculator performs division correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("simple_calculator.ml"), language="en"
        )
        self.assertTrue(result.success)
        output_lines = result.output.strip().split("\n")
        self.assertEqual(output_lines[3], "2.0")

    def test_calculator_operations_french_parity(self):
        """French calculator corpus matches expected output."""
        source = self._load_corpus_for_language("simple_calculator.ml", "fr")
        result = self.runner.execute_multilingual(source, language="fr")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_calculator_operations_spanish_parity(self):
        """Spanish calculator corpus matches expected output."""
        source = self._load_corpus_for_language("simple_calculator.ml", "es")
        result = self.runner.execute_multilingual(source, language="es")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())


class RecursiveFactorialTestSuite(unittest.TestCase):
    """Tests recursive function calls."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("recursive_factorial")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def _load_corpus_for_language(self, filename: str, language: str) -> str:
        lang_path = Path("tests/corpus") / language / filename
        if lang_path.exists():
            return lang_path.read_text(encoding="utf-8")
        return self._load_corpus(filename)

    def test_recursive_factorial(self):
        """Calculate factorial using recursion."""
        result = self.runner.execute_multilingual(
            self._load_corpus("recursive_factorial.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 3)
        self.assertIn("120", output_lines[0])

    def test_recursive_factorial_5(self):
        """Factorial of 5 is 120."""
        result = self.runner.execute_multilingual(
            self._load_corpus("recursive_factorial.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("120", result.output)

    def test_recursive_factorial_6(self):
        """Factorial of 6 is 720."""
        result = self.runner.execute_multilingual(
            self._load_corpus("recursive_factorial.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("720", result.output)

    def test_recursive_factorial_7(self):
        """Factorial of 7 is 5040."""
        result = self.runner.execute_multilingual(
            self._load_corpus("recursive_factorial.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("5040", result.output)

    def test_recursive_factorial_french_parity(self):
        """French recursive factorial corpus matches expected output."""
        source = self._load_corpus_for_language("recursive_factorial.ml", "fr")
        result = self.runner.execute_multilingual(source, language="fr")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())

    def test_recursive_factorial_spanish_parity(self):
        """Spanish recursive factorial corpus matches expected output."""
        source = self._load_corpus_for_language("recursive_factorial.ml", "es")
        result = self.runner.execute_multilingual(source, language="es")
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertEqual(result.output.strip(), self.project.expected_output.strip())


class LambdaFunctionsTestSuite(unittest.TestCase):
    """Tests lambda functions and functional programming."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("lambda_functions")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_lambda_functions(self):
        """Test lambda functions with map, filter, reduce."""
        result = self.runner.execute_multilingual(
            self._load_corpus("lambda_functions.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertIn("[2, 4, 6, 8, 10]", result.output)

    def test_lambda_map(self):
        """Lambda with map function."""
        result = self.runner.execute_multilingual(
            self._load_corpus("lambda_functions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[2, 4, 6, 8, 10]", result.output)

    def test_lambda_filter(self):
        """Lambda with filter function."""
        result = self.runner.execute_multilingual(
            self._load_corpus("lambda_functions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[2, 4]", result.output)

    def test_lambda_reduce(self):
        """Lambda with reduce function."""
        result = self.runner.execute_multilingual(
            self._load_corpus("lambda_functions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("15", result.output)


class ExceptionHandlingTestSuite(unittest.TestCase):
    """Tests exception handling with try/except/finally."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("exception_handling")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_exception_handling(self):
        """Test try/except/finally blocks."""
        result = self.runner.execute_multilingual(
            self._load_corpus("exception_handling.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertIn("Error caught", result.output)
        self.assertIn("Cleanup", result.output)

    def test_exception_caught(self):
        """Exception is caught and handled."""
        result = self.runner.execute_multilingual(
            self._load_corpus("exception_handling.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("Error caught", result.output)

    def test_finally_executed(self):
        """Finally block is executed."""
        result = self.runner.execute_multilingual(
            self._load_corpus("exception_handling.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("Cleanup", result.output)

    def test_success_case(self):
        """Normal execution after exception handling."""
        result = self.runner.execute_multilingual(
            self._load_corpus("exception_handling.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("Success", result.output)


class ComprehensionsTestSuite(unittest.TestCase):
    """Tests list/dict/set comprehensions."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("comprehensions")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_comprehensions(self):
        """Test list, dict, and set comprehensions."""
        result = self.runner.execute_multilingual(
            self._load_corpus("comprehensions.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        self.assertIn("[1, 4, 9, 16, 25]", result.output)

    def test_list_comprehension(self):
        """List comprehension produces correct result."""
        result = self.runner.execute_multilingual(
            self._load_corpus("comprehensions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[1, 4, 9, 16, 25]", result.output)

    def test_dict_comprehension(self):
        """Dict comprehension produces correct result."""
        result = self.runner.execute_multilingual(
            self._load_corpus("comprehensions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("{1: 1, 2: 4, 3: 9}", result.output)

    def test_set_comprehension(self):
        """Set comprehension produces correct result."""
        result = self.runner.execute_multilingual(
            self._load_corpus("comprehensions.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("{1, 4, 9}", result.output)


class EdgeCasesTestSuite(unittest.TestCase):
    """Tests edge cases and boundary conditions."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("edge_cases")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_edge_cases(self):
        """Test edge cases like empty collections and negative numbers."""
        result = self.runner.execute_multilingual(
            self._load_corpus("edge_cases.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 4)

    def test_empty_collection(self):
        """Empty collections handled correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("edge_cases.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("[]", result.output)

    def test_negative_numbers(self):
        """Negative numbers work correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("edge_cases.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("-5", result.output)

    def test_zero_handling(self):
        """Zero is handled correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("edge_cases.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("0", result.output)


class PerformanceTestSuite(unittest.TestCase):
    """Tests performance with larger data structures."""

    def setUp(self):
        self.runner = EcosystemTestRunner()
        self.project = CorpusProjectRegistry.get("performance")

    def _load_corpus(self, filename: str) -> str:
        return (Path("tests/corpus") / filename).read_text(encoding="utf-8")

    def test_performance_basic(self):
        """Performance test with larger data structures."""
        result = self.runner.execute_multilingual(
            self._load_corpus("performance.ml"), language="en"
        )
        self.assertTrue(
            result.success, msg=f"Failed: {result.error or 'Unknown error'}"
        )
        output_lines = result.output.strip().split("\n")
        self.assertEqual(len(output_lines), 3)

    def test_large_list_length(self):
        """Large list length calculated correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("performance.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("1000", result.output)

    def test_large_list_last_element(self):
        """Last element of large list accessed correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("performance.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("999", result.output)

    def test_large_list_sum(self):
        """Sum of large list calculated correctly."""
        result = self.runner.execute_multilingual(
            self._load_corpus("performance.ml"), language="en"
        )
        self.assertTrue(result.success)
        self.assertIn("4950", result.output)


if __name__ == "__main__":
    unittest.main()
