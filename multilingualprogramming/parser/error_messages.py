#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Multilingual error message registry for the parser and semantic analyzer."""

import json
import os


class ErrorMessageRegistry:
    """
    Loads and formats multilingual error messages from JSON resources.

    Singleton pattern, consistent with KeywordRegistry.
    """

    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if ErrorMessageRegistry._data is None:
            self._load()

    def _load(self):
        """Load error_messages.json from resources."""
        resource_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "resources", "parser", "error_messages.json"
        )
        with open(resource_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        ErrorMessageRegistry._data = raw.get("messages", {})

    def format(self, message_key, language="en", **kwargs):
        """
        Format an error message in the given language.

        Parameters:
            message_key: Key from error_messages.json
            language: Language code (falls back to 'en')
            **kwargs: Template variables

        Returns:
            Formatted error message string
        """
        templates = self._data.get(message_key)
        if templates is None:
            return f"Unknown error: {message_key}"

        template = templates.get(language)
        if template is None:
            template = templates.get("en", message_key)

        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def get_supported_keys(self):
        """Return all available message keys."""
        return list(self._data.keys())

    @classmethod
    def reset(cls):
        """Reset singleton for testing."""
        cls._instance = None
        cls._data = None
