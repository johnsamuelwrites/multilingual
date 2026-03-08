#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for localized built-in aliases across non-English languages."""

import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor


def _execute(source, language="fr"):
    return ProgramExecutor(language=language).execute(source)


class TestLocalizedBuiltins(unittest.TestCase):
    """Extended built-in aliases are recognized and executable in all 16 languages."""

    def test_eval_french(self):
        r = _execute("x = evaluer('1 + 1')\nprint(x)", language="fr")
        self.assertEqual(r.output.strip(), "2")

    def test_exec_french(self):
        r = _execute("executer('print(42)')", language="fr")
        self.assertEqual(r.output.strip(), "42")

    def test_globals_french(self):
        r = _execute("g = globaux()\nprint(type(g).__name__)", language="fr")
        self.assertEqual(r.output.strip(), "dict")

    def test_locals_french(self):
        r = _execute("l = locaux()\nprint(type(l).__name__)", language="fr")
        self.assertEqual(r.output.strip(), "dict")

    def test_vars_german(self):
        r = _execute("v = variablen()\nprint(type(v).__name__)", language="de")
        self.assertEqual(r.output.strip(), "dict")

    def test_breakpoint_german(self):
        r = _execute("print(type(haltepunkt).__name__)", language="de")
        self.assertIn("builtin", r.output.lower())

    def test_compile_spanish(self):
        r = _execute(
            "c = compilar('1+1', '<string>', 'eval')\nprint(type(c).__name__)",
            language="es"
        )
        self.assertEqual(r.output.strip(), "code")

    def test_eval_spanish(self):
        r = _execute("x = evaluar('3 * 3')\nprint(x)", language="es")
        self.assertEqual(r.output.strip(), "9")

    def test_globals_italian(self):
        r = _execute("g = globali()\nprint(type(g).__name__)", language="it")
        self.assertEqual(r.output.strip(), "dict")

    def test_locals_portuguese(self):
        r = _execute("l = locais()\nprint(type(l).__name__)", language="pt")
        self.assertEqual(r.output.strip(), "dict")

    def test_vars_italian(self):
        """Italian 'variabili' maps to vars."""
        r = _execute("v = variabili()\nprint(type(v).__name__)", language="it")
        self.assertEqual(r.output.strip(), "dict")

    def test_compile_italian(self):
        """Italian 'compilare' maps to compile."""
        r = _execute(
            "c = compilare('1+1', '<s>', 'eval')\nprint(type(c).__name__)",
            language="it"
        )
        self.assertEqual(r.output.strip(), "code")

    def test_aiter_callable(self):
        """aiter is callable in English."""
        r = _execute("print(callable(aiter))", language="en")
        self.assertEqual(r.output.strip(), "True")

    def test_anext_callable(self):
        """anext is callable in English."""
        r = _execute("print(callable(anext))", language="en")
        self.assertEqual(r.output.strip(), "True")

    def test_memoryview_callable(self):
        """memoryview is callable in English."""
        r = _execute("print(callable(memoryview))", language="en")
        self.assertEqual(r.output.strip(), "True")


if __name__ == "__main__":
    unittest.main()
