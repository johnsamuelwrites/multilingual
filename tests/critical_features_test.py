#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for Phase 3.5 critical features."""

import unittest

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_nodes import (
    FunctionDef, ClassDef, Assignment, ExpressionStatement,
    ForLoop, IndexAccess, CallExpr, SliceExpr, Parameter, TupleLiteral,
    ListComprehension, DictComprehension, GeneratorExpr,
    FStringLiteral, StringLiteral, Identifier,
)
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


def _parse(source, language="en"):
    """Helper: tokenize and parse source code."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language)
    return parser.parse()


def _generate(source, language="en"):
    """Helper: parse and generate Python source."""
    prog = _parse(source, language)
    gen = PythonCodeGenerator()
    return gen.generate(prog).strip()


def _execute(source, language="en"):
    """Helper: full execution pipeline."""
    executor = ProgramExecutor(language=language, check_semantics=False)
    return executor.execute(source)


# ======================================================================
# WS1a: Triple-quoted strings
# ======================================================================

class TripleQuotedStringTestSuite(unittest.TestCase):
    """Tests for triple-quoted string support."""

    def test_triple_double_quote(self):
        source = '\"\"\"hello world\"\"\"\n'
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, StringLiteral)
        self.assertEqual(stmt.expression.value, "hello world")

    def test_triple_single_quote(self):
        source = "'''hello world'''\n"
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, StringLiteral)
        self.assertEqual(stmt.expression.value, "hello world")

    def test_triple_quote_multiline(self):
        source = '\"\"\"line1\nline2\nline3\"\"\"\n'
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt.expression, StringLiteral)
        self.assertIn("line1", stmt.expression.value)
        self.assertIn("line2", stmt.expression.value)

    def test_triple_quote_codegen(self):
        source = '\"\"\"hello world\"\"\"\n'
        result = _generate(source)
        self.assertIn("hello world", result)


# ======================================================================
# WS3: Slice syntax
# ======================================================================

class SliceSyntaxTestSuite(unittest.TestCase):
    """Tests for slice syntax support."""

    def test_parse_simple_slice(self):
        source = "a[1:3]\n"
        prog = _parse(source)
        stmt = prog.body[0]
        idx = stmt.expression
        self.assertIsInstance(idx, IndexAccess)
        self.assertIsInstance(idx.index, SliceExpr)
        self.assertIsNotNone(idx.index.start)
        self.assertIsNotNone(idx.index.stop)
        self.assertIsNone(idx.index.step)

    def test_parse_slice_with_step(self):
        source = "a[1:10:2]\n"
        prog = _parse(source)
        idx = prog.body[0].expression
        self.assertIsInstance(idx.index, SliceExpr)
        self.assertIsNotNone(idx.index.step)

    def test_parse_slice_no_start(self):
        source = "a[:5]\n"
        prog = _parse(source)
        idx = prog.body[0].expression
        self.assertIsInstance(idx.index, SliceExpr)
        self.assertIsNone(idx.index.start)
        self.assertIsNotNone(idx.index.stop)

    def test_parse_slice_no_stop(self):
        source = "a[2:]\n"
        prog = _parse(source)
        idx = prog.body[0].expression
        self.assertIsInstance(idx.index, SliceExpr)
        self.assertIsNotNone(idx.index.start)
        self.assertIsNone(idx.index.stop)

    def test_parse_slice_reverse(self):
        source = "a[::-1]\n"
        prog = _parse(source)
        idx = prog.body[0].expression
        self.assertIsInstance(idx.index, SliceExpr)
        self.assertIsNone(idx.index.start)
        self.assertIsNone(idx.index.stop)
        self.assertIsNotNone(idx.index.step)

    def test_codegen_slice(self):
        source = "a[1:3]\n"
        result = _generate(source)
        self.assertEqual(result, "a[1:3]")

    def test_codegen_slice_step(self):
        source = "a[::2]\n"
        result = _generate(source)
        self.assertEqual(result, "a[::2]")

    def test_codegen_slice_reverse(self):
        source = "a[::-1]\n"
        result = _generate(source)
        self.assertIn("::", result)
        self.assertIn("-1", result)

    def test_execute_slice(self):
        source = 'let x = [1, 2, 3, 4, 5]\nprint(x[1:3])\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[2, 3]")

    def test_execute_slice_reverse(self):
        source = 'let x = [1, 2, 3]\nprint(x[::-1])\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[3, 2, 1]")

    def test_execute_string_slice(self):
        source = 'let s = "hello"\nprint(s[1:4])\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "ell")


# ======================================================================
# WS2: Parameter system (defaults, *args, **kwargs)
# ======================================================================

class ParameterSystemTestSuite(unittest.TestCase):
    """Tests for default parameters, *args, and **kwargs."""

    def test_parse_default_param(self):
        source = "def f(x=5):\n    return x\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertIsInstance(func, FunctionDef)
        self.assertEqual(len(func.params), 1)
        param = func.params[0]
        self.assertIsInstance(param, Parameter)
        self.assertEqual(param.name, "x")
        self.assertIsNotNone(param.default)

    def test_parse_mixed_params(self):
        source = "def f(a, b=10, c=20):\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.params), 3)
        self.assertIsNone(func.params[0].default)
        self.assertIsNotNone(func.params[1].default)
        self.assertIsNotNone(func.params[2].default)

    def test_parse_varargs(self):
        source = "def f(*args):\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.params), 1)
        self.assertTrue(func.params[0].is_vararg)
        self.assertEqual(func.params[0].name, "args")

    def test_parse_kwargs(self):
        source = "def f(**kwargs):\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.params), 1)
        self.assertTrue(func.params[0].is_kwarg)
        self.assertEqual(func.params[0].name, "kwargs")

    def test_parse_all_param_types(self):
        source = "def f(a, b=5, *args, **kwargs):\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.params), 4)
        self.assertFalse(func.params[0].is_vararg)
        self.assertIsNotNone(func.params[1].default)
        self.assertTrue(func.params[2].is_vararg)
        self.assertTrue(func.params[3].is_kwarg)

    def test_codegen_default_param(self):
        source = "def f(x=5):\n    return x\n"
        result = _generate(source)
        self.assertIn("def f(x=5):", result)

    def test_codegen_varargs(self):
        source = "def f(*args, **kwargs):\n    pass\n"
        result = _generate(source)
        self.assertIn("def f(*args, **kwargs):", result)

    def test_execute_default_param(self):
        source = "def f(x=10):\n    return x\nprint(f())\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "10")

    def test_execute_default_param_override(self):
        source = "def f(x=10):\n    return x\nprint(f(42))\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "42")

    def test_execute_varargs(self):
        source = "def f(*args):\n    return len(args)\nprint(f(1, 2, 3))\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "3")

    def test_execute_kwargs(self):
        source = "def f(**kwargs):\n    return len(kwargs)\nprint(f(a=1, b=2))\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "2")

    def test_starred_call_args(self):
        source = "def f(a, b, c):\n    print(a + b + c)\nlet args = [1, 2, 3]\nf(*args)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "6")

    def test_double_starred_call_args(self):
        source = 'def f(a=0, b=0):\n    print(a + b)\nlet d = {"a": 3, "b": 7}\nf(**d)\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "10")


# ======================================================================
# WS5: Tuple unpacking
# ======================================================================

class TupleUnpackingTestSuite(unittest.TestCase):
    """Tests for tuple unpacking support."""

    def test_parse_tuple_assignment(self):
        source = "a, b = 1, 2\n"
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertIsInstance(stmt.target, TupleLiteral)
        self.assertEqual(len(stmt.target.elements), 2)

    def test_parse_triple_assignment(self):
        source = "a, b, c = 1, 2, 3\n"
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt.target, TupleLiteral)
        self.assertEqual(len(stmt.target.elements), 3)

    def test_codegen_tuple_assignment(self):
        source = "a, b = 1, 2\n"
        result = _generate(source)
        self.assertIn("a, b", result)

    def test_execute_tuple_unpacking(self):
        source = "a, b = 1, 2\nprint(a)\nprint(b)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        lines = result.output.strip().split("\n")
        self.assertEqual(lines[0], "1")
        self.assertEqual(lines[1], "2")

    def test_execute_tuple_unpacking_list(self):
        source = "a, b, c = [10, 20, 30]\nprint(a + b + c)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "60")

    def test_parse_for_tuple_unpacking(self):
        source = "for a, b in items:\n    pass\n"
        prog = _parse(source)
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ForLoop)
        self.assertIsInstance(stmt.target, TupleLiteral)

    def test_execute_for_tuple_unpacking(self):
        source = (
            "let items = [[1, 2], [3, 4], [5, 6]]\n"
            "let total = 0\n"
            "for a, b in items:\n"
            "    total = total + a + b\n"
            "print(total)\n"
        )
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "21")

    def test_execute_swap(self):
        source = "let a = 1\nlet b = 2\na, b = b, a\nprint(a)\nprint(b)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        lines = result.output.strip().split("\n")
        self.assertEqual(lines[0], "2")
        self.assertEqual(lines[1], "1")


# ======================================================================
# WS4: Comprehensions
# ======================================================================

class ComprehensionTestSuite(unittest.TestCase):
    """Tests for list, dict, and generator comprehensions."""

    def test_parse_list_comprehension(self):
        source = "[x * 2 for x in items]\n"
        prog = _parse(source)
        stmt = prog.body[0]
        expr = stmt.expression
        self.assertIsInstance(expr, ListComprehension)
        self.assertIsNotNone(expr.element)
        self.assertIsNotNone(expr.target)
        self.assertIsNotNone(expr.iterable)

    def test_parse_list_comprehension_with_if(self):
        source = "[x for x in items if x > 0]\n"
        prog = _parse(source)
        expr = prog.body[0].expression
        self.assertIsInstance(expr, ListComprehension)
        self.assertEqual(len(expr.conditions), 1)

    def test_parse_nested_list_comprehension(self):
        source = "[x for row in items for x in row]\n"
        prog = _parse(source)
        expr = prog.body[0].expression
        self.assertIsInstance(expr, ListComprehension)
        self.assertEqual(len(expr.clauses), 2)

    def test_parse_dict_comprehension(self):
        source = "{k: v for k, v in items}\n"
        prog = _parse(source)
        expr = prog.body[0].expression
        self.assertIsInstance(expr, DictComprehension)

    def test_parse_generator_expression(self):
        source = "sum(x for x in items)\n"
        prog = _parse(source)
        call = prog.body[0].expression
        self.assertIsInstance(call, CallExpr)
        self.assertEqual(len(call.args), 1)
        self.assertIsInstance(call.args[0], GeneratorExpr)

    def test_codegen_list_comprehension(self):
        source = "[x * 2 for x in items]\n"
        result = _generate(source)
        self.assertIn("[", result)
        self.assertIn("for", result)
        self.assertIn("in", result)

    def test_codegen_list_comp_with_if(self):
        source = "[x for x in items if x > 0]\n"
        result = _generate(source)
        self.assertIn("if", result)

    def test_codegen_dict_comprehension(self):
        source = "{k: v for k, v in items}\n"
        result = _generate(source)
        self.assertIn("{", result)
        self.assertIn("for", result)

    def test_codegen_nested_list_comprehension(self):
        source = "[x for row in items for x in row]\n"
        result = _generate(source)
        self.assertEqual(result.count(" for "), 2)

    def test_execute_list_comprehension(self):
        source = "let result = [x * 2 for x in range(5)]\nprint(result)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[0, 2, 4, 6, 8]")

    def test_execute_list_comp_with_filter(self):
        source = "let result = [x for x in range(10) if x % 2 == 0]\nprint(result)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[0, 2, 4, 6, 8]")

    def test_execute_dict_comprehension(self):
        source = 'let d = {x: x * x for x in range(4)}\nprint(d)\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertIn("0: 0", result.output)
        self.assertIn("3: 9", result.output)

    def test_execute_generator_sum(self):
        source = "print(sum(x * x for x in range(5)))\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "30")

    def test_execute_nested_comp(self):
        source = "let flat = [x for row in [[1, 2], [3, 4]] for x in row]\nprint(flat)\n"
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[1, 2, 3, 4]")


# ======================================================================
# WS6: Decorators
# ======================================================================

class DecoratorTestSuite(unittest.TestCase):
    """Tests for decorator support."""

    def test_parse_simple_decorator(self):
        source = "@mydecorator\ndef f():\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertIsInstance(func, FunctionDef)
        self.assertEqual(len(func.decorators), 1)

    def test_parse_decorator_with_args(self):
        source = "@mydecorator(arg1, arg2)\ndef f():\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.decorators), 1)
        self.assertIsInstance(func.decorators[0], CallExpr)

    def test_parse_multiple_decorators(self):
        source = "@dec1\n@dec2\ndef f():\n    pass\n"
        prog = _parse(source)
        func = prog.body[0]
        self.assertEqual(len(func.decorators), 2)

    def test_parse_class_decorator(self):
        source = "@mydecorator\nclass Foo:\n    pass\n"
        prog = _parse(source)
        cls = prog.body[0]
        self.assertIsInstance(cls, ClassDef)
        self.assertEqual(len(cls.decorators), 1)

    def test_codegen_decorator(self):
        source = "@mydecorator\ndef f():\n    pass\n"
        result = _generate(source)
        self.assertIn("@mydecorator", result)
        self.assertIn("def f():", result)

    def test_codegen_decorator_with_args(self):
        source = "@mydecorator(1, 2)\ndef f():\n    pass\n"
        result = _generate(source)
        self.assertIn("@mydecorator(1, 2)", result)

    def test_execute_decorator(self):
        source = (
            "def double_result(func):\n"
            "    def wrapper(*args, **kwargs):\n"
            "        return func(*args, **kwargs) * 2\n"
            "    return wrapper\n"
            "@double_result\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "print(add(3, 4))\n"
        )
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "14")


# ======================================================================
# WS1b: F-strings
# ======================================================================

class FStringTestSuite(unittest.TestCase):
    """Tests for f-string support."""

    def test_parse_fstring_simple(self):
        source = 'f"hello {name}"\n'
        prog = _parse(source)
        stmt = prog.body[0]
        expr = stmt.expression
        self.assertIsInstance(expr, FStringLiteral)
        self.assertEqual(len(expr.parts), 2)
        self.assertEqual(expr.parts[0], "hello ")
        self.assertIsInstance(expr.parts[1], Identifier)

    def test_parse_fstring_multiple_exprs(self):
        source = 'f"{a} + {b} = {c}"\n'
        prog = _parse(source)
        expr = prog.body[0].expression
        self.assertIsInstance(expr, FStringLiteral)
        # parts: expr, " + ", expr, " = ", expr
        self.assertEqual(len(expr.parts), 5)

    def test_parse_fstring_no_exprs(self):
        source = 'f"plain text"\n'
        prog = _parse(source)
        expr = prog.body[0].expression
        self.assertIsInstance(expr, FStringLiteral)
        self.assertEqual(len(expr.parts), 1)
        self.assertEqual(expr.parts[0], "plain text")

    def test_codegen_fstring(self):
        source = 'f"hello {name}"\n'
        result = _generate(source)
        self.assertIn('f"', result)
        self.assertIn("{name}", result)

    def test_execute_fstring(self):
        source = 'let name = "world"\nprint(f"hello {name}")\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "hello world")

    def test_execute_fstring_expr(self):
        source = 'let x = 5\nprint(f"result: {x * 2}")\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "result: 10")

    def test_execute_fstring_multiple(self):
        source = 'let a = 3\nlet b = 4\nprint(f"{a} + {b} = {a + b}")\n'
        result = _execute(source)
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "3 + 4 = 7")


# ======================================================================
# Integration: multilingual execution of new features
# ======================================================================

class MultilingualCriticalFeaturesTestSuite(unittest.TestCase):
    """Tests for critical features across multiple languages."""

    def test_french_list_comprehension(self):
        reg = KeywordRegistry()
        kw_for = reg.get_keyword("LOOP_FOR", "fr")
        kw_in = reg.get_keyword("IN", "fr")
        kw_let = reg.get_keyword("LET", "fr")
        kw_print = reg.get_keyword("PRINT", "fr")
        source = f"{kw_let} result = [x * 2 {kw_for} x {kw_in} range(5)]\n{kw_print}(result)\n"
        result = _execute(source, language="fr")
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[0, 2, 4, 6, 8]")

    def test_french_default_params(self):
        reg = KeywordRegistry()
        kw_def = reg.get_keyword("FUNC_DEF", "fr")
        kw_return = reg.get_keyword("RETURN", "fr")
        kw_print = reg.get_keyword("PRINT", "fr")
        source = f"{kw_def} f(x=10):\n    {kw_return} x\n{kw_print}(f())\n"
        result = _execute(source, language="fr")
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "10")

    def test_french_slice(self):
        reg = KeywordRegistry()
        kw_let = reg.get_keyword("LET", "fr")
        kw_print = reg.get_keyword("PRINT", "fr")
        source = f"{kw_let} x = [1, 2, 3, 4, 5]\n{kw_print}(x[1:3])\n"
        result = _execute(source, language="fr")
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "[2, 3]")

    def test_hindi_tuple_unpacking(self):
        reg = KeywordRegistry()
        kw_print = reg.get_keyword("PRINT", "hi")
        source = f"a, b = 1, 2\n{kw_print}(a + b)\n"
        result = _execute(source, language="hi")
        self.assertTrue(result.success)
        self.assertEqual(result.output.strip(), "3")
