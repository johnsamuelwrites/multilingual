# Python 3.12 Compatibility Roadmap

This roadmap defines the execution plan to move from the current compatibility
baseline to high-confidence CPython 3.12 compatibility.

Target runtime:
- CPython `3.12.x`

Non-goal for early milestones:
- immediate full compatibility with every third-party package

## Principles

- Compatibility claims must be test-backed.
- Behavior parity matters more than syntax acceptance alone.
- Regressions block merges once a capability is marked "supported".

## Milestone M0: Baseline Freeze and Measurement

Goal:
- lock current capabilities and establish measurable progress metrics

Deliverables:
- keep `docs/compatibility_matrix.md` as source-of-truth status table
- freeze baseline examples:
  - `examples/complete_features_en.ml`
  - `examples/complete_features_fr.ml`
  - `examples/complete_features_es.ml`
- add initial differential tests:
  - `tests/compatibility/differential_312_test.py`
- add CI job running compatibility smoke examples on Python 3.12

Exit criteria:
- CI runs baseline compatibility checks on every PR
- matrix entries map to at least one executable test/example

## Milestone M1: Syntax Coverage Parity (Parser/Lexer)

Goal:
- support CPython 3.12 syntax surface for targeted language subset

Workstreams:
- expand parser tests for remaining constructs and edge forms
- add negative tests for precise syntax error behavior
- ensure AST normalization is deterministic across supported languages

Exit criteria:
- feature checklist for syntax forms is complete and test-linked
- no known parser gaps for advertised features

## Milestone M2: Semantic and Runtime Parity

Goal:
- align runtime behavior with CPython 3.12 semantics for supported syntax

Workstreams:
- differential tests (`multilingual` output/errors vs CPython)
- exception type/message parity for common failure paths
- scope/closure/class/object model behavioral checks
- truthiness, identity, mutation, and evaluation-order edge cases

Exit criteria:
- differential suite passes for targeted semantics
- documented deviations are explicit and intentional

## Milestone M3: Import/Stdlib Parity

Goal:
- make import behavior and selected stdlib interactions predictable vs CPython

Workstreams:
- package/module resolution parity tests (`import`, `from`, aliases, packages)
- `.ml` and Python module interop tests
- prioritized stdlib parity set (math, json, datetime, itertools, pathlib)

Exit criteria:
- import behavior matrix complete for documented patterns
- prioritized stdlib smoke suite green on CI

## Milestone M4: Ecosystem Compatibility

Goal:
- execute representative real-world Python code with minimal rewrites

Workstreams:
- curated external corpus (small/medium pure-Python projects)
- compatibility adapters where needed
- triage and classify failures (parser, semantics, runtime, imports, stdlib)

Exit criteria:
- target pass-rate achieved on curated corpus
- compatibility score and regression trend published per release

## CI Gates (Python 3.12)

Minimum gates:

1. Unit/regression tests
2. Full pipeline tests
3. Compatibility smoke examples
4. Differential parity tests (incremental rollout)

Recommended policy:
- no merge when a previously passing compatibility gate fails

## Measurement Model

Track per release:

- Syntax coverage (% of checklist items passing)
- Semantic parity (% of differential tests passing)
- Import/stdlib parity (% of selected suites passing)
- Ecosystem pass-rate (% of curated projects passing)

## Immediate Next Tasks

1. Add `tests/compatibility/` for differential tests against CPython 3.12.
2. Tag current tests by capability area (syntax/semantic/import/runtime).
3. Expand complete-feature examples to include missing high-impact constructs.
4. Publish a simple compatibility score in CI summary.
