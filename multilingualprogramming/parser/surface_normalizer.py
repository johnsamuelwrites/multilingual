#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Declarative surface-syntax normalization before canonical parsing."""

import json
from pathlib import Path

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.token import Token
from multilingualprogramming.lexer.token_types import TokenType

_PAIRS = {"(": ")", "[": "]", "{": "}"}
_PATTERN_SPEC_KINDS = {"literal", "delimiter", "keyword", "identifier", "expr"}
_OUTPUT_SPEC_KINDS = {"keyword", "delimiter", "identifier_slot", "expr_slot"}


def _ensure(condition, message):
    if not condition:
        raise ValueError(message)


def _validate_keyword_spec(spec, context):
    _ensure("concept" in spec, f"{context}: missing 'concept'")
    _ensure(isinstance(spec["concept"], str), f"{context}: 'concept' must be a string")


def _validate_delimiter_or_literal(spec, context):
    _ensure("value" in spec, f"{context}: missing 'value'")
    _ensure(isinstance(spec["value"], str), f"{context}: 'value' must be a string")


def _validate_slot_spec(spec, context):
    _ensure("slot" in spec, f"{context}: missing 'slot'")
    _ensure(isinstance(spec["slot"], str), f"{context}: 'slot' must be a string")


def _validate_pattern_spec(spec, context):
    _ensure(isinstance(spec, dict), f"{context}: each entry must be an object")
    kind = spec.get("kind")
    _ensure(kind in _PATTERN_SPEC_KINDS, f"{context}: unsupported kind '{kind}'")
    if kind == "keyword":
        _validate_keyword_spec(spec, context)
    elif kind in {"literal", "delimiter"}:
        _validate_delimiter_or_literal(spec, context)
    elif kind in {"identifier", "expr"}:
        _validate_slot_spec(spec, context)


def _validate_output_spec(spec, context):
    _ensure(isinstance(spec, dict), f"{context}: each entry must be an object")
    kind = spec.get("kind")
    _ensure(kind in _OUTPUT_SPEC_KINDS, f"{context}: unsupported kind '{kind}'")
    if kind == "keyword":
        _validate_keyword_spec(spec, context)
    elif kind == "delimiter":
        _validate_delimiter_or_literal(spec, context)
    elif kind in {"identifier_slot", "expr_slot"}:
        _validate_slot_spec(spec, context)


def validate_surface_patterns_config(config):
    """Validate schema and internal consistency of surface pattern config."""
    _ensure(isinstance(config, dict), "surface patterns config must be a JSON object")

    templates = config.get("templates", {})
    _ensure(isinstance(templates, dict), "'templates' must be an object when provided")
    for name, specs in templates.items():
        ctx = f"template '{name}'"
        _ensure(isinstance(name, str), "template names must be strings")
        _ensure(isinstance(specs, list) and specs, f"{ctx}: must be a non-empty list")
        for idx, spec in enumerate(specs):
            _validate_output_spec(spec, f"{ctx}[{idx}]")

    patterns = config.get("patterns")
    _ensure(isinstance(patterns, list) and patterns, "'patterns' must be a non-empty list")

    registry = KeywordRegistry()
    supported_languages = set(registry.get_supported_languages())

    for ridx, rule in enumerate(patterns):
        ctx = f"pattern[{ridx}]"
        _ensure(isinstance(rule, dict), f"{ctx}: must be an object")
        _ensure(isinstance(rule.get("name"), str), f"{ctx}: missing/invalid 'name'")
        _ensure(isinstance(rule.get("language"), str), f"{ctx}: missing/invalid 'language'")
        _ensure(rule["language"] in supported_languages,
                f"{ctx}: unsupported language '{rule['language']}'")

        pattern_specs = rule.get("pattern")
        _ensure(isinstance(pattern_specs, list) and pattern_specs,
                f"{ctx}: 'pattern' must be a non-empty list")
        captured_slots = set()
        for sidx, spec in enumerate(pattern_specs):
            _validate_pattern_spec(spec, f"{ctx}.pattern[{sidx}]")
            if spec["kind"] in {"identifier", "expr"}:
                captured_slots.add(spec["slot"])

        has_norm = "normalize_to" in rule
        has_template = "normalize_template" in rule
        _ensure(has_norm ^ has_template,
                f"{ctx}: provide exactly one of 'normalize_to' or 'normalize_template'")

        output_specs = None
        if has_norm:
            output_specs = rule.get("normalize_to")
            _ensure(isinstance(output_specs, list) and output_specs,
                    f"{ctx}: 'normalize_to' must be a non-empty list")
        else:
            tname = rule.get("normalize_template")
            _ensure(isinstance(tname, str), f"{ctx}: 'normalize_template' must be a string")
            _ensure(tname in templates, f"{ctx}: unknown template '{tname}'")
            output_specs = templates[tname]

        for oidx, spec in enumerate(output_specs):
            _validate_output_spec(spec, f"{ctx}.normalize[{oidx}]")
            if spec["kind"] in {"identifier_slot", "expr_slot"}:
                _ensure(spec["slot"] in captured_slots,
                        f"{ctx}: output references unknown slot '{spec['slot']}'")


class SurfaceNormalizer:
    """Normalize language-specific surface patterns to canonical token order."""

    _patterns = None
    _templates = None

    @classmethod
    def _load_patterns(cls):
        if cls._patterns is not None:
            return cls._patterns

        path = (
            Path(__file__).resolve().parent.parent
            / "resources" / "usm" / "surface_patterns.json"
        )
        with open(path, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
        validate_surface_patterns_config(data)
        cls._templates = data.get("templates", {})
        cls._patterns = data.get("patterns", [])
        return cls._patterns

    @staticmethod
    def _is_boundary(token):
        return token.type in (TokenType.NEWLINE, TokenType.EOF)

    @staticmethod
    def _is_statement_start(tokens, index):
        if index == 0:
            return True
        prev = tokens[index - 1]
        return prev.type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT)

    @staticmethod
    def _match_single(token, spec):
        kind = spec.get("kind")
        if kind == "literal":
            return token.value == spec.get("value")
        if kind == "delimiter":
            return token.type == TokenType.DELIMITER and token.value == spec.get("value")
        if kind == "keyword":
            return token.type == TokenType.KEYWORD and token.concept == spec.get("concept")
        if kind == "identifier":
            return token.type == TokenType.IDENTIFIER
        return False

    def _find_expr_end(self, tokens, start_idx, next_spec):
        idx = start_idx
        depth = 0

        while idx < len(tokens):
            tok = tokens[idx]
            if depth == 0 and self._is_boundary(tok):
                break

            if tok.type == TokenType.DELIMITER:
                if tok.value in _PAIRS:
                    depth += 1
                elif tok.value in _PAIRS.values():
                    depth = max(0, depth - 1)

            if depth == 0 and next_spec is not None:
                if self._match_single(tok, next_spec):
                    break
            idx += 1

        return idx

    def _render_token(self, spec, slots, language, anchor):
        kind = spec.get("kind")
        if kind == "keyword":
            concept = spec.get("concept")
            value = KeywordRegistry().get_keyword(concept, language)
            return Token(
                TokenType.KEYWORD, value, anchor.line, anchor.column,
                concept=concept, language=language
            )
        if kind == "delimiter":
            return Token(TokenType.DELIMITER, spec.get("value"), anchor.line, anchor.column)
        if kind == "identifier_slot":
            return slots[spec.get("slot")]
        return None

    def _render_output(self, rule, slots, language, anchor):
        normalize_to = rule.get("normalize_to")
        template_name = rule.get("normalize_template")
        if normalize_to is None and template_name:
            normalize_to = (self._templates or {}).get(template_name, [])

        out = []
        for spec in normalize_to or []:
            kind = spec.get("kind")
            if kind == "expr_slot":
                out.extend(slots[spec.get("slot")])
                continue
            tok = self._render_token(spec, slots, language, anchor)
            if tok is not None:
                out.append(tok)
        return out

    def _match_rule(self, tokens, start_idx, rule, language):
        if language != rule.get("language"):
            return None
        if not self._is_statement_start(tokens, start_idx):
            return None

        idx = start_idx
        slots = {}
        specs = rule.get("pattern", [])
        for pos, spec in enumerate(specs):
            kind = spec.get("kind")
            if kind == "expr":
                next_spec = specs[pos + 1] if pos + 1 < len(specs) else None
                expr_end = self._find_expr_end(tokens, idx, next_spec)
                if expr_end <= idx:
                    return None
                slots[spec.get("slot")] = tokens[idx:expr_end]
                idx = expr_end
                if idx >= len(tokens):
                    return None
                continue

            if idx >= len(tokens) or not self._match_single(tokens[idx], spec):
                return None
            if kind == "identifier":
                slots[spec.get("slot")] = tokens[idx]
            idx += 1

        out = self._render_output(rule, slots, language, tokens[start_idx])
        return idx, out

    def normalize(self, tokens, language):
        """Return a new token list with declarative surface patterns normalized."""
        patterns = self._load_patterns()
        normalized = []
        i = 0
        while i < len(tokens):
            replaced = False
            for rule in patterns:
                matched = self._match_rule(tokens, i, rule, language)
                if matched is None:
                    continue
                end_idx, replacement = matched
                normalized.extend(replacement)
                i = end_idx
                replaced = True
                break
            if replaced:
                continue
            normalized.append(tokens[i])
            i += 1
        return normalized


def normalize_surface_tokens(tokens, language):
    """Convenience wrapper used by parser entry points."""
    if not language:
        return tokens
    return SurfaceNormalizer().normalize(tokens, language)
