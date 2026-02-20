# Evaluation Plan

This document describes how to evaluate multilingual frontend claims.

## Core Questions

1. Do distinct surface forms map to equivalent core structure?
2. Do equivalent core structures execute identically?
3. Do normalization rules reduce naturalness gaps without destabilizing parsing?

## Test Matrix

- Language pairs: at least English/French + one typologically distinct language.
- Surface variants: canonical form + normalized alternate form.
- Feature slices: variable binding, conditionals, loops, functions, calls.

## Required Checks

1. Parser equivalence:
   compare `ASTPrinter` output for paired programs.
2. Runtime equivalence:
   compare final program output and success status.
3. Regression checks:
   run existing parser/executor/surface tests.

## Metrics (Lightweight)

- Number of equivalent frontend pairs covered by tests.
- Number of deterministic normalization rules per language.
- Parse ambiguity failures caught by tests/validators.

## Current Baseline

Initial equivalence tests are in:

- `tests/frontend_equivalence_test.py`
- `tests/core_ir_test.py`

Recent additions include:

- Japanese/Arabic/Spanish/Portuguese iterable-first loop surface variants
- `try`/`except`/`else` frontend/runtime equivalence coverage
