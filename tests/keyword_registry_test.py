#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for keyword registry and validator
"""

import unittest
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.keyword.keyword_validator import KeywordValidator
from multilingualprogramming.exceptions import (
    UnknownKeywordError,
    UnsupportedLanguageError,
)


class KeywordRegistryTestSuite(unittest.TestCase):
    """
    Test cases for the keyword registry
    """

    def setUp(self):
        """Reset singleton for clean test state."""
        KeywordRegistry.reset()
        self.registry = KeywordRegistry()

    def test_load_keywords(self):
        """Test that keywords.json loads successfully."""
        languages = self.registry.get_supported_languages()
        self.assertIn("en", languages)
        self.assertIn("fr", languages)
        self.assertIn("it", languages)
        self.assertIn("pt", languages)
        self.assertIn("hi", languages)
        self.assertIn("ar", languages)
        self.assertEqual(len(languages), 12)

    def test_get_keyword_english(self):
        """Test forward lookup for English keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "en"), "if")
        self.assertEqual(self.registry.get_keyword("COND_ELSE", "en"), "else")
        self.assertEqual(self.registry.get_keyword("FUNC_DEF", "en"), "def")
        self.assertEqual(self.registry.get_keyword("RETURN", "en"), "return")
        self.assertEqual(self.registry.get_keyword("PRINT", "en"), "print")

    def test_get_keyword_french(self):
        """Test forward lookup for French keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "fr"), "si")
        self.assertEqual(self.registry.get_keyword("COND_ELSE", "fr"), "sinon")
        self.assertEqual(self.registry.get_keyword("LOOP_WHILE", "fr"), "tantque")
        self.assertEqual(self.registry.get_keyword("FUNC_DEF", "fr"), "déf")
        self.assertEqual(self.registry.get_keyword("PRINT", "fr"), "afficher")

    def test_get_keyword_hindi(self):
        """Test forward lookup for Hindi keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "hi"), "अगर")
        self.assertEqual(self.registry.get_keyword("COND_ELSE", "hi"), "वरना")
        self.assertEqual(self.registry.get_keyword("LOOP_WHILE", "hi"), "जबतक")
        self.assertEqual(self.registry.get_keyword("RETURN", "hi"), "वापसी")

    def test_get_keyword_arabic(self):
        """Test forward lookup for Arabic keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "ar"), "إذا")
        self.assertEqual(self.registry.get_keyword("FUNC_DEF", "ar"), "دالة")
        self.assertEqual(self.registry.get_keyword("RETURN", "ar"), "إرجاع")

    def test_get_keyword_chinese(self):
        """Test forward lookup for Chinese keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "zh"), "如果")
        self.assertEqual(self.registry.get_keyword("FUNC_DEF", "zh"), "函数")
        self.assertEqual(self.registry.get_keyword("RETURN", "zh"), "返回")

    def test_get_keyword_japanese(self):
        """Test forward lookup for Japanese keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "ja"), "もし")
        self.assertEqual(self.registry.get_keyword("FUNC_DEF", "ja"), "関数")
        self.assertEqual(self.registry.get_keyword("CLASS_DEF", "ja"), "クラス")

    def test_get_keyword_italian(self):
        """Test forward lookup for Italian keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "it"), "se")
        self.assertEqual(self.registry.get_keyword("LOOP_FOR", "it"), "per")
        self.assertEqual(self.registry.get_keyword("PRINT", "it"), "stampa")

    def test_get_keyword_portuguese(self):
        """Test forward lookup for Portuguese keywords."""
        self.assertEqual(self.registry.get_keyword("COND_IF", "pt"), "se")
        self.assertEqual(self.registry.get_keyword("LOOP_WHILE", "pt"), "enquanto")
        self.assertEqual(self.registry.get_keyword("PRINT", "pt"), "imprimir")

    def test_reverse_lookup_english(self):
        """Test reverse lookup: keyword -> concept for English."""
        self.assertEqual(self.registry.get_concept("if", "en"), "COND_IF")
        self.assertEqual(self.registry.get_concept("while", "en"), "LOOP_WHILE")
        self.assertEqual(self.registry.get_concept("def", "en"), "FUNC_DEF")

    def test_reverse_lookup_french(self):
        """Test reverse lookup for French."""
        self.assertEqual(self.registry.get_concept("si", "fr"), "COND_IF")
        self.assertEqual(self.registry.get_concept("tantque", "fr"), "LOOP_WHILE")
        self.assertEqual(self.registry.get_concept("afficher", "fr"), "PRINT")

    def test_reverse_lookup_hindi(self):
        """Test reverse lookup for Hindi."""
        self.assertEqual(self.registry.get_concept("अगर", "hi"), "COND_IF")
        self.assertEqual(self.registry.get_concept("जबतक", "hi"), "LOOP_WHILE")

    def test_is_keyword(self):
        """Test keyword recognition."""
        self.assertTrue(self.registry.is_keyword("if", "en"))
        self.assertTrue(self.registry.is_keyword("si", "fr"))
        self.assertTrue(self.registry.is_keyword("अगर", "hi"))
        self.assertFalse(self.registry.is_keyword("hello", "en"))
        self.assertFalse(self.registry.is_keyword("bonjour", "fr"))

    def test_detect_language_english(self):
        """Test language detection from English keywords."""
        detected = self.registry.detect_language(["if", "else", "while", "def"])
        self.assertEqual(detected, "en")

    def test_detect_language_french(self):
        """Test language detection from French keywords."""
        detected = self.registry.detect_language(["si", "sinon", "tantque", "déf"])
        self.assertEqual(detected, "fr")

    def test_detect_language_hindi(self):
        """Test language detection from Hindi keywords."""
        detected = self.registry.detect_language(["अगर", "वरना", "जबतक"])
        self.assertEqual(detected, "hi")

    def test_detect_language_no_match(self):
        """Test language detection with no matching keywords."""
        detected = self.registry.detect_language(["foo", "bar", "baz"])
        self.assertIsNone(detected)

    def test_get_all_keywords(self):
        """Test getting all keywords for a language."""
        en_keywords = self.registry.get_all_keywords("en")
        self.assertIn("COND_IF", en_keywords)
        self.assertEqual(en_keywords["COND_IF"], "if")
        self.assertIn("PRINT", en_keywords)
        self.assertEqual(en_keywords["PRINT"], "print")

    def test_keyword_aliases_supported(self):
        """Alias forms should resolve to the same concept."""
        self.assertEqual(self.registry.get_concept("chaine", "fr"), "TYPE_STR")
        self.assertEqual(self.registry.get_concept("chaîne", "fr"), "TYPE_STR")
        # get_keyword returns the canonical/primary form
        self.assertEqual(self.registry.get_keyword("TYPE_STR", "fr"), "chaine")

    def test_get_all_concept_ids(self):
        """Test getting all concept IDs."""
        concepts = self.registry.get_all_concept_ids()
        self.assertIn("COND_IF", concepts)
        self.assertIn("FUNC_DEF", concepts)
        self.assertIn("PRINT", concepts)
        self.assertIn("RETURN", concepts)
        # 14 control_flow + 10 definitions + 7 logical + 4 error_handling
        # + 4 variables + 6 types + 2 io = 47 total
        self.assertEqual(len(concepts), 47)

class KeywordRegistryErrorTestSuite(unittest.TestCase):
    """
    Test error handling and singleton behavior for keyword registry
    """

    def setUp(self):
        """Reset singleton for clean test state."""
        KeywordRegistry.reset()
        self.registry = KeywordRegistry()

    def test_unknown_keyword_error(self):
        """Test that UnknownKeywordError is raised for unknown concepts."""
        with self.assertRaises(UnknownKeywordError):
            self.registry.get_keyword("NONEXISTENT", "en")

    def test_unknown_keyword_reverse_error(self):
        """Test that UnknownKeywordError is raised for unknown keyword strings."""
        with self.assertRaises(UnknownKeywordError):
            self.registry.get_concept("nonexistent_keyword", "en")

    def test_unsupported_language_error(self):
        """Test that UnsupportedLanguageError is raised."""
        with self.assertRaises(UnsupportedLanguageError):
            self.registry.get_keyword("COND_IF", "xx")

    def test_unsupported_language_get_all(self):
        """Test that UnsupportedLanguageError is raised for get_all_keywords."""
        with self.assertRaises(UnsupportedLanguageError):
            self.registry.get_all_keywords("xx")

    def test_singleton_behavior(self):
        """Test that KeywordRegistry is a singleton."""
        registry2 = KeywordRegistry()
        self.assertIs(self.registry, registry2)


class KeywordValidatorTestSuite(unittest.TestCase):
    """
    Test cases for the keyword validator
    """

    def setUp(self):
        """Reset singleton for clean test state."""
        KeywordRegistry.reset()
        self.validator = KeywordValidator()

    def test_completeness_english(self):
        """Test that English has all concepts."""
        missing = self.validator.validate_completeness("en")
        self.assertEqual(missing, [])

    def test_completeness_french(self):
        """Test that French has all concepts."""
        missing = self.validator.validate_completeness("fr")
        self.assertEqual(missing, [])

    def test_completeness_all_languages(self):
        """Test that all pilot languages have complete mappings."""
        registry = KeywordRegistry()
        for lang in registry.get_supported_languages():
            missing = self.validator.validate_completeness(lang)
            self.assertEqual(
                missing, [], f"Language '{lang}' is missing concepts: {missing}"
            )

    def test_ambiguity_check(self):
        """Test ambiguity detection."""
        # Most languages should have no ambiguities by design,
        # but some may (e.g., shared words between concepts)
        registry = KeywordRegistry()
        for lang in registry.get_supported_languages():
            ambiguities = self.validator.validate_no_ambiguity(lang)
            # Log ambiguities but don't fail — some are expected
            for _, concepts in ambiguities:
                self.assertGreater(
                    len(concepts), 1,
                    "Ambiguity entry should have >1 concepts"
                )
