## Usage

The project provides several independent modules.

## Related Docs

- Quick start: [README.md](README.md)
- Detailed reference: [docs/README.md](docs/README.md)

## Numerals

```python
from multilingualprogramming.numeral.mp_numeral import MPNumeral

num1 = MPNumeral("VII")
num2 = MPNumeral("III")
print(num1 + num2)  # X
```

## Keywords

```python
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry

registry = KeywordRegistry()
print(registry.get_keyword("COND_IF", "fr"))  # si
```

## Date/Time

```python
from multilingualprogramming.datetime.mp_date import MPDate

d = MPDate.from_string("15-Janvier-2024")
print(d.to_string("en"))
```

## Lexer

```python
from multilingualprogramming.lexer.lexer import Lexer

lexer = Lexer("if x > 5:\n    print(x)", language="en")
tokens = lexer.tokenize()
print(tokens)
```

## Execute a Program

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

## Parse and Inspect AST

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


