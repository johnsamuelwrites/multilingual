#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the interactive REPL."""

import io
import unittest
from contextlib import redirect_stdout

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

    def test_continuation_state_detects_unclosed_triple_string(self):
        count, has_unclosed_string = self.repl._continuation_state(
            'let s = """Ligne 1'
        )
        self.assertEqual(count, 0)
        self.assertTrue(has_unclosed_string)

    def test_continuation_state_closes_triple_string(self):
        text = 'let s = """Ligne 1\nLigne 2"""'
        count, has_unclosed_string = self.repl._continuation_state(text)
        self.assertEqual(count, 0)
        self.assertFalse(has_unclosed_string)


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

    def test_french_function_type_annotations(self):
        self.repl.eval_line("""\
déf saluer(nom: chaine) -> chaine:
    retour f"Bonjour {nom}"

""")
        output = self.repl.eval_line('afficher(saluer("Nina"))\n')
        self.assertEqual(output.strip(), "Bonjour Nina")

    def test_french_type_keyword_as_parameter_name(self):
        self.repl.eval_line("""\
déf moyenne(liste):
    retour somme(liste) / longueur(liste)

""")
        output = self.repl.eval_line("afficher(moyenne([2, 4]))\n")
        self.assertEqual(output.strip(), "3.0")

    def test_french_help_alias_without_colon(self):
        result = self.repl._handle_command("aide")
        self.assertTrue(result)

    def test_french_lang_alias_without_colon(self):
        result = self.repl._handle_command("langue en")
        self.assertTrue(result)
        self.assertEqual(self.repl.language, "en")

    def test_keywords_command_french_alias(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = self.repl._handle_command("mots-cles")

        self.assertTrue(result)
        output = stream.getvalue()
        self.assertIn("Mots-cles [fr]", output)
        self.assertIn("pour -> LOOP_FOR", output)

    def test_keywords_command_language_override(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = self.repl._handle_command(":keywords en")

        self.assertTrue(result)
        output = stream.getvalue()
        self.assertIn("Mots-cles [en]", output)
        self.assertIn("for -> LOOP_FOR", output)

    def test_symbols_command(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = self.repl._handle_command(":symboles fr")

        self.assertTrue(result)
        output = stream.getvalue()
        self.assertIn("Operateurs et symboles [fr]", output)
        self.assertIn("arithmetic:", output)
        self.assertIn("ADD: +", output)

    def test_keywords_unsupported_language(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = self.repl._handle_command(":keywords xx")

        self.assertTrue(result)
        self.assertIn("Langue non prise en charge : xx", stream.getvalue())

    def test_symbols_command_spanish_localization(self):
        repl = REPL(language="es")
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = repl._handle_command(":operadores es")

        self.assertTrue(result)
        output = stream.getvalue()
        self.assertIn("Operadores y simbolos [es]:", output)
