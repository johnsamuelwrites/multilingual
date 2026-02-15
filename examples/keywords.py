#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Examples demonstrating the keyword registry system."""

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry

registry = KeywordRegistry()

# Show 'if' in all 10 languages
print("== The 'if' keyword in 10 languages ==")
for lang in registry.get_supported_languages():
    keyword = registry.get_keyword("COND_IF", lang)
    print(f"  {lang}: {keyword}")

# Reverse lookup: given a keyword, find the concept
print("\n== Reverse lookup ==")
print(f"  'si' (fr) -> {registry.get_concept('si', 'fr')}")
print(f"  'अगर' (hi) -> {registry.get_concept('अगर', 'hi')}")
print(f"  '如果' (zh) -> {registry.get_concept('如果', 'zh')}")

# Language detection from keywords
print("\n== Language detection ==")
detected = registry.detect_language(["si", "sinon", "tantque", "déf"])
print(f"  Keywords ['si', 'sinon', 'tantque', 'déf'] -> language: {detected}")

detected = registry.detect_language(["अगर", "वरना", "जबतक"])
print(f"  Keywords ['अगर', 'वरना', 'जबतक'] -> language: {detected}")

# Show function definition keyword across languages
print("\n== 'def' (function definition) in all languages ==")
for lang in registry.get_supported_languages():
    keyword = registry.get_keyword("FUNC_DEF", lang)
    print(f"  {lang}: {keyword}")
