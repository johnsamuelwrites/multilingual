# Release Notes

## v0.4.0 

### WAT/WASM Code Generation
- New `WATCodeGenerator` compiles the multilingual AST directly to WebAssembly Text (WAT).
- Browser playground shows the generated WAT and executes it via wabt.js + native `WebAssembly.instantiate()`.
- Playground also shows the generated Rust/Wasmtime bridge scaffold for local compilation.
- Regression tests validate WAT output across all 17 languages (`tests/complete_features_wat_test.py`).

### WASM Backend
- WebAssembly compilation target with performance gains on compute-intensive operations.
- Python ↔ WASM bridge for type conversion and memory management.
- Smart backend selector for auto-detection and transparent fallback to Python.
- 25+ pure Python fallback implementations for guaranteed cross-platform compatibility.
- 20 multilingual WASM corpus projects in 4 languages each.
- Documentation suite: WASM architecture overview, installation guides, performance tuning, troubleshooting, and FAQ.

### REPL Code-View Commands
- `:wat` (`:wasm`) — toggle display of generated WAT before execution.
- `:rust` (`:wasmtime`) — toggle display of generated Rust/Wasmtime bridge code before execution.
- `--show-wat` and `--show-rust` startup flags for the `repl` subcommand mirror the interactive toggles.
- Extends the existing `:python` / `--show-python` pattern uniformly across all three backends.

### Python 3.12 Feature Completion
- All 17 `complete_features_XX.ml` example files now cover the full Python 3.12 feature checklist: numeric literals, augmented and bitwise assignments, chained assignment, type annotations, ternary expressions, default/variadic parameters, lambdas, list/dict/generator/nested/filtered comprehensions, `try/except/else`, exception chaining, multiple handlers, `match/case/default`, decorators, multiple inheritance, static/class methods, properties, and docstrings.
- Keyword-variable name clashes (Spanish `y` = AND, Danish/Swedish `i` = IN) resolved in example files.

### Quality and Fixes
- Fixed broken relative links (`../CHANGELOG.md`, `../USAGE.md`, `../examples/README.md`) in `docs/reference.md` and `docs/fr/programmation.md`.
- CLI `multilingual run <file>.ml` correctly handles `.ml` file execution.
- New tests: `language_completeness_cli_test.py`, `operators_cli_test.py`.
- 1671 tests passing, 2 skipped (WASM Rust compile requires `rustc` wasm32 target).

## v0.3.0

### Complete Features Repository
- Created comprehensive `examples/complete_features_XX.ml` files for all 17 supported languages.
- Each file demonstrates full language feature set: imports, functions, closures, classes, control flow, generators, exceptions, comprehensions, and advanced constructs.
- Ensures feature parity across all languages—if code works in English, equivalent translated code works identically in all other 16 languages.

### Frontend Equivalence
- Added an all-language full-pipeline regression test that starts from one core template, renders per-language keywords, transpiles, and executes for every supported language.
- Expanded equivalence validation to check deterministic transpiled Python parity across language frontends.

### Cross-Language Imports
- Added import-hook support for loading `.ml` modules and packages (`__init__.ml`) via Python import machinery.
- Enabled multilingual imports automatically in executor and REPL runtime paths.
- Added integration tests for English/French cross-imports, package imports, and manual enable/disable flow.

### Language Coverage
- Added five new European language packs: Polish (`pl`), Dutch (`nl`), Swedish (`sv`), Danish (`da`), and Finnish (`fi`).
- Localized keyword mappings, parser/semantic error messages, REPL help/messages/aliases, operator descriptions, and runtime builtin aliases for the new languages.
- Fixed legacy keyword placeholders surfaced by full-pipeline testing (Italian `IS`, Tamil `NOT`).
- All 17 languages now have complete feature coverage with working examples.

### Language Onboarding
- Added a contributor-ready onboarding checklist/template for new language packs.
- Added a `multilingual smoke` language-pack validation path and wired it into workflows.

### Tooling and Quality
- Strengthened CI gates with packaging sanity checks and CLI smoke runs in addition to tests/lint.
- Added cross-language import examples under `examples/` and updated docs (`README.md`, `USAGE.md`, `examples/README.md`).
- Test suite: 85 tests passing with zero regressions.

## v0.2.0

### Core Language
- Added a surface-normalization layer for selected alternate phrasing patterns.
- Expanded frontend equivalence coverage, including iterable-first loop variants.
- Added support for advanced constructs such as async flows, walrus operator, set literals, and dict unpacking.

### REPL and Execution
- Improved multilingual REPL usage with language switching and optional generated-Python display.
- Strengthened end-to-end parity across language frontends targeting one core execution path.

### Documentation and Positioning
- Refined README project positioning around "one programming model, many human languages."
- Added focused docs for naturalness, CNL scope, stdlib localization boundaries, and translation governance.

### Quality and Validation
- Expanded regression and equivalence tests across parser, core IR, runtime, and surface normalization.
- Updated package metadata and released as `0.2.0`.

## v0.1.0

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
- Added extensive multilingual REPL smoke-test examples in `docs/reference.md`.
- Added `docs/language_onboarding.md` documenting the data-driven process for adding new languages.
- Improved cross-linking between `README.md`, `USAGE.md`, and `docs/reference.md`.
- Moved detailed execution/AST examples and full example command list into `USAGE.md`.

### Quality and Validation
- Addressed lint issues in touched files and normalized line endings.
- Test suite status at latest run: `602 passed, 1 skipped`.
