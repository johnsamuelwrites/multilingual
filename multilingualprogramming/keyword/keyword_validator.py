#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Validator for keyword mappings, checking ambiguity and completeness."""

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


class KeywordValidator:
    """
    Validates keyword mappings for a language.

    Checks for:
    - Ambiguity: same string maps to multiple concepts
    - Completeness: all concepts have a translation
    """

    def __init__(self):
        self.registry = KeywordRegistry()

    def validate_no_ambiguity(self, language):
        """
        Check if any keywords in a language map to multiple concepts.

        Parameters:
            language (str): Language code

        Returns:
            list[tuple[str, list[str]]]: List of (keyword, [concept_ids])
                for ambiguous keywords. Empty list if no ambiguities.
        """
        self.registry._check_language(language)
        ambiguities = []
        lang_index = self.registry._reverse_index.get(language, {})
        for keyword, concepts in lang_index.items():
            if len(concepts) > 1:
                ambiguities.append((keyword, concepts))
        return ambiguities

    def validate_completeness(self, language):
        """
        Check if a language has translations for all concepts.

        Parameters:
            language (str): Language code

        Returns:
            list[str]: List of concept IDs missing translations.
                Empty list if complete.
        """
        self.registry._check_language(language)
        missing = []
        for concept_id, translations in self.registry._concept_map.items():
            if language not in translations:
                missing.append(concept_id)
        return missing
