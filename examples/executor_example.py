#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Execute equivalent programs in all pilot languages."""

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


def build_sum_program(registry, language):
    """Return a tiny program that computes and prints 2 + 3."""
    kw_def = registry.get_keyword("FUNC_DEF", language)
    kw_return = registry.get_keyword("RETURN", language)
    kw_print = registry.get_keyword("PRINT", language)
    return (
        f"{kw_def} add(a, b):\n"
        f"    {kw_return} a + b\n"
        "\n"
        f"{kw_print}(add(2, 3))\n"
    )


registry = KeywordRegistry()

print("=== Execute in all 10 pilot languages ===")
for lang in registry.get_supported_languages():
    source = build_sum_program(registry, lang)
    result = ProgramExecutor(language=lang).execute(source)
    output = result.output.strip()
    print(f"{lang}: success={result.success}, output={output!r}")
