#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for language completeness and CLI behavior."""

# pylint: disable=duplicate-code

import unittest
from argparse import Namespace
from unittest.mock import patch

from multilingualprogramming import (
    Lexer, Parser, PythonCodeGenerator,
    ProgramExecutor, REPL,
)
import multilingualprogramming.__main__ as main_module
from multilingualprogramming.__main__ import cmd_compile, cmd_run, cmd_smoke
from multilingualprogramming.parser.ast_nodes import (
    ConditionalExpr, CompareOp, AssertStatement,
    ChainedAssignment, Assignment,
)
from multilingualprogramming.keyword.language_pack_validator import (
    LanguagePackValidator,
)


def _parse(source, lang="en"):
    tokens = Lexer(source, language=lang).tokenize()
    return Parser(tokens, source_language=lang).parse()


def _generate(source, lang="en"):
    program = _parse(source, lang)
    return PythonCodeGenerator().generate(program)


def _execute(source, lang="en", check_semantics=True):
    return ProgramExecutor(language=lang, check_semantics=check_semantics).execute(source)


# ---------------------------------------------------------------
# WS1: Augmented assignment operators
# ---------------------------------------------------------------

class AugmentedAssignmentTestSuite(unittest.TestCase):
    """Test augmented assignment operators beyond +=, -=, *=, /=."""

    def test_power_assign(self):
        r = _execute("let x = 3\nx **= 2\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "9")

    def test_floor_div_assign(self):
        r = _execute("let x = 17\nx //= 5\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "3")

    def test_mod_assign(self):
        r = _execute("let x = 17\nx %= 5\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "2")

    def test_bitwise_and_assign(self):
        r = _execute("let x = 15\nx &= 10\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "10")

    def test_bitwise_or_assign(self):
        r = _execute("let x = 10\nx |= 5\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "15")

    def test_bitwise_xor_assign(self):
        r = _execute("let x = 15\nx ^= 10\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "5")

    def test_left_shift_assign(self):
        r = _execute("let x = 1\nx <<= 4\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "16")

    def test_right_shift_assign(self):
        r = _execute("let x = 16\nx >>= 2\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "4")

    def test_codegen_power_assign(self):
        code = _generate("let x = 2\nx **= 3\n")
        self.assertIn("**=", code)


# ---------------------------------------------------------------
# WS2: in / not in / is / is not operators
# ---------------------------------------------------------------

class MembershipIdentityTestSuite(unittest.TestCase):
    """Test in, not in, is, is not operators."""

    def test_in_list(self):
        r = _execute("print(3 in [1, 2, 3])\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_not_in_list(self):
        r = _execute("print(4 not in [1, 2, 3])\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_in_string(self):
        r = _execute('print("el" in "hello")\n')
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_is_none(self):
        r = _execute("print(None is None)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_is_not_none(self):
        r = _execute('print("hello" is not None)\n')
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_parse_in_produces_compare_op(self):
        prog = _parse("x in items\n")
        stmt = prog.body[0].expression
        self.assertIsInstance(stmt, CompareOp)
        self.assertEqual(stmt.comparators[0][0], "in")

    def test_parse_not_in_produces_compare_op(self):
        prog = _parse("x not in items\n")
        stmt = prog.body[0].expression
        self.assertIsInstance(stmt, CompareOp)
        self.assertEqual(stmt.comparators[0][0], "not in")

    def test_parse_is_produces_compare_op(self):
        prog = _parse("x is None\n")
        stmt = prog.body[0].expression
        self.assertIsInstance(stmt, CompareOp)
        self.assertEqual(stmt.comparators[0][0], "is")

    def test_parse_is_not_produces_compare_op(self):
        prog = _parse("x is not None\n")
        stmt = prog.body[0].expression
        self.assertIsInstance(stmt, CompareOp)
        self.assertEqual(stmt.comparators[0][0], "is not")

    def test_chained_in_and_comparison(self):
        r = _execute("let x = 3\nprint(1 <= x <= 5 and x in [1,2,3])\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_french_in_operator(self):
        r = _execute('afficher(3 dans [1, 2, 3])\n', lang="fr",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_french_is_operator(self):
        r = _execute('afficher(Rien est Rien)\n', lang="fr",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")


# ---------------------------------------------------------------
# WS3: Ternary expression
# ---------------------------------------------------------------

class TernaryExpressionTestSuite(unittest.TestCase):
    """Test ternary (conditional) expression parsing and execution."""

    def test_parse_ternary(self):
        prog = _parse("x if True else y\n")
        stmt = prog.body[0].expression
        self.assertIsInstance(stmt, ConditionalExpr)

    def test_execute_ternary_true(self):
        r = _execute("print(10 if True else 20)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "10")

    def test_execute_ternary_false(self):
        r = _execute("print(10 if False else 20)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "20")

    def test_ternary_with_expression_condition(self):
        r = _execute('let x = 5\nprint("big" if x > 3 else "small")\n')
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "big")

    def test_nested_ternary(self):
        r = _execute("print(1 if False else 2 if True else 3)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "2")

    def test_ternary_in_assignment(self):
        r = _execute("let x = 42 if True else 0\nprint(x)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "42")

    def test_ternary_with_comprehension_if(self):
        """Ternary if must not conflict with comprehension if."""
        r = _execute("print([x for x in range(10) if x > 5])\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "[6, 7, 8, 9]")

    def test_french_ternary(self):
        r = _execute('afficher(10 si Vrai sinon 20)\n', lang="fr")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "10")


# ---------------------------------------------------------------
# WS4: Assert statement
# ---------------------------------------------------------------

class AssertStatementTestSuite(unittest.TestCase):
    """Test assert statement parsing and execution."""

    def test_parse_assert(self):
        prog = _parse("assert True\n")
        self.assertIsInstance(prog.body[0], AssertStatement)
        self.assertIsNone(prog.body[0].msg)

    def test_parse_assert_with_message(self):
        prog = _parse('assert x > 0, "must be positive"\n')
        stmt = prog.body[0]
        self.assertIsInstance(stmt, AssertStatement)
        self.assertIsNotNone(stmt.msg)

    def test_execute_assert_pass(self):
        r = _execute("assert 1 + 1 == 2\n")
        self.assertTrue(r.success)

    def test_execute_assert_fail(self):
        r = _execute("assert False\n")
        self.assertFalse(r.success)

    def test_execute_assert_with_message(self):
        r = _execute('assert False, "expected failure"\n')
        self.assertFalse(r.success)

    def test_codegen_assert(self):
        code = _generate("assert x > 0\n")
        self.assertIn("assert", code)

    def test_codegen_assert_with_msg(self):
        code = _generate('assert x > 0, "positive"\n')
        self.assertIn("assert", code)
        self.assertIn(",", code)

    def test_french_assert(self):
        r = _execute("affirmer Vrai\n", lang="fr")
        self.assertTrue(r.success)


# ---------------------------------------------------------------
# WS5: Chained assignment
# ---------------------------------------------------------------

class ChainedAssignmentTestSuite(unittest.TestCase):
    """Test chained assignment parsing and execution."""

    def test_parse_chained(self):
        prog = _parse("a = b = c = 0\n")
        self.assertIsInstance(prog.body[0], ChainedAssignment)
        self.assertEqual(len(prog.body[0].targets), 3)

    def test_execute_chained(self):
        r = _execute("a = b = c = 42\nprint(a, b, c)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "42 42 42")

    def test_execute_chained_two(self):
        r = _execute("x = y = 10\nprint(x + y)\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "20")

    def test_codegen_chained(self):
        code = _generate("a = b = c = 0\n")
        self.assertIn("a = b = c = 0", code)

    def test_simple_assign_still_works(self):
        prog = _parse("x = 5\n")
        self.assertIsInstance(prog.body[0], Assignment)


# ---------------------------------------------------------------
# WS6: CLI
# ---------------------------------------------------------------

class CLITestSuite(unittest.TestCase):
    """Test CLI entry point module."""

    def test_main_module_importable(self):
        self.assertTrue(hasattr(main_module, "main"))

    def test_cmd_compile_function_exists(self):
        self.assertTrue(callable(cmd_compile))

    def test_cmd_run_function_exists(self):
        self.assertTrue(callable(cmd_run))

    def test_cmd_smoke_function_exists(self):
        self.assertTrue(callable(cmd_smoke))

    def test_language_pack_validator_en_passes(self):
        validator = LanguagePackValidator()
        errors = validator.validate("en")
        self.assertEqual(errors, [])

    def test_cmd_smoke_single_language_success(self):
        args = Namespace(lang="en", all=False)
        cmd_smoke(args)

    def test_cmd_smoke_invalid_language_exits(self):
        args = Namespace(lang="xx", all=False)
        with self.assertRaises(SystemExit) as exc:
            cmd_smoke(args)
        self.assertEqual(exc.exception.code, 1)

    def test_cmd_smoke_all_languages_success(self):
        args = Namespace(lang="en", all=True)
        cmd_smoke(args)

    def test_cmd_smoke_exits_when_a_language_fails(self):
        args = Namespace(lang="en", all=False)
        with patch.object(
            LanguagePackValidator,
            "validate",
            return_value=["synthetic failure"],
        ):
            with self.assertRaises(SystemExit) as exc:
                cmd_smoke(args)
        self.assertEqual(exc.exception.code, 1)


# ---------------------------------------------------------------
# WS7: REPL improvements
# ---------------------------------------------------------------

class REPLImprovementsTestSuite(unittest.TestCase):
    """Test REPL improvements."""

    def setUp(self):
        self.repl = REPL(language="en")

    def test_expression_auto_print(self):
        out = self.repl.eval_line("1 + 2")
        self.assertEqual(out.strip(), "3")

    def test_none_not_printed(self):
        self.repl.eval_line("let x = 42")
        out = self.repl.eval_line("x")
        self.assertEqual(out.strip(), "42")

    def test_assignment_no_output(self):
        out = self.repl.eval_line("let x = 10")
        self.assertEqual(out.strip(), "")

    def test_list_expression_auto_print(self):
        out = self.repl.eval_line("[1, 2, 3]")
        self.assertEqual(out.strip(), "[1, 2, 3]")

    def test_bracket_counting(self):
        count = self.repl._count_open_brackets("[1, 2,")
        self.assertEqual(count, 1)

    def test_bracket_counting_closed(self):
        count = self.repl._count_open_brackets("[1, 2]")
        self.assertEqual(count, 0)

    def test_bracket_counting_string_ignored(self):
        count = self.repl._count_open_brackets('"[not a bracket"')
        self.assertEqual(count, 0)

    def test_command_help(self):
        result = self.repl._handle_command(":help")
        self.assertTrue(result)

    def test_command_lang_switch(self):
        self.repl._handle_command(":lang fr")
        self.assertEqual(self.repl.language, "fr")

    def test_command_python_toggle(self):
        self.assertFalse(self.repl.show_python)
        self.repl._handle_command(":python")
        self.assertTrue(self.repl.show_python)

    def test_command_reset(self):
        self.repl.eval_line("let x = 42")
        self.repl._handle_command(":reset")
        out = self.repl.eval_line("x")
        self.assertIn("Error", out)

    def test_show_python_mode(self):
        self.repl.show_python = True
        out = self.repl.eval_line("print(1)")
        self.assertIn("[Python]", out)
        self.assertIn("1", out)


# ---------------------------------------------------------------
# Multilingual integration
# ---------------------------------------------------------------

class MultilingualCompletenessCLITestSuite(unittest.TestCase):
    """Test language completeness/CLI features with non-English languages."""

    def test_hindi_ternary(self):
        r = _execute('प्रिंट(10 अगर सत्य वरना 20)\n', lang="hi",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "10")

    def test_spanish_in_operator(self):
        r = _execute('print(3 en [1, 2, 3])\n', lang="es",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")

    def test_german_assert(self):
        r = _execute('behaupten Wahr\n', lang="de",
                      check_semantics=False)
        self.assertTrue(r.success)

    def test_chinese_ternary(self):
        r = _execute('打印(10 如果 真 否则 20)\n', lang="zh",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "10")

    def test_japanese_assert(self):
        r = _execute('断言 真\n', lang="ja", check_semantics=False)
        self.assertTrue(r.success)

    def test_arabic_in_operator(self):
        r = _execute('طباعة(3 في [1, 2, 3])\n', lang="ar",
                      check_semantics=False)
        self.assertTrue(r.success)
        self.assertEqual(r.output.strip(), "True")
