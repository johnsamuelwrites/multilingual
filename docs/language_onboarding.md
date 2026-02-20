# Adding a New Language (Data-Driven)

This project is designed so new programming languages can be added mainly by updating data files, not parser/codegen logic.

Language onboarding follows a controlled-language policy: add deterministic,
testable surface forms only. See [cnl_scope.md](cnl_scope.md).

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

## 5. Add Built-in Aliases (Optional)

File: `multilingualprogramming/resources/usm/builtins_aliases.json`

Add localized aliases for selected universal builtins (for example `range`, `len`, `sum`).
The universal English built-in name remains available; aliases are additive.

Why:

- `RuntimeBuiltins` loads this file dynamically.
- Users can write either universal names or localized aliases in programs/REPL.

## 6. Add Surface Syntax Patterns (Optional)

File: `multilingualprogramming/resources/usm/surface_patterns.json`

Use this file when keyword translation alone is not enough for natural phrasing.
Rules are declarative and normalize alternate surface token order into canonical
concept order before parser grammar runs.

Validation is enforced at load time by `validate_surface_patterns_config`
(`multilingualprogramming/parser/surface_normalizer.py`), including:

- rule/template schema shape
- language support checks
- exactly one of `normalize_to` / `normalize_template`
- slot-reference consistency between `pattern` captures and output rewrite

Typical use:

- iterable-first `for` headers
- language-specific particles around loop/condition clauses
- alternate phrase forms that still map to one core AST

Keep rules narrow and test-backed. Prefer additive normalization over parser forks.

### How This Connects To The Pipeline

1. `Lexer` tokenizes source and resolves known keywords to concepts.
2. `SurfaceNormalizer` matches token-level surface rules.
3. Matched rules rewrite tokens into canonical concept order.
4. `Parser` consumes rewritten tokens with existing grammar.

Important: surface patterns do not replace lexing. They operate on lexer output.

### Rule Model

`surface_patterns.json` has two top-level sections:

- `templates`: reusable canonical rewrites
- `patterns`: language-scoped matching rules

Each pattern must include:

- `name`
- `language`
- `pattern` (what to match)
- exactly one of:
 - `normalize_template` (reference a template)
 - `normalize_to` (inline rewrite)

### Pattern Token Kinds

Allowed `pattern` kinds:

- `expr`: capture an expression span into a slot (for example `iterable`)
- `identifier`: capture one identifier token into a slot (for example `target`)
- `keyword`: require a specific concept token (for example `LOOP_FOR`)
- `delimiter`: require a delimiter token (for example `:`)
- `literal`: require a literal token value (for particles like `内の`, `ضمن`)

Allowed output (`normalize_to`/template) kinds:

- `keyword`: emit a concept keyword token in the target language
- `delimiter`: emit a delimiter token
- `identifier_slot`: emit captured identifier slot
- `expr_slot`: emit captured expression slot

### Example A: Shared Template (Recommended)

Use a template when multiple languages share one canonical rewrite target.

```json
{
  "templates": {
    "for_iterable_first": [
      { "kind": "keyword", "concept": "LOOP_FOR" },
      { "kind": "identifier_slot", "slot": "target" },
      { "kind": "keyword", "concept": "IN" },
      { "kind": "expr_slot", "slot": "iterable" },
      { "kind": "delimiter", "value": ":" }
    ]
  },
  "patterns": [
    {
      "name": "ja_for_iterable_first",
      "language": "ja",
      "normalize_template": "for_iterable_first",
      "pattern": [
        { "kind": "expr", "slot": "iterable" },
        { "kind": "literal", "value": "内の" },
        { "kind": "literal", "value": "各" },
        { "kind": "identifier", "slot": "target" },
        { "kind": "literal", "value": "に対して" },
        { "kind": "delimiter", "value": ":" }
      ]
    }
  ]
}
```

Surface input:

```text
範囲(4) 内の 各 i に対して:
    パス
```

Normalized parse shape:

```text
毎 i 中 範囲(4):
    パス
```

### Example B: Inline Rewrite (`normalize_to`)

Use inline output for a one-off rule that is not worth templating.

```json
{
  "name": "xx_for_custom",
  "language": "xx",
  "pattern": [
    { "kind": "expr", "slot": "iterable" },
    { "kind": "literal", "value": "particleA" },
    { "kind": "identifier", "slot": "target" },
    { "kind": "literal", "value": "particleB" },
    { "kind": "delimiter", "value": ":" }
  ],
  "normalize_to": [
    { "kind": "keyword", "concept": "LOOP_FOR" },
    { "kind": "identifier_slot", "slot": "target" },
    { "kind": "keyword", "concept": "IN" },
    { "kind": "expr_slot", "slot": "iterable" },
    { "kind": "delimiter", "value": ":" }
  ]
}
```

### Authoring Workflow For Complex Grammar

1. Write 2-3 real source examples from native speakers.
2. Tokenize with lexer tests to confirm surface particles are tokenized as expected.
3. Add the narrowest possible `pattern` that matches those forms.
4. Rewrite to one canonical concept order via template or inline output.
5. Add parser + executor tests before adding more variants.
6. Repeat with additional rules rather than broad/fragile mega-rules.

### Common Mistakes

- Capturing a slot in output that was never captured in `pattern`.
- Defining both `normalize_to` and `normalize_template` in one rule.
- Using unsupported language code in `language`.
- Overly broad `expr` patterns that unintentionally match unrelated lines.
- Trying to encode full natural-language grammar in one rule.

### Debugging Tips

If a surface form does not parse:

1. Confirm lexer tokenization first (`tests/lexer_test.py` patterns are good references).
2. Add a parser unit test for just the failing statement.
3. Check that slot names are consistent (`target` vs `iterator`, etc.).
4. Confirm template name exists and is spelled exactly.
5. Ensure the final normalized sequence is compatible with existing parser grammar.

## 7. Add Tests

Minimum recommended tests:

1. `tests/keyword_registry_test.py`
 - language appears in `get_supported_languages()`
 - concept lookups for representative keywords
2. `tests/executor_test.py`
 - one end-to-end program using new language keywords (`ProgramExecutor`)
3. `tests/error_messages_test.py`
 - new language included in "all messages have all languages" coverage
4. `tests/runtime_builtins_test.py`
 - localized aliases map to the expected Python built-ins
5. `tests/surface_normalizer_test.py` (when adding surface rules)
 - config stays schema-valid
 - invalid rule shapes fail with `ValueError`
6. `tests/parser_test.py` + `tests/executor_test.py` (when adding surface rules)
 - parser accepts new surface form
 - end-to-end execution still works

This validates lexer -> parser -> semantic -> codegen/runtime in one path.

## 8. Update Documentation

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

Surface-pattern focused checks:

```bash
python -m pytest -q tests/surface_normalizer_test.py tests/parser_test.py tests/executor_test.py
```

Language-pack smoke checks:

```bash
python -m multilingualprogramming smoke --lang xx
python -m multilingualprogramming smoke --all
```

## Starter Checklist Template

Use this template when opening a PR for a new language pack:

- `docs/templates/language_pack_checklist.md`
