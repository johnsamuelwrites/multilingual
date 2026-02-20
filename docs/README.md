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
- Italian
- Portuguese
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
- comprehensions (list, dict, generator), including nested `for` clauses
- default parameters, `*args`, `**kwargs`
- tuple unpacking
- decorators
- f-strings
- triple-quoted strings

Example (nested comprehension):

```text
let rows = [[1, 2], [3, 4]]
let flat = [x for row in rows for x in row]
print(flat)  # [1, 2, 3, 4]
```

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
- `:language <code>`
- `:python`
- `:reset`
- `:kw [XX]`
- `:ops [XX]`
- `:q`

## REPL Language Smoke Tests

Use these two snippets to quickly validate each language in REPL.

Snippet A (variables + print):

```text
<LET> x = 2
<LET> y = 3
<PRINT>(x + y)
```

Snippet B (for loop):

```text
<LET> total = 0
<FOR> i <IN> <RANGE_ALIAS>(4):
    total = total + i
<PRINT>(total)
```

Built-in aliases are also available for selected universal functions.
Both the universal name and localized alias work. Example (French):

```text
afficher(intervalle(4))
afficher(longueur([10, 20, 30]))
afficher(somme([1, 2, 3]))
```

Language-specific forms:

### English (`en`)

```text
let x = 2
let y = 3
print(x + y)

let total = 0
for i in range(4):
    total = total + i
print(total)
```

### French (`fr`)

```text
soit x = 2
soit y = 3
afficher(x + y)

soit somme = 0
pour i dans intervalle(4):
    somme = somme + i
afficher(somme)
```

### Spanish (`es`)

```text
sea x = 2
sea y = 3
imprimir(x + y)

sea suma = 0
para i en rango(4):
    suma = suma + i
imprimir(suma)
```

### German (`de`)

```text
sei x = 2
sei y = 3
ausgeben(x + y)

sei summe = 0
für i in bereich(4):
    summe = summe + i
ausgeben(summe)
```

### Italian (`it`)

```text
sia x = 2
sia y = 3
stampa(x + y)

sia totale = 0
per i in intervallo(4):
    totale = totale + i
stampa(totale)
```

### Portuguese (`pt`)

```text
seja x = 2
seja y = 3
imprimir(x + y)

seja soma = 0
para i em intervalo(4):
    soma = soma + i
imprimir(soma)
```

### Hindi (`hi`)

```text
मान x = 2
मान y = 3
छापो(x + y)

मान योग = 0
के_लिए i में परास(4):
    योग = योग + i
छापो(योग)
```

### Arabic (`ar`)

```text
ليكن x = 2
ليكن y = 3
اطبع(x + y)

ليكن المجموع = 0
لكل i في مدى(4):
    المجموع = المجموع + i
اطبع(المجموع)
```

### Bengali (`bn`)

```text
ধরি x = 2
ধরি y = 3
ছাপাও(x + y)

ধরি মোট = 0
জন্য i মধ্যে পরিসর(4):
    মোট = মোট + i
ছাপাও(মোট)
```

### Tamil (`ta`)

```text
இருக்கட்டும் x = 2
இருக்கட்டும் y = 3
அச்சிடு(x + y)

இருக்கட்டும் மொத்தம் = 0
ஒவ்வொரு i இல் வரம்பு(4):
    மொத்தம் = மொத்தம் + i
அச்சிடு(மொத்தம்)
```

### Chinese (`zh`)

```text
令 x = 2
令 y = 3
打印(x + y)

令 总计 = 0
对于 i 里 范围(4):
    总计 = 总计 + i
打印(总计)
```

### Japanese (`ja`)

```text
変数 x = 2
変数 y = 3
表示(x + y)

変数 合計 = 0
毎 i 中 範囲(4):
    合計 = 合計 + i
表示(合計)
```

## Examples

Runnable examples are documented in:

- [examples/README.md](../examples/README.md)

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

- Project quick start: [README.md](../README.md)
- Design overview: [design.md](design.md)
- Core formal specification: [core_spec.md](core_spec.md)
- Frontend translation contracts: [frontend_contracts.md](frontend_contracts.md)
- Related work and differentiation: [related_work.md](related_work.md)
- Controlled language scope: [cnl_scope.md](cnl_scope.md)
- Evaluation plan: [evaluation_plan.md](evaluation_plan.md)
- Word order and syntax naturalness: [word_order_and_naturalness.md](word_order_and_naturalness.md)
- Standard library localization strategy: [stdlib_localization.md](stdlib_localization.md)
- Translation governance: [translation_guidelines.md](translation_guidelines.md)
- Usage snippets: [USAGE.md](../USAGE.md)
- Examples guide: [examples/README.md](../examples/README.md)
- French programming guide: [programmation_fr.md](programmation_fr.md)
- Language onboarding: [language_onboarding.md](language_onboarding.md)

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
