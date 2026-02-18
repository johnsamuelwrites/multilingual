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
