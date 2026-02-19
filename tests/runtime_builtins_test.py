#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the runtime built-in functions."""

import unittest

from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


class RuntimeBuiltinsTestSuite(unittest.TestCase):
    """Test the runtime builtins namespace."""

    def test_english_namespace_has_print(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("print", ns)
        self.assertIs(ns["print"], print)

    def test_english_namespace_has_input(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("input", ns)
        self.assertIs(ns["input"], input)

    def test_french_namespace_has_afficher(self):
        ns = RuntimeBuiltins("fr").namespace()
        self.assertIn("afficher", ns)
        self.assertIs(ns["afficher"], print)

    def test_french_namespace_has_saisir(self):
        ns = RuntimeBuiltins("fr").namespace()
        self.assertIn("saisir", ns)
        self.assertIs(ns["saisir"], input)

    def test_hindi_namespace_has_print_keyword(self):
        ns = RuntimeBuiltins("hi").namespace()
        # Hindi keyword for PRINT
        registry = KeywordRegistry()
        hi_print = registry.get_keyword("PRINT", "hi")
        self.assertIn(hi_print, ns)
        self.assertIs(ns[hi_print], print)

    def test_french_range_alias(self):
        ns = RuntimeBuiltins("fr").namespace()
        self.assertIn("intervalle", ns)
        self.assertIs(ns["intervalle"], range)
        self.assertIn("range", ns)
        self.assertIs(ns["range"], range)

    def test_portuguese_len_alias(self):
        ns = RuntimeBuiltins("pt").namespace()
        self.assertIn("comprimento", ns)
        self.assertIs(ns["comprimento"], len)
        self.assertIn("len", ns)
        self.assertIs(ns["len"], len)

    def test_hindi_print_alias(self):
        ns = RuntimeBuiltins("hi").namespace()
        self.assertIn("प्रिंट", ns)
        self.assertIs(ns["प्रिंट"], print)

    def test_namespace_has_universal_builtins(self):
        ns = RuntimeBuiltins("en").namespace()
        # Check several universal builtins
        self.assertIn("len", ns)
        self.assertIs(ns["len"], len)
        self.assertIn("range", ns)
        self.assertIs(ns["range"], range)
        self.assertIn("abs", ns)
        self.assertIs(ns["abs"], abs)
        self.assertIn("min", ns)
        self.assertIn("max", ns)
        self.assertIn("sorted", ns)

    def test_namespace_has_type_builtins(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("int", ns)
        self.assertIs(ns["int"], int)
        self.assertIn("float", ns)
        self.assertIs(ns["float"], float)
        self.assertIn("str", ns)
        self.assertIs(ns["str"], str)
        self.assertIn("bool", ns)
        self.assertIs(ns["bool"], bool)
        self.assertIn("list", ns)
        self.assertIs(ns["list"], list)
        self.assertIn("dict", ns)
        self.assertIs(ns["dict"], dict)

    def test_namespace_has_exception_types(self):
        ns = RuntimeBuiltins("en").namespace()
        self.assertIn("ValueError", ns)
        self.assertIs(ns["ValueError"], ValueError)
        self.assertIn("TypeError", ns)
        self.assertIs(ns["TypeError"], TypeError)
        self.assertIn("Exception", ns)
        self.assertIs(ns["Exception"], Exception)

    def test_french_type_keywords(self):
        """French type keywords should map to Python types."""
        ns = RuntimeBuiltins("fr").namespace()
        registry = KeywordRegistry()
        fr_int = registry.get_keyword("TYPE_INT", "fr")
        self.assertIn(fr_int, ns)
        self.assertIs(ns[fr_int], int)

    def test_all_languages_namespace(self):
        """all_languages_namespace should contain mappings for all languages."""
        ns = RuntimeBuiltins.all_languages_namespace()
        # Should have English keywords
        self.assertIn("print", ns)
        # Should have French keywords
        self.assertIn("afficher", ns)
        # Should include localized built-in aliases
        self.assertIn("intervallo", ns)
        self.assertIn("intervalo", ns)
        # Universal builtins
        self.assertIn("len", ns)
        self.assertIn("range", ns)

    def test_namespace_values_are_callable(self):
        """All function-type builtins should be callable."""
        ns = RuntimeBuiltins("en").namespace()
        for name, obj in ns.items():
            if name not in ("True", "False", "None"):
                self.assertTrue(
                    callable(obj),
                    f"Built-in {name!r} is not callable"
                )

    def test_canonical_builtin_wins_on_alias_collision(self):
        """If an alias collides with a canonical builtin name, canonical wins."""
        original_catalog = RuntimeBuiltins._BUILTIN_ALIAS_CATALOG
        try:
            RuntimeBuiltins._BUILTIN_ALIAS_CATALOG = {
                "aliases": {
                    "range": {"fr": ["len", "plage_test"]},
                }
            }
            ns = RuntimeBuiltins("fr").namespace()
            self.assertIs(ns["len"], len)
            self.assertIn("plage_test", ns)
            self.assertIs(ns["plage_test"], range)
        finally:
            RuntimeBuiltins._BUILTIN_ALIAS_CATALOG = original_catalog
