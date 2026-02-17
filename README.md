# multilingualprogramming

A Python framework for multilingual programming: write source code using keywords and numerals from multiple human languages while keeping one common semantic model.

Current version: `0.3.0`

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
# or
pip install .
```

### 2. Use the REPL (interactive mode)

```bash
# Start REPL
python -m multilingualprogramming repl

# Start REPL with a language
python -m multilingualprogramming repl --lang fr

# Start REPL and show generated Python
python -m multilingualprogramming repl --show-python
```

Inside the REPL:

- `:help` show commands
- `:lang <code>` switch language
- `:python` toggle generated Python display
- `:reset` clear session state
- `:quit` exit

French REPL example:

```text
soit somme = 0
pour i dans intervalle(4):
    somme = somme + i
afficher(somme)
```

Note: selected universal built-ins (for example `range`, `len`, `sum`) support localized aliases while keeping the universal names available.

### 3. Execute a program

```python
from multilingualprogramming import ProgramExecutor

result = ProgramExecutor(language="en").execute("""\
def add(a, b):
    return a + b
print(add(2, 3))
""")

print(result.success)  # True
print(result.output)   # 5
```

### 4. Parse and inspect AST

```python
from multilingualprogramming import Lexer, Parser, ASTPrinter

source = """\
def square(x):
    return x * x
"""

tokens = Lexer(source, language="en").tokenize()
ast = Parser(tokens, source_language="en").parse()
print(ASTPrinter().print(ast))
```

## What You Can Use

- Numerals across scripts: `MPNumeral`, `UnicodeNumeral`, `RomanNumeral`
- Extended numerals: `ComplexNumeral`, `FractionNumeral`, `NumeralConverter`
- Keyword model: `KeywordRegistry`, `KeywordValidator`
- Date/time: `MPDate`, `MPTime`, `MPDatetime`
- Frontend: `Lexer`, `Parser`, AST nodes, `SemanticAnalyzer`
- Runtime: `PythonCodeGenerator`, `RuntimeBuiltins`, `ProgramExecutor`, `REPL`

Supported pilot languages: English, French, Spanish, German, Italian, Portuguese, Hindi, Arabic, Bengali, Tamil, Chinese (Simplified), Japanese.

## Run Examples

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

## Documentation

- Usage guide: `USAGE.md`
- Examples guide: `examples/README.md`
- Detailed reference: `docs/README.md`
- Language onboarding guide: `docs/language_onboarding.md`

## Development

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
