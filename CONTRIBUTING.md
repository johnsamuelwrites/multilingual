# Contributing

Thanks for your interest in `multilingual`.
This project is experimental and contributions of all sizes are welcome.

## What We Welcome

- new human language support
- keyword/translation fixes
- tests, docs, and examples
- parser/runtime improvements

Small, focused pull requests are preferred.

## Add A New Human Language

## 1. Add language metadata and keywords

- Update supported languages and concept mappings in:
  - `multilingualprogramming/resources/usm/keywords.json`
- For each concept (`COND_IF`, `FUNC_DEF`, `RETURN`, etc.), add your language form.

Keyword localization is concept-driven, so most language additions do not require parser grammar rewrites.

## 2. Add built-in aliases (optional but recommended)

- Update built-in alias mappings in:
  - `multilingualprogramming/resources/usm/builtins_aliases.json`

This enables localized names for selected runtime built-ins.

## 3. Add/adjust operator or delimiter localization (if needed)

- Update:
  - `multilingualprogramming/resources/usm/operators.json`

Only needed when introducing additional symbol variants.

## 4. Grammar and parser changes (only when adding new concepts/syntax)

If your contribution adds a new semantic concept or syntax form (not just a translation), update:

- parser logic:
  - `multilingualprogramming/parser/parser.py`
- AST model:
  - `multilingualprogramming/parser/ast_nodes.py`
- semantic checks:
  - `multilingualprogramming/parser/semantic_analyzer.py`
- code generation:
  - `multilingualprogramming/codegen/python_generator.py`

## 5. Add tests

At minimum, add or update tests in:

- `tests/keyword_registry_test.py` (new language/concept mapping)
- `tests/lexer_test.py` (tokenization in your language)
- `tests/parser_test.py` (core constructs parse correctly)

When relevant, also update:

- `tests/python_generator_test.py`
- `tests/semantic_analyzer_test.py`
- `tests/repl_test.py`

## 6. Update docs/examples

- Add short examples in:
  - `README.md`
  - `docs/README.md`
  - `docs/programmation_fr.md` (or add equivalent docs for your language)

## Local Checks

Run before submitting:

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## Expectations

- Be respectful and practical.
- Keep changes scoped and explain the motivation.
- Include tests with behavior changes.
- It is okay to submit partial improvements; this is an evolving project and feedback is encouraged.
