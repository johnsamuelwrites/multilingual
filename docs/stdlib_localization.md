# Standard Library Localization Strategy

This document explains how `multilingual` handles localization beyond core keywords.

## Problem Statement

Localizing syntax keywords is straightforward compared to localizing library symbols such as `print`, `range`, `len`, and module APIs.

## Scope Layers

- **Language keywords**: grammar-level terms (`if`, `for`, `def`, etc.), mapped by concept.
- **Core builtins**: common runtime names (`print`, `range`, `len`, `sum`, ...).
- **Library APIs**: module/member names from Python stdlib and third-party ecosystems.

These layers must be treated differently.

## Current Behavior

- Keywords are localized via concept mapping.
- Selected builtins support localized aliases.
- Universal names remain valid and are never removed.
- Python stdlib module/member names are generally kept canonical.

## Compatibility Policy

- Canonical Python names are the interoperability baseline.
- Localized aliases are additive, not replacing canonical names.
- If conflict exists, canonical name wins for deterministic behavior.

## Design Rationale

- Preserves compatibility with Python ecosystem docs and examples.
- Reduces ambiguity and breakage in imports and runtime dispatch.
- Lets users mix localized authoring with globally recognized API names.

## Open Questions

- Should there be opt-in localized wrappers for selected stdlib modules?
- How should alias collisions be resolved across languages and scripts?
- How should error messages present canonical vs localized names?
