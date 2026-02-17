# multilingualprogramming Reference

This document is the detailed reference for the project.

## Overview

`multilingualprogramming` is a Python framework for multilingual programming. It supports writing source code with keywords, numerals, and literals from multiple human languages while mapping everything to a shared semantic model.

Current version: `0.3.0`

## Supported Languages

- English
- French
- Spanish
- German
- Hindi
- Arabic
- Bengali
- Tamil
- Chinese (Simplified)
- Japanese

## Core Components

### Numeral System

- `MPNumeral`
- `UnicodeNumeral`
- `RomanNumeral`
- `ComplexNumeral`
- `FractionNumeral`
- `NumeralConverter`

Key capabilities:

- arithmetic across numeral scripts
- conversion across scripts
- Unicode fraction handling
- scientific notation helpers

### Keyword and Concept Model

- `KeywordRegistry`
- `KeywordValidator`

Key capabilities:

- concept -> keyword lookup (`COND_IF` -> `if`, `si`, etc.)
- keyword -> concept reverse lookup
- supported-language discovery
- ambiguity/completeness checks

### Date and Time

- `MPDate`
- `MPTime`
- `MPDatetime`

Key capabilities:

- multilingual parsing and formatting
- script-aware numeric rendering

### Frontend (Lexing, Parsing, Semantic Analysis)

- `Lexer`
- `Parser`
- AST node model in `multilingualprogramming/parser/ast_nodes.py`
- `SemanticAnalyzer`
- `ASTPrinter`

Key capabilities:

- Unicode-aware tokenization
- AST generation from multilingual source
- scope and symbol checks
- multilingual semantic error messages

### Runtime and Execution

- `PythonCodeGenerator`
- `RuntimeBuiltins`
- `ProgramExecutor`
- `REPL`

Key capabilities:

- transpile multilingual AST to Python source
- execute full pipeline: source -> tokens -> AST -> checks -> Python -> runtime
- inject multilingual runtime builtins
- interactive REPL with language switching and Python-preview mode

## Language Features

The implementation includes support for:

- variable declarations and assignment
- control flow (`if/else`, loops)
- functions and classes
- imports
- assertions
- chained assignment
- slices (`a[1:3]`, `a[::-1]`)
- comprehensions (list, dict, generator)
- default parameters, `*args`, `**kwargs`
- tuple unpacking
- decorators
- f-strings
- triple-quoted strings

## API Entry Points

Most commonly used imports:

```python
from multilingualprogramming import (
    MPNumeral,
    KeywordRegistry,
    MPDate,
    Lexer,
    Parser,
    SemanticAnalyzer,
    ASTPrinter,
    PythonCodeGenerator,
    ProgramExecutor,
    REPL,
)
```

## CLI and REPL

Run interactive mode:

```bash
python -m multilingualprogramming repl
python -m multilingualprogramming repl --lang fr
python -m multilingualprogramming repl --show-python
```

REPL commands:

- `:help`
- `:lang <code>`
- `:python`
- `:reset`
- `:quit`

## Examples

Runnable examples are documented in:

- `examples/README.md`

Run all examples from repository root:

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

## Development

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## Related Docs

- Project quick start: `../README.md`
- Usage snippets: `../USAGE.md`
- Examples guide: `../examples/README.md`

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
