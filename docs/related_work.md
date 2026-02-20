# Related Work and Positioning

This project is positioned at the intersection of:

- multi-frontend compilation into a shared core
- syntax extensibility and macro-style surface design
- controlled natural-language-inspired frontend design

It does not claim novelty for the general idea of many languages mapping to one
core. The contribution is a coordinated multilingual frontend family with
grammar-sensitive normalization targeting one formal core.

## 1) Multi-Frontend Core and IR Work

Established systems already map multiple source languages to shared internal
representations (for example LLVM-style IR ecosystems, GCC internals, and core
calculi such as lambda calculus/System F in language theory contexts).

Alignment with this project:

- many-to-one mapping from surface language to shared core
- separation of frontend concerns from backend/codegen

Difference in focus:

- this project coordinates multiple natural-language-inspired frontend variants
  within one family, rather than unrelated general-purpose languages.

## 2) Syntactic Extensibility and Macro Ecosystems

Work on pluggable syntax and macro systems demonstrates that one semantic core
can support many surface forms (for example Racket `#lang`, macro-centric
language extension work, and syntax-skin style ideas).

Alignment with this project:

- core-first architecture
- syntactic variation layered on stable semantics

Difference in focus:

- this project emphasizes multilingual frontends and data-driven language
  onboarding, not a general macro metaprogramming framework.

## 3) Controlled Language, NLP Boundaries, and Logic

Community feedback correctly highlights that once syntax approaches natural
language, the hard problems shift from classic parsing to linguistic ambiguity,
morphology, and intent extraction.

Project stance:

- explicitly controlled subsets per language (CNL-style)
- declarative and test-backed normalization rules
- deterministic parsing and forward compilation
- no claim of full natural-language understanding

## Boundary Clarification

The architecture draws the boundary as:

- Parsing/frontends: `CS_lang -> CoreAST`
- Core typing boundary: `CoreAST -> CoreIRProgram`
- Codegen/runtime: `CoreIRProgram -> Python -> execution`

The project deliberately does not promise lossless round-tripping from core to
original surface syntax.

## References

- [Reddit discussion thread](https://www.reddit.com/r/ProgrammingLanguages/comments/1r860hw/multilingual_a_programming_language_with_one/)
- [Hedy language](https://www.hedy.org/)
- [ALGOL 68](https://en.wikipedia.org/wiki/ALGOL_68)
- [Non-English-based programming languages](https://en.wikipedia.org/wiki/Non-English-based_programming_languages)
- [Rouille](https://github.com/bnjbvr/rouille)
