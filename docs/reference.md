# multilingualprogramming Reference

This document is the detailed reference for the project.

## Overview

`multilingualprogramming` is a Python framework for multilingual programming. It supports writing source code with keywords, numerals, and literals from multiple human languages while mapping everything to a shared semantic model.

Python compatibility baseline:
- [compatibility_matrix.md](compatibility_matrix.md)
- [compatibility_roadmap.md](compatibility_roadmap.md)

Version and release status:
- Package version: `multilingualprogramming/version.py`
- Release notes: [`CHANGELOG.md`](CHANGELOG.md)

## Supported Languages

- English
- French
- Spanish
- German
- Italian
- Portuguese
- Polish
- Dutch
- Swedish
- Danish
- Finnish
- Hindi
- Arabic
- Bengali
- Tamil
- Chinese (Simplified)
- Japanese

## Core Components

### Numeral System

- `MPNumeral`
- `UnicodeNumeral`
- `RomanNumeral`
- `ComplexNumeral`
- `FractionNumeral`
- `NumeralConverter`

Key capabilities:

- arithmetic across numeral scripts
- conversion across scripts
- Unicode fraction handling
- scientific notation helpers

### Keyword and Concept Model

- `KeywordRegistry`
- `KeywordValidator`

Key capabilities:

- concept -> keyword lookup (`COND_IF` -> `if`, `si`, etc.)
- keyword -> concept reverse lookup
- supported-language discovery
- ambiguity/completeness checks

### Date and Time

- `MPDate`
- `MPTime`
- `MPDatetime`

Key capabilities:

- multilingual parsing and formatting
- script-aware numeric rendering

### Frontend (Lexing, Parsing, Semantic Analysis)

- `Lexer`
- `Parser`
- AST node model in `multilingualprogramming/parser/ast_nodes.py`
- `core.semantic_analyzer.SemanticAnalyzer`
- `ASTPrinter`

Key capabilities:

- Unicode-aware tokenization
- AST generation from multilingual source
- scope and symbol checks
- multilingual semantic error messages

### Runtime and Execution

- `PythonCodeGenerator`
- `RuntimeBuiltins`
- `ProgramExecutor`
- `REPL`

Key capabilities:

- transpile multilingual semantic IR to Python source
- execute full pipeline: source -> tokens -> optional normalization -> AST -> IR -> checks -> Python/WAT -> runtime
- inject multilingual runtime builtins
- interactive REPL with language switching and Python-preview mode

### AI Runtime

- `AIRuntime` — singleton registry that dispatches AI calls to the active provider
- `AIProvider` — abstract base class for LLM backends
- `AnthropicProvider` — concrete provider backed by the Anthropic Messages API

Key capabilities:

- `prompt(model, template)` — single-turn text completion
- `think(model, template)` — extended chain-of-thought reasoning (returns `Reasoning`)
- `generate(model, template, target_type)` — structured / JSON-mode generation
- `stream(model, template)` — token-by-token streaming (returns `Iterator[StreamChunk]`)
- `embed(model, text)` — text embedding (returns `EmbeddingVector`)
- `extract / classify / plan / transcribe / retrieve` — specialised AI operations
- provider registration: `AIRuntime.register(AnthropicProvider())`

Model reference literals in source (`@claude-sonnet`, `@claude-haiku`, …) resolve to
full model IDs via `AnthropicProvider._MODEL_ALIASES`.

### Reactive / UI Runtime

- `ReactiveEngine` — engine managing observable `Signal` objects
- `Signal` — a value cell that notifies subscribers on change
- `CanvasNode` — a named UI canvas region
- `stream_to_view(signal, target)` — bind a signal stream to a view target

Key capabilities:

- `observe name = value` / `on name.change:` reactive declarations
- `canvas name:` / `render target = value` canvas and rendering
- `view target = signal` binding

### Structured Concurrency Runtime

- `Channel` — typed async FIFO channel backed by `asyncio.Queue`

Key capabilities:

- `channel<T>()` creates a `Channel` (unbounded or with `capacity`)
- `await ch.send(value)` / `await ch.receive()` — async message passing
- `async for item in ch:` — iteration until channel is closed
- `par [ expr1, expr2, … ]` — parallel fan-out; lowers to `asyncio.gather()`
- `spawn expr` — background task; lowers to `asyncio.create_task()`

### Observability Runtime

- `ml_trace(value, label)` — record a `TraceEvent` and return value unchanged
- `ml_cost(value)` — return `(value, CostInfo)` with token and latency data
- `ml_explain(value)` — return `(value, explanation_text)` from the model

Key capabilities:

- transparent: original result always flows through unchanged
- `TraceEvent` / `CostInfo` data classes for structured inspection
- global trace log via `get_trace_log()` / `clear_trace_log()`

### Placement Runtime

- `@local` / `@edge` / `@cloud` — deployment target annotations

Key capabilities:

- decorators attach `__ml_placement__` to any function or agent
- Python backend executes locally; a distributed backend routes on the hint
- `get_placement(fn)` — inspect the placement of any callable

### Agent Memory and Coordination Runtime

- `MemoryStore` / `ml_memory(name, scope)` — named key-value stores
- `Swarm` — pool of named sub-agents with fan-out and delegation
- `ml_delegate(swarm_or_agent, …)` — async message to an agent
- `swarm_decorator` — `@swarm(agents=[…])` decorator factory

Key capabilities:

- memory scopes: `"session"` (in-process), `"persistent"` (JSON file), `"shared"` (swarm-wide)
- `Swarm.broadcast(message)` — fan-out to all sub-agents concurrently
- `delegate(agent, message)` in source lowers to `await ml_delegate(…)`

## Language Features

### AI-native constructs

Effects must be declared on the enclosing function or agent with `uses ai`:

```text
fn summarise(text: str) -> str uses ai:
    return prompt @claude-sonnet: "Summarise: " + text

fn reasoning_demo() uses ai:
    let r = think @claude-sonnet:
        What are the implications of AI-native programming?
    print(r.conclusion)

fn typed_output() uses ai:
    let result: SentimentLabel = generate @claude-sonnet: "Classify: great product"
```

Available AI keywords (all 17 languages supported — see `keywords.json`):

| Concept | English | French | Japanese |
|---------|---------|--------|----------|
| prompt  | `prompt` | `requête` / `requete` | `プロンプト` |
| think   | `think` | `réfléchir` | `考える` |
| generate | `generate` | `générer` | `生成する` |
| stream  | `stream` | `diffuser` | `ストリーム` |
| embed   | `embed` | `incorporer` | `埋め込む` |
| extract | `extract` | `extraire` | `抽出する` |
| classify | `classify` | `classifier` | `分類する` |
| plan    | `plan` | `planifier` | `計画する` |
| transcribe | `transcribe` | `transcrire` | `書き起こす` |
| retrieve | `retrieve` | `récupérer` | `取得する` |

Agent and tool declarations:

```text
@tool(description="Search the web")
fn web_search(query: str) -> str uses net:
    pass

@agent(model=@claude-sonnet)
fn researcher(question: str) -> str uses ai, net:
    return prompt @claude-sonnet: question
```

### Structured concurrency

```text
# Parallel fan-out — all branches run concurrently, results returned as tuple
let results = parallel [
    prompt @claude-sonnet: "Answer A",
    prompt @claude-sonnet: "Answer B"
]

# Background task — returns immediately with a future
let task = spawn long_running_operation()

# Typed channel — async FIFO between tasks
let ch = channel()
spawn producer(ch)
let item = ch.receive()
```

All concurrency keywords are multilingual:

| Concept | English | French | Japanese |
|---------|---------|--------|----------|
| parallel | `par` / `parallel` | `parallèle` | `並列` |
| spawn   | `spawn` / `launch` | `lancer` | `起動` |
| channel | `channel` | `canal` | `チャネル` |
| send    | `send` | `envoyer` | `送る` |
| receive | `receive` | `recevoir` | `受信` |

### Observability

```text
fn monitored() uses ai:
    # trace — log timing; value passes through unchanged
    let result = trace(prompt @claude-sonnet: "Hello", "my-label")

    # cost — returns (value, CostInfo) with token counts
    let answer, info = cost(prompt @claude-sonnet: "What is AI?")
    print(info)   # CostInfo(model='claude-sonnet-4-6', tokens=42, latency=1200ms)

    # explain — returns (value, explanation_text)
    let value, why = explain(answer)
```

### Distributed placement

```text
@local
fn preprocess(data: str) -> str:
    pass          # hint: run on local machine

@edge
fn classify_fast(img: str) -> str uses ai:
    pass          # hint: run at the network edge

@cloud
@agent(model=@claude-sonnet)
fn heavy_reasoning(prompt: str) -> str uses ai:
    pass          # hint: run in the cloud
```

Placement keywords are multilingual (`local`/`lokal`/`स्थानीय`/`本地`/`ローカル` …).

### Agent memory and coordination

```text
fn with_memory() uses ai:
    # Named session store (dict-like)
    let facts = memory("facts")
    facts["answer"] = "Paris"

    # Persistent across runs
    let cache = memory("cache", scope="persistent")

@swarm(agents=[researcher, writer, reviewer])
fn team_coordinator(task: str) -> str uses ai:
    # Fan-out to two sub-agents simultaneously
    let draft, review = parallel [
        delegate(writer, task),
        delegate(reviewer, task)
    ]
    return prompt @claude-sonnet: "Merge: " + draft + "\n" + review
```

Memory scopes: `"session"` (default, in-process), `"persistent"` (JSON-backed file), `"shared"` (swarm-wide in-process).

### General language features

The implementation includes support for:
- booleans and `None`, including identity checks (`is`, `is not`)
- control flow (`if/else`, `for`, `while`)
- async constructs (`async def`, `await`, `async for`, `async with`)
- functions and classes
- imports (`import`, `from ... import ...`, aliases with `as`)
- assertions
- exception handling (`try`, `except`, `else`, `finally`)
- chained assignment
- slices (`a[1:3]`, `a[::-1]`)
- comprehensions (list, dict, generator), including nested `for` clauses
- default parameters, `*args`, `**kwargs`
- tuple unpacking
- decorators
- f-strings
- triple-quoted strings

Example (nested comprehension):

```text
let rows = [[1, 2], [3, 4]]
let flat = [x for row in rows for x in row]
print(flat)  # [1, 2, 3, 4]
```

Example (async for / async with):

```text
import asyncio

class AsyncCtx:
    async def __aenter__(self):
        return 1
    async def __aexit__(self, exc_type, exc, tb):
        return False

async def main(xs):
    let total = 0
    async with AsyncCtx() as base:
        async for i in xs:
            total = total + i + base
    return total

print(asyncio.run(main([1, 2, 3])))
```

## API Entry Points

Most commonly used imports:

```python
from multilingualprogramming import (
    MPNumeral,
    KeywordRegistry,
    MPDate,
    Lexer,
    Parser,
    ASTPrinter,
    PythonCodeGenerator,
    ProgramExecutor,
    REPL,
)

from multilingualprogramming.core.semantic_analyzer import SemanticAnalyzer
```

## CLI and REPL

Run interactive mode:

```bash
python -m multilingualprogramming repl
python -m multilingualprogramming repl --lang fr
python -m multilingualprogramming repl --show-python
python -m multilingualprogramming repl --show-wat
python -m multilingualprogramming repl --show-rust
```

REPL commands:

- `:help`
- `:language <code>`
- `:python` — toggle generated Python display
- `:wat` — toggle generated WAT (WebAssembly Text) display
- `:rust` — toggle generated Rust/Wasmtime bridge code display
- `:reset`
- `:kw [XX]`
- `:ops [XX]`
- `:q`

## REPL Language Smoke Tests

Use these two snippets to quickly validate each language in REPL.

Snippet A (variables + print):

```text
<LET> x = 2
<LET> y = 3
<PRINT>(x + y)
```

Snippet B (for loop):

```text
<LET> total = 0
<FOR> i <IN> <RANGE_ALIAS>(4):
    total = total + i
<PRINT>(total)
```

Built-in aliases are also available for selected universal functions.
Both the universal name and localized alias work. Example (French):

```text
afficher(intervalle(4))
afficher(longueur([10, 20, 30]))
afficher(somme([1, 2, 3]))
```

Language-specific forms:

### English (`en`)

```text
let x = 2
let y = 3
print(x + y)

let total = 0
for i in range(4):
    total = total + i
print(total)
```

### French (`fr`)

```text
soit x = 2
soit y = 3
afficher(x + y)

soit somme = 0
pour i dans intervalle(4):
    somme = somme + i
afficher(somme)
```

### Spanish (`es`)

```text
sea x = 2
sea y = 3
imprimir(x + y)

sea suma = 0
para i en rango(4):
    suma = suma + i
imprimir(suma)
```

### German (`de`)

```text
sei x = 2
sei y = 3
ausgeben(x + y)

sei summe = 0
für i in bereich(4):
    summe = summe + i
ausgeben(summe)
```

### Italian (`it`)

```text
sia x = 2
sia y = 3
stampa(x + y)

sia totale = 0
per i in intervallo(4):
    totale = totale + i
stampa(totale)
```

### Portuguese (`pt`)

```text
seja x = 2
seja y = 3
imprimir(x + y)

seja soma = 0
para i em intervalo(4):
    soma = soma + i
imprimir(soma)
```

### Hindi (`hi`)

```text
मान x = 2
मान y = 3
छापो(x + y)

मान योग = 0
के_लिए i में परास(4):
    योग = योग + i
छापो(योग)
```

### Arabic (`ar`)

```text
ليكن x = 2
ليكن y = 3
اطبع(x + y)

ليكن المجموع = 0
لكل i في مدى(4):
    المجموع = المجموع + i
اطبع(المجموع)
```

### Bengali (`bn`)

```text
ধরি x = 2
ধরি y = 3
ছাপাও(x + y)

ধরি মোট = 0
জন্য i মধ্যে পরিসর(4):
    মোট = মোট + i
ছাপাও(মোট)
```

### Tamil (`ta`)

```text
இருக்கட்டும் x = 2
இருக்கட்டும் y = 3
அச்சிடு(x + y)

இருக்கட்டும் மொத்தம் = 0
ஒவ்வொரு i இல் வரம்பு(4):
    மொத்தம் = மொத்தம் + i
அச்சிடு(மொத்தம்)
```

### Chinese (`zh`)

```text
令 x = 2
令 y = 3
打印(x + y)

令 总计 = 0
对于 i 里 范围(4):
    总计 = 总计 + i
打印(总计)
```

### Japanese (`ja`)

```text
変数 x = 2
変数 y = 3
表示(x + y)

変数 合計 = 0
毎 i 中 範囲(4):
    合計 = 合計 + i
表示(合計)
```

## Examples

Runnable examples are documented in:

- [examples/README.md](_generated/examples/README.md)

Preferred starter examples:

- `examples/hello_en.multi`
- `examples/hello_fr.multi`
- `examples/cross_import_main_en.multi`

Complete feature coverage examples:

- `examples/complete_features_*.multi` (one file per supported language; `.ml` also supported)

Run:

```bash
python -m multilingualprogramming run examples/complete_features_en.multi --lang en
python -m multilingualprogramming run examples/complete_features_fr.multi --lang fr
python -m multilingualprogramming run examples/complete_features_es.multi --lang es
```

Run all examples from repository root:

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

## Development

```bash
python -m pytest -q
python -m pylint $(git ls-files '*.py')
```

## Related Docs

- Project quick start: [README.md](index.md)
- Design overview: [design.md](design.md)
- Core formal specification: [core_spec.md](core_spec.md)
- Frontend translation contracts: [frontend_contracts.md](frontend_contracts.md)
- Related work and differentiation: [related_work.md](related_work.md)
- Controlled language scope: [cnl_scope.md](cnl_scope.md)
- Evaluation plan: [evaluation_plan.md](evaluation_plan.md)
- Word order and syntax naturalness: [word_order_and_naturalness.md](word_order_and_naturalness.md)
- Standard library localization strategy: [stdlib_localization.md](stdlib_localization.md)
- Translation governance: [translation_guidelines.md](translation_guidelines.md)
- Development and debugging guide: [development.md](development.md)
- Python compatibility matrix: [compatibility_matrix.md](compatibility_matrix.md)
- Python 3.12 compatibility roadmap: [compatibility_roadmap.md](compatibility_roadmap.md)
- Usage snippets: [USAGE.md](_generated/USAGE.md)
- Examples guide: [examples/README.md](_generated/examples/README.md)
- French programming guide: [fr/programmation.md](fr/programmation.md)
- Language onboarding: [language_onboarding.md](language_onboarding.md)

## License

- Code: GPLv3+
- Documentation/content: CC BY-SA 4.0
