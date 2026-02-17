# Release Notes

## v0.1.0 (Current)

### Core Language
- Expanded supported programming languages to 12: `en`, `fr`, `es`, `de`, `it`, `pt`, `hi`, `ar`, `bn`, `ta`, `zh`, `ja`.
- Added full keyword coverage for Italian and Portuguese in the USM keyword registry.
- Added parser/semantic error message coverage for Italian and Portuguese.

### REPL
- Reworked REPL command handling to be data-driven via `resources/repl/commands.json`.
- Added multilingual command aliases and localized help/messages.
- Added discovery commands:
  - `:kw [XX]` for language keywords
  - `:ops [XX]` for operators/symbols
- Localized REPL listing messages across supported languages.

### Runtime Builtins
- Introduced data-driven localized builtin aliases via `resources/usm/builtins_aliases.json`.
- Kept universal builtin names available while adding localized aliases (e.g., French `intervalle` for `range`).
- Runtime builtin alias loading is now dynamic in `RuntimeBuiltins`.

### Documentation
- Simplified and reorganized top-level documentation.
- Updated `README.md` with a clearer multilingual-first introduction and improved REPL guidance.
- Added extensive multilingual REPL smoke-test examples in `docs/README.md`.
- Added `docs/language_onboarding.md` documenting the data-driven process for adding new languages.
- Improved cross-linking between `README.md`, `USAGE.md`, and `docs/README.md`.
- Moved detailed execution/AST examples and full example command list into `USAGE.md`.

### Quality and Validation
- Addressed lint issues in touched files and normalized line endings.
- Test suite status at latest run: `602 passed, 1 skipped`.
