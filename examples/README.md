## Running Examples

All examples are runnable as modules from the repository root.

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

## Example Overview

### Phase 1 — Foundation

- `examples/arithmetic.py`: base numeral operations with Roman and Unicode numerals.
- `examples/numeral_extended.py`: complex numbers, fractions, conversion, and scientific notation.
- `examples/keywords.py`: keyword lookups and language detection.
- `examples/datetime_example.py`: multilingual date/time parsing and formatting.
- `examples/lexer_example.py`: tokenization using multilingual keywords and Unicode operators.

### Phase 2 — Parser & Semantic Analysis

- `examples/parser_example.py`: full pipeline from source code to tokens to AST with pretty-printing.
- `examples/ast_example.py`: programmatic AST construction (building a factorial function as AST nodes).
- `examples/multilingual_parser_example.py`: the same factorial function parsed in all 10 pilot languages.
- `examples/semantic_example.py`: semantic analysis in all 10 pilot languages with both valid and invalid programs.

### Phase 3 — Code Generation & Runtime

- `examples/codegen_example.py`: code generation from multilingual AST to Python source, with numeral conversion.
- `examples/multilingual_codegen_example.py`: equivalent source transpiled to Python in all 10 pilot languages.
- `examples/executor_example.py`: execute equivalent programs in all 10 pilot languages through the full pipeline.
