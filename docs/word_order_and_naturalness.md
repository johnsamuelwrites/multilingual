# Word Order and Syntax Naturalness

This note documents an important design criticism: literal keyword substitution does not always produce natural code in every language.

## The Core Tension

- The project keeps one shared grammar and semantic structure.
- Human languages vary in word order, inflection, and how imperative statements are naturally expressed.
- Result: valid localized code can still feel linguistically unnatural.

## Current Design Choice

`multilingual` uses:

- one parser grammar,
- concept-level keyword mapping,
- localized surface forms for those concepts.

This optimizes implementation consistency and cross-language semantic equivalence.

As of the current implementation, the parser also runs a small
data-driven surface normalization pass before canonical parsing.
This allows selected alternate word orders to map to the same core AST
without forking parser grammar per language.

## Known Limitation

A shared positional structure favors technical consistency over fully native phrasing. This is an explicit tradeoff in the current architecture.

## Why Keep This Tradeoff (for now)

- Keeps parser and analyzer complexity manageable.
- Preserves deterministic forward compilation to a shared core/Python output.
- Avoids committing to impossible or brittle source round-trip guarantees.
- Avoids language-specific grammar forks too early.

## Surface Normalization (Generic Mechanism)

Surface forms are defined declaratively in:
`multilingualprogramming/resources/usm/surface_patterns.json`

The linkage with lexing is token-based:

- `Lexer` still performs all tokenization and concept resolution.
- Surface normalization consumes those lexer tokens (it does not re-lex text).
- Rewrites produce canonical keyword-concept tokens consumed by `Parser`.

Each rule is language-scoped but follows one generic pipeline:

1. match a surface token pattern,
2. capture slots (for example `target`, `iterable`),
3. rewrite to canonical concept order (for example `LOOP_FOR target IN iterable`),
4. parse normally.

To reduce repetition, canonical rewrites can be shared through named
`templates` in the same JSON file, and rules can reference a template.

This keeps semantics centralized while allowing incremental syntax
naturalness improvements for any language, including RTL scripts.

Current pilot rules include iterable-first `for` loop headers for Japanese,
Arabic, Spanish, and Portuguese.

## Future Directions

- Add more syntax profiles per language family where needed.
- Expand alternate surface forms that normalize to the same concept.
- Explore IDE display transforms (render localized forms while storing canonical forms).

## Status

Open design area. Contributions should prefer additive experiments (feature flags, language profiles, or transform layers) over immediate grammar fragmentation.
