# Related Work and Differentiation

This document captures major prior art raised by the community and clarifies how `multilingual` is positioned.

## Why This Section Exists

Multilingual syntax has precedent. This project does not claim to be first; it focuses on one specific implementation strategy and target.

## Notable Prior Work

- **Hedy**: educational language with multilingual keyword support and gradual pedagogy.
- **Algol 68 localized representations**: historical precedent for localized language surfaces.
- **Non-English-based programming languages**: broad ecosystem of language-localized and language-native PLs.
- **Citrine**: community-cited reference point in multilingual or non-English-oriented syntax discussions.
- **Excel formulas (localized names)**: mainstream example of localized function names over shared semantics.
- **Perligata (Lingua::Romana::Perligata)**: notable language experiment demonstrating alternative linguistic surfaces.

## Comparison (High Level)

| Dimension | Hedy (community reference) | multilingual (this project) |
|---|---|---|
| Primary goal | Introductory education | Shared multilingual surface over broader Python semantics |
| Core model | Level-based simplification | Single semantic pipeline with concept-based keyword mapping |
| Runtime target | Teaching-focused execution model | Python code generation and execution |
| Localization unit | Language forms for educational syntax | Concept-to-keyword registry + localized builtin aliases |
| Intended usage | Classroom onboarding | Experimentation, language tooling, multilingual authoring |

## Current Differentiation Claim

`multilingual` currently differentiates on:

- **Concept-driven keyword normalization** before parsing.
- **Shared parser/codegen across languages** (language growth is data-first).
- **Runtime interoperability** through Python output and selected builtin aliases.

## Boundaries of the Claim

The differentiation is architectural, not ideological. This project does not claim that multilingual keywords alone solve documentation, community support, or professional ecosystem access.

## References

- [Reddit discussion thread](https://www.reddit.com/r/ProgrammingLanguages/comments/1r860hw/multilingual_a_programming_language_with_one/)
- [Hedy language](https://www.hedy.org/)
- [ALGOL 68](https://en.wikipedia.org/wiki/ALGOL_68)
- [Non-English-based programming languages](https://en.wikipedia.org/wiki/Non-English-based_programming_languages)
