# Changelog

All notable changes to this project should be documented in this file.

The format is inspired by Keep a Changelog, and this project follows SemVer.

## [Unreleased]

### Added

#### WAT/WASM backend — string operations
- **`str(x)` number-to-string conversion**: `str(42)` → `"42"`, `str(3.14)` → `"3.14"` via new
  `$__str_from_f64` WAT helper. Correctly formats integers without a decimal point and floats with
  up to 6 significant decimal digits (trailing zeros trimmed). String and string-variable arguments
  pass through unchanged.
- **F-string numeric interpolation**: `f"{x}"` where `x` is a numeric `f64` variable now calls
  `$__str_from_f64`, producing correct float output (`f"{3.14}"` → `"3.14"` rather than `"3"`).
- **String method `.upper()` / `.lower()`**: ASCII case conversion, returns heap-allocated copy.
- **String method `.startswith(prefix)` / `.endswith(suffix)`**: Returns `0.0` / `1.0`.
- **String method `.count(needle)`**: Counts non-overlapping occurrences; returns f64.
- **String method `.replace(old, new)`**: Replaces all occurrences; returns heap-allocated copy.
- **`str()` recognized as string-valued**: `_is_string_value` updated so `str(x)` composes
  correctly inside f-strings and string concatenation.

#### WAT/WASM backend — math
- **`math.sin` / `math.cos` / `math.tan`**: Horner-polynomial approximations (6-term).
- **`math.exp`**: 10-term Horner polynomial for e^x.
- **`math.log` / `math.log2` / `math.log10`**: atanh-series natural log; scaled for base 2/10.
- **`math.atan` / `math.atan2`**: 6-term series with |x|>1 identity; quadrant-adjusted atan2.
- **`math.trunc` / `math.hypot` / `math.degrees` / `math.radians`**: Inline WAT lowering.
- **`math.pi` / `math.e` / `math.tau` / `math.inf` / `math.nan`**: Emitted as `f64.const` literals.

#### WAT/WASM backend — list mutation
- **`list.append(x)`**: `$__list_append` allocates a new block with `count+1` slots, copies
  existing data, appends the element, and updates the local variable.
- **`list.pop()`**: `$__list_pop` decrements the count in-place and returns the last element;
  works in both statement and expression contexts.
- **`list.extend(other)`**: `$__list_extend` merges two lists into a new heap block.
- **`list(existing_list)`**: Produces a shallow copy when called with an existing list local.

#### WAT/WASM backend — iteration
- **`enumerate(lst)` in `for` loops**: `for i, x in enumerate(lst)` lowers to a counted list
  loop that unpacks the two-element tuple target `(i, x)` via `_emit_sequence_len_setup` /
  `_emit_sequence_value_load`.
- **`list(map(fn, lst))`**: Applies a known WAT function to every element of a list local;
  produces a new list of the same length.
- **`list(filter(fn, lst))`**: Keeps elements where `fn` returns a truthy value; count updated
  after the loop.

#### WAT/WASM backend — dict methods
- **`dict.values()`**: Returns the dict pointer itself (dicts are stored as f64 value lists).
- **`dict.keys()`**: Allocates a new list of interned string pointers for each compile-time key.
- **`dict.items()`**: Allocates an outer list of 2-element `[key_ptr, val]` tuple pairs.
- **`dict.get(key)` / `dict.get(key, default)`**: Compile-time string-literal key lookup;
  returns the element f64, the default expression, or `0.0` if the key is absent.

#### WAT/WASM backend — OOP / type checking
- **`isinstance(obj, ClassName)`**: Emits a type-tag check at `obj_ptr - 8` against the
  compile-time class ID from `_class_ids`. Returns `1.0` (true) or `0.0` (false) as f64.
- **OOP state reset fix**: `_static_method_names`, `_property_getters`, `_class_ids`, and
  `_dispatch_func_names` are now reset between `generate()` calls, eliminating stale OOP
  state that could corrupt subsequent compilations in the same generator instance.

#### WAT/WASM backend — DOM
- **`dom_on(handle, event, callback)`**: Registers a WAT function-table callback for a DOM
  event. The generated module exports `__dom_dispatch(idx)` which JS calls on the event;
  `ml_dom_on` host import added to the DOM bridge.

#### WAT/WASM backend — JSON
- **`json.dumps(list)`**: Encodes a tracked f64 list as a JSON array string
  (`[n1,n2,...]`) using a new `$__json_encode_list` WAT helper.

#### WAT/WASM backend — generators
- **`yield from range(n)`**: Now materializes correctly via Shape 1b in `_simple_generator_spec`.

### Fixed
- **F-string float formatting**: Default `{x}` interpolation previously truncated floats to
  their integer part; now delegates to `$__str_from_f64` for correct output.
- **`math.atan` WAT stack error**: The conditional negation inside `if` without a declared
  result type caused a WASM validation failure; fixed by saving the result to `(local $r f64)`.
- **`$__json_encode_list` copy-index clobbering**: Inner copy loop used `$i` (element index)
  as its write pointer, corrupting output after the first element; fixed with a separate `$ci`.

## [0.6.0] - 2026-03-09

### Added
- **WAT/WASM OOP object model**: Stateful classes (those with `self.attr = …` assignments)
  now use a linear-memory bump allocator in generated WAT. Each field is an `f64` stored at
  a compile-time-computed byte offset. Object pointers are carried as `f64` values and
  converted at field-access sites via `i32.trunc_f64_u` / `f64.convert_i32_u`.
- **Heap-pointer global**: `(global $__heap_ptr (mut i32) …)` is emitted only when at least
  one stateful class is present; `HEAP_BASE` is aligned to 8 bytes after the string data section.
- **`self.attr` store/load lowering**: Attribute writes (`self.x = val`) compile to `f64.store`;
  attribute reads (`self.x`) compile to `f64.load`. Compound assignments (`self.x += delta`)
  use a temporary `f64` local to avoid address recomputation issues.
- **External `obj.attr` reads**: `obj.attr` outside the class body lowers to `f64.load` when
  the variable's class is statically known from local assignments.
- **Stateful instance method calls**: Instance method calls (`obj.method(…)`) pass the actual
  heap address as `self` (as `f64`) for stateful classes; stateless classes keep the old
  `f64.const 0` behavior.
- **Inheritance and method resolution in WAT/WASM**: Subclass hierarchies are now resolved
  at WAT-emit time; inherited methods are dispatched to the correct parent-class WAT export.
- **`with` statement lowering in WAT**: Context-manager blocks (`with expr as var`) lower to
  WAT with enter/exit call sequences.
- **`try/except` lowering in WAT**: Try-except blocks compile to WAT control-flow blocks,
  providing structured exception handling in the WASM backend.
- **`lambda` lowering in WAT**: Lambda expressions lower to anonymous WAT functions with
  captured parameters forwarded as explicit arguments.
- **`match/case` lowering in WAT**: Structural pattern-matching statements lower to WAT
  `if/else` chains using equality comparisons.
- **`async/await` lowering in WAT**: Async function definitions and `await` expressions lower
  to synchronous WAT equivalents with stub scheduling hooks.
- **`@property` setter/getter in WAT**: Property descriptors (`@property`, `@x.setter`) lower
  to distinct WAT getter/setter exports following the established class-method mangling scheme.
- **Bytes literals in WAT**: `b"..."` byte-string literals are stored in the WAT data section
  and referenced by pointer/length pairs.
- **WAT generation organized by themes**: The WAT backend code is now split into focused
  modules by language construct theme (control flow, OOP, literals, builtins) for maintainability.
- **`TupleLiteral` code generation fix**: Tuple literals now wrap generated elements in
  parentheses, producing correctly parenthesized WAT output.
- **Updated builtin aliases**: Expanded localized builtin alias coverage across supported languages.
- **New WAT OOP tests** in `tests/wat_generator_test.py`:
  - `WATOopObjectModelTestSuite` — 6 WAT pattern tests (no wasmtime required).
  - 3 new execution tests in `WATClassWasmExecutionTestSuite`: single-field counter get,
    increment-then-get, and two independent instances.
- **`docs/wat_oop_model.md`**: Reference document covering the object model design, memory
  layout, field layout rules, constructor sequence, store/load patterns, limitations, and a
  full end-to-end WAT example.
- **`AGENTS.md`**: Agent guidance document for AI-assisted development workflows in this repository.

### Changed
- Stateless classes (no `self.attr` assignments) are unaffected and keep the `f64.const 0`
  self path — no existing tests are broken.
- WAT backend source split into themed sub-modules for clarity and maintainability.

### Fixed
- `TupleLiteral` code generation now wraps output in parentheses (previously emitted bare elements).
- Various WAT backend correctness fixes surfaced during gap-filling and test stabilization.

## v0.5.1
- Update documentation

## v0.5.0

### Added
- **Class lowering in WAT backend**: Top-level `ClassDef` methods now lower to standalone WAT exports with deterministic mangled names.
- **Constructor and method call lowering**:
  - `ClassName(...)` lowers to class `__init__` in WAT with implicit `self` handling.
  - `Class.method(...)` lowers to mangled class method exports.
  - `obj = Class(...); obj.method(...)` lowers via lightweight local class-type tracking.
- **Executable WASM validation for complete features**:
  - New test `tests/complete_features_wasm_execution_test.py` compiles every `examples/complete_features_*.multi` from WAT to binary WASM, materializes `.wat/.wasm` artifacts, instantiates modules, and executes `__main`.
- **CI workflow gate for complete-feature WASM execution**:
  - `.github/workflows/wasm-backends-test.yml` now runs the new complete-feature WAT/WASM execution test on primary WASM jobs.

### Changed
- **WAT symbol emission now Unicode-safe**:
  - Function, parameter, and local identifiers are sanitized to valid WAT symbols while preserving original export names.
  - Fixes WAT→WASM compilation failures for non-Latin identifiers in multilingual examples.
- **WASM execution test runtime bounded**:
  - Added Wasmtime fuel metering in complete-feature execution tests to prevent long CI hangs while still validating instantiation and execution.

### Fixed
- **WAT/WASM class regressions**:
  - Fixed incorrect argument mapping for implicit `self` in constructor/instance lowering that could leave stack values and produce invalid WASM.
- **Tooling quality**:
  - Updated test/config and corpus fixtures to remove warning noise and stabilize CI signal.
- **Release docs**:
  - Documented PyPI file-name immutability and the correct recovery path for `HTTP 400 File already exists` uploads.

## [0.4.0]
### Added
- **WATCodeGenerator**: New backend compiling the multilingual AST directly to WebAssembly Text (WAT); fully tested via `tests/complete_features_wat_test.py` across all 17 languages.
- **Playground WAT/WASM tab**: Interactive playground now shows generated WAT source and executes it in the browser via wabt.js + native `WebAssembly.instantiate()`.
- **Playground Rust/Wasmtime tab**: Playground shows generated Rust/Wasmtime bridge scaffold alongside the WAT view for local compilation workflows.
- **REPL `:wat` command**: Toggles display of generated WAT code before execution (alias `:wasm`).
- **REPL `:rust` command**: Toggles display of generated Rust/Wasmtime bridge code before execution (alias `:wasmtime`).
- **CLI `--show-wat` / `--show-rust` flags**: Startup equivalents of `:wat` and `:rust` for the `repl` subcommand.
- **Python 3.12 feature completion**: All 17 `complete_features_XX.multi` example files updated with the full checklist — numeric literals (hex/octal/binary/scientific), augmented assignments, bitwise operators, chained assignment, type annotations, ternary expressions, default/variadic params, lambdas, list/dict/generator/nested/filtered comprehensions, `try/except/else`, exception chaining, multiple `except` handlers, `match/case/default`, decorators, multiple inheritance, `@staticmethod` / `@classmethod` / `@property`, and docstrings.
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
- Complete feature examples (`examples/complete_features_XX.multi`) for all 17 supported languages.
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
