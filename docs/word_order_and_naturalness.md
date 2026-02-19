# Word Order and Syntax Naturalness

This note documents an important design criticism: literal keyword substitution does not always produce natural code in every language.

## The Core Tension

- The project keeps one shared grammar and semantic structure.
- Human languages vary in word order, inflection, and how imperative statements are naturally expressed.
- Result: valid localized code can still feel linguistically unnatural.

## Current Design Choice

`multilingual` currently uses:

- one parser grammar,
- concept-level keyword mapping,
- localized surface forms for those concepts.

This optimizes implementation consistency and cross-language semantic equivalence.

## Known Limitation

A shared positional structure favors technical consistency over fully native phrasing. This is an explicit tradeoff in the current architecture.

## Why Keep This Tradeoff (for now)

- Keeps parser and analyzer complexity manageable.
- Preserves deterministic round-tripping to a shared AST/Python output.
- Avoids language-specific grammar forks too early.

## Future Directions

- Add syntax profiles per language family where needed.
- Introduce optional alternate surface forms that normalize to the same concept.
- Explore IDE display transforms (render localized forms while storing canonical forms).

## Status

Open design area. Contributions should prefer additive experiments (feature flags, language profiles, or transform layers) over immediate grammar fragmentation.
