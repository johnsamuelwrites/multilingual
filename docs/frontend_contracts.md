# Frontend Contracts

This document specifies how language frontends relate to the shared core.

## Translation Function

For each supported language `lang`, define:

`T_lang: CS_lang -> CoreAST`

Where:

- `CS_lang` is concrete syntax in that language frontend.
- `CoreAST` is the shared parser AST (`ast_nodes.py`).

## Contract Goals

Each frontend should satisfy:

1. Compositional mapping: syntax constructs map predictably into core nodes.
2. Conservative extension: frontend-specific surface variants normalize into
   existing core constructs, not new semantics by default.
3. Semantics-preserving embedding: equivalent constructs in different
   frontends should execute identically after lowering/codegen.

## Non-Goals

- No requirement to reconstruct original surface form from `CoreAST`.
- No claim of full natural-language understanding.

## Current Mechanisms

- Concept-keyword registry in `resources/usm/keywords.json`
- Optional surface normalization in `resources/usm/surface_patterns.json`
- Core wrapping via `lower_to_core_ir`

## Validation Strategy

The project validates frontend contracts through tests:

- parser-level equivalence tests (same `ASTPrinter` output)
- executor-level equivalence tests (same runtime output)
- per-language onboarding checks for keyword completeness and ambiguity
