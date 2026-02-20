# Controlled Language Scope

`multilingual` uses controlled language subsets (CNL-style), not unconstrained
natural language.

## Why This Exists

Natural language introduces ambiguity, morphology, and cultural variability.
To keep compilation deterministic, each frontend supports a constrained surface.

## In Scope

- Concept-keyword mappings from curated registries
- Finite built-in alias sets
- Finite declarative surface normalization patterns
- Deterministic parse and execution behavior

## Out of Scope

- Open-ended intent extraction
- Free-form conversational programming
- Full morphology and synonym resolution per language

## Ambiguity Policy

- Prefer explicit token-level concepts over heuristic interpretation.
- Keep conflicting keyword mappings disallowed by validation/tests.
- Add surface patterns incrementally and narrowly, with dedicated tests.

## Practical Authoring Rule

When onboarding a language, encode only forms that can be specified and tested
as stable grammar rules. Reject forms that require broad NLP inference.
