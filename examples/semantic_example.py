#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Example: Semantic analysis across all pilot languages."""

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import SemanticAnalyzer


def safe_text(text):
    """Render Unicode text safely on non-UTF-8 consoles."""
    return text.encode("ascii", "backslashreplace").decode("ascii")


def analyze(source, language):
    """Lex, parse, and run semantic analysis."""
    tokens = Lexer(source, language=language).tokenize()
    program = Parser(tokens, source_language=language).parse()
    analyzer = SemanticAnalyzer(source_language=language)
    return analyzer.analyze(program)


def build_valid_source(registry, language):
    """Program with no semantic errors: declare then reference variable."""
    kw_let = registry.get_keyword("LET", language)
    return (
        f"{kw_let} x = 1\n"
        "x\n"
    )


def build_invalid_source(registry, language):
    """Program with semantic error: break outside loop."""
    kw_break = registry.get_keyword("LOOP_BREAK", language)
    return f"{kw_break}\n"


registry = KeywordRegistry()

print("=== Semantic analysis in all 10 pilot languages ===")
for lang in registry.get_supported_languages():
    ok_source = build_valid_source(registry, lang)
    bad_source = build_invalid_source(registry, lang)

    ok_errors = analyze(ok_source, lang)
    bad_errors = analyze(bad_source, lang)

    print(f"\n=== {lang.upper()} ===")
    print(f"valid program errors: {len(ok_errors)}")
    print(f"invalid program errors: {len(bad_errors)}")
    if bad_errors:
        print(f"first error: {safe_text(str(bad_errors[0]))}")
