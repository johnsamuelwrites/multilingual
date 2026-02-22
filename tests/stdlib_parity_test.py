"""
Standard Library Parity Tests

Verify that stdlib functions behave consistently with CPython 3.12 when called
from multilingual programs. Focus on key modules: math, json, datetime,
itertools, pathlib, collections, functools.
"""

# pylint: disable=line-too-long

import unittest
from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute(source: str, language: str = "en") -> str:
    """Execute multilingual source and return stdout."""
    result = ProgramExecutor(language=language, check_semantics=True).execute(source)
    return result.output if result.success else ""


class MathModuleTestSuite(unittest.TestCase):
    """Test math module functions."""

    def test_math_sqrt(self):
        """math.sqrt returns correct value."""
        source = "import math\nlet result = math.sqrt(16)\nprint(result)"
        output = _execute(source)
        self.assertIn("4", output)

    def test_math_sqrt_float(self):
        """math.sqrt works with floats."""
        source = "import math\nlet result = math.sqrt(2.25)\nprint(result)"
        output = _execute(source)
        self.assertIn("1.5", output)

    def test_math_floor(self):
        """math.floor rounds down."""
        source = "import math\nlet result = math.floor(3.7)\nprint(result)"
        output = _execute(source)
        self.assertIn("3", output)

    def test_math_ceil(self):
        """math.ceil rounds up."""
        source = "import math\nlet result = math.ceil(3.2)\nprint(result)"
        output = _execute(source)
        self.assertIn("4", output)

    def test_math_fabs(self):
        """math.fabs returns absolute value."""
        source = "import math\nlet result = math.fabs(-5.5)\nprint(result)"
        output = _execute(source)
        self.assertIn("5.5", output)

    def test_math_factorial(self):
        """math.factorial computes factorial."""
        source = "import math\nlet result = math.factorial(5)\nprint(result)"
        output = _execute(source)
        self.assertIn("120", output)

    def test_math_gcd(self):
        """math.gcd finds greatest common divisor."""
        source = "import math\nlet result = math.gcd(48, 18)\nprint(result)"
        output = _execute(source)
        self.assertIn("6", output)

    def test_math_pow(self):
        """math.pow computes power."""
        source = "import math\nlet result = math.pow(2, 3)\nprint(result)"
        output = _execute(source)
        self.assertIn("8", output)

    def test_math_sin_cos_tan(self):
        """math trigonometric functions."""
        source = "import math\nlet result = math.sin(0)\nprint(result)"
        output = _execute(source)
        self.assertIn("0", output)

    def test_math_log(self):
        """math.log computes logarithm."""
        source = "import math\nlet result = math.log(2.718281828) > 0.999\nprint(result)"
        output = _execute(source)
        self.assertIn("True", output)

    def test_math_constants(self):
        """math.pi and math.e constants."""
        source = "import math\nlet pi = math.pi > 3.14\nlet e = math.e > 2.71\nprint(pi and e)"
        output = _execute(source)
        self.assertIn("True", output)


class JsonModuleTestSuite(unittest.TestCase):
    """Test json module functions."""

    def test_json_dumps_dict(self):
        """json.dumps serializes dict."""
        source = 'import json\nlet data = json.dumps({"a": 1})\nprint("a" in data)'
        output = _execute(source)
        self.assertIn("True", output)

    def test_json_dumps_list(self):
        """json.dumps serializes list."""
        source = "import json\nlet data = json.dumps([1, 2, 3])\nprint(data)"
        output = _execute(source)
        self.assertIn("[1, 2, 3]", output)

    def test_json_loads_dict(self):
        """json.loads deserializes dict."""
        source = 'import json\nlet data = json.loads(\'{"key": "value"}\')\nprint(data["key"])'
        output = _execute(source)
        self.assertIn("value", output)

    def test_json_loads_list(self):
        """json.loads deserializes list."""
        source = "import json\nlet data = json.loads('[1, 2, 3]')\nprint(len(data))"
        output = _execute(source)
        self.assertIn("3", output)

    def test_json_dumps_indent(self):
        """json.dumps with indent parameter."""
        # Check that json.dumps with indent=2 produces different output than without
        source = "import json\nlet data = json.dumps({\"a\": 1}, indent=2)\nlet data_compact = json.dumps({\"a\": 1})\nprint(len(data) > len(data_compact))"
        output = _execute(source)
        self.assertIn("True", output)

    def test_json_loads_invalid(self):
        """json.loads with invalid JSON raises error."""
        source = "import json\njson.loads('invalid json')"
        result = ProgramExecutor(language="en", check_semantics=True).execute(source)
        self.assertFalse(result.success)

    def test_json_roundtrip(self):
        """json dumps/loads roundtrip."""
        source = """
import json
let original = {"a": 1, "b": [2, 3]}
let serialized = json.dumps(original)
let deserialized = json.loads(serialized)
print(deserialized["a"] == 1)
"""
        output = _execute(source)
        self.assertIn("True", output)


class DatetimeModuleTestSuite(unittest.TestCase):
    """Test datetime module functions."""

    def test_datetime_today(self):
        """datetime.date.today returns date object."""
        source = "from datetime import date\nlet today = date.today()\nprint(type(today).__name__)"
        output = _execute(source)
        self.assertIn("date", output)

    def test_datetime_now(self):
        """datetime.datetime.now returns datetime object."""
        source = "from datetime import datetime\nlet now = datetime.now()\nprint(type(now).__name__)"
        output = _execute(source)
        self.assertIn("datetime", output)

    def test_datetime_create(self):
        """Create datetime object."""
        source = "from datetime import datetime\nlet dt = datetime(2023, 1, 15)\nprint(dt.year)"
        output = _execute(source)
        self.assertIn("2023", output)

    def test_datetime_year_month_day(self):
        """Access date components."""
        source = "from datetime import date\nlet d = date(2023, 3, 15)\nprint(d.month)"
        output = _execute(source)
        self.assertIn("3", output)

    def test_datetime_timedelta(self):
        """timedelta for date arithmetic."""
        source = """
from datetime import date, timedelta
let d1 = date(2023, 1, 1)
let d2 = d1 + timedelta(days=10)
print(d2.day)
"""
        output = _execute(source)
        self.assertIn("11", output)

    def test_datetime_strftime(self):
        """strftime formats date as string."""
        source = """
from datetime import date
let d = date(2023, 3, 15)
let formatted = d.strftime("%Y-%m-%d")
print(formatted)
"""
        output = _execute(source)
        self.assertIn("2023-03", output)


class ItertoolsModuleTestSuite(unittest.TestCase):
    """Test itertools module functions."""

    def test_itertools_chain(self):
        """itertools.chain concatenates iterables."""
        source = "from itertools import chain\nlet result = list(chain([1, 2], [3, 4]))\nprint(result)"
        output = _execute(source)
        self.assertIn("[1, 2, 3, 4]", output)

    def test_itertools_repeat(self):
        """itertools.repeat repeats element."""
        source = "from itertools import repeat\nlet result = list(repeat(5, 3))\nprint(result)"
        output = _execute(source)
        self.assertIn("[5, 5, 5]", output)

    def test_itertools_combinations(self):
        """itertools.combinations generates combinations."""
        source = "from itertools import combinations\nlet result = list(combinations([1, 2, 3], 2))\nprint(len(result))"
        output = _execute(source)
        self.assertIn("3", output)

    def test_itertools_permutations(self):
        """itertools.permutations generates permutations."""
        source = "from itertools import permutations\nlet result = list(permutations([1, 2, 3], 2))\nprint(len(result))"
        output = _execute(source)
        self.assertIn("6", output)

    def test_itertools_count(self):
        """itertools.count generates infinite sequence."""
        source = "from itertools import count, islice\nlet result = list(islice(count(0, 2), 5))\nprint(result)"
        output = _execute(source)
        self.assertIn("[0, 2, 4, 6, 8]", output)

    def test_itertools_islice(self):
        """itertools.islice slices iterable."""
        source = "from itertools import islice\nlet result = list(islice(range(10), 2, 5))\nprint(result)"
        output = _execute(source)
        self.assertIn("[2, 3, 4]", output)


class PathlibModuleTestSuite(unittest.TestCase):
    """Test pathlib module functions."""

    def test_pathlib_path_creation(self):
        """Create Path object."""
        source = "from pathlib import Path\nlet p = Path('.')\nprint(type(p).__name__)"
        output = _execute(source)
        self.assertIn("Path", output)

    def test_pathlib_path_properties(self):
        """Access Path properties."""
        source = "from pathlib import Path\nlet p = Path('test.txt')\nprint(p.suffix)"
        output = _execute(source)
        self.assertIn(".txt", output)

    def test_pathlib_path_join(self):
        """Join paths."""
        source = "from pathlib import Path\nlet p = Path('dir') / 'file.txt'\nprint(type(p).__name__)"
        output = _execute(source)
        self.assertIn("Path", output)

    def test_pathlib_path_exists(self):
        """Check if path exists."""
        source = "from pathlib import Path\nlet p = Path('.')\nprint(p.exists())"
        output = _execute(source)
        self.assertIn("True", output)

    def test_pathlib_path_is_dir(self):
        """Check if path is directory."""
        source = "from pathlib import Path\nlet p = Path('.')\nprint(p.is_dir())"
        output = _execute(source)
        self.assertIn("True", output)


class CollectionsModuleTestSuite(unittest.TestCase):
    """Test collections module functions."""

    def test_collections_counter(self):
        """Counter counts elements."""
        source = "from collections import Counter\nlet c = Counter([1, 1, 2, 2, 2])\nprint(c[2])"
        output = _execute(source)
        self.assertIn("3", output)

    def test_collections_counter_most_common(self):
        """Counter.most_common returns most frequent."""
        source = "from collections import Counter\nlet c = Counter([1, 1, 2, 2, 2])\nlet mc = c.most_common(1)\nprint(mc[0][0])"
        output = _execute(source)
        self.assertIn("2", output)

    def test_collections_defaultdict(self):
        """defaultdict provides default values."""
        source = """
from collections import defaultdict
let d = defaultdict(list)
d['a'].append(1)
print(len(d['a']))
"""
        output = _execute(source)
        self.assertIn("1", output)

    def test_collections_namedtuple(self):
        """namedtuple creates tuple subclass."""
        source = """
from collections import namedtuple
let Point = namedtuple('Point', ['x', 'y'])
let p = Point(1, 2)
print(p.x)
"""
        output = _execute(source)
        self.assertIn("1", output)

    def test_collections_deque(self):
        """deque provides efficient append/pop."""
        source = """
from collections import deque
let d = deque([1, 2, 3])
d.append(4)
print(len(d))
"""
        output = _execute(source)
        self.assertIn("4", output)


class FunctoolsModuleTestSuite(unittest.TestCase):
    """Test functools module functions."""

    def test_functools_reduce(self):
        """reduce applies function cumulatively."""
        source = "from functools import reduce\nlet result = reduce(lambda x, y: x + y, [1, 2, 3, 4])\nprint(result)"
        output = _execute(source)
        self.assertIn("10", output)

    def test_functools_lru_cache(self):
        """lru_cache memoizes function results."""
        source = """
from functools import lru_cache
@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
print(fib(5))
"""
        output = _execute(source)
        self.assertIn("5", output)

    def test_functools_wraps(self):
        """wraps preserves function metadata."""
        source = """
from functools import wraps
def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
@decorator
def foo():
    pass
print(foo.__name__)
"""
        output = _execute(source)
        self.assertIn("foo", output)

    def test_functools_partial(self):
        """partial creates function with fixed args."""
        source = """
from functools import partial
let add = lambda x, y: x + y
let add5 = partial(add, 5)
print(add5(3))
"""
        output = _execute(source)
        self.assertIn("8", output)


class StdlibInteropTestSuite(unittest.TestCase):
    """Test interoperability between stdlib modules."""

    def test_json_datetime_serialization(self):
        """JSON with datetime objects (custom serialization)."""
        # Note: datetime objects aren't JSON serializable by default
        source = """
import json
from datetime import date
let d = date(2023, 1, 1)
let data = json.dumps({"date": str(d)})
print("2023" in data)
"""
        output = _execute(source)
        self.assertIn("True", output)

    def test_pathlib_json_integration(self):
        """Use pathlib with json files."""
        source = """
import json
from pathlib import Path
let p = Path(".")
let is_path_like = "Path" in type(p).__name__
print(is_path_like)
"""
        output = _execute(source)
        self.assertIn("True", output)

    def test_collections_math_integration(self):
        """Use collections with math functions."""
        source = """
import math
from collections import Counter
let nums = [1, 1, 2, 2, 2, 3, 3, 3, 3]
let counter = Counter(nums)
let mode = counter.most_common(1)[0][0]
print(mode)
"""
        output = _execute(source)
        self.assertIn("3", output)


if __name__ == "__main__":
    unittest.main()
