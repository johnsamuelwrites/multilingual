#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for encoding guardrails on generated artifacts."""

import unittest

from multilingualprogramming.codegen.encoding_guard import (
    assert_clean_text_encoding,
    detect_text_encoding_issues,
)


class EncodingGuardTestSuite(unittest.TestCase):
    """Validate detection of mojibake and replacement characters."""

    def test_clean_text_has_no_issues(self):
        issues = detect_text_encoding_issues("print('hello')\n")
        self.assertEqual(issues, [])

    def test_replacement_character_is_detected(self):
        issues = detect_text_encoding_issues("bad\ufffdtext")
        self.assertTrue(any("suspicious_marker" in item for item in issues))

    def test_mojibake_marker_is_detected(self):
        issues = detect_text_encoding_issues("ParamÃ¨tres")
        self.assertTrue(any("suspicious_marker" in item for item in issues))

    def test_assert_clean_text_encoding_raises_on_issue(self):
        with self.assertRaises(ValueError):
            assert_clean_text_encoding("generated", "x â€” y")


if __name__ == "__main__":
    unittest.main()
