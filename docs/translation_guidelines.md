# Translation Guidelines

This guide defines how new keyword/localization entries should be proposed and reviewed.

## Goals

- Keep meaning stable across languages.
- Avoid ambiguous or misleading translations.
- Preserve interoperability with existing code and tooling.

## Translation Rules

1. Prioritize semantic accuracy over literal translation.
2. Prefer widely understood programming terms when local usage is established.
3. Choose one canonical localized form per concept per language.
4. Use aliases sparingly and document each one.
5. Avoid translating user identifiers; only language concepts and approved builtin aliases are localized.

## Abbreviations vs Full Words

When both short and full forms exist (for example, `const`-like terms):

- Prefer the form most common in developer usage for that language.
- If usage is split, choose one canonical form and keep the other as an alias only if it is unambiguous.
- Document the decision rationale in PR notes.

## Collision and Ambiguity Policy

Reject or revise entries when a translation:

- overlaps another concept in the same language pack,
- is a high-frequency homonym with unrelated meaning in code context,
- creates parser ambiguity with existing operators/tokens.

## False Friends and Cross-Language Safety

- Flag terms that appear similar across languages but differ in meaning.
- Add explicit tests for these terms before accepting the translation.

## Contributor Checklist

- Added/updated keyword entry in registry resources.
- Added tests for forward (concept -> token) and reverse (token -> concept) lookup.
- Ran ambiguity/collision validation checks.
- Added a short note for any non-obvious linguistic decisions.

## Review Criteria

A translation change is ready when:

- concept mapping is unambiguous,
- parser behavior remains stable,
- tests cover the new forms,
- docs mention major tradeoffs or aliases.
