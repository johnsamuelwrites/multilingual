# Changelog

All notable changes to this project should be documented in this file.

The format is inspired by Keep a Changelog, and this project follows SemVer.

## [Unreleased]
## [0.4.0]
### Added
- **WATCodeGenerator**: New backend compiling the multilingual AST directly to WebAssembly Text (WAT); fully tested via `tests/complete_features_wat_test.py` across all 17 languages.
- **Playground WAT/WASM tab**: Interactive playground now shows generated WAT source and executes it in the browser via wabt.js + native `WebAssembly.instantiate()`.
- **Playground Rust/Wasmtime tab**: Playground shows generated Rust/Wasmtime bridge scaffold alongside the WAT view for local compilation workflows.
- **REPL `:wat` command**: Toggles display of generated WAT code before execution (alias `:wasm`).
- **REPL `:rust` command**: Toggles display of generated Rust/Wasmtime bridge code before execution (alias `:wasmtime`).
- **CLI `--show-wat` / `--show-rust` flags**: Startup equivalents of `:wat` and `:rust` for the `repl` subcommand.
- **Python 3.12 feature completion**: All 17 `complete_features_XX.ml` example files updated with the full checklist — numeric literals (hex/octal/binary/scientific), augmented assignments, bitwise operators, chained assignment, type annotations, ternary expressions, default/variadic params, lambdas, list/dict/generator/nested/filtered comprehensions, `try/except/else`, exception chaining, multiple `except` handlers, `match/case/default`, decorators, multiple inheritance, `@staticmethod` / `@classmethod` / `@property`, and docstrings.
- **New CLI tests**: `language_completeness_cli_test.py` and `operators_cli_test.py`.
- **WASM Backend**: WebAssembly compilation target with significant performance gains on compute-intensive operations (benchmark-dependent).
- **Python ↔ WASM Bridge**: Type conversion and memory management for seamless interop between Python and WASM.
- **Smart Backend Selector**: Auto-detection and transparent routing between WASM and Python fallback execution paths.
- **Python Fallback Implementations**: 25+ pure Python implementations for guaranteed compatibility across all platforms.
- **WASM Corpus Projects**: 20 multilingual example projects (matrix operations, cryptography, image processing, JSON parsing, scientific computing) in 4 languages each.
- **Comprehensive Test Suite**: 33+ tests covering correctness, performance, fallback mechanisms, integration, and platform compatibility.
- **PyPI Distribution Infrastructure**: Complete packaging for PyPI with optional WASM dependencies and Python 3.12+ support.
- **Documentation Suite**: WASM architecture overview, installation guides, performance tuning, troubleshooting, and FAQ.

### Changed
- CLI `multilingual run <file>.ml` correctly handles `.ml` file execution.
- **Python Version Support**: 3.12+ (advanced features).
- **Performance Profile**: CPU-bound operations can execute substantially faster via WASM backend (benchmark-dependent).
- **Dependency Model**: WASM support now optional via `[wasm]` extra; numpy support optional via `[performance]`.

### Fixed
- Broken relative links in `docs/reference.md` and `docs/fr/programmation.md` (`../CHANGELOG.md`, `../USAGE.md`, `../examples/README.md`).
- Variable name clashes in Spanish (`y` = AND keyword) and Danish/Swedish (`i` = IN keyword) comprehension examples.
- Complete multilingual support for WASM infrastructure across all 17 languages.
- All 1671 tests passing, 2 skipped (WASM Rust compile, requires `rustc` wasm32 target).

## [0.3.0] - 2026-02-22

### Added
- Complete feature examples (`examples/complete_features_XX.ml`) for all 17 supported languages.
- Verified feature parity across all languages with comprehensive test coverage.

### Changed
- Enhanced language coverage from 12 to 17 supported languages with complete examples.
- Test suite expanded with integrated complete feature validation for all languages.

### Fixed
- Zero regressions; all 85 tests passing.

## [0.2.0] - 2026-02-21

### Added
- Advanced language feature support across parser/codegen/runtime tests.
- Expanded localized built-in alias coverage and compatibility fixtures.
- Python 3.12+ packaging baseline with 3.12/3.13/3.14 CI verification.

### Changed
- Test module naming migrated away from milestone-oriented file names.
- Example programs refreshed to include newer feature coverage.
