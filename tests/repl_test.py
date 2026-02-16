#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the interactive REPL."""

import unittest

from multilingualprogramming.codegen.repl import REPL


class REPLTestSuite(unittest.TestCase):
    """Test the REPL eval_line functionality."""

    def setUp(self):
        self.repl = REPL(language="en")

    def test_simple_print(self):
        output = self.repl.eval_line('print("hello")\n')
        self.assertEqual(output.strip(), "hello")

    def test_variable_persistence(self):
        """Variables should persist across eval_line calls."""
        self.repl.eval_line("let x = 42\n")
        output = self.repl.eval_line("print(x)\n")
        self.assertEqual(output.strip(), "42")

    def test_function_persistence(self):
        """Functions should persist across eval_line calls."""
        self.repl.eval_line("def double(n):\n    return n * 2\n\n")
        output = self.repl.eval_line("print(double(21))\n")
        self.assertEqual(output.strip(), "42")

    def test_arithmetic(self):
        self.repl.eval_line("let a = 10\n")
        self.repl.eval_line("let b = 20\n")
        output = self.repl.eval_line("print(a + b)\n")
        self.assertEqual(output.strip(), "30")

    def test_error_returns_message(self):
        output = self.repl.eval_line("let x = 1 / 0\n")
        self.assertIn("Error", output)

    def test_empty_input(self):
        output = self.repl.eval_line("")
        self.assertEqual(output, "")

    def test_whitespace_only(self):
        output = self.repl.eval_line("   \n")
        self.assertEqual(output, "")

    def test_reset_clears_state(self):
        self.repl.eval_line("let x = 42\n")
        self.repl.reset()
        output = self.repl.eval_line("print(x)\n")
        self.assertIn("Error", output)

    def test_show_python_mode(self):
        repl = REPL(language="en", show_python=True)
        output = repl.eval_line('print("hi")\n')
        self.assertIn("[Python]", output)
        self.assertIn("hi", output)

    def test_for_loop_block(self):
        source = """\
let total = 0
for i in range(5):
    total = total + i

print(total)
"""
        output = self.repl.eval_line(source)
        self.assertEqual(output.strip(), "10")


class REPLFrenchTestSuite(unittest.TestCase):
    """Test the REPL with French language."""

    def setUp(self):
        self.repl = REPL(language="fr")

    def test_french_print(self):
        output = self.repl.eval_line('afficher("bonjour")\n')
        self.assertEqual(output.strip(), "bonjour")

    def test_french_variable_and_function(self):
        self.repl.eval_line("""\
déf carre(n):
    retour n * n

""")
        output = self.repl.eval_line("afficher(carre(7))\n")
        self.assertEqual(output.strip(), "49")

    def test_french_for_loop(self):
        source = """\
soit somme = 0
pour i dans range(4):
    somme = somme + i

afficher(somme)
"""
        output = self.repl.eval_line(source)
        self.assertEqual(output.strip(), "6")
