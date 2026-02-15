# multilingualprogramming

Python library for multilingual programming primitives:

- Numerals across scripts (`MPNumeral`, `UnicodeNumeral`, `RomanNumeral`)
- Extended numerals (`ComplexNumeral`, `FractionNumeral`, `NumeralConverter`)
- Multilingual keyword registry and validation (`KeywordRegistry`, `KeywordValidator`)
- Multilingual date/time (`MPDate`, `MPTime`, `MPDatetime`)
- Prototype multilingual lexer (`Lexer`, `Token`, `TokenType`)

Current version: `0.2.0`

## Installation

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install .
```

## Quick Start

```python
from multilingualprogramming.numeral.mp_numeral import MPNumeral
from multilingualprogramming.datetime.mp_date import MPDate
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry

# Numerals
print(MPNumeral("VII") + MPNumeral("III"))   # X
print(MPNumeral("123") + MPNumeral("4"))     # 127

# Date parsing/formatting
d = MPDate.from_string("15-January-2024")
print(d.to_string("fr"))

# Keyword lookup
registry = KeywordRegistry()
print(registry.get_keyword("COND_IF", "en"))  # if
print(registry.get_keyword("COND_IF", "fr"))  # si
```

## Examples

Run examples with:

```bash
python -m examples.arithmetic
python -m examples.numeral_extended
python -m examples.keywords
python -m examples.datetime_example
python -m examples.lexer_example
```

See `examples/README.md` for details.

## Development

Run tests:

```bash
python -m pytest -q
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

## License

- Code: GPLv3+.
- Documentation/content: CC BY-SA 4.0.
