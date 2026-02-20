## Narrative `.ml` Examples

This folder includes semantically equivalent source programs in different
human languages. They are designed to show the core project idea quickly.

## 1. Arithmetic Equivalence

- English: `examples/arithmetics_en.ml`
- French: `examples/arithmetics_fr.ml`

Run:

```bash
python -m multilingualprogramming run examples/arithmetics_en.ml --lang en
python -m multilingualprogramming run examples/arithmetics_fr.ml --lang fr
```

## 2. Simple CLI Tool

Small realistic example: collect user input and compute invoice total.

- English: `examples/cli_tool_en.ml`
- French: `examples/cli_tool_fr.ml`

Run:

```bash
python -m multilingualprogramming run examples/cli_tool_en.ml --lang en
python -m multilingualprogramming run examples/cli_tool_fr.ml --lang fr
```

## 3. Tiny Data Processing Script

Small realistic example: filter data and compute average.

- English: `examples/data_processing_en.ml`
- French: `examples/data_processing_fr.ml`

Run:

```bash
python -m multilingualprogramming run examples/data_processing_en.ml --lang en
python -m multilingualprogramming run examples/data_processing_fr.ml --lang fr
```

## 4. Japanese Surface Syntax Example

These two programs compute the same result with different loop phrasing.

- Surface form: `examples/surface_for_ja.ml`
- Canonical form: `examples/surface_for_ja_canonical.ml`

Run:

```bash
python -m multilingualprogramming run examples/surface_for_ja.ml --lang ja
python -m multilingualprogramming run examples/surface_for_ja_canonical.ml --lang ja
```

## 5. Spanish And Portuguese Surface Syntax Examples

These files demonstrate iterable-first loop normalization in Romance languages.

- Spanish surface: `examples/surface_for_es.ml`
- Spanish canonical: `examples/surface_for_es_canonical.ml`
- Portuguese surface: `examples/surface_for_pt.ml`
- Portuguese canonical: `examples/surface_for_pt_canonical.ml`

Run:

```bash
python -m multilingualprogramming run examples/surface_for_es.ml --lang es
python -m multilingualprogramming run examples/surface_for_es_canonical.ml --lang es
python -m multilingualprogramming run examples/surface_for_pt.ml --lang pt
python -m multilingualprogramming run examples/surface_for_pt_canonical.ml --lang pt
```

## 6. Cross-Language Import Examples

These examples import `.ml` modules across languages from a shared package:

- Package initializer: `examples/crosslingual/__init__.ml`
- French module: `examples/crosslingual/fr_math.ml`
- English module: `examples/crosslingual/en_text.ml`
- English main: `examples/cross_import_main_en.ml`
- French main: `examples/cross_import_main_fr.ml`

Run:

```bash
python -m multilingualprogramming run examples/cross_import_main_en.ml --lang en
python -m multilingualprogramming run examples/cross_import_main_fr.ml --lang fr
```

Expected output:

```text
crosslingual-imports
total=42
```

for the English entry program, and:

```text
crosslingual-imports
total=22
```

for the French entry program.

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
