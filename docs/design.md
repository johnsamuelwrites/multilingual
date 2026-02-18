# multilingual Design Overview

This document explains how `multilingual` works at a design level.
It is intended for contributors, language-onboarding authors, and curious users.

## Core Concepts

### Values and literals

The language supports:

- numerals across scripts (plus hex/octal/binary/scientific notation)
- strings (including f-strings and triple-quoted strings)
- booleans and none-like literals
- collections: list, dict, set, tuple
- date literals via dedicated delimiters

### Types

Runtime behavior is Pythonic and dynamically typed.
Optional type annotations are supported in:

- variable annotations (`x: int`)
- parameter annotations (`f(x: int)`)
- function return annotations (`-> str`)

Annotations are preserved through parsing/codegen and emitted to Python output.

### Control flow and structure

Current constructs include:

- `if` / `elif` / `else`
- `while` / `for`
- `match` / `case`
- `try` / `except` / `finally`
- `with` (including multiple context managers)
- functions, classes, decorators
- async/await

## Keyword Localization Model

Localization is concept-driven, not grammar-driven.

1. Universal semantic concepts (e.g., `COND_IF`, `FUNC_DEF`) are stored in `multilingualprogramming/resources/usm/keywords.json`.
2. Each concept maps to language-specific surface keywords (`if`, `si`, etc.).
3. The lexer resolves concrete keywords to concepts.
4. The parser operates on concepts, so grammar logic is shared across languages.

This keeps parser/codegen stable while allowing language growth mostly through data files.

## Identifier Interoperability Across Languages

Identifiers are Unicode-aware and are not translated.

- Keywords are localized.
- User-defined names stay as written.
- Mixed scripts are allowed (for example, Latin + Devanagari in one file), though a single style per file is recommended for readability.

Interoperability rule of thumb:

- semantic keywords are normalized to concepts
- identifiers remain exact user symbols

So a French keyword file can still call a function named in English (or another script), as long as names match.

## Pipeline Summary

The execution pipeline is:

1. `Lexer` tokenizes source and resolves keyword concepts.
2. `Parser` builds a language-agnostic AST.
3. `SemanticAnalyzer` checks scope and structural constraints.
4. `PythonCodeGenerator` emits executable Python.
5. Runtime/executor runs generated code with multilingual built-in aliases.

## Roadmap (Short)

- v0 (today): toy-but-working interpreter/transpiler, multiple languages, core constructs, REPL, tests.
- next:
  - better tooling and diagnostics
  - stronger IDE/editor integration
  - more languages and improved locale quality
  - formalized language spec
  - possible LLM-assisted translation/refactoring workflows

`multilingual` is intentionally both serious and experimental: stable enough to use, open enough for community feedback.
