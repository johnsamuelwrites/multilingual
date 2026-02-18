# multilingual
Not yet another programming language. A multilingual one.

> **One programming model. Many human languages.**  
> Write code in your language while keeping a shared semantic core.

## Why Multilingual

- **Language-inclusive syntax**: Use localized keywords and built-in aliases (for example, `intervalle`, `rango`, `intervallo`).
- **Single execution pipeline**: Same flow for every language: lexer -> parser -> semantic checks -> Python codegen -> runtime.
- **Data-driven extensibility**: Add languages by updating registries/resources, not by rewriting parser/codegen logic.
- **REPL-first experience**: Start quickly, switch languages live, inspect keywords/operators from inside REPL.

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
# or
pip install .
```

### 2. Use the REPL (interactive mode)

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

REPL commands:

- `:help` show commands
- `:language <code>` switch language
- `:python` toggle generated Python display
- `:reset` clear session state
- `:kw [XX]` show language keywords
- `:ops [XX]` show operators and symbols
- `:q` exit

Note: selected universal built-ins (for example `range`, `len`, `sum`) support localized aliases while keeping the universal names available.

### 3. Execute and inspect programs

Execution/transpilation examples and AST parsing examples are in [USAGE.md](USAGE.md).

## What You Can Use

- Numerals across scripts: `MPNumeral`, `UnicodeNumeral`, `RomanNumeral`
- Extended numerals: `ComplexNumeral`, `FractionNumeral`, `NumeralConverter`
- Keyword model: `KeywordRegistry`, `KeywordValidator`
- Date/time: `MPDate`, `MPTime`, `MPDatetime`
- Frontend: `Lexer`, `Parser`, AST nodes, `SemanticAnalyzer`
- Runtime: `PythonCodeGenerator`, `RuntimeBuiltins`, `ProgramExecutor`, `REPL`

Supported pilot languages: English, French, Spanish, German, Italian, Portuguese, Hindi, Arabic, Bengali, Tamil, Chinese (Simplified), Japanese.

## Run Examples

See [USAGE.md](USAGE.md) for the complete runnable examples list.

## Documentation

- Usage guide: [USAGE.md](USAGE.md)
- Examples guide: [examples/README.md](examples/README.md)
- Detailed reference: [docs/README.md](docs/README.md)
- Guide complet en francais: [docs/programmation_fr.md](docs/programmation_fr.md)
- Language onboarding guide: [docs/language_onboarding.md](docs/language_onboarding.md)

## Development

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
