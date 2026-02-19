# multilingual
Not yet another programming language. A multilingual one.

> **One programming model. Many human languages.**  
> Write code in your language while keeping a shared semantic core.

## Motivation

- Problem: programming is still heavily bound to English-centric syntax and keywords.
- Idea: keep one semantic core, but expose it through multiple human languages.
- Today: this is a small but working prototype; you can already write and run programs in English, French, Spanish, and other supported languages.

## Project Positioning

- This is not a beginner-only teaching DSL.
- This project targets broad Python-compatible semantics with localized language surfaces.
- Goal: language-inclusive authoring without fragmenting runtime behavior.

## Who Is This For?

`multilingual` is for teachers, language enthusiasts, programming-language hobbyists, and people exploring LLM-assisted coding workflows across multiple human languages.

## Why Multilingual

- **Language-inclusive syntax**: Use localized keywords and built-in aliases (for example, `intervalle`, `rango`, `intervallo`).
- **Single execution pipeline**: Same flow for every language: lexer -> parser -> semantic checks -> Python codegen -> runtime.
- **Data-driven extensibility**: Add languages by updating registries/resources, not by rewriting parser/codegen logic.
- **REPL-first experience**: Start quickly, switch languages live, inspect keywords/operators from inside REPL.

### Pipeline Illustration

![Multilingual pipeline with surface normalization](docs/assets/multilingual_pipeline_surface.svg)

## What This Is / Is Not

- `Is`: a shared-semantics multilingual programming model.
- `Is`: a research/prototyping platform for localization-aware language tooling.
- `Is not`: a claim that syntax translation alone solves all onboarding barriers.
- `Is not`: a replacement for English-heavy ecosystem docs, examples, and tooling (yet).

## Current Limitations

- Localized keywords can still feel unnatural in some languages because grammar/word order is mostly shared.
- A small declarative surface-normalization layer now supports selected alternate phrasing patterns, but coverage is still limited.
- Standard library/module APIs mostly stay canonical Python names; localization is focused on keywords and selected builtins.

Details:
- Word order and naturalness: [docs/word_order_and_naturalness.md](docs/word_order_and_naturalness.md)
- Stdlib localization boundaries: [docs/stdlib_localization.md](docs/stdlib_localization.md)

## Quick Start

Source files for this language use the `.ml` extension (for example: `hello.ml`).

### 1. Install

```bash
pip install -r requirements.txt
# or
pip install .
```

### 2. Hello World In Multiple Languages

```text
# English
print("Hello world")

# French
afficher("Bonjour le monde")

# Spanish (another language example)
imprimir("Hola mundo")

# Japanese
表示("こんにちは世界")

```

### 3. Use the REPL (interactive mode)

Start REPL:

```bash
# 1) Default mode (English keywords)
python -m multilingualprogramming repl

# 2) French mode
python -m multilingualprogramming repl --lang fr

# Optional: show generated Python while executing
python -m multilingualprogramming repl --show-python
```

Inside the REPL, type code and press Enter to execute.

Default mode example (English):

```text
>>> let total = 0
>>> for i in range(4):
...     total = total + i
...
>>> print(total)
6
```

French mode example:

```text
>>> soit somme = 0
>>> pour i dans intervalle(4):
...     somme = somme + i
...
>>> afficher(somme)
6
```

French phrase aliases are also supported:

```text
si x:
    afficher("ok")
sinon si y:
    afficher("fallback")

pour chaque i dans intervalle(3):
    afficher(i)
```

REPL commands:

- `:help` show commands
- `:language <code>` switch language
- `:python` toggle generated Python display
- `:reset` clear session state
- `:kw [XX]` show language keywords
- `:ops [XX]` show operators and symbols
- `:q` exit

Note: selected universal built-ins (for example `range`, `len`, `sum`) support localized aliases while keeping the universal names available.

### 4. Execute and inspect programs

Execution/transpilation examples and AST parsing examples are in [USAGE.md](USAGE.md).

### 5. Run A `.ml` Source File

Create a file, for example `hello.ml`:

```text
print("Hello world")
```

Run it:

```bash
python -m multilingualprogramming run hello.ml
```

Optional (force language instead of auto-detect):

```bash
python -m multilingualprogramming run hello.ml --lang fr
```

## Roadmap (Short)

- v0 (today): toy-but-working interpreter/transpiler, multiple languages, core constructs, REPL, and a tested end-to-end pipeline.
- next: better tooling, IDE support, more languages, a clearer formal spec, and potential LLM-assisted code translation workflows.

## What You Can Use

- Numerals across scripts: `MPNumeral`, `UnicodeNumeral`, `RomanNumeral`
- Extended numerals: `ComplexNumeral`, `FractionNumeral`, `NumeralConverter`
- Keyword model: `KeywordRegistry`, `KeywordValidator`
- Date/time: `MPDate`, `MPTime`, `MPDatetime`
- Frontend: `Lexer`, `Parser`, AST nodes, `SemanticAnalyzer`
- Runtime: `PythonCodeGenerator`, `RuntimeBuiltins`, `ProgramExecutor`, `REPL`

Additional syntax now supported:

- Type annotations (`x: int`, `def f(x: int) -> str`)
- Set literals (`{1, 2, 3}`)
- Multiple context managers (`with A() as a, B() as b`)
- Dictionary unpacking (`{**d1, **d2}`)
- Hex/oct/bin literals (`0xFF`, `0o77`, `0b101`)
- Scientific notation (`1.5e-3`)
- Async/await (`async def`, `await ...`)
- Walrus operator (`:=`)

Supported pilot languages: English, French, Spanish, German, Italian, Portuguese, Hindi, Arabic, Bengali, Tamil, Chinese (Simplified), Japanese.

## Run Examples

See [examples/README.md](examples/README.md) for narrative `.ml` examples
(English/French equivalents) and runnable commands.

### Japanese Surface Syntax Example

These two files compute the same result (`15`) using canonical and alternate
surface loop phrasing:

- Surface form: `examples/surface_for_ja.ml`
- Canonical form: `examples/surface_for_ja_canonical.ml`

Run:

```bash
python -m multilingualprogramming run examples/surface_for_ja.ml --lang ja
python -m multilingualprogramming run examples/surface_for_ja_canonical.ml --lang ja
```

### Semantic Equivalence (English vs French)

These two snippets are semantically equivalent:

English (`examples/arithmetics_en.ml`):

```text
let a = 10
let b = 3
print("a + b =", a + b)
```

French (`examples/arithmetics_fr.ml`):

```text
soit a = 10
soit b = 3
afficher("a + b =", a + b)
```

## Documentation

Use this README for setup and workflow; use `docs/` for design rationale and policy details.

- Usage guide: [USAGE.md](USAGE.md)
- Examples guide: [examples/README.md](examples/README.md)
- Detailed reference: [docs/README.md](docs/README.md)
- Design overview: [docs/design.md](docs/design.md)
- Related work and differentiation: [docs/related_work.md](docs/related_work.md)
- Word order and syntax naturalness notes: [docs/word_order_and_naturalness.md](docs/word_order_and_naturalness.md)
- Standard library localization strategy: [docs/stdlib_localization.md](docs/stdlib_localization.md)
- Translation governance guide: [docs/translation_guidelines.md](docs/translation_guidelines.md)
- Guide complet en francais: [docs/programmation_fr.md](docs/programmation_fr.md)
- Language onboarding guide: [docs/language_onboarding.md](docs/language_onboarding.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## Development

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
