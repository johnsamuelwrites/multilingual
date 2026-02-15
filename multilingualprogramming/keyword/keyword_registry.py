#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Registry for multilingual keyword lookups based on the Universal Semantic Model."""
# pylint: disable=unsubscriptable-object

import json
from pathlib import Path
from typing import Any, cast
from multilingualprogramming.exceptions import (
    UnknownKeywordError,
    UnsupportedLanguageError,
)


class KeywordRegistry:
    """
    Loads and queries the USM keyword ontology.

    Provides forward lookup (concept -> keyword), reverse lookup
    (keyword -> concept), and language detection from a set of keywords.
    """

    _instance = None
    _data: dict[str, Any] | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if KeywordRegistry._data is None:
            self._load()
        if not hasattr(self, "_reverse_index"):
            self._reverse_index = {}
        if not hasattr(self, "_concept_map"):
            self._concept_map = {}

    def _load(self):
        """Load keywords.json from the resources directory."""
        resources_dir = Path(__file__).parent.parent / "resources" / "usm"
        keywords_path = resources_dir / "keywords.json"
        with open(keywords_path, "r", encoding="utf-8") as f:
            KeywordRegistry._data = json.load(f)

        # Build reverse index: {language: {keyword_string: concept_id}}
        self._reverse_index = {}
        # Build flat concept map: {concept_id: {language: keyword}}
        self._concept_map = {}
        data = cast(dict[str, Any] | None, KeywordRegistry._data)
        if data is None:
            raise UnsupportedLanguageError("unknown")

        for category_concepts in data["categories"].values():
            for concept_id, translations in category_concepts.items():
                self._concept_map[concept_id] = translations
                for lang, keyword in translations.items():
                    if lang not in self._reverse_index:
                        self._reverse_index[lang] = {}
                    if keyword not in self._reverse_index[lang]:
                        self._reverse_index[lang][keyword] = []
                    self._reverse_index[lang][keyword].append(concept_id)

    def _check_language(self, language):
        """Raise UnsupportedLanguageError if language is not in the registry."""
        data = cast(dict[str, Any] | None, self._data)
        if data is None:
            raise UnsupportedLanguageError(language)
        if language not in data["languages"]:
            raise UnsupportedLanguageError(language)

    def check_language(self, language):
        """Public language validation helper."""
        self._check_language(language)

    def get_keyword(self, concept_id, language):
        """
        Look up a keyword for a concept in a given language.

        Parameters:
            concept_id (str): The USM concept ID (e.g., "COND_IF")
            language (str): Language code (e.g., "en", "fr", "hi")

        Returns:
            str: The keyword string in the requested language

        Raises:
            UnsupportedLanguageError: If the language is not supported
            UnknownKeywordError: If the concept_id is not found
        """
        self._check_language(language)
        if concept_id not in self._concept_map:
            raise UnknownKeywordError(concept_id)
        translations = self._concept_map[concept_id]
        if language not in translations:
            raise UnsupportedLanguageError(
                f"{language} (not available for concept {concept_id})"
            )
        return translations[language]

    def get_concept(self, keyword, language):
        """
        Reverse lookup: given a keyword in a language, return the concept ID.

        Parameters:
            keyword (str): The keyword string (e.g., "si", "अगर")
            language (str): Language code

        Returns:
            str: The concept ID

        Raises:
            UnsupportedLanguageError: If the language is not supported
            UnknownKeywordError: If the keyword is not found
        """
        self._check_language(language)
        lang_index = self._reverse_index.get(language, {})
        concepts = lang_index.get(keyword)
        if concepts is None:
            raise UnknownKeywordError(f"'{keyword}' in language '{language}'")
        if len(concepts) == 1:
            return concepts[0]
        # Return the first match; ambiguity is checked via KeywordValidator
        return concepts[0]

    def get_concepts(self, keyword, language):
        """
        Get all concept IDs that match a keyword in a language.

        Parameters:
            keyword (str): The keyword string
            language (str): Language code

        Returns:
            list[str]: List of matching concept IDs
        """
        self._check_language(language)
        lang_index = self._reverse_index.get(language, {})
        return lang_index.get(keyword, [])

    def is_keyword(self, word, language):
        """
        Check if a word is a recognized keyword in the given language.

        Parameters:
            word (str): The word to check
            language (str): Language code

        Returns:
            bool: True if the word is a keyword
        """
        lang_index = self._reverse_index.get(language, {})
        return word in lang_index

    def get_all_keywords(self, language):
        """
        Get all keywords for a language.

        Parameters:
            language (str): Language code

        Returns:
            dict: Mapping of concept_id -> keyword string
        """
        self._check_language(language)
        result = {}
        for concept_id, translations in self._concept_map.items():
            if language in translations:
                result[concept_id] = translations[language]
        return result

    def get_supported_languages(self):
        """
        Get list of all supported languages.

        Returns:
            list[str]: Language codes
        """
        data = cast(dict[str, Any] | None, self._data)
        if data is None:
            return []
        return list(data["languages"])

    def detect_language(self, keywords):
        """
        Given a list of keyword strings, detect which language they belong to.

        Scores each language by how many of the provided keywords match.

        Parameters:
            keywords (list[str]): List of keyword strings

        Returns:
            str | None: The language code with the most matches, or None
        """
        data = cast(dict[str, Any] | None, self._data)
        if data is None:
            return None
        scores = {}
        for lang in data["languages"]:
            lang_index = self._reverse_index.get(lang, {})
            score = sum(1 for kw in keywords if kw in lang_index)
            if score > 0:
                scores[lang] = score

        if not scores:
            return None
        return max(scores, key=scores.get)

    def get_all_concept_ids(self):
        """
        Get all concept IDs in the registry.

        Returns:
            list[str]: All concept IDs
        """
        return list(self._concept_map.keys())

    def get_language_index(self, language):
        """Get reverse index for a language."""
        self._check_language(language)
        return self._reverse_index.get(language, {})

    def get_concept_map(self):
        """Get concept map used for validation workflows."""
        return self._concept_map

    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
        cls._data = None
