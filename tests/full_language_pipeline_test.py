#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Comprehensive all-language pipeline test from one core template."""

import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


_CORE_TEMPLATE = """\
{IMPORT} math
{FROM} math {IMPORT} sqrt {AS} root_fn

{LET} acc_total = 0
{LET} numbers = [1, 2, 3, 4]

{FOR} num_item {IN} numbers:
    acc_total = acc_total + num_item

{LET} idx_counter = 0
{WHILE} idx_counter < 2:
    idx_counter = idx_counter + 1
    acc_total = acc_total + idx_counter

{DEF} adjust_val(value):
    {IF} value > 5:
        {RETURN} value - 1
    {ELSE}:
        {RETURN} value + 1

{LET} adjusted = [adjust_val(v_item) {FOR} v_item {IN} numbers {IF} v_item > 2]
{LET} flag_ok = {TRUE} {AND} {NOT} {FALSE}
{ASSERT} flag_ok

{TRY}:
    {LET} root_value = root_fn(16)
{EXCEPT} Exception {AS} handled_error:
    {LET} root_value = 0
{FINALLY}:
    acc_total = acc_total + int(root_value)

{CLASS} CounterBox:
    {DEF} __init__(self, start_value):
        self.value = start_value
    {DEF} bump(self):
        self.value = self.value + 1
        {RETURN} self.value

{LET} box = CounterBox(acc_total)
{LET} bumped_value = box.bump()

print(acc_total)
print(len(adjusted))
print(bumped_value)
print(acc_total {IS} {NONE})
"""

_KEYWORD_SLOTS = {
    "IMPORT": "IMPORT",
    "FROM": "FROM",
    "AS": "AS",
    "LET": "LET",
    "FOR": "LOOP_FOR",
    "IN": "IN",
    "WHILE": "LOOP_WHILE",
    "DEF": "FUNC_DEF",
    "IF": "COND_IF",
    "ELSE": "COND_ELSE",
    "RETURN": "RETURN",
    "TRUE": "TRUE",
    "AND": "AND",
    "NOT": "NOT",
    "FALSE": "FALSE",
    "ASSERT": "ASSERT",
    "TRY": "TRY",
    "EXCEPT": "EXCEPT",
    "FINALLY": "FINALLY",
    "CLASS": "CLASS_DEF",
    "IS": "IS",
    "NONE": "NONE",
}


def _render_program_for_language(registry, language):
    values = {}
    for slot, concept_id in _KEYWORD_SLOTS.items():
        values[slot] = registry.get_keyword(concept_id, language)
    return _CORE_TEMPLATE.format(**values)


class FullLanguagePipelineTestSuite(unittest.TestCase):
    """Generate, parse, and execute one core program in all languages."""

    def test_all_supported_languages_parse_and_execute_same_core_program(self):
        registry = KeywordRegistry()
        supported_languages = registry.get_supported_languages()

        reference_source = _render_program_for_language(registry, "en")
        reference_python = ProgramExecutor(language="en").transpile(reference_source)
        expected_output = "17\n2\n18\nFalse\n"

        for lang in supported_languages:
            with self.subTest(language=lang):
                source = _render_program_for_language(registry, lang)
                transpiled_python = ProgramExecutor(language=lang).transpile(source)
                self.assertEqual(
                    transpiled_python,
                    reference_python,
                    f"Transpiled Python mismatch for language '{lang}'",
                )

                result = ProgramExecutor(language=lang).execute(source)
                self.assertTrue(
                    result.success,
                    f"Execution failed for language '{lang}': {result.errors}",
                )
                self.assertEqual(
                    result.output,
                    expected_output,
                    f"Output mismatch for language '{lang}'",
                )
