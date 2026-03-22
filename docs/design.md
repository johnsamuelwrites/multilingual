# multilingual Design Overview

This document explains how `multilingual` works at a design level.
It is intended for contributors, language-onboarding authors, and curious users.

## Layered Model

The implementation is structured as five explicit layers:

1. Concrete surface syntax (`CS_lang`): language-specific source text.
2. Shared Core AST: language-agnostic parser output (`ast_nodes.py`).
3. Typed Core IR container: `CoreIRProgram` (`multilingualprogramming/core/ir.py`).
4. Backend lowering/codegen: Python and WAT/WASM oriented generation paths.
5. Runtime execution and backend selection.

This makes boundary questions explicit: parsing maps `CS_lang` to Core AST,
semantic bridging consumes shared frontend structures, and execution targets
consume backend artifacts rather than raw frontend text.

This document describes the current implementation shape. It should be read
alongside the broader [Vision](vision.md) and [Core 1.0](spec/core_1_0.md)
documents, which define where the language is heading beyond the present
compiler architecture.

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
- `try` / `except` / `else` / `finally`
- `with` (including multiple context managers)
- functions, classes, decorators
- async/await, `async for`, `async with`

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
2. Optional surface normalization rewrites supported alternate forms.
3. `Parser` builds a language-agnostic AST.
4. `lower_to_semantic_ir` lowers parser output into `IRProgram`.
5. `core.semantic_analyzer.SemanticAnalyzer` checks scope and structural constraints.
6. Backends emit Python or WAT/WASM artifacts.
7. Runtime/executor selects the available execution path and runs with multilingual built-in aliases.

The long-term direction is not "a Python transpiler with translations" but a
portable semantic language with multiple execution targets. The current
pipeline is the implementation vehicle for that direction.

## Frontend Contract

Each language is treated as a frontend with a translation function:

`T_lang: CS_lang -> CoreAST`

Current claim is forward-only: all supported frontends are designed as
semantics-preserving embeddings into the shared core. The project does not
guarantee lossless round-tripping from core back to original surface form.

See also:

- [core_spec.md](core_spec.md)
- [frontend_contracts.md](frontend_contracts.md)
- [cnl_scope.md](cnl_scope.md)

## Roadmap (Short)

- v0 (today): working multilingual language platform with a transitional compiler pipeline, multiple languages, REPL, tests, Python execution, and WAT/WASM support.
- next:
  - stronger semantic IR and capability-aware analysis
  - more unmistakable Core 1.0 language features
  - better tooling and diagnostics
  - stronger IDE/editor integration
  - more languages and improved locale quality
  - formalized language spec for AI-native, multimodal, reactive, and distributed workflows

`multilingual` is intentionally both serious and experimental: stable enough to use, open enough for community feedback.
