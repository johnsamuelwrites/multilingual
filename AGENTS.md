# AGENTS.md — AI Agent Guide for `multilingual`

> **This file is the authoritative reference for AI agents (Claude, GPT, Gemini, Copilot, etc.)
> working on this codebase. Read it fully before making changes.**

---

## Table of Contents

1. [Project Identity](#1-project-identity)
2. [Core Architecture](#2-core-architecture)
3. [Repository Map](#3-repository-map)
4. [Universal Semantic Model (USM)](#4-universal-semantic-model-usm)
5. [Pipeline Deep-Dive](#5-pipeline-deep-dive)
6. [WAT / WASM Backend](#6-wat--wasm-backend)
7. [OOP Object Model (WAT)](#7-oop-object-model-wat)
8. [Inheritance Model (WAT)](#8-inheritance-model-wat)
9. [Development Workflow](#9-development-workflow)
10. [Testing](#10-testing)
11. [CLI Reference](#11-cli-reference)
12. [Common Tasks — Patterns & Pitfalls](#12-common-tasks--patterns--pitfalls)
13. [Known Issues & Gotchas](#13-known-issues--gotchas)
14. [Supported Languages](#14-supported-languages)
15. [Version & Release Info](#15-version--release-info)

---

## 1. Project Identity

| Field | Value |
|---|---|
| **Package name** | `multilingualprogramming` |
| **CLI commands** | `multilingual`, `multilg` (alias) |
| **Tagline** | "One programming model. Many human languages." |
| **Version** | `0.6.0` (see `multilingualprogramming/version.py`) |
| **Status** | Beta (Development Status :: 4) |
| **Python requirement** | ≥ 3.12 |
| **License** | GPL-3.0-or-later (code), CC BY-SA 4.0 (docs) |
| **PyPI** | https://pypi.org/project/multilingualprogramming/ |
| **Repository** | https://github.com/johnsamuelwrites/multilingual |
| **Playground** | https://johnsamuel.info/multilingual/playground.html |

**Purpose**: A multilingual programming language where code can be written in any of 17 natural
languages. The long-term direction is a human-language-first semantic platform
for AI-native, multimodal, reactive, concurrent, and distributed programming.
The current repository implements a transitional compiler/runtime stack toward
that goal. Keywords, operators, and builtins are data-driven (JSON), not
hard-coded.

---

## 2. Core Architecture

### End-to-end Pipeline

```
Source (.ml, 17 languages)
        │
        ▼
    Lexer                   multilingualprogramming/lexer/lexer.py
        │  tokens
        ▼
SurfaceNormalizer?          multilingualprogramming/parser/surface_normalizer.py
        │  normalized tokens
        ▼
    Parser                  multilingualprogramming/parser/parser.py
        │  AST
        ▼
Semantic IR lowering        multilingualprogramming/core/lowering.py
        │  IRProgram
        ▼
 SemanticAnalyzer           multilingualprogramming/core/semantic_analyzer.py
        │  checked IR / analysis
        ▼
  ┌─────┴──────┐
  │            │
  ▼            ▼
PythonCodeGen  WATCodeGen   multilingualprogramming/codegen/python_generator.py
  │            │            multilingualprogramming/codegen/wat_generator.py
  ▼            ▼
Python src    WAT text / WASM artifacts
  │            │
  ▼            ▼
exec()       wasmtime      (or Python fallbacks via runtime/backend_selector.py)
```

### Key Design Principles

- **Data-driven**: All language-specific knowledge lives in JSON under
  `multilingualprogramming/resources/usm/`. No language keywords are hard-coded in Python.
- **Single AST**: All 17 language frontends produce the same AST node types
  (`multilingualprogramming/parser/ast_nodes.py`).
- **Semantic-core direction**: the parser output is increasingly bridged into a
  shared semantic IR so the project can grow beyond a historical
  parser-to-backend compiler shape into a fuller Core 1.0 language model.
- **Dual backend**: Python backend (always available) + optional WAT/WASM backend
  (`wasmtime` optional dependency). Smart backend selector lives in
  `multilingualprogramming/runtime/backend_selector.py`.
- **Surface normalization**: Alternate keyword forms (e.g., Spanish iterable-first, Japanese
  variants) are normalized by `multilingualprogramming/parser/surface_normalizer.py` before
  parsing.

### Architecture Note for Agents

When updating docs or implementation notes, distinguish between:

- **Current implementation**: the repository's working parser/IR/backend pipeline.
- **Strategic vision**: Multilingual 1.0 as a human-language-first semantic
  platform for AI, multimodal, reactive, concurrent, and distributed programs.

Do not collapse those into one claim. Prefer wording like "currently", "today",
"transitional", "direction", or "long-term" when a statement is about roadmap
rather than shipped behavior.

---

## 3. Repository Map

```
multilingual/
├── AGENTS.md                           ← you are here
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── RELEASE.md
├── USAGE.md
├── mkdocs.yml
├── pyproject.toml                      ← package metadata, deps, entry points
├── pytest.ini                          ← test configuration
├── requirements.txt                    ← roman, python-dateutil
├── setup.py                            ← setuptools shim (metadata in pyproject.toml)
├── .pylintrc                           ← linting config
├── .github/workflows/                  ← CI/CD (8 workflows)
│
├── multilingualprogramming/            ← main package
│   ├── __init__.py                     ← public API exports (88 items)
│   ├── __main__.py                     ← CLI entry point (argparse)
│   ├── version.py                      ← version = "0.6.0"
│   ├── exceptions.py                   ← custom exceptions
│   ├── imports.py                      ← multilingual .ml import support
│   ├── unicode_string.py               ← Unicode string utilities
│   │
│   ├── codegen/
│   │   ├── executor.py                 ← ProgramExecutor: full pipeline + backend/runtime execution
│   │   ├── python_generator.py         ← AST/IR → Python source transpiler
│   │   ├── wat_generator.py            ← AST → WAT: top-level entry point
│   │   ├── wat_generator_core.py       ← WAT: core state and helpers
│   │   ├── wat_generator_expression.py ← WAT: expression lowering
│   │   ├── wat_generator_loop.py       ← WAT: loop lowering (for/while)
│   │   ├── wat_generator_manifest.py   ← WAT: manifest/ABI metadata
│   │   ├── wat_generator_match.py      ← WAT: match/case lowering
│   │   ├── wat_generator_oop.py        ← WAT: OOP / class lowering
│   │   ├── wat_generator_runtime.py    ← WAT: runtime builtins (input, DOM calls)
│   │   ├── wat_generator_support.py    ← WAT: shared support utilities
│   │   ├── wasm_generator.py           ← WAT → WASM binary
│   │   ├── runtime_builtins.py         ← RuntimeBuiltins + make_exec_globals()
│   │   ├── repl.py                     ← interactive REPL
│   │   ├── build_orchestrator.py       ← build system
│   │   └── encoding_guard.py           ← UTF-8 validation
│   │
│   ├── core/
│   │   ├── ir.py                       ← Core IR representation
│   │   ├── lowering.py                 ← AST → Core IR
│   │   └── semantic_analyzer.py        ← scope, symbol table, type/effect checks
│   │
│   ├── datetime/
│   │   ├── mp_date.py / mp_time.py / mp_datetime.py
│   │   ├── date_parser.py
│   │   └── resource_loader.py
│   │
│   ├── keyword/
│   │   ├── keyword_registry.py         ← singleton: loads keywords.json, builds reverse-index
│   │   ├── keyword_validator.py
│   │   └── language_pack_validator.py
│   │
│   ├── lexer/
│   │   ├── lexer.py                    ← multilingual tokenizer (greedy, up to 3 words)
│   │   ├── token.py
│   │   ├── token_types.py              ← TokenType enum
│   │   └── source_reader.py
│   │
│   ├── numeral/
│   │   ├── mp_numeral.py               ← multilingual numeral arithmetic
│   │   ├── unicode_numeral.py          ← Unicode script digits
│   │   ├── roman_numeral.py
│   │   ├── complex_numeral.py
│   │   ├── fraction_numeral.py
│   │   ├── numeral_converter.py
│   │   └── abstract_numeral.py
│   │
│   ├── parser/
│   │   ├── parser.py                   ← recursive-descent parser
│   │   ├── ast_nodes.py                ← all AST node classes
│   │   ├── ast_printer.py              ← AST pretty-printer
│   │   ├── error_messages.py           ← localized error messages
│   │   └── surface_normalizer.py       ← keyword/form normalization
│   │
│   ├── resources/
│   │   ├── usm/
│   │   │   ├── keywords.json           ← concept → keyword mapping (17 langs, 50+ concepts)
│   │   │   ├── builtins_aliases.json   ← localized builtin names (len→longueur, etc.)
│   │   │   ├── operators.json          ← operator symbol variants
│   │   │   ├── surface_patterns.json   ← surface normalization rules
│   │   │   └── schema.json             ← schema validation
│   │   ├── datetime/
│   │   │   └── months.json, weekdays.json, eras.json, formats.json
│   │   ├── parser/
│   │   │   └── error_messages.json     ← multilingual error messages
│   │   └── repl/
│   │       └── commands.json           ← REPL command translations
│   │
│   ├── runtime/
│   │   ├── backend_selector.py         ← WASM/Python auto-selector
│   │   ├── python_fallbacks.py         ← 25+ pure Python fallback implementations
│   │   └── numeric_primitives.py       ← performance primitives
│   │
│   └── wasm/
│       ├── loader.py                   ← WASM module loader
│       ├── tuple_abi.py                ← tuple serialization
│       └── tuple_memory.py             ← memory management
│
├── tests/                              ← 67 test files, ~22,284 lines
├── examples/                           ← 33 .ml example files (17 languages)
├── docs/                               ← 29+ markdown files + French docs
└── tools/                              ← development utilities
```

---

## 4. Universal Semantic Model (USM)

The USM is the central concept store. All language-specific knowledge derives from it.

### `resources/usm/keywords.json`

Maps **concept names** → **per-language keyword arrays**:

```json
{
  "COND_IF": {
    "en": ["if"],
    "fr": ["si"],
    "de": ["wenn"],
    "ja": ["もし"],
    ...
  }
}
```

- **50+ concepts** total. The count is asserted in `tests/keyword_registry_test.py`.
- Each concept can have **multiple keyword forms** per language (multi-word keywords as both
  space-separated and underscore-joined: `"not in"` and `"not_in"`).
- Keyword categories: compound statements (COND_IF, LOOP_WHILE, LOOP_FOR, FUNC_DEF, CLASS_DEF,
  TRY, MATCH, WITH), simple statements (LET, CONST, RETURN, YIELD, RAISE, IMPORT, PASS, BREAK,
  CONTINUE, DELETE, ASSERT, GLOBAL, NONLOCAL), callables (PRINT, INPUT), logical (AND, OR, NOT,
  NOT_IN, IN, IS, IS_NOT), type keywords (TYPE_INT, TYPE_FLOAT, TYPE_STR, TYPE_BOOL, TYPE_LIST,
  TYPE_DICT), boolean literals (TRUE, FALSE), and more.

### `resources/usm/builtins_aliases.json`

Maps localized builtin names → Python builtins for exec() injection:

```json
{
  "fr": {
    "longueur": "len",
    "valeurabsolue": "abs",
    "minimum": "min",
    "maximum": "max"
  }
}
```

### `resources/usm/operators.json`

Operator symbol variants across languages (e.g., `×` for `*`, `÷` for `/`, `≠` for `!=`).

### `resources/usm/surface_patterns.json`

Surface normalization rules (e.g., French iterable-first `pour chaque x dans y`, Japanese
variants, Portuguese alternate forms). Processed by `surface_normalizer.py` before lexing.

### `keyword/keyword_registry.py`

Singleton that loads `keywords.json` at startup and builds a reverse-index (keyword → concept).
Used by the lexer to identify keyword tokens. Import as:

```python
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
registry = KeywordRegistry.get_instance()
```

---

## 5. Pipeline Deep-Dive

### Lexer (`lexer/lexer.py`)

- **Greedy multi-word matching**: tries up to 3 consecutive tokens as a single keyword.
  Both space-separated (`"not in"`) and underscore-joined (`"not_in"`) forms are recognized.
- **Unicode operators**: `×`, `÷`, `−`, `≠`, `≤`, `≥`, `→`, fullwidth brackets, CJK corner
  brackets `「」`, guillemets `«»`, smart quotes, etc.
- **String quote pairs**: standard `"`, `'`, plus `「」`, `«»`, `""`, `''`.
- **Date literals**: delimited by `〔〕`.
- **INDENT/DEDENT**: emitted even inside bracket pairs (unlike CPython). See gotchas below.

### Parser (`parser/parser.py`)

- Recursive-descent parser; entry: `Parser(tokens, language).parse()` → `Program` AST node.
- `DEFAULT_MAX_DEPTH = 100`, `DEFAULT_MAX_RECURSION = 500`.
- Key parse methods: `_parse_stmt()`, `_parse_expr()`, `_parse_comparison()`,
  `_parse_list_literal()`, `_parse_brace_literal()`, `_parse_call()`, `_parse_atom()`.
- `_skip_newlines()`: skips NEWLINE/COMMENT tokens only.
- `_skip_bracket_newlines()`: skips NEWLINE, COMMENT, INDENT, DEDENT — **required** inside
  list/dict/call/tuple to handle multi-line literals.

### Semantic IR Lowering (`core/lowering.py`)

- Bridges the shared parser AST toward the Core 1.0 semantic direction.
- Produces `IRProgram` and related IR nodes for downstream analysis/codegen.
- This layer matters when documenting future-facing work: new language ideas
  often appear conceptually in IR before every backend fully converges.

### SemanticAnalyzer (`core/semantic_analyzer.py`)

- Builds symbol table, checks scope, does basic type analysis.
- **Builtins scope**: `executor.py` pre-seeds a *parent* builtins scope (not the global scope),
  so user variables that shadow a builtin alias do not trigger `DUPLICATE_DEFINITION`.
- Use `check_semantics=False` in tests that need to isolate parser/codegen from analysis.

### PythonCodeGenerator (`codegen/python_generator.py`)

- Emits Python source from the repository's current shared frontend
  representation rather than a purely legacy AST-only path.

### ProgramExecutor (`codegen/executor.py`)

- `ProgramExecutor.execute(source, globals_dict=None)` → `ExecutionResult`.
- `ExecutionResult`: `.output`, `.return_value`, `.python_source`, `.errors`, `.success`.
- Internally drives lexing, parsing, semantic analysis, backend generation, and
  runtime namespace setup via `make_exec_globals(language)`.

### Runtime Builtins (`codegen/runtime_builtins.py`)

- `RuntimeBuiltins(language).namespace()` → dict for exec().
- `make_exec_globals(language, extra=None)` → convenience wrapper (also sets `__name__`,
  `__package__`, `__spec__`).

---

## 6. WAT / WASM Backend

### WAT Generator (`codegen/wat_generator.py`)

Translates AST to WebAssembly Text format. Supports a subset of the full language:

| Construct | WAT support |
|---|---|
| Variable declaration/assignment | ✓ |
| Arithmetic (+, -, *, /) | ✓ (f64) |
| Augmented assignment (+=, -=, *=, /=, //=, %=) | ✓ native f64 arithmetic |
| Augmented assignment (&=, \|=, ^=, <<=, >>=) | ✓ i32 round-trip |
| Augmented assignment (**=) | ✓ via `call $pow_f64` host import (`Math.pow` in JS) |
| Comparisons | ✓ |
| Boolean logic | ✓ |
| `if` / `elif` / `else` | ✓ |
| `while` loop | ✓ |
| `for` loop over `range()` | ✓ |
| `for` loop over list/tuple variable | ✓ index-based using linear-memory list header |
| Function definition | ✓ |
| `async def` / `await` | ✓ best-effort (`async def` = regular WAT func; `await` evaluates operand) |
| `return` | ✓ |
| Class definition (OOP) | ✓ (see §7) |
| Inheritance | ✓ (see §8) |
| `match`/`case` (numeric/boolean patterns) | ✓ lowered to WAT block + nested if |
| `match`/`case` (string patterns) | ✓ interned-offset `f64.eq` comparison (compile-time strings only) |
| `match`/`case` (`None` pattern) | ✓ `f64.eq` with `f64.const 0` |
| `match`/`case` (capture variable `case x:`) | ✓ binds subject to local, always matches |
| `match`/`case` (tuple/list literal patterns) | ✓ element-wise `f64.eq` + length check (list/tuple subject only) |
| `match`/`case` (class/complex patterns) | stub comment |
| `print` | ✓ (host import) |
| `abs` | ✓ native `f64.abs` |
| `min(a,b,…)` n-arg | ✓ chained `f64.min` |
| `max(a,b,…)` n-arg | ✓ chained `f64.max` |
| `len(str_literal)` / `len(str_var)` | ✓ compile-time byte length / parallel length local |
| `len(list_var)` / `len(tuple_var)` | ✓ loaded from list/tuple header in linear memory |
| List/tuple literal allocation | ✓ heap bump-allocator; layout = [len_f64, elem0, elem1, …] |
| `list[i]` / `tuple[i]` index read | ✓ `f64.load` at `base + 8 + i*8` |
| `try/except/finally` | ✓ numeric exception-code model: `raise` stores a non-zero f64 code; `except ExcType` matches that code; `except:` / `except Exception:` catch any non-zero code; `finally` runs unconditionally (emitted on both the unhandled path before `unreachable` and the normal/handled path after the handler block); `as e` binds the actual exception code |
| `with` statement | ✓ best-effort (body executed; `__enter__`/`__exit__` not callable from WAT) |
| Lambda expressions | ✓ lifted to WAT functions; stored as table index (f64); called via `call_indirect` |
| List/generator comprehension over `range` | ✓ lowered to WAT loop + f64 accumulator |
| List/generator comprehension over list variable | ✓ index-based loop + f64 accumulator |
| Other comprehensions | stub comment (dynamic collections not representable as f64) |
| String concatenation (`+`) | ✓ compile-time (both literals) → interned; runtime → `$__str_concat` heap helper |
| String indexing (`s[i]`) | ✓ `i32.load8_u` → char code as f64 |
| String slicing (`s[a:b]`) | ✓ `$__str_slice` heap copy helper |
| `async for` over `range()` / list var | ✓ best-effort (same lowering as sync `for`) |
| `async with` | ✓ best-effort (same lowering as sync `with`) |
| `async for` over other iterables | not supported |
| `input()` | ✓ reads a line from WASI fd 0 (stdin), strips trailing CR/LF, returns as f64 string pointer; `$__last_str_len` is set |
| `argc()` | ✓ builtin returning the WASI argument count as f64 |
| `argv(i)` | ✓ builtin returning the i-th WASI argument as f64 string pointer; `$__last_str_len` is set |
| DOM manipulation | ✓ conditional `"env"` host imports emitted when any DOM builtin is used; WAT wrapper functions for `dom_get`, `dom_text`, `dom_html`, `dom_value`, `dom_attr`, `dom_create`, `dom_append`, `dom_style`, `dom_remove`, `dom_class` |
| Source location comments | ✓ `;;  @line:col` WAT comment emitted at the top of each compiled statement when source position is available |

### Host Imports (expected by WAT modules)

```wat
(import "env" "print_str"     (func $print_str (param i32 i32)))
(import "env" "print_f64"     (func $print_f64 (param f64)))
(import "env" "print_bool"    (func $print_bool (param f64)))
(import "env" "print_sep"     (func $print_sep))
(import "env" "print_newline" (func $print_newline))
(import "env" "pow_f64"       (func $pow_f64 (param f64 f64) (result f64)))
```

WASI host imports (always emitted):

```wat
(import "wasi_snapshot_preview1" "fd_write"        (func $fd_write        (param i32 i32 i32 i32) (result i32)))
(import "wasi_snapshot_preview1" "fd_read"         (func $fd_read         (param i32 i32 i32 i32) (result i32)))
(import "wasi_snapshot_preview1" "args_sizes_get"  (func $args_sizes_get  (param i32 i32) (result i32)))
(import "wasi_snapshot_preview1" "args_get"        (func $args_get        (param i32 i32) (result i32)))
```

DOM host imports (emitted only when any DOM builtin is used, module `"env"`):

```wat
(import "env" "ml_dom_get"       (func $ml_dom_get       (param i32 i32) (result f64)))
(import "env" "ml_dom_set_text"  (func $ml_dom_set_text  (param f64 i32 i32)))
(import "env" "ml_dom_set_html"  (func $ml_dom_set_html  (param f64 i32 i32)))
(import "env" "ml_dom_get_value" (func $ml_dom_get_value (param f64 i32 i32) (result i32)))
(import "env" "ml_dom_set_attr"  (func $ml_dom_set_attr  (param f64 i32 i32 i32 i32)))
(import "env" "ml_dom_create"    (func $ml_dom_create    (param i32 i32) (result f64)))
(import "env" "ml_dom_append"    (func $ml_dom_append    (param f64 f64)))
(import "env" "ml_dom_set_style" (func $ml_dom_set_style (param f64 i32 i32 i32 i32)))
(import "env" "ml_dom_remove"    (func $ml_dom_remove    (param f64)))
(import "env" "ml_dom_toggle_class" (func $ml_dom_toggle_class (param f64 i32 i32)))
```

Internal WAT helper functions (emitted on demand, no host import needed):
- `$__str_concat (ptr1 len1 ptr2 len2 : f64) → f64` — heap-allocates concatenated string
- `$__str_slice (ptr start stop : f64) → f64` — heap-allocates string slice
- `$__ml_init_argv` — reads WASI argc/argv into static memory on startup
- `$argc` — returns argument count as f64
- `$argv (i: f64) → f64` — returns i-th argument string pointer as f64
- `$input → f64` — reads one line from fd 0 (stdin), strips CR/LF, returns string pointer
- DOM wrapper functions (`$dom_get`, `$dom_text`, etc.) — thin wrappers over the raw DOM imports with caller-friendly signatures (str→ptr+len, f64 element handles)
- Lambda `funcref` table at index 0 + `call_indirect` for lambda calls

### Stub Detection

Unsupported calls emit a WAT comment stub:

```wat
;; unsupported call: len(mylist)
```

Use `has_stub_calls(wat_text)` (exported from `wat_generator.py`) to detect stubs programmatically.
The presence of an export in the WAT does **not** guarantee it is functionally correct if stubs exist.

### Native WAT Instructions

- `abs(x)` → `f64.abs`
- `min(a, b)` → `f64.min` (2-arg only)
- `max(a, b)` → `f64.max` (2-arg only)

### String Storage

String literals are stored in the linear memory data section. String load/store uses `i32` offsets.

### WASM Binary (`codegen/wasm_generator.py`)

Converts WAT text to a WASM binary using the `wabt` toolchain (optional). Loaded via
`multilingualprogramming/wasm/loader.py` using `wasmtime`.

### Python Fallbacks (`runtime/python_fallbacks.py`)

25+ pure Python implementations of WAT-lowerable operations, used when `wasmtime` is unavailable.
Activated automatically by `runtime/backend_selector.py`.

---

## 7. OOP Object Model (WAT)

Stateful classes (those with `self.attr = ...` assignments) use a linear-memory bump allocator.
Stateless classes use `f64.const 0` as the `self` value (backward compatible).

### Key Internal State in WATCodeGenerator

| Attribute | Description |
|---|---|
| `_class_direct_fields[cls]` | Own (non-inherited) fields scanned from class body |
| `_class_field_layouts[cls]` | Effective layout: parent fields first, then own; each f64 = 8 bytes |
| `_class_obj_sizes[cls]` | Total object byte size |
| `_current_class` | Class currently being emitted |
| `_var_class_types` | Tracks which variables hold which class type (for `obj.attr` access) |

### Heap Allocator

```wat
(global $__heap_ptr (mut i32) (i32.const HEAP_BASE))
```

- Emitted only when at least one stateful class exists.
- `HEAP_BASE = max(ceil(string_data_len / 8) * 8, 64)`.
- Constructor call: advances heap pointer by object size, calls `__init__` with `ptr`-as-f64,
  returns `ptr`-as-f64.

### Field Access

```wat
;; self.attr store:
local.get $self
i32.trunc_f64_u
i32.const <field_offset>   ;; field_index * 8
i32.add
f64.store

;; self.attr load:
local.get $self
i32.trunc_f64_u
i32.const <field_offset>
i32.add
f64.load
```

External access (`obj.attr`) works when `obj` is tracked in `_var_class_types`.

### Instance Method Calls

- **Stateful classes**: pass actual object reference (`f64` holding `i32` pointer) as `self`.
- **Stateless classes**: pass `f64.const 0` as `self`.

---

## 8. Inheritance Model (WAT)

### Key Internal State

| Attribute | Description |
|---|---|
| `_class_bases[cls]` | List of base class name strings (from `cls.bases` Identifier nodes) |
| `_class_ctor_names[cls]` | WAT function name for constructor |
| `_class_attr_call_names["Sub.method"]` | Resolved WAT function name for method (handles inheritance) |

### Method Resolution

- `_effective_field_layout(cls)`: recursive merge — parent fields prepended before own fields.
- `_mro(cls)`: C3 linearization (same algorithm as CPython, cycle-safe); class itself first.
  Implemented via `_c3_mro()` + `_c3_merge()` — replaces the original DFS approximation.
- Method inheritance: `_class_attr_call_names["SubClass.method"]` resolves to the parent's
  lowered WAT function name if the subclass does not define the method.
- Constructor inheritance: if a class has no `__init__`, `_class_ctor_names[cls]` is set to the
  parent's constructor.

### `super()` Calls

- `_resolve_super_call(expr)` detects `super().method(...)` patterns.
- Returns the parent's lowered WAT function name.
- The `super()` guard runs **first** in both `_gen_stmt()` and `_gen_expr()` CallExpr branches.

---

## 9. Development Workflow

### Installation (Development)

```bash
# Clone
git clone https://github.com/johnsamuelwrites/multilingual
cd multilingual

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

# Optional: WASM support
pip install -e ".[wasm]"

# Optional: dev tools
pip install -e ".[dev]"
```

### Dependencies

| Package | Version | Purpose |
|---|---|---|
| `roman` | ≥3.3 | Roman numeral support |
| `python-dateutil` | ≥2.8 | Date parsing |
| `wasmtime` | ≥1.0.0 | WASM execution (optional) |
| `numpy` | ≥1.20.0 | Performance primitives (optional) |
| `pytest` | — | Testing (dev) |
| `pytest-cov` | — | Coverage (dev) |
| `pylint` | — | Linting (dev) |

### Linting

```bash
pylint $(git ls-files '*.py')
# or against specific files:
pylint multilingualprogramming/
```

### Smoke Tests (quick validation of all language packs)

```bash
multilingual smoke --all
# or for a single language:
multilingual smoke --lang fr
```

### CI/CD

Eight GitHub Actions workflows:

| Workflow | Trigger | What it does |
|---|---|---|
| `pythonpackage.yml` | push/PR | Full test suite (Python 3.12, 3.13, 3.14) |
| `wasm-backends-test.yml` | push/PR | WASM backend validation |
| `pylint.yml` | push/PR | Code quality checks |
| `codeql-analysis.yml` | push/PR | Security analysis |
| `docs-pages.yml` | push to main | Deploy MkDocs site |
| `compatibility-312.yml` | push/PR | Python 3.12 differential tests |
| `package-artifacts.yml` | push/PR | Package creation test |
| `release-pypi.yml` | release tag | PyPI publication |

CI gates before merge: `pythonpackage`, `pylint`, `package-artifacts`, `compatibility-312`.

---

## 10. Testing

### Test Suite Overview

- **Location**: `tests/`
- **Files**: 67 test files, ~22,284 lines of test code
- **Discovery**: `test_*.py` and `*_test.py`
- **Total tests**: ~2,022 (2 skipped — require `rustc wasm32` target)

### Running Tests

```bash
# All tests, quiet
python -m pytest -q

# All tests with coverage
python -m pytest --cov=multilingualprogramming tests/ -v

# Single file
python -m pytest tests/lexer_test.py -v

# By marker
python -m pytest -m "not slow" tests/     # skip slow tests
python -m pytest -m wasm tests/           # WASM tests only
python -m pytest -m correctness tests/    # correctness tests only
python -m pytest -m corpus tests/         # 20 corpus project tests

# Pattern match
python -m pytest -k "inheritance" tests/  # tests with "inheritance" in name
```

### Test Markers (defined in `pytest.ini`)

`wasm`, `fallback`, `correctness`, `performance`, `integration`, `corpus`, `multilingual`, `slow`

### Key Test Files

| File | What it covers |
|---|---|
| `lexer_test.py` | Tokenization: keywords, operators, multi-word, Unicode |
| `parser_test.py` | AST generation for all language constructs |
| `keyword_registry_test.py` | Keyword mapping + concept count assertion (currently 50) |
| `executor_test.py` | Full pipeline: source → execution |
| `runtime_builtins_test.py` | Builtin aliases (longueur→len, etc.) |
| `wat_generator_test.py` | AST → WAT, includes OOP, inheritance, and DOM bridge tests (`WATDOMBridgeTestSuite`) |
| `wat_generator_wasm_execution_test.py` | WASM execution validation; includes `WATExceptionHandlingTestSuite` (catch-all, `finally`, `as e`) and `WATArgvTestSuite` (argc/argv) |
| `wat_generator_manifest_test.py` | WAT manifest/ABI metadata generation; checks all 4 WASI imports and JS shim stubs |
| `wat_generator_string_lambda_test.py` | String operations and lambda lowering in WAT |
| `wat_oop_dispatch_test.py` | WAT OOP dynamic dispatch and type-tag tests |
| `wasm_corpus_test.py` | 20 multilingual corpus projects (end-to-end) |
| `complete_features_wat_test.py` | Full WAT feature coverage across 17 languages |
| `complete_features_wasm_execution_test.py` | Executable WASM validation |
| `frontend_equivalence_test.py` | All 17 frontends produce equivalent output |
| `semantic_analyzer_test.py` | Scope, symbol table, type checking |
| `scope_closure_object_model_test.py` | Scope, closures, and object model integration |
| `core_ir_test.py` | Core IR representation and lowering |
| `surface_normalizer_test.py` | Surface normalization (Spanish, Japanese, Portuguese) |
| `regression_fixes_test.py` | Regression guard for past bug fixes |

### Testing Conventions

- Use `check_semantics=False` in tests that exercise parser/codegen in isolation, to bypass the
  pre-existing SemanticAnalyzer false-positive for top-level assignments in some languages.
- WAT tests: use `has_stub_calls(wat_text)` to assert no stubs exist when testing lowerable code.
- WASM execution tests span multiple files: `WATInheritanceWasmExecutionTestSuite` (3 inheritance exec tests in `wat_generator_test.py`) and broader coverage in `wat_generator_wasm_execution_test.py`.

---

## 11. CLI Reference

### Entry Point

`multilingualprogramming.__main__:main()` — invoked as `multilingual` or `multilg`.

### Subcommands

```bash
# Execute a .ml file
multilingual run hello.ml
multilingual run hello.ml --lang fr

# Start interactive REPL
multilingual repl
multilingual repl --lang fr --show-python --show-wat

# Transpile to Python (print output)
multilingual compile hello.ml --lang en

# Build WASM bundle
multilingual build-wasm-bundle hello.ml --lang en --out-dir ./dist

# Validate language packs
multilingual smoke --all
multilingual smoke --lang fr

# Check generated output encoding
multilingual encoding-check-generated hello.ml --lang en

# Version
multilingual --version
```

### REPL Interactive Commands

| Command | Description |
|---|---|
| `:help` | Show help |
| `:language <code>` | Switch active language (e.g., `:language fr`) |
| `:python` | Toggle display of generated Python |
| `:wat` / `:wasm` | Toggle display of generated WAT |
| `:rust` / `:wasmtime` | Toggle Wasmtime bridge display |
| `:reset` | Clear session state |
| `:kw [lang]` | Show keywords for a language |
| `:ops [lang]` | Show operators and symbols |
| `:q` | Exit REPL |

---

## 12. Common Tasks — Patterns & Pitfalls

### Adding a New Keyword Concept

1. Add the concept to `multilingualprogramming/resources/usm/keywords.json` under the appropriate
   section, with translations for all (or relevant) languages.
2. Update the concept count assertion in `tests/keyword_registry_test.py`.
3. Handle the new concept token in `multilingualprogramming/parser/parser.py` (add to the
   relevant parse method).
4. If the concept needs WAT lowering, add handling in `multilingualprogramming/codegen/wat_generator.py`.

### Adding a New Language

Follow `docs/language_onboarding.md`. At minimum:
1. Add a new language code and all concept translations to `keywords.json`.
2. Add localized builtins to `builtins_aliases.json`.
3. Add operator symbols to `operators.json`.
4. Add error messages to `resources/parser/error_messages.json`.
5. Add datetime resources to `resources/datetime/`.
6. Add any surface normalization rules to `surface_patterns.json`.
7. Write smoke tests and run `multilingual smoke --lang <code>`.

### Adding a New Builtin Alias

Add to `multilingualprogramming/resources/usm/builtins_aliases.json`:

```json
{
  "fr": {
    "nouvelnomlocal": "python_builtin_name"
  }
}
```

### Handling Multi-line Literals in Parser

Inside list/dict/call/tuple parse methods, use `_skip_bracket_newlines()` instead of
`_skip_newlines()`. This skips INDENT and DEDENT tokens emitted by the lexer even inside brackets.

### Debugging exec() Namespace Issues

Use `make_exec_globals(language, extra=None)` from `codegen/runtime_builtins.py`:

```python
from multilingualprogramming.codegen.runtime_builtins import make_exec_globals
ns = make_exec_globals("fr", extra={"myvar": 42})
exec(python_source, ns)
```

### Checking WAT Output for Unsupported Constructs

```python
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator, has_stub_calls

gen = WATCodeGenerator("en")
wat = gen.generate(ast)
if has_stub_calls(wat):
    print("WAT contains unsupported call stubs")
```

---

## 13. Known Issues & Gotchas

### SemanticAnalyzer — Augmented Assignment on Undefined Variable

Augmented assignment (`x += 1`) correctly reports `UNDEFINED_NAME` when the target variable has
not been previously defined. Plain assignment (`x = 1`) implicitly defines the variable (Python
semantics).

### Lexer INDENT/DEDENT Inside Brackets

The lexer emits INDENT and DEDENT tokens even inside bracket pairs (unlike CPython, which
suppresses them). Any parser method that handles multi-line constructs inside brackets
**must** call `_skip_bracket_newlines()` rather than `_skip_newlines()`.

### WAT `min`/`max` — n-arg Supported

The WAT backend lowers `min(a, b, c, …)` and `max(a, b, c, …)` to chained `f64.min` /
`f64.max` for any number of arguments ≥ 1.

### `super()` in WAT — Guard Ordering

The `super()` detection guard in `_gen_stmt()` and `_gen_expr()` **must run first** before
the generic CallExpr branch. If you add new statement/expression types, insert them after
the super() guard or ensure the guard still runs first.

### Concept Count in Tests

`tests/keyword_registry_test.py` has a hardcoded assertion on the number of concepts (50).
When adding a new concept to `keywords.json`, **update this count** or the test will fail.

### WASM Execution Tests Requiring `rustc`

2 tests in `WATInheritanceWasmExecutionTestSuite` are skipped because they require the
`rustc` compiler with the `wasm32` target installed. This is expected — they are marked as
skipped in the test report.

### `keywords.json` Multi-word Forms

Always add **both** forms for multi-word keywords:
- Space-separated: `"not in"`
- Underscore-joined: `"not_in"`

Both forms must appear in the language's array for reliable lexer matching.

---

## 14. Supported Languages

| Code | Language | Code | Language |
|---|---|---|---|
| `en` | English | `it` | Italian |
| `fr` | French | `pt` | Portuguese |
| `es` | Spanish | `pl` | Polish |
| `de` | German | `nl` | Dutch |
| `hi` | Hindi | `sv` | Swedish |
| `ar` | Arabic | `da` | Danish |
| `bn` | Bengali | `fi` | Finnish |
| `ta` | Tamil | | |
| `zh` | Chinese (Simplified) | `ja` | Japanese |

**All 17 languages have**:
- Keyword translations (keywords.json)
- Operator symbols (operators.json)
- Localized builtin aliases (builtins_aliases.json)
- Localized error messages (error_messages.json)
- Datetime resources (months, weekdays, eras, formats)

---

## 15. Version & Release Info

### Current Version: `0.6.0`

Defined in `multilingualprogramming/version.py`.

### Recent Release History

| Version | Highlights |
|---|---|
| `0.6.0` | WAT/WASM OOP object model, inheritance, `with`/`try`/`match`/`lambda`/`async` lowering, bytes support, WAT backend reorganization; real `try/except/finally` with numeric exception codes; `input()` / `argc()` / `argv()` builtins; DOM bridge (`"env"` host imports + WAT wrappers); source location comments in WAT |
| `0.5.1` | Documentation updates |
| `0.5.0` | WAT/WASM OOP object model; class lowering; inheritance; WAT execution tests; Unicode identifier reliability |
| `0.4.0` | WAT/WASM code generation; browser playground; WASM backend with 25+ Python fallbacks; 20 corpus projects |
| `0.3.0` | Earlier milestone |

### Supported Python Versions

Python 3.12, 3.13, 3.14. Minimum required: **3.12**.

### Release Process

See `docs/releasing.md`. Releases are triggered by a git tag and published automatically to PyPI
via the `release-pypi.yml` GitHub Actions workflow.

---

*Last updated: 2026-03-16. For changes after this date, check CHANGELOG.md and git log.*
