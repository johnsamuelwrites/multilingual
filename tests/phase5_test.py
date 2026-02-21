#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for Phase 5: Advanced Language Features."""

import json
import unittest
from pathlib import Path

from multilingualprogramming import (
    Lexer, Parser, PythonCodeGenerator,
    ProgramExecutor,
)
from multilingualprogramming.parser.ast_nodes import (
    WhileLoop, ForLoop, RaiseStatement, YieldStatement,
    SetComprehension, MatchStatement, FromImportStatement, FunctionDef,
)
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.parser.surface_normalizer import (
    SurfaceNormalizer, validate_surface_patterns_config,
)


def _parse(source, lang="en"):
    tokens = Lexer(source, language=lang).tokenize()
    return Parser(tokens, source_language=lang).parse()


def _generate(source, lang="en"):
    program = _parse(source, lang)
    return PythonCodeGenerator().generate(program)


def _execute(source, lang="en", check_semantics=True):
    return ProgramExecutor(
        language=lang, check_semantics=check_semantics
    ).execute(source)


# ---------------------------------------------------------------
# Tier 1: While/For else
# ---------------------------------------------------------------

class WhileElseTestSuite(unittest.TestCase):
    """Test while...else loops."""

    def test_while_else_parse(self):
        src = "let x = 0\nwhile x < 3:\n    x += 1\nelse:\n    print(x)\n"
        program = _parse(src)
        while_node = program.body[1]
        self.assertIsInstance(while_node, WhileLoop)
        self.assertIsNotNone(while_node.else_body)

    def test_while_else_codegen(self):
        src = "let x = 0\nwhile x < 3:\n    x += 1\nelse:\n    print(x)\n"
        code = _generate(src)
        self.assertIn("while", code)
        self.assertIn("else:", code)

    def test_while_else_executes(self):
        src = (
            "let x = 0\n"
            "while x < 3:\n"
            "    x += 1\n"
            "else:\n"
            "    print(x)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3")

    def test_while_no_else(self):
        src = "let x = 0\nwhile x < 1:\n    x += 1\n"
        program = _parse(src)
        while_node = program.body[1]
        self.assertIsNone(while_node.else_body)


class ForElseTestSuite(unittest.TestCase):
    """Test for...else loops."""

    def test_for_else_parse(self):
        src = "for i in range(3):\n    pass\nelse:\n    print(42)\n"
        program = _parse(src)
        for_node = program.body[0]
        self.assertIsInstance(for_node, ForLoop)
        self.assertIsNotNone(for_node.else_body)

    def test_for_else_codegen(self):
        src = "for i in range(3):\n    pass\nelse:\n    print(42)\n"
        code = _generate(src)
        self.assertIn("for i in range(3):", code)
        self.assertIn("else:", code)

    def test_for_else_executes(self):
        src = (
            "for i in range(3):\n"
            "    pass\n"
            "else:\n"
            "    print(42)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "42")

    def test_for_no_else(self):
        src = "for i in range(3):\n    pass\n"
        program = _parse(src)
        for_node = program.body[0]
        self.assertIsNone(for_node.else_body)


# ---------------------------------------------------------------
# Tier 1: Yield from
# ---------------------------------------------------------------

class YieldFromTestSuite(unittest.TestCase):
    """Test yield from syntax."""

    def test_yield_from_statement_parse(self):
        src = "def gen():\n    yield from range(3)\n"
        program = _parse(src, lang="en")
        func = program.body[0]
        yield_stmt = func.body[0]
        self.assertIsInstance(yield_stmt, YieldStatement)
        self.assertTrue(yield_stmt.is_from)

    def test_yield_from_codegen(self):
        src = "def gen():\n    yield from range(3)\n"
        code = _generate(src)
        self.assertIn("yield from", code)

    def test_yield_from_executes(self):
        src = (
            "def gen():\n"
            "    yield from range(3)\n"
            "let result = list(gen())\n"
            "print(result)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[0, 1, 2]")

    def test_yield_without_from(self):
        src = "def gen():\n    yield 42\n"
        program = _parse(src)
        func = program.body[0]
        yield_stmt = func.body[0]
        self.assertFalse(yield_stmt.is_from)


# ---------------------------------------------------------------
# Tier 1: Raise from
# ---------------------------------------------------------------

class RaiseFromTestSuite(unittest.TestCase):
    """Test raise X from Y syntax."""

    def test_raise_from_parse(self):
        src = (
            "try:\n"
            "    raise ValueError(\"a\") from TypeError(\"b\")\n"
            "except ValueError:\n"
            "    print(\"caught\")\n"
        )
        program = _parse(src)
        try_stmt = program.body[0]
        raise_stmt = try_stmt.body[0]
        self.assertIsInstance(raise_stmt, RaiseStatement)
        self.assertIsNotNone(raise_stmt.cause)

    def test_raise_from_codegen(self):
        src = (
            "try:\n"
            "    raise ValueError(\"a\") from TypeError(\"b\")\n"
            "except ValueError:\n"
            "    pass\n"
        )
        code = _generate(src)
        self.assertIn("from", code)
        self.assertIn("TypeError", code)

    def test_raise_from_executes(self):
        src = (
            "try:\n"
            "    raise ValueError(\"a\") from TypeError(\"b\")\n"
            "except ValueError as e:\n"
            "    print(type(e.__cause__).__name__)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "TypeError")


# ---------------------------------------------------------------
# Tier 1: From import *
# ---------------------------------------------------------------

class FromImportStarTestSuite(unittest.TestCase):
    """Test from module import * syntax."""

    def test_from_import_star_parse(self):
        src = "from os import *\n"
        program = _parse(src)
        imp = program.body[0]
        self.assertIsInstance(imp, FromImportStatement)
        self.assertEqual(imp.names, [("*", None)])

    def test_from_import_star_codegen(self):
        src = "from os import *\n"
        code = _generate(src)
        self.assertIn("from os import *", code)


# ---------------------------------------------------------------
# Tier 1: Set comprehension
# ---------------------------------------------------------------

class SetComprehensionTestSuite(unittest.TestCase):
    """Test set comprehension syntax."""

    def test_set_comprehension_parse(self):
        src = "let s = {x * x for x in range(5)}\n"
        program = _parse(src)
        decl = program.body[0]
        self.assertIsInstance(decl.value, SetComprehension)

    def test_set_comprehension_codegen(self):
        src = "let s = {x * x for x in range(5)}\n"
        code = _generate(src)
        self.assertIn("{", code)
        self.assertIn("for x in range(5)", code)

    def test_set_comprehension_executes(self):
        src = (
            "let s = {x * x for x in range(5)}\n"
            "print(sorted(s))\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[0, 1, 4, 9, 16]")

    def test_set_comprehension_with_condition(self):
        src = (
            "let s = {x for x in range(10) if x % 2 == 0}\n"
            "print(sorted(s))\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[0, 2, 4, 6, 8]")


# ---------------------------------------------------------------
# Tier 1: Positional-only and keyword-only parameters
# ---------------------------------------------------------------

class ParameterSeparatorTestSuite(unittest.TestCase):
    """Test positional-only (/) and keyword-only (*) parameter separators."""

    def test_positional_only_parse(self):
        src = "def f(a, b, /, c):\n    pass\n"
        program = _parse(src)
        func = program.body[0]
        self.assertIsInstance(func, FunctionDef)
        names = [p.name for p in func.params]
        self.assertIn("/", names)

    def test_keyword_only_parse(self):
        src = "def f(a, *, b):\n    pass\n"
        program = _parse(src)
        func = program.body[0]
        names = [p.name for p in func.params]
        self.assertIn("*", names)

    def test_positional_only_codegen(self):
        src = "def f(a, b, /, c):\n    pass\n"
        code = _generate(src)
        self.assertIn("/", code)

    def test_keyword_only_codegen(self):
        src = "def f(a, *, b):\n    pass\n"
        code = _generate(src)
        self.assertIn("*", code)

    def test_positional_only_executes(self):
        src = (
            "def f(a, b, /, c):\n"
            "    return a + b + c\n"
            "print(f(1, 2, c=3))\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "6")

    def test_keyword_only_executes(self):
        src = (
            "def f(a, *, b):\n"
            "    return a + b\n"
            "print(f(1, b=2))\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3")


# ---------------------------------------------------------------
# Tier 1: F-string format specs and conversions
# ---------------------------------------------------------------

class FStringFormatTestSuite(unittest.TestCase):
    """Test f-string format specs and conversions."""

    def test_fstring_format_spec_codegen(self):
        src = 'let x = 3.14159\nlet s = f"{x:.2f}"\n'
        code = _generate(src)
        self.assertIn(":.2f", code)

    def test_fstring_conversion_codegen(self):
        src = 'let s = f"{42!r}"\n'
        code = _generate(src)
        self.assertIn("!r", code)

    def test_fstring_format_spec_executes(self):
        src = 'let x = 3.14159\nprint(f"{x:.2f}")\n'
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3.14")

    def test_fstring_conversion_r_executes(self):
        src = 'let s = "hello"\nprint(f"{s!r}")\n'
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "'hello'")

    def test_fstring_conversion_s_executes(self):
        src = 'print(f"{42!s}")\n'
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "42")


# ---------------------------------------------------------------
# Tier 2: Match/case guard clauses
# ---------------------------------------------------------------

class MatchGuardTestSuite(unittest.TestCase):
    """Test match/case with guard clauses."""

    def test_guard_parse(self):
        src = (
            "match x:\n"
            "    case 1 if x > 0:\n"
            "        pass\n"
        )
        program = _parse(src)
        match_stmt = program.body[0]
        self.assertIsInstance(match_stmt, MatchStatement)
        case = match_stmt.cases[0]
        self.assertIsNotNone(case.guard)

    def test_guard_codegen(self):
        src = (
            "match x:\n"
            "    case 1 if x > 0:\n"
            "        pass\n"
        )
        code = _generate(src)
        self.assertIn("case 1 if", code)

    def test_guard_executes(self):
        src = (
            "let x = 5\n"
            "match x:\n"
            "    case n if n > 3:\n"
            "        print(\"big\")\n"
            "    case n:\n"
            "        print(\"small\")\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "big")


# ---------------------------------------------------------------
# Tier 2: Match/case OR patterns
# ---------------------------------------------------------------

class MatchOrPatternTestSuite(unittest.TestCase):
    """Test match/case OR patterns with |."""

    def test_or_pattern_parse(self):
        src = (
            "match x:\n"
            "    case 1 | 2 | 3:\n"
            "        pass\n"
        )
        program = _parse(src)
        match_stmt = program.body[0]
        case = match_stmt.cases[0]
        self.assertIsNotNone(case.pattern)

    def test_or_pattern_codegen(self):
        src = (
            "match x:\n"
            "    case 1 | 2 | 3:\n"
            "        pass\n"
        )
        code = _generate(src)
        self.assertIn("1 | 2", code)
        self.assertIn("| 3", code)

    def test_or_pattern_executes(self):
        src = (
            "let x = 2\n"
            "match x:\n"
            "    case 1 | 2 | 3:\n"
            "        print(\"matched\")\n"
            "    case _:\n"
            "        print(\"no\")\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "matched")


# ---------------------------------------------------------------
# Tier 2: Match/case AS binding
# ---------------------------------------------------------------

class MatchAsPatternTestSuite(unittest.TestCase):
    """Test match/case AS binding."""

    def test_as_pattern_codegen(self):
        src = (
            "match x:\n"
            "    case 1 | 2 as val:\n"
            "        pass\n"
        )
        code = _generate(src)
        self.assertIn("as", code)
        self.assertIn("val", code)

    def test_as_pattern_executes(self):
        src = (
            "let x = 2\n"
            "match x:\n"
            "    case 1 | 2 as val:\n"
            "        print(val)\n"
            "    case _:\n"
            "        print(\"no\")\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "2")


# ---------------------------------------------------------------
# Tier 3: Global/nonlocal semantic fix
# ---------------------------------------------------------------

class GlobalNonlocalSemanticTestSuite(unittest.TestCase):
    """Test that global/nonlocal statements properly define names in scope."""

    def test_global_no_undefined_error(self):
        src = (
            "let x = 10\n"
            "def f():\n"
            "    global x\n"
            "    x = 20\n"
            "f()\n"
            "print(x)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "20")

    def test_nonlocal_no_undefined_error(self):
        src = (
            "def outer():\n"
            "    let x = 10\n"
            "    def inner():\n"
            "        nonlocal x\n"
            "        x = 20\n"
            "    inner()\n"
            "    print(x)\n"
            "outer()\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "20")


# ---------------------------------------------------------------
# Tier 4: Runtime builtins — additional functions
# ---------------------------------------------------------------

class AdditionalBuiltinsTestSuite(unittest.TestCase):
    """Test additional built-in functions in runtime namespace."""

    def test_pow_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("pow", ns)
        self.assertEqual(ns["pow"](2, 3), 8)

    def test_divmod_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("divmod", ns)
        self.assertEqual(ns["divmod"](17, 5), (3, 2))

    def test_complex_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("complex", ns)
        self.assertEqual(ns["complex"](1, 2), (1+2j))

    def test_format_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("format", ns)
        self.assertEqual(ns["format"](3.14, ".1f"), "3.1")

    def test_ascii_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("ascii", ns)

    def test_slice_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("slice", ns)

    def test_issubclass_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("issubclass", ns)
        self.assertTrue(ns["issubclass"](bool, int))

    def test_delattr_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("delattr", ns)


# ---------------------------------------------------------------
# Tier 4: Runtime builtins — exception types
# ---------------------------------------------------------------

class ExceptionTypesTestSuite(unittest.TestCase):
    """Test exception types in runtime namespace."""

    def test_arithmetic_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["ArithmeticError"], ArithmeticError)

    def test_assertion_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["AssertionError"], AssertionError)

    def test_eof_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["EOFError"], EOFError)

    def test_permission_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["PermissionError"], PermissionError)

    def test_recursion_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["RecursionError"], RecursionError)

    def test_timeout_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["TimeoutError"], TimeoutError)

    def test_unicode_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["UnicodeError"], UnicodeError)

    def test_stop_async_iteration(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["StopAsyncIteration"], StopAsyncIteration)


# ---------------------------------------------------------------
# Tier 4: Runtime builtins — special values
# ---------------------------------------------------------------

class SpecialValuesTestSuite(unittest.TestCase):
    """Test Ellipsis and NotImplemented in namespace."""

    def test_ellipsis_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("Ellipsis", ns)
        self.assertIs(ns["Ellipsis"], Ellipsis)

    def test_not_implemented_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("NotImplemented", ns)
        self.assertIs(ns["NotImplemented"], NotImplemented)


# ---------------------------------------------------------------
# Tier 5: Surface normalization — new templates
# ---------------------------------------------------------------

class SurfaceNormalizationTestSuite(unittest.TestCase):
    """Test surface pattern normalization for while/if/with."""

    def _reload_surface_patterns(self):
        setattr(SurfaceNormalizer, "_patterns", None)
        setattr(SurfaceNormalizer, "_templates", None)
        return getattr(SurfaceNormalizer, "_load_patterns")()

    def test_patterns_validate(self):
        """All surface patterns should pass schema validation."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "surface_patterns.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            config = json.load(f)
        # Should not raise
        validate_surface_patterns_config(config)

    def test_while_template_exists(self):
        self._reload_surface_patterns()
        templates = getattr(SurfaceNormalizer, "_templates")
        self.assertIn("while_condition_first", templates)

    def test_if_template_exists(self):
        self._reload_surface_patterns()
        templates = getattr(SurfaceNormalizer, "_templates")
        self.assertIn("if_condition_first", templates)

    def test_with_template_exists(self):
        self._reload_surface_patterns()
        templates = getattr(SurfaceNormalizer, "_templates")
        self.assertIn("with_expr_first", templates)

    def test_ja_while_pattern_exists(self):
        patterns = self._reload_surface_patterns()
        names = [p["name"] for p in patterns]
        self.assertIn("ja_while_condition_first", names)

    def test_ar_if_pattern_exists(self):
        patterns = self._reload_surface_patterns()
        names = [p["name"] for p in patterns]
        self.assertIn("ar_if_condition_first", names)

    def test_ar_with_pattern_exists(self):
        patterns = self._reload_surface_patterns()
        names = [p["name"] for p in patterns]
        self.assertIn("ar_with_expr_first", names)


# ---------------------------------------------------------------
# Tier 6: Data quality — Arabic TYPE_INT and Danish sum alias
# ---------------------------------------------------------------

class DataQualityTestSuite(unittest.TestCase):
    """Test data quality fixes for keywords and aliases."""

    def test_arabic_type_int_not_placeholder(self):
        """Arabic TYPE_INT should not be a placeholder."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "keywords.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        # Find TYPE_INT
        type_int = data["categories"]["types"]["TYPE_INT"]
        ar_val = type_int["ar"]
        self.assertNotEqual(ar_val, "???_????")
        self.assertTrue(len(ar_val) > 0)

    def test_arabic_type_int_no_ambiguity_with_true(self):
        """Arabic TYPE_INT must differ from TRUE."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "keywords.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        type_int_ar = data["categories"]["types"]["TYPE_INT"]["ar"]
        true_ar = data["categories"]["logical"]["TRUE"]["ar"]
        self.assertNotEqual(type_int_ar, true_ar)

    def test_danish_sum_alias_exists(self):
        """Danish should have a sum alias."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "builtins_aliases.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        sum_aliases = data["aliases"]["sum"]
        self.assertIn("da", sum_aliases)
        self.assertIsInstance(sum_aliases["da"], list)
        self.assertTrue(len(sum_aliases["da"]) > 0)


# ---------------------------------------------------------------
# Integration tests: end-to-end execution
# ---------------------------------------------------------------

class Phase5IntegrationTestSuite(unittest.TestCase):
    """End-to-end integration tests for all Phase 5 features."""

    def test_while_else_break_skips_else(self):
        src = (
            "let x = 0\n"
            "while x < 10:\n"
            "    if x == 5:\n"
            "        break\n"
            "    x += 1\n"
            "else:\n"
            "    print(\"completed\")\n"
            "print(x)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        # break should skip else, only x is printed
        self.assertEqual(r.output.strip(), "5")

    def test_for_else_break_skips_else(self):
        src = (
            "for i in range(5):\n"
            "    if i == 3:\n"
            "        break\n"
            "else:\n"
            "    print(\"completed\")\n"
            "print(i)\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3")

    def test_for_else_no_break(self):
        src = (
            "for i in range(3):\n"
            "    pass\n"
            "else:\n"
            "    print(\"done\")\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "done")

    def test_set_comprehension_nested(self):
        src = (
            "let s = {a * 10 + b for a in range(2) for b in range(2)}\n"
            "print(sorted(s))\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[0, 1, 10, 11]")

    def test_match_combined_or_and_guard(self):
        src = (
            "let x = 4\n"
            "match x:\n"
            "    case 1 | 2 | 3:\n"
            "        print(\"small\")\n"
            "    case n if n > 3:\n"
            "        print(\"big\")\n"
            "    case _:\n"
            "        print(\"other\")\n"
        )
        r = _execute(src, check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "big")

    def test_fstring_combined_conversion_and_format(self):
        src = 'let x = 3.14\nprint(f"{x!s}")\n'
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3.14")

    def test_raise_from_none(self):
        src = (
            "try:\n"
            "    raise ValueError(\"a\") from None\n"
            "except ValueError as e:\n"
            "    print(e.__cause__)\n"
        )
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "None")

    def test_pow_executes(self):
        src = "print(pow(2, 10))\n"
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "1024")

    def test_divmod_executes(self):
        src = "print(divmod(17, 5))\n"
        r = _execute(src)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "(3, 2)")


# ---------------------------------------------------------------
# Multilingual tests
# ---------------------------------------------------------------

class MultilingualPhase5TestSuite(unittest.TestCase):
    """Test Phase 5 features in non-English languages."""

    def test_french_while_else(self):
        src = (
            "soit x = 0\n"
            "tantque x < 3:\n"
            "    x += 1\n"
            "sinon:\n"
            "    afficher(x)\n"
        )
        r = _execute(src, lang="fr")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3")

    def test_french_for_else(self):
        src = (
            "pour i dans intervalle(3):\n"
            "    passer\n"
            "sinon:\n"
            "    afficher(42)\n"
        )
        r = _execute(src, lang="fr")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "42")

    def test_german_set_comprehension(self):
        src = (
            "sei s = {x * x für x in bereich(5)}\n"
            "ausgeben(sorted(s))\n"
        )
        r = _execute(src, lang="de")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[0, 1, 4, 9, 16]")

    def test_spanish_for_else(self):
        src = (
            "para i en rango(3):\n"
            "    pasar\n"
            "sino:\n"
            "    imprimir(42)\n"
        )
        r = _execute(src, lang="es")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "42")


# ---------------------------------------------------------------
# Extended builtins: new entries in _UNIVERSAL_BUILTINS
# ---------------------------------------------------------------

class ExtendedBuiltinsTestSuite(unittest.TestCase):
    """Test newly added builtins in runtime namespace (Phase 5.5)."""

    def test_base_exception_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["BaseException"], BaseException)

    def test_keyboard_interrupt_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["KeyboardInterrupt"], KeyboardInterrupt)

    def test_module_not_found_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["ModuleNotFoundError"], ModuleNotFoundError)

    def test_indentation_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["IndentationError"], IndentationError)

    def test_tab_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["TabError"], TabError)

    def test_unicode_translate_error(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["UnicodeTranslateError"], UnicodeTranslateError)

    def test_exception_group(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["ExceptionGroup"], ExceptionGroup)

    def test_base_exception_group(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["BaseExceptionGroup"], BaseExceptionGroup)

    def test_bytes_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["BytesWarning"], BytesWarning)

    def test_encoding_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["EncodingWarning"], EncodingWarning)

    def test_import_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["ImportWarning"], ImportWarning)

    def test_pending_deprecation_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(
            ns["PendingDeprecationWarning"], PendingDeprecationWarning
        )

    def test_runtime_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["RuntimeWarning"], RuntimeWarning)

    def test_syntax_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["SyntaxWarning"], SyntaxWarning)

    def test_unicode_warning(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["UnicodeWarning"], UnicodeWarning)

    def test_aiter_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["aiter"], aiter)

    def test_anext_in_namespace(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIs(ns["anext"], anext)


# ---------------------------------------------------------------
# Extended aliases: multilingual alias resolution
# ---------------------------------------------------------------

class ExtendedAliasResolutionTestSuite(unittest.TestCase):
    """Test that new builtin aliases resolve correctly per language."""

    def test_french_sorted_alias(self):
        ns = RuntimeBuiltins("fr").namespace()
        # French alias for sorted
        found = any(
            v is sorted for k, v in ns.items()
            if k not in ("sorted",) and v is sorted
        )
        self.assertTrue(found, "French sorted alias not found")

    def test_french_enumerate_alias(self):
        ns = RuntimeBuiltins("fr").namespace()
        found = any(
            v is enumerate for k, v in ns.items()
            if k not in ("enumerate",) and v is enumerate
        )
        self.assertTrue(found, "French enumerate alias not found")

    def test_german_filter_alias(self):
        ns = RuntimeBuiltins("de").namespace()
        found = any(
            v is filter for k, v in ns.items()
            if k not in ("filter",) and v is filter
        )
        self.assertTrue(found, "German filter alias not found")

    def test_spanish_isinstance_alias(self):
        ns = RuntimeBuiltins("es").namespace()
        found = any(
            v is isinstance for k, v in ns.items()
            if k not in ("isinstance",) and v is isinstance
        )
        self.assertTrue(found, "Spanish isinstance alias not found")

    def test_hindi_input_alias(self):
        ns = RuntimeBuiltins("hi").namespace()
        found = any(
            v is input for k, v in ns.items()
            if k not in ("input",) and v is input
        )
        self.assertTrue(found, "Hindi input alias not found")

    def test_chinese_type_alias(self):
        ns = RuntimeBuiltins("zh").namespace()
        found = any(
            v is type for k, v in ns.items()
            if k not in ("type",) and v is type
        )
        self.assertTrue(found, "Chinese type alias not found")

    def test_japanese_map_alias(self):
        ns = RuntimeBuiltins("ja").namespace()
        found = any(
            v is map for k, v in ns.items()
            if k not in ("map",) and v is map
        )
        self.assertTrue(found, "Japanese map alias not found")

    def test_all_16_languages_have_sorted_alias(self):
        """Every non-English language should have a sorted alias."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "builtins_aliases.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        sorted_aliases = data["aliases"]["sorted"]
        langs = [
            "fr", "es", "de", "it", "pt", "hi", "ar", "bn",
            "ta", "zh", "ja", "pl", "nl", "sv", "da", "fi",
        ]
        for lang in langs:
            self.assertIn(lang, sorted_aliases, f"Missing sorted alias for {lang}")

    def test_alias_count_at_least_41(self):
        """builtins_aliases.json should have at least 41 aliased builtins."""
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources" / "usm"
            / "builtins_aliases.json"
        )
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        self.assertGreaterEqual(len(data["aliases"]), 41)


# ---------------------------------------------------------------
# Extended aliases: execution tests (use aliases in real programs)
# ---------------------------------------------------------------

class ExtendedAliasExecutionTestSuite(unittest.TestCase):
    """Test that alias-named builtins execute correctly in programs."""

    def test_french_sorted_executes(self):
        src = (
            "soit s = trier([3, 1, 2])\n"
            "afficher(s)\n"
        )
        r = _execute(src, lang="fr", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[1, 2, 3]")

    def test_french_enumerate_executes(self):
        src = (
            "pour i, v dans enumerer([10, 20]):\n"
            "    afficher(i, v)\n"
        )
        r = _execute(src, lang="fr", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        lines = r.output.strip().split("\n")
        self.assertEqual(lines[0].strip(), "0 10")
        self.assertEqual(lines[1].strip(), "1 20")

    def test_french_any_all_executes(self):
        src = (
            "afficher(un_quelconque([Faux, Vrai, Faux]))\n"
            "afficher(tous([Vrai, Vrai, Vrai]))\n"
        )
        r = _execute(src, lang="fr", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        lines = r.output.strip().split("\n")
        self.assertEqual(lines[0].strip(), "True")
        self.assertEqual(lines[1].strip(), "True")

    def test_spanish_reversed_executes(self):
        src = (
            "sea s = lista(invertido([1, 2, 3]))\n"
            "imprimir(s)\n"
        )
        r = _execute(src, lang="es", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "[3, 2, 1]")

    def test_german_isinstance_executes(self):
        src = (
            'ausgeben(ist_instanz(42, int))\n'
            'ausgeben(ist_instanz("hi", int))\n'
        )
        r = _execute(src, lang="de", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        lines = r.output.strip().split("\n")
        self.assertEqual(lines[0].strip(), "True")
        self.assertEqual(lines[1].strip(), "False")

    def test_french_map_filter_executes(self):
        src = (
            "soit nums = liste(appliquer(lambda x: x * 2, [1, 2, 3]))\n"
            "afficher(nums)\n"
            "soit evens = liste(filtrer(lambda x: x > 3, nums))\n"
            "afficher(evens)\n"
        )
        r = _execute(src, lang="fr", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        lines = r.output.strip().split("\n")
        self.assertEqual(lines[0].strip(), "[2, 4, 6]")
        self.assertEqual(lines[1].strip(), "[4, 6]")

    def test_french_round_executes(self):
        src = "afficher(arrondir(3.14159, 2))\n"
        r = _execute(src, lang="fr", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "3.14")

    def test_spanish_pow_executes(self):
        src = "imprimir(potencia(2, 10))\n"
        r = _execute(src, lang="es", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.output.strip(), "1024")

    def test_chinese_len_range_executes(self):
        src = (
            "打印(长度([1, 2, 3]))\n"
            "打印(列表(范围(4)))\n"
        )
        r = _execute(src, lang="zh", check_semantics=False)
        self.assertTrue(r.success, r.errors)
        lines = r.output.strip().split("\n")
        self.assertEqual(lines[0].strip(), "3")
        self.assertEqual(lines[1].strip(), "[0, 1, 2, 3]")


if __name__ == "__main__":
    unittest.main()
