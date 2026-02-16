# multilingualprogramming

A Python framework for building programming languages that use **any human language** for keywords, identifiers, numerals, dates, and operators. Write code in English, French, Hindi, Arabic, Chinese, Japanese, and more — all backed by a Universal Semantic Model that maps programming concepts across 10 pilot languages.

Current version: `0.2.0`

## Features

### Phase 1 — Foundation

- **Numerals across scripts** — `MPNumeral`, `UnicodeNumeral`, `RomanNumeral` supporting arithmetic in any Unicode numeral system
- **Extended numerals** — `ComplexNumeral` (e.g. `"൩+൪i"`), `FractionNumeral` (Unicode vulgar fractions), `NumeralConverter` for cross-script conversion and scientific notation
- **Universal Semantic Model (USM)** — 43 keyword concepts across 10 languages, with `KeywordRegistry` for bidirectional lookup and `KeywordValidator` for ambiguity/completeness checks
- **Multilingual date/time** — `MPDate`, `MPTime`, `MPDatetime` parsing and formatting in any supported script (e.g. `"१५-जनवरी-२०२४"`)
- **Prototype lexer** — `Lexer` producing `Token` streams with INDENT/DEDENT, Unicode operators (`×`, `÷`, `≤`, `≥`, `≠`), multilingual string delimiters (`«»`, `「」`, `""`), and date literals

### Phase 2 — Parser & Semantic Analysis

- **Recursive-descent parser** — `Parser` consuming token streams and producing an AST, dispatching on `token.concept` for language-agnostic parsing
- **35 AST node classes** — `Program`, 7 literal types, 11 expression types, 11 statement types, 10 compound statement types, 2 import types, all with visitor pattern support
- **14-level operator precedence** — from logical OR down through power and primary expressions, with chained comparisons (`a < b < c`)
- **Semantic analyzer** — `SemanticAnalyzer` with `SymbolTable` and scope chain (global/function/class/block), detecting undefined names, const reassignment, break/continue/return/yield context errors
- **Multilingual error messages** — `ErrorMessageRegistry` with 16 error templates in all 10 languages, using `{placeholder}` substitution
- **AST pretty-printer** — `ASTPrinter` producing indented tree representations for debugging

### Phase 3 — Code Generation & Runtime

- **Python code generator** — `PythonCodeGenerator` transpiles the multilingual AST into valid Python 3 source, converting Unicode numerals (Devanagari, Arabic-Indic, Roman, etc.) to Python numeric literals
- **Runtime built-ins** — `RuntimeBuiltins` injects multilingual names for built-in functions (`afficher` -> `print`, `saisir` -> `input`, etc.) into the execution environment
- **Program executor** — `ProgramExecutor` provides the full pipeline: source -> lex -> parse -> semantic check -> generate Python -> execute, with captured output and error reporting
- **Interactive REPL** — `REPL` for interactive multilingual programming with persistent state across interactions, multi-line block support, and optional Python source display

### Supported Languages

| # | Language | Script | Direction |
|---|----------|--------|-----------|
| 1 | English | Latin | LTR |
| 2 | French | Latin | LTR |
| 3 | Spanish | Latin | LTR |
| 4 | German | Latin | LTR |
| 5 | Hindi | Devanagari | LTR |
| 6 | Arabic | Arabic | RTL |
| 7 | Bengali | Bengali | LTR |
| 8 | Tamil | Tamil | LTR |
| 9 | Chinese (Simplified) | Han | LTR |
| 10 | Japanese | Mixed (Kanji+Kana) | LTR |

## Installation

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install .
```

## Quick Start

### Numerals

```python
from multilingualprogramming import MPNumeral, NumeralConverter

print(MPNumeral("VII") + MPNumeral("III"))   # X
print(MPNumeral("१२३") + MPNumeral("४"))     # १२७
```

### Keywords

```python
from multilingualprogramming import KeywordRegistry

registry = KeywordRegistry()
print(registry.get_keyword("COND_IF", "en"))   # if
print(registry.get_keyword("COND_IF", "fr"))   # si
print(registry.get_keyword("COND_IF", "hi"))   # अगर
print(registry.get_keyword("COND_IF", "ar"))   # إذا
```

### Dates

```python
from multilingualprogramming import MPDate

d = MPDate.from_string("15-January-2024")
print(d.to_string("fr"))   # 15-Janvier-2024
print(d.to_string("hi"))   # १५-जनवरी-२०२४
```

### Lexing, Parsing & Semantic Analysis

```python
from multilingualprogramming import Lexer, Parser, ASTPrinter, SemanticAnalyzer

source = """\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

# Tokenize
tokens = Lexer(source, language="en").tokenize()

# Parse into AST
tree = Parser(tokens, source_language="en").parse()

# Pretty-print
print(ASTPrinter().print(tree))

# Semantic analysis
errors = SemanticAnalyzer(source_language="en").analyze(tree)
```

The same code works in French:

```python
source_fr = """\
déf factoriel(n):
    si n <= 1:
        retour 1
    retour n * factoriel(n - 1)
"""

tokens = Lexer(source_fr, language="fr").tokenize()
tree = Parser(tokens, source_language="fr").parse()
```

Or Hindi:

```python
source_hi = """\
परिभाषा फैक्टोरियल(न):
    अगर न <= १:
        वापसी १
    वापसी न * फैक्टोरियल(न - १)
"""

tokens = Lexer(source_hi, language="hi").tokenize()
tree = Parser(tokens, source_language="hi").parse()
```

### Execute Multilingual Programs

```python
from multilingualprogramming import ProgramExecutor

# Execute English code
result = ProgramExecutor(language="en").execute("""\
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(10))
""")
print(result.output)   # 3628800

# Execute French code
result = ProgramExecutor(language="fr").execute("""\
déf factoriel(n):
    si n <= 1:
        retour 1
    retour n * factoriel(n - 1)

afficher(factoriel(6))
""")
print(result.output)   # 720

# Transpile to Python without executing
python_code = ProgramExecutor(language="zh").transpile("""\
函数 加法(甲, 乙):
    返回 甲 + 乙
""")
print(python_code)
# def 加法(甲, 乙):
#     return (甲 + 乙)
```

## Examples

Run examples with:

```bash
python -m examples.arithmetic           # Basic numeral operations
python -m examples.numeral_extended     # Complex numbers, fractions, conversions
python -m examples.keywords             # Keyword lookups and language detection
python -m examples.datetime_example     # Multilingual date/time
python -m examples.lexer_example        # Tokenization with multilingual keywords
python -m examples.parser_example       # Full pipeline: source -> tokens -> AST
python -m examples.ast_example          # Programmatic AST construction
python -m examples.multilingual_parser_example  # Same program parsed in all 10 pilot languages
python -m examples.codegen_example      # Code generation: multilingual AST -> Python
python -m examples.multilingual_codegen_example  # Equivalent source transpiled in all 10 pilot languages
python -m examples.semantic_example     # Semantic analysis in all 10 pilot languages
python -m examples.executor_example     # Execute equivalent programs in all 10 pilot languages
```

See `examples/README.md` for details.

## Architecture

```
multilingualprogramming/
├── numeral/          # MPNumeral, UnicodeNumeral, RomanNumeral, ComplexNumeral, FractionNumeral
├── keyword/          # KeywordRegistry, KeywordValidator (USM concept ↔ keyword mapping)
├── datetime/         # MPDate, MPTime, MPDatetime (multilingual date parsing/formatting)
├── lexer/            # Lexer, Token, TokenType, SourceReader
├── parser/           # Parser, AST nodes, SemanticAnalyzer, ASTPrinter, ErrorMessageRegistry
├── codegen/          # PythonCodeGenerator, RuntimeBuiltins, ProgramExecutor, REPL
├── resources/
│   ├── usm/          # keywords.json, operators.json, schema.json
│   ├── datetime/     # months.json, weekdays.json, formats.json, eras.json
│   └── parser/       # error_messages.json (16 templates × 10 languages)
└── exceptions.py     # All custom exception types
```

## Development

Run tests:

```bash
python -m pytest -q
```

Run with verbose output:

```bash
python -m pytest tests/ -v --tb=short
```

Run pylint:

```bash
python -m pylint multilingualprogramming tests examples
```

## Resources

- `resources/README.md` contains references and resource notes.

## Contributing

- Add or improve multilingual resource data under `multilingualprogramming/resources/`.
- Add tests in `tests/` for new behavior.
- Keep examples in `examples/` runnable with `python -m ...`.
- See `PLAN.md` for the Phase 1 implementation plan and roadmap context.

## License

- Code: GPLv3+.
- Documentation/content: CC BY-SA 4.0.
