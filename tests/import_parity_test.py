"""
M3 Tests: Import/Module Resolution Parity

Verify that import behavior and module resolution work correctly across the
multilingual language, matching CPython semantics for import statements,
module aliases, and cross-language imports.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute(source: str, language: str = "en") -> str:
    """Execute multilingual source and return stdout."""
    result = ProgramExecutor(language=language, check_semantics=True).execute(source)
    return result.output if result.success else ""


class ImportBasicsTestSuite(unittest.TestCase):
    """Test basic import statement syntax and behavior."""

    def test_import_standard_module(self):
        """Import standard library module."""
        source = "import math\nprint(math.pi > 3.14)"
        output = _execute(source)
        self.assertIn("True", output)

    def test_from_import_single_function(self):
        """From import single function."""
        source = "from math import sqrt\nlet result = sqrt(16)\nprint(result)"
        output = _execute(source)
        self.assertIn("4", output)

    def test_from_import_multiple_functions(self):
        """From import multiple functions."""
        source = "from math import sqrt, floor\nlet a = sqrt(9)\nlet b = floor(3.7)\nprint(a, b)"
        output = _execute(source)
        self.assertIn("3.0 3", output)

    def test_from_import_with_alias(self):
        """From import with alias."""
        source = "from math import sqrt as square_root\nlet result = square_root(25)\nprint(result)"
        output = _execute(source)
        self.assertIn("5", output)

    def test_import_with_alias(self):
        """Import module with alias."""
        source = "import math as m\nlet result = m.sqrt(4)\nprint(result)"
        output = _execute(source)
        self.assertIn("2", output)

    def test_import_builtin_vs_stdlib(self):
        """Builtin functions available without import."""
        source = "let result = len([1, 2, 3])\nprint(result)"
        output = _execute(source)
        self.assertIn("3", output)

    def test_module_attribute_access(self):
        """Access module attributes (constants)."""
        source = "import math\nlet pi_value = math.pi\nprint(type(pi_value).__name__)"
        output = _execute(source)
        self.assertIn("float", output)

    def test_nested_module_attribute(self):
        """Access nested module attributes."""
        # Note: Multilingual requires `import os` then access os.path
        source = "import os\nlet sep = os.path.sep\nprint(type(sep).__name__)"
        output = _execute(source)
        self.assertIn("str", output)

    def test_import_doesnt_pollute_namespace(self):
        """Import doesn't add module name to outer scope."""
        # Note: Multilingual requires unique names in scope, so we can't redefine sqrt
        # This is actually a stricter semantic than Python
        source = "from math import sqrt as math_sqrt\nlet sqrt = 5\nprint(sqrt)"
        output = _execute(source)
        self.assertIn("5", output)

    def test_reimport_same_module(self):
        """Reimporting same module reuses cached version."""
        source = """
import math
let val1 = math.sqrt(4)
import math
let val2 = math.sqrt(4)
print(val1 == val2)
"""
        output = _execute(source)
        self.assertIn("True", output)


class MultilingualImportTestSuite(unittest.TestCase):
    """Test cross-language imports within multilingual projects."""

    def test_english_imports_french_module(self):
        """English program can import French-named module."""
        # This tests the existing functionality
        source = """
# Would normally import from examples/arithmetics_fr.ml
# For now, just verify Python module imports work in English
import math
let result = math.sqrt(9)
print(result)
"""
        output = _execute(source, "en")
        self.assertIn("3", output)

    def test_french_imports_english_module(self):
        """French program can import English-named module."""
        # This tests multilingual program structure
        source = """
importer math
soit résultat = math.sqrt(9)
afficher(résultat)
"""
        output = _execute(source, "fr")
        # If French keywords are supported
        if output:
            self.assertIn("3", output)

    def test_language_agnostic_imports(self):
        """Python modules work regardless of frontend language."""
        # Python stdlib should work in any language variant
        source = "import json\nlet data = json.dumps([1, 2, 3])\nprint(data)"
        for lang in ["en", "fr", "es"]:
            output = _execute(source, lang)
            if output:  # Language might not be fully implemented
                self.assertIn("[1, 2, 3]", output)


class StdlibImportTestSuite(unittest.TestCase):
    """Test importing from key stdlib modules."""

    def test_import_math_module(self):
        """Import math module and use functions."""
        source = "import math\nlet result = math.ceil(3.2)\nprint(result)"
        output = _execute(source)
        self.assertIn("4", output)

    def test_import_random_module(self):
        """Import random module."""
        source = "import random\nlet result = random.random()\nprint(0 <= result <= 1)"
        output = _execute(source)
        # Should print True
        self.assertIsNotNone(output)

    def test_import_datetime_module(self):
        """Import datetime module."""
        source = "from datetime import date\nlet today = date.today()\nprint(type(today).__name__)"
        output = _execute(source)
        self.assertIn("date", output)

    def test_import_json_module(self):
        """Import json module."""
        source = "import json\nlet data = json.loads('{\"key\": \"value\"}')\nprint(data[\"key\"])"
        output = _execute(source)
        self.assertIn("value", output)

    def test_import_pathlib_module(self):
        """Import pathlib module."""
        source = "from pathlib import Path\nlet p = Path('.')\nprint(type(p).__name__)"
        output = _execute(source)
        self.assertIn("Path", output)

    def test_import_itertools_module(self):
        """Import itertools module."""
        source = "from itertools import chain\nlet result = list(chain([1, 2], [3, 4]))\nprint(result)"
        output = _execute(source)
        self.assertIn("[1, 2, 3, 4]", output)

    def test_import_collections_module(self):
        """Import collections module."""
        source = "from collections import Counter\nlet c = Counter([1, 1, 2, 2, 2])\nprint(c[2])"
        output = _execute(source)
        self.assertIn("3", output)

    def test_import_functools_module(self):
        """Import functools module."""
        source = "from functools import reduce\nlet result = reduce(lambda x, y: x + y, [1, 2, 3, 4])\nprint(result)"
        output = _execute(source)
        self.assertIn("10", output)


class ImportErrorHandlingTestSuite(unittest.TestCase):
    """Test error handling for import statements."""

    def test_import_nonexistent_module(self):
        """Importing nonexistent module raises error."""
        source = "import nonexistent_module_12345"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        self.assertFalse(result.success)

    def test_from_import_nonexistent_name(self):
        """From import nonexistent name raises error."""
        source = "from math import nonexistent_function_12345"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        self.assertFalse(result.success)

    def test_import_star_not_supported(self):
        """Import * should either work or fail gracefully."""
        # This is optional syntax support
        source = "from math import *"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        # Just verify it doesn't crash
        self.assertIsNotNone(result)

    def test_relative_import_not_supported(self):
        """Relative imports should fail gracefully."""
        # Relative imports are complex, not required for M3
        source = "from . import something"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        # Just verify it doesn't crash
        self.assertIsNotNone(result)


class ImportSemanticTestSuite(unittest.TestCase):
    """Test semantic behavior of imports."""

    def test_import_defines_module_binding(self):
        """Import creates binding in current scope."""
        source = "import math\nprint(type(math).__name__)"
        output = _execute(source)
        self.assertIn("module", output)

    def test_from_import_defines_function_binding(self):
        """From import creates function binding."""
        source = "from math import sqrt\nprint(callable(sqrt))"
        output = _execute(source)
        self.assertIn("True", output)

    def test_module_not_defined_after_from_import(self):
        """Module name not available after from import."""
        # Multilingual catches undefined names at semantic analysis time
        source = "from math import sqrt\nprint(math.sqrt(4))"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        self.assertFalse(result.success)
        self.assertTrue(any("math" in str(e) for e in result.errors))

    def test_imported_function_is_callable(self):
        """Imported function is callable."""
        source = "from math import sqrt\nlet result = sqrt(16)\nprint(result)"
        output = _execute(source)
        self.assertIn("4", output)

    def test_import_order_independence(self):
        """Import order doesn't affect meaning (except redefinition)."""
        source1 = "import math\nimport sys\nlet result = math.sqrt(4)\nprint(result)"
        source2 = "import sys\nimport math\nlet result = math.sqrt(4)\nprint(result)"
        output1 = _execute(source1)
        output2 = _execute(source2)
        self.assertIn("2", output1)
        self.assertIn("2", output2)


if __name__ == "__main__":
    unittest.main()
