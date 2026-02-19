#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for declarative surface pattern validation."""

import json
import unittest
from pathlib import Path

from multilingualprogramming.parser.surface_normalizer import (
    validate_surface_patterns_config,
)


class SurfacePatternValidationTestSuite(unittest.TestCase):
    """Validate schema and cross-field consistency checks."""

    def _load_real_config(self):
        path = (
            Path(__file__).resolve().parent.parent
            / "multilingualprogramming" / "resources"
            / "usm" / "surface_patterns.json"
        )
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_real_surface_patterns_config_is_valid(self):
        config = self._load_real_config()
        validate_surface_patterns_config(config)

    def test_rejects_missing_patterns(self):
        with self.assertRaises(ValueError):
            validate_surface_patterns_config({})

    def test_rejects_both_template_and_normalize_to(self):
        bad = {
            "templates": {"x": [{"kind": "delimiter", "value": ":"}]},
            "patterns": [{
                "name": "bad",
                "language": "en",
                "pattern": [{"kind": "identifier", "slot": "target"}],
                "normalize_template": "x",
                "normalize_to": [{"kind": "delimiter", "value": ":"}],
            }],
        }
        with self.assertRaises(ValueError):
            validate_surface_patterns_config(bad)

    def test_rejects_unknown_template_reference(self):
        bad = {
            "patterns": [{
                "name": "bad",
                "language": "en",
                "pattern": [{"kind": "identifier", "slot": "target"}],
                "normalize_template": "missing_template",
            }],
        }
        with self.assertRaises(ValueError):
            validate_surface_patterns_config(bad)

    def test_rejects_unknown_output_slot(self):
        bad = {
            "patterns": [{
                "name": "bad",
                "language": "en",
                "pattern": [{"kind": "identifier", "slot": "target"}],
                "normalize_to": [{"kind": "expr_slot", "slot": "iterable"}],
            }],
        }
        with self.assertRaises(ValueError):
            validate_surface_patterns_config(bad)

    def test_rejects_unsupported_language(self):
        bad = {
            "patterns": [{
                "name": "bad",
                "language": "xx",
                "pattern": [{"kind": "identifier", "slot": "target"}],
                "normalize_to": [{"kind": "identifier_slot", "slot": "target"}],
            }],
        }
        with self.assertRaises(ValueError):
            validate_surface_patterns_config(bad)


if __name__ == "__main__":
    unittest.main()
