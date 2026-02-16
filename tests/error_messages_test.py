#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the multilingual error message registry."""

import unittest
from multilingualprogramming.parser.error_messages import ErrorMessageRegistry


class ErrorMessageRegistryTestSuite(unittest.TestCase):
    """Tests for error message loading and formatting."""

    def setUp(self):
        ErrorMessageRegistry.reset()
        self.registry = ErrorMessageRegistry()

    def test_load_messages(self):
        keys = self.registry.get_supported_keys()
        self.assertIn("UNEXPECTED_TOKEN", keys)
        self.assertIn("BREAK_OUTSIDE_LOOP", keys)
        self.assertIn("CONST_REASSIGNMENT", keys)

    def test_format_english_unexpected_token(self):
        msg = self.registry.format(
            "UNEXPECTED_TOKEN", "en",
            token="x", line=5, column=3
        )
        self.assertIn("x", msg)
        self.assertIn("5", msg)
        self.assertIn("3", msg)

    def test_format_french_unexpected_token(self):
        msg = self.registry.format(
            "UNEXPECTED_TOKEN", "fr",
            token="x", line=5, column=3
        )
        self.assertIn("inattendu", msg)

    def test_format_hindi_undefined_name(self):
        msg = self.registry.format(
            "UNDEFINED_NAME", "hi", name="x"
        )
        self.assertIn("x", msg)

    def test_format_chinese_const_reassignment(self):
        msg = self.registry.format(
            "CONST_REASSIGNMENT", "zh", name="PI"
        )
        self.assertIn("PI", msg)

    def test_format_arabic_break_outside_loop(self):
        msg = self.registry.format(
            "BREAK_OUTSIDE_LOOP", "ar"
        )
        self.assertTrue(len(msg) > 0)

    def test_fallback_to_english(self):
        msg = self.registry.format(
            "INVALID_SYNTAX", "xx"  # unsupported language
        )
        self.assertIn("Invalid syntax", msg)

    def test_all_messages_have_all_languages(self):
        languages = ["en", "fr", "es", "de", "hi", "ar", "bn", "ta", "zh", "ja"]
        keys = self.registry.get_supported_keys()
        for key in keys:
            for lang in languages:
                msg = self.registry.format(key, lang)
                self.assertTrue(len(msg) > 0,
                                f"Missing message: {key} for {lang}")

    def test_placeholder_substitution(self):
        msg = self.registry.format(
            "EXPECTED_COLON", "en", construct="if statement"
        )
        self.assertIn("if statement", msg)

    def test_unknown_message_key(self):
        msg = self.registry.format("NONEXISTENT_KEY", "en")
        self.assertIn("Unknown error", msg)

    def test_singleton_behavior(self):
        r1 = ErrorMessageRegistry()
        r2 = ErrorMessageRegistry()
        self.assertIs(r1, r2)

    def test_reset_singleton(self):
        r1 = ErrorMessageRegistry()
        ErrorMessageRegistry.reset()
        r2 = ErrorMessageRegistry()
        self.assertIsNot(r1, r2)


if __name__ == "__main__":
    unittest.main()
