#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Validation helpers for language pack smoke checks."""

import json
from pathlib import Path

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.keyword.keyword_validator import KeywordValidator


class LanguagePackValidator:
    """Validate consistency and basic execution for one language pack."""

    def __init__(self):
        self._registry = KeywordRegistry()
        self._keyword_validator = KeywordValidator()
        resources = Path(__file__).resolve().parent.parent / "resources"
        self._error_messages_path = resources / "parser" / "error_messages.json"
        self._repl_commands_path = resources / "repl" / "commands.json"

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8-sig") as handle:
            return json.load(handle)

    def _validate_error_messages(self, language):
        data = self._load_json(self._error_messages_path)
        missing = []
        for message_key, by_language in data.get("messages", {}).items():
            if language not in by_language:
                missing.append(message_key)
        if not missing:
            return None
        return f"missing parser error messages for {len(missing)} keys"

    def _validate_repl_catalog(self, language):
        data = self._load_json(self._repl_commands_path)

        if language not in data.get("help_titles", {}):
            return "missing REPL help title"

        for message_key, by_language in data.get("messages", {}).items():
            if language not in by_language:
                return f"missing REPL message '{message_key}'"

        commands = data.get("commands", {})
        for command_name, meta in commands.items():
            aliases = meta.get("aliases", {}).get(language)
            descriptions = meta.get("descriptions", {}).get(language)
            if aliases is None:
                return f"missing REPL aliases for '{command_name}'"
            if not aliases:
                return f"empty REPL aliases for '{command_name}'"
            if descriptions is None:
                return f"missing REPL description for '{command_name}'"
        return None

    def _validate_executor_smoke(self, language):
        let_kw = self._registry.get_keyword("LET", language)
        print_kw = self._registry.get_keyword("PRINT", language)
        source = f"{let_kw} x = 1\n{print_kw}(x)\n"
        result = ProgramExecutor(language=language).execute(source)
        if not result.success:
            return "executor smoke program failed"
        if result.output.strip() != "1":
            return f"executor smoke output mismatch: {result.output!r}"
        return None

    def get_supported_languages(self):
        """Return supported language codes from the keyword registry."""
        return self._registry.get_supported_languages()

    def validate(self, language):
        """
        Return a list of validation errors for a language.

        Empty list means validation passed.
        """
        self._registry.check_language(language)
        errors = []

        missing_concepts = self._keyword_validator.validate_completeness(language)
        if missing_concepts:
            errors.append(
                f"missing keyword translations for {len(missing_concepts)} concepts"
            )

        ambiguities = self._keyword_validator.validate_no_ambiguity(language)
        if ambiguities:
            errors.append(f"ambiguous keywords found: {len(ambiguities)}")

        error_msg_issue = self._validate_error_messages(language)
        if error_msg_issue:
            errors.append(error_msg_issue)

        repl_issue = self._validate_repl_catalog(language)
        if repl_issue:
            errors.append(repl_issue)

        exec_issue = self._validate_executor_smoke(language)
        if exec_issue:
            errors.append(exec_issue)

        return errors
