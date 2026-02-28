#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Regression tests for the following fixes:

Issue 1 — ``fonction`` keyword accepted for French class methods
Issue 2 — Multi-line list / dict / set / tuple / call literals parse correctly
Issue 3 — ``pas_dans`` / ``pas dans`` / ``not in`` operator in French mode
Issue 4 — ``make_exec_globals()`` convenience function for plain exec() usage
Issues 5-7 — WAT backend lowers abs/min/max to native f64 instructions
Issue 6 — ``_name()`` helper returns a readable string for AttributeAccess nodes
Issue 8 — ``has_stub_calls()`` distinguishes functional WAT from stub-only exports
"""

import io
import sys
import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.runtime_builtins import make_exec_globals
from multilingualprogramming.codegen.wat_generator import (
    WATCodeGenerator,
    _name as wat_name,
    has_stub_calls,
)
from multilingualprogramming.parser.ast_nodes import (
    Program,
    NumeralLiteral,
    Identifier,
    CallExpr,
    VariableDeclaration,
    ExpressionStatement,
    ReturnStatement,
    FunctionDef,
    Parameter,
    AttributeAccess,
)


# ---------------------------------------------------------------------------
# Helpers shared by WAT tests
# ---------------------------------------------------------------------------

def _prog(*stmts):
    return Program(list(stmts))


def _gen(*stmts):
    return WATCodeGenerator().generate(_prog(*stmts))


def _param(name: str) -> Parameter:
    return Parameter(Identifier(name))


# ---------------------------------------------------------------------------
# Issue 1 — ``fonction`` as French method keyword
# ---------------------------------------------------------------------------

class FrenchFonctionKeywordTestSuite(unittest.TestCase):
    """``fonction`` must be accepted wherever ``déf`` is accepted for methods."""

    def _exec(self, source):
        return ProgramExecutor(language="fr", check_semantics=False).execute(source)

    def test_fonction_accepted_as_method_keyword(self):
        """``fonction`` inside a class body must not raise a parse error."""
        src = """\
classe Boite:
    fonction ouvrir(soi):
        afficher("ouvert")
soit b = Boite()
b.ouvrir()
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "ouvert")

    def test_fonction_and_def_interchangeable_in_class(self):
        """``fonction`` and ``déf`` must coexist inside the same class body."""
        src = """\
classe Calcul:
    déf __init__(soi):
        soi.valeur = 0
    fonction incrementer(soi):
        soi.valeur = soi.valeur + 1
soit c = Calcul()
c.incrementer()
afficher(c.valeur)
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "1")

    def test_fonction_with_return_value(self):
        """A method defined with ``fonction`` must return values normally."""
        src = """\
classe Math:
    fonction doubler(soi, x):
        retour x * 2
soit m = Math()
afficher(m.doubler(7))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "14")

    def test_fonction_as_top_level_function(self):
        """``fonction`` must also work for module-level function definitions."""
        src = """\
fonction carre(n):
    retour n * n
afficher(carre(5))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "25")


# ---------------------------------------------------------------------------
# Issue 2 — Multi-line list / dict / set / tuple / call literals
# ---------------------------------------------------------------------------

class MultiLineLiteralTestSuite(unittest.TestCase):
    """Bracket-enclosed literals that span multiple lines must parse correctly."""

    def _exec(self, source):
        return ProgramExecutor(language="fr").execute(source)

    def test_multiline_list_literal(self):
        src = """\
soit x = [
    1,
    2,
    3
]
afficher(longueur(x))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "3")

    def test_multiline_list_trailing_comma(self):
        """A trailing comma before ``]`` must be tolerated."""
        src = """\
soit x = [
    10,
    20,
]
afficher(longueur(x))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "2")

    def test_multiline_dict_literal(self):
        src = """\
soit d = {
    "a": 1,
    "b": 2
}
afficher(longueur(d))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "2")

    def test_multiline_dict_trailing_comma(self):
        src = """\
soit d = {
    "x": 10,
    "y": 20,
}
afficher(longueur(d))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "2")

    def test_multiline_tuple_literal(self):
        src = """\
soit t = (
    100,
    200
)
afficher(longueur(t))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "2")

    def test_multiline_function_call(self):
        """Arguments to a function call may span multiple lines."""
        src = """\
afficher(
    1 + 2
)
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "3")

    def test_multiline_function_call_multiple_args(self):
        src = """\
afficher(
    "a",
    "b",
    "c"
)
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertIn("a", result.output)
        self.assertIn("c", result.output)

    def test_multiline_list_values_are_correct(self):
        """Values in a multi-line list must be preserved in order."""
        src = """\
soit nums = [
    10,
    20,
    30
]
afficher(nums[0])
afficher(nums[2])
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        lines = result.output.strip().split("\n")
        self.assertEqual(lines[0], "10")
        self.assertEqual(lines[1], "30")

    def test_multiline_empty_list(self):
        """An empty list spread across lines must still parse."""
        src = """\
soit x = [
]
afficher(longueur(x))
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "0")


# ---------------------------------------------------------------------------
# Issue 3 — ``pas_dans`` / ``pas dans`` / ``not in`` in French mode
# ---------------------------------------------------------------------------

class NotInOperatorFrenchTestSuite(unittest.TestCase):
    """All three spellings of the 'not in' operator must work in French mode."""

    def _exec(self, source):
        return ProgramExecutor(language="fr").execute(source)

    def test_pas_dans_underscore_true_branch(self):
        """``pas_dans`` must trigger the true branch when element is absent."""
        src = """\
soit x = 5
si x pas_dans [1, 2, 3]:
    afficher("absent")
sinon:
    afficher("present")
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "absent")

    def test_pas_dans_underscore_false_branch(self):
        """``pas_dans`` must fall through to ``sinon`` when element is present."""
        src = """\
soit x = 2
si x pas_dans [1, 2, 3]:
    afficher("absent")
sinon:
    afficher("present")
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "present")

    def test_pas_dans_two_words_true_branch(self):
        """Space-separated ``pas dans`` must behave identically."""
        src = """\
soit x = 99
si x pas dans [1, 2, 3]:
    afficher("absent")
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "absent")

    def test_not_in_english_spelling_in_french_mode(self):
        """English ``not in`` must be accepted when the source language is French."""
        src = """\
soit x = 7
si x not in [1, 2, 3]:
    afficher("absent")
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "absent")

    def test_pas_dans_with_string_membership(self):
        """``pas_dans`` must work for string membership checks."""
        src = """\
soit s = "bonjour"
si "z" pas_dans s:
    afficher("ok")
"""
        result = self._exec(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "ok")

    def test_not_in_english_mode(self):
        """``not in`` must continue to work in English mode."""
        src = """\
let x = 5
if x not in [1, 2, 3]:
    print("absent")
"""
        result = ProgramExecutor(language="en").execute(src)
        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "absent")


# ---------------------------------------------------------------------------
# Issue 4 — ``make_exec_globals()`` convenience function
# ---------------------------------------------------------------------------

class MakeExecGlobalsTestSuite(unittest.TestCase):
    """``make_exec_globals()`` must return a complete namespace for exec()."""

    def test_returns_dict(self):
        ns = make_exec_globals("fr")
        self.assertIsInstance(ns, dict)

    def test_french_print_alias_present(self):
        ns = make_exec_globals("fr")
        self.assertIn("afficher", ns)
        self.assertIs(ns["afficher"], print)

    def test_french_len_alias_present(self):
        ns = make_exec_globals("fr")
        self.assertIn("longueur", ns)
        self.assertIs(ns["longueur"], len)

    def test_python_import_sentinels_present(self):
        """``__name__``, ``__package__`` and ``__spec__`` must be set."""
        ns = make_exec_globals("en")
        self.assertIn("__name__", ns)
        self.assertIn("__package__", ns)
        self.assertIn("__spec__", ns)
        self.assertEqual(ns["__name__"], "__main__")

    def test_extra_dict_merged(self):
        """Names in *extra* must appear in the returned namespace."""
        ns = make_exec_globals("en", extra={"my_var": 42})
        self.assertEqual(ns["my_var"], 42)

    def test_extra_overrides_builtins(self):
        """Keys from *extra* take precedence over the builtins namespace."""
        sentinel = object()
        ns = make_exec_globals("en", extra={"print": sentinel})
        self.assertIs(ns["print"], sentinel)

    def test_exec_transpiled_french_code(self):
        """Transpiled French code must run without NameError using the namespace."""
        executor = ProgramExecutor(language="fr")
        python_src = executor.transpile('afficher("salut")\n')
        ns = make_exec_globals("fr")
        captured = io.StringIO()
        old = sys.stdout
        sys.stdout = captured
        try:
            exec(python_src, ns)  # pylint: disable=exec-used
        finally:
            sys.stdout = old
        self.assertEqual(captured.getvalue().strip(), "salut")

    def test_default_language_is_english(self):
        """Calling with no arguments must default to English."""
        ns = make_exec_globals()
        self.assertIn("print", ns)
        self.assertIn("len", ns)

    def test_hindi_namespace(self):
        """``make_exec_globals`` must also work for non-Latin scripts."""
        ns = make_exec_globals("hi")
        self.assertIn("छापो", ns)
        self.assertIs(ns["छापो"], print)


# ---------------------------------------------------------------------------
# Issues 5-7 — WAT backend lowers abs / min / max to native f64 instructions
# ---------------------------------------------------------------------------

class WATBuiltinLoweringTestSuite(unittest.TestCase):
    """abs/min/max calls must emit f64.abs / f64.min / f64.max, not stubs."""

    # --- abs ---

    def test_abs_in_expression_emits_f64_abs(self):
        """abs(x) used as an rvalue must produce a f64.abs instruction."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("abs"), [Identifier("x")])
            )
        )
        self.assertIn("f64.abs", wat)

    def test_abs_in_expression_no_stub(self):
        """abs(x) as expression must not produce an unsupported-call stub."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("abs"), [Identifier("x")])
            )
        )
        self.assertFalse(has_stub_calls(wat))

    def test_abs_as_statement_emits_f64_abs(self):
        """abs(x) used as a statement must also emit f64.abs."""
        wat = _gen(
            ExpressionStatement(
                CallExpr(Identifier("abs"), [NumeralLiteral("3")])
            )
        )
        self.assertIn("f64.abs", wat)

    def test_abs_inside_function_body(self):
        """abs() inside a function definition must lower correctly."""
        prog = _prog(
            FunctionDef(
                "compute",
                [_param("x")],
                [ReturnStatement(
                    CallExpr(Identifier("abs"), [Identifier("x")])
                )]
            )
        )
        wat = WATCodeGenerator().generate(prog)
        self.assertIn("f64.abs", wat)
        self.assertFalse(has_stub_calls(wat))

    # --- min ---

    def test_min_two_args_emits_f64_min(self):
        """min(a, b) must produce a f64.min instruction."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("min"),
                         [NumeralLiteral("3"), NumeralLiteral("7")])
            )
        )
        self.assertIn("f64.min", wat)

    def test_min_two_args_no_stub(self):
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("min"),
                         [NumeralLiteral("3"), NumeralLiteral("7")])
            )
        )
        self.assertFalse(has_stub_calls(wat))

    def test_min_as_statement_emits_f64_min(self):
        wat = _gen(
            ExpressionStatement(
                CallExpr(Identifier("min"),
                         [NumeralLiteral("1"), NumeralLiteral("2")])
            )
        )
        self.assertIn("f64.min", wat)

    # --- max ---

    def test_max_two_args_emits_f64_max(self):
        """max(a, b) must produce a f64.max instruction."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("max"),
                         [NumeralLiteral("5"), NumeralLiteral("9")])
            )
        )
        self.assertIn("f64.max", wat)

    def test_max_two_args_no_stub(self):
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("max"),
                         [NumeralLiteral("5"), NumeralLiteral("9")])
            )
        )
        self.assertFalse(has_stub_calls(wat))

    def test_max_as_statement_emits_f64_max(self):
        wat = _gen(
            ExpressionStatement(
                CallExpr(Identifier("max"),
                         [NumeralLiteral("4"), NumeralLiteral("8")])
            )
        )
        self.assertIn("f64.max", wat)

    # --- localized aliases ---

    def test_french_abs_alias_emits_f64_abs(self):
        """The French alias ``valeurabsolue`` must also lower to f64.abs."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("valeurabsolue"), [NumeralLiteral("5")])
            )
        )
        self.assertIn("f64.abs", wat)
        self.assertFalse(has_stub_calls(wat))

    def test_french_min_alias_emits_f64_min(self):
        """The French/universal alias ``minimum`` must lower to f64.min."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("minimum"),
                         [NumeralLiteral("2"), NumeralLiteral("8")])
            )
        )
        self.assertIn("f64.min", wat)
        self.assertFalse(has_stub_calls(wat))

    def test_french_max_alias_emits_f64_max(self):
        """The alias ``maximum`` must lower to f64.max."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("maximum"),
                         [NumeralLiteral("2"), NumeralLiteral("8")])
            )
        )
        self.assertIn("f64.max", wat)
        self.assertFalse(has_stub_calls(wat))

    # --- abs/min/max combined ---

    def test_abs_min_max_combined_no_stubs(self):
        """A function using abs, min, and max must produce zero stubs."""
        prog = _prog(
            FunctionDef(
                "f",
                [_param("a"), _param("b")],
                [ReturnStatement(
                    CallExpr(Identifier("min"), [
                        CallExpr(Identifier("abs"), [Identifier("a")]),
                        CallExpr(Identifier("max"), [
                            Identifier("b"),
                            NumeralLiteral("0")
                        ])
                    ])
                )]
            )
        )
        wat = WATCodeGenerator().generate(prog)
        self.assertIn("f64.abs", wat)
        self.assertIn("f64.min", wat)
        self.assertIn("f64.max", wat)
        self.assertFalse(has_stub_calls(wat))


# ---------------------------------------------------------------------------
# Issue 6 — ``_name()`` helper handles AttributeAccess nodes
# ---------------------------------------------------------------------------

class WATNameHelperAttributeAccessTestSuite(unittest.TestCase):
    """``_name()`` must return a readable dotted string for AttributeAccess."""

    def test_simple_attribute_access(self):
        node = AttributeAccess(Identifier("module"), "func")
        self.assertEqual(wat_name(node), "module.func")

    def test_nested_attribute_access(self):
        inner = AttributeAccess(Identifier("pkg"), "mod")
        outer = AttributeAccess(inner, "func")
        self.assertEqual(wat_name(outer), "pkg.mod.func")

    def test_attribute_access_stub_comment_is_readable(self):
        """Unsupported attribute-call stubs must use the dotted name."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(
                    AttributeAccess(Identifier("os"), "getcwd"),
                    []
                )
            )
        )
        wat = WATCodeGenerator().generate(prog)
        self.assertIn("os.getcwd", wat)

    def test_plain_identifier_unchanged(self):
        self.assertEqual(wat_name(Identifier("foo")), "foo")

    def test_string_unchanged(self):
        self.assertEqual(wat_name("bar"), "bar")


# ---------------------------------------------------------------------------
# Issue 8 — ``has_stub_calls()`` utility
# ---------------------------------------------------------------------------

class WATHasStubCallsTestSuite(unittest.TestCase):
    """``has_stub_calls()`` must accurately classify WAT modules."""

    def test_empty_program_has_no_stubs(self):
        wat = _gen()
        self.assertFalse(has_stub_calls(wat))

    def test_arithmetic_program_has_no_stubs(self):
        wat = _gen(
            VariableDeclaration(
                "x",
                NumeralLiteral("42")
            )
        )
        self.assertFalse(has_stub_calls(wat))

    def test_known_function_call_has_no_stubs(self):
        """Calling a user-defined WAT function must not produce stubs."""
        prog = _prog(
            FunctionDef("add", [_param("a"), _param("b")],
                        [ReturnStatement(Identifier("a"))]),
            ExpressionStatement(
                CallExpr(Identifier("add"),
                         [NumeralLiteral("1"), NumeralLiteral("2")])
            )
        )
        wat = WATCodeGenerator().generate(prog)
        self.assertFalse(has_stub_calls(wat))

    def test_abs_call_has_no_stubs(self):
        """abs() must be fully lowered — no stub."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("abs"), [NumeralLiteral("3")])
            )
        )
        self.assertFalse(has_stub_calls(wat))

    def test_unknown_builtin_produces_stub(self):
        """An unrecognised function name must produce a stub comment."""
        wat = _gen(
            ExpressionStatement(
                CallExpr(Identifier("some_unknown_func"), [NumeralLiteral("1")])
            )
        )
        self.assertTrue(has_stub_calls(wat))

    def test_attribute_call_produces_stub(self):
        """A cross-module attribute call (e.g. os.getcwd) must produce a stub."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(
                    AttributeAccess(Identifier("os"), "getcwd"),
                    []
                )
            )
        )
        wat = WATCodeGenerator().generate(prog)
        self.assertTrue(has_stub_calls(wat))

    def test_stub_in_expression_context_detected(self):
        """A stub emitted inside an expression (rvalue) must also be detected."""
        wat = _gen(
            VariableDeclaration(
                "r",
                CallExpr(Identifier("closure_func"), [NumeralLiteral("1")])
            )
        )
        self.assertTrue(has_stub_calls(wat))

    def test_returns_bool(self):
        self.assertIsInstance(has_stub_calls("(module)"), bool)
        self.assertIsInstance(has_stub_calls(""), bool)

    def test_plain_wat_text_without_stub_marker(self):
        self.assertFalse(has_stub_calls("(module (func $foo (result f64) f64.const 1.0))"))

    def test_plain_wat_text_with_stub_marker(self):
        self.assertTrue(has_stub_calls(
            "(module (func $__main f64.const 0  ;; unsupported call: foo(...)))"
        ))


if __name__ == "__main__":
    unittest.main()
