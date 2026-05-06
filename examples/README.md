## Narrative Source Examples

This folder includes semantically equivalent source programs in different
human languages. They are designed to show the core project idea quickly.

Repository examples now use `.multi` throughout. The runtime still accepts legacy `.ml` files for backward compatibility.

## 1. Hello World In `.multi`

- English: `examples/hello_en.multi`
- French: `examples/hello_fr.multi`

Run:

```bash
python -m multilingualprogramming run examples/hello_en.multi --lang en
python -m multilingualprogramming run examples/hello_fr.multi --lang fr
```

## 2. Arithmetic Equivalence

- English: `examples/arithmetics_en.multi`
- French: `examples/arithmetics_fr.multi`

Run:

```bash
python -m multilingualprogramming run examples/arithmetics_en.multi --lang en
python -m multilingualprogramming run examples/arithmetics_fr.multi --lang fr
```

## 3. Simple CLI Tool

Small realistic example: collect user input and compute invoice total.

- English: `examples/cli_tool_en.multi`
- French: `examples/cli_tool_fr.multi`

Run:

```bash
python -m multilingualprogramming run examples/cli_tool_en.multi --lang en
python -m multilingualprogramming run examples/cli_tool_fr.multi --lang fr
```

## 4. Tiny Data Processing Script

Small realistic example: filter data and compute average.

- English: `examples/data_processing_en.multi`
- French: `examples/data_processing_fr.multi`

Run:

```bash
python -m multilingualprogramming run examples/data_processing_en.multi --lang en
python -m multilingualprogramming run examples/data_processing_fr.multi --lang fr
```

## 5. Japanese Surface Syntax Example

These two programs compute the same result with different loop phrasing.

- Surface form: `examples/surface_for_ja.multi`
- Canonical form: `examples/surface_for_ja_canonical.multi`

Run:

```bash
python -m multilingualprogramming run examples/surface_for_ja.multi --lang ja
python -m multilingualprogramming run examples/surface_for_ja_canonical.multi --lang ja
```

## 6. Spanish And Portuguese Surface Syntax Examples

These files demonstrate iterable-first loop normalization in Romance languages.

- Spanish surface: `examples/surface_for_es.multi`
- Spanish canonical: `examples/surface_for_es_canonical.multi`
- Portuguese surface: `examples/surface_for_pt.multi`
- Portuguese canonical: `examples/surface_for_pt_canonical.multi`

Run:

```bash
python -m multilingualprogramming run examples/surface_for_es.multi --lang es
python -m multilingualprogramming run examples/surface_for_es_canonical.multi --lang es
python -m multilingualprogramming run examples/surface_for_pt.multi --lang pt
python -m multilingualprogramming run examples/surface_for_pt_canonical.multi --lang pt
```

## 7. Cross-Language Import Examples

These examples import source modules across languages from shared packages:

- Preferred `.multi` package initializer: `examples/crosslingual_multi/__init__.multi`
- Preferred `.multi` French module: `examples/crosslingual_multi/fr_math.multi`
- Preferred `.multi` English module: `examples/crosslingual_multi/en_text.multi`
- Preferred `.multi` English main: `examples/cross_import_main_en.multi`
- Legacy package initializer: `examples/crosslingual/__init__.multi`
- Legacy French module: `examples/crosslingual/fr_math.multi`
- Legacy English module: `examples/crosslingual/en_text.multi`
- Legacy English main: `examples/cross_import_main_en_legacy.multi`
- Legacy French main: `examples/cross_import_main_fr.multi`

Run:

```bash
python -m multilingualprogramming run examples/cross_import_main_en.multi --lang en
python -m multilingualprogramming run examples/cross_import_main_en_legacy.multi --lang en
python -m multilingualprogramming run examples/cross_import_main_fr.multi --lang fr
```

Expected output for the preferred `.multi` English entry program:

```text
crosslingual-imports-multi
total=42
```

Expected output for the legacy cross-language entry programs:

```text
crosslingual-imports
total=42
```

and:

```text
crosslingual-imports
total=22
```

for the French entry program.

## 8. Complete Feature Examples (EN/FR/ES)

These examples use a broad set of supported features in one file:

- imports (`import`, `from ... import ... as ...`)
- variables, loops (`for`, `while`)
- functions and classes
- list comprehensions
- boolean logic + `assert`
- `try` / `except` / `finally`

Compatibility baseline reference:
- `docs/compatibility_matrix.md`

Files:

- English: `examples/complete_features_en.multi`
- French: `examples/complete_features_fr.multi`
- Spanish: `examples/complete_features_es.multi`

Run:

```bash
python -m multilingualprogramming run examples/complete_features_en.multi --lang en
python -m multilingualprogramming run examples/complete_features_fr.multi --lang fr
python -m multilingualprogramming run examples/complete_features_es.multi --lang es
```

## Python Module Examples

The original Python-module examples are still available:

```bash
python -m examples.arithmetic
python -m examples.numeral_extended
python -m examples.keywords
python -m examples.datetime_example
python -m examples.lexer_example
python -m examples.parser_example
python -m examples.ast_example
python -m examples.multilingual_parser_example
python -m examples.codegen_example
python -m examples.multilingual_codegen_example
python -m examples.semantic_example
python -m examples.executor_example
```
