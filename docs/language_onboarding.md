# Adding a New Language (Data-Driven)

This project is designed so new programming languages can be added mainly by updating data files, not parser/codegen logic.

## Goal

Enable a new language code (for example `xx`) across:

- lexing and parsing (keyword recognition)
- semantic analysis error reporting
- runtime builtins and execution
- REPL command/help localization

## 1. Add Keyword Mappings

File: `multilingualprogramming/resources/usm/keywords.json`

1. Add the new code to `languages`.
2. For every concept in every category, add a translation key for the new language.

Important:

- All concepts must have a translation to keep validation complete.
- Prefer unique tokens per language to avoid ambiguity.
- Keep tokens identifier-safe (letters/underscores, no spaces).

Why this is enough:

- `KeywordRegistry` loads this file dynamically.
- `Lexer` detects/recognizes keywords through `KeywordRegistry`.
- `Parser` consumes concept tokens, so syntax support follows automatically.
- `RuntimeBuiltins` maps builtins from concept IDs, so execution picks up new language keywords automatically.

## 2. Add Parser/Semantic Error Messages

File: `multilingualprogramming/resources/parser/error_messages.json`

For each message key under `messages`, add the new language translation (same placeholders, e.g. `{token}`, `{line}`).

Why:

- `ErrorMessageRegistry.format()` reads this file dynamically and parser/semantic analyzer use it for diagnostics.

## 3. Add REPL Localization

File: `multilingualprogramming/resources/repl/commands.json`

Update:

1. `help_titles` for the language.
2. `messages` keys (`keywords_title`, `symbols_title`, `unsupported_language`).
3. `commands.<name>.aliases` for command words.
4. `commands.<name>.descriptions` for help text.

Why:

- REPL command parsing/help is fully catalog-driven from this JSON.

## 4. (Optional) Add Operator Description Localization

File: `multilingualprogramming/resources/usm/operators.json`

Add the new language under `description` where available.

Why:

- REPL `:symbols` uses these descriptions when present; otherwise it falls back to English.

## 5. Add Tests

Minimum recommended tests:

1. `tests/keyword_registry_test.py`
 - language appears in `get_supported_languages()`
 - concept lookups for representative keywords
2. `tests/executor_test.py`
 - one end-to-end program using new language keywords (`ProgramExecutor`)
3. `tests/error_messages_test.py`
 - new language included in "all messages have all languages" coverage

This validates lexer -> parser -> semantic -> codegen/runtime in one path.

## 6. Update Documentation

At minimum:

- `README.md` supported languages list
- `docs/README.md` supported languages list
- link this onboarding guide where relevant

## Validation Commands

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

For focused checks while iterating:

```bash
python -m pytest -q tests/keyword_registry_test.py tests/error_messages_test.py tests/executor_test.py tests/repl_test.py
```
