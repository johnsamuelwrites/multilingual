# Multilingual 1.0 Roadmap

This roadmap translates the Multilingual 1.0 vision into repository-shaped
implementation phases.

## Goal

Build Multilingual 1.0 into a multilingual semantic platform with AI-native,
multimodal, and reactive capabilities.

## Current Starting Point

The repository already provides strong leverage:

- data-driven multilingual keyword infrastructure
- shared AST across supported natural languages
- parser and semantic analyzer pipeline
- Python backend
- WAT/WASM backend
- browser-oriented DOM functionality
- a large regression suite

The main limitation is that the core layer is still too thin. The repository
has a `CoreIRProgram`, but not yet a rich semantic IR that defines the language
independently of backend behavior.

## Success Criteria

Multilingual 1.0 is successful when:

- the semantic IR is the true language boundary
- structured data and matching are central language features
- AI and multimodal workflows are first-class
- reactive web programming is part of the main story
- the transition is test-backed and staged rather than disruptive

## Workstreams

The roadmap is organized into six workstreams:

- language definition
- compiler architecture
- type/effect system
- AI and multimodal runtime
- reactive UI and web tooling
- ecosystem and developer experience

## Phase 1: Define the New Center

Goal:

- establish Multilingual 1.0 as a new language direction before major runtime
  changes

Tasks:

- add a product-level vision document
- publish a Core 1.0 semantic draft
- define a stable list of new semantic pillars

Repository targets:

- `docs/vision.md`
- `docs/spec/core_1_0.md`
- future companion specs for `ai`, `effects`, `reactive_ui`, and `multimodal`

Exit criteria:

- contributors can describe Multilingual 1.0 as a language in its own right
- new features can be judged against an explicit 1.0 direction

## Phase 2: Introduce a Real Semantic IR

Goal:

- make the shared core executable as a semantic layer rather than a thin wrapper

Tasks:

- add semantic IR node types
- add typed declarations for records and unions
- represent mutability explicitly
- represent `option`, `result`, and pattern matching directly in the IR
- represent capabilities/effects in the IR

Suggested repository additions:

- `multilingualprogramming/core/ir_nodes.py`
- `multilingualprogramming/core/types.py`
- `multilingualprogramming/core/effects.py`
- `multilingualprogramming/core/semantic_lowering.py`
- `multilingualprogramming/core/validators.py`

Exit criteria:

- AST is lowered into a semantic IR that is meaningfully richer than the parser
  tree
- backend codegen can consume semantic IR as the primary semantic boundary

## Phase 3: Modernize the Core Language

Goal:

- ship the first unmistakable Core 1.0 language features

Tasks:

- introduce `fn` as the primary function keyword
- add `var` alongside existing `let` for explicit mutability
- add `|>` pipe operator to the lexer, parser, and AST
- add `?` error-propagation operator for `result<T, E>` functions
- add `enum` for tagged union declarations
- add record type declarations with `type Name = { ... }`
- add `option<T>` and `result<T, E>` as built-in generic types
- expand `match` into a flagship feature with record and union destructuring,
  guard expressions, and exhaustiveness checking
- improve async semantics for backend-neutral lowering
- register all new keywords (`fn`, `var`, `enum`, `observe`) in the USM
  keyword registry for all 17 languages

Suggested parser and resource targets:

- `multilingualprogramming/parser/parser.py`
- `multilingualprogramming/parser/ast_nodes.py`
- `multilingualprogramming/resources/usm/keywords.json`
- `multilingualprogramming/resources/usm/surface_patterns.json`

Suggested tests:

- `tests/core1/test_fn_syntax.py`
- `tests/core1/test_pipe_operator.py`
- `tests/core1/test_types.py`
- `tests/core1/test_pattern_matching.py`
- `tests/core1/test_results_options.py`
- `tests/core1/test_async_core.py`

Exit criteria:

- users can model modern structured state with clear Core 1.0 constructs
- `fn`, `|>`, and `?` are usable in all 17 supported surface languages
- pattern matching is powerful enough to be a signature feature

## Phase 4: Add Capabilities and Effect Checking

Goal:

- make external interaction explicit and analyzable

Tasks:

- add capability declarations such as `uses ai`, `uses dom`, `uses net`
- perform semantic checks over effect boundaries
- integrate capability metadata into package and backend planning

Suggested repository targets:

- `multilingualprogramming/core/effects.py`
- `multilingualprogramming/parser/semantic_analyzer.py`
- `multilingualprogramming/runtime/backend_selector.py`

Exit criteria:

- effectful operations are visible in semantic analysis
- diagnostics can explain capability violations clearly

## Phase 5: AI-Native and Multimodal Runtime

Goal:

- make Multilingual distinct in the LLM and multimodal era

Tasks:

### AI language constructs

- add `prompt` as a language keyword that produces a string from a model
- add `think` as a block form that returns a structured reasoning result with
  `.conclusion` and `.trace` fields
- add `stream` as a keyword that returns `stream<string>` from a model
- add `generate` as a typed output keyword constrained by the declared return
  type
- add `embed` as a keyword returning `vector<float>` from a model
- add `extract` and `classify` as semantic shorthand for structured generation
- add `~=` semantic match operator backed by embedding distance
- add model reference literals: `@model-name` resolves to a `model` value
- register `prompt`, `think`, `stream`, `generate`, `embed`, `extract`,
  `classify`, `observe` in the USM registry for all 17 languages

### Agent and tool semantics

- add `@agent` decorator with a required `model` parameter and automatic
  tool-loop scaffolding provided by the runtime
- add `@tool` decorator with a required `description` parameter; tools are
  automatically registered for use by agents in scope
- add `plan` as a structured multi-step reasoning primitive for agents

### Structured output and retrieval

- add schema-constrained generation: `result: Invoice = generate @m: ...`
- add structured output validation using the declared type at runtime
- add `nearest(vec, index, top_k)` as a built-in retrieval primitive
- add retrieval-oriented runtime helpers for building RAG pipelines

### Multimodal types

- add first-class `image`, `audio`, `video`, and `document` value types
- add a `canvas` render target for multimodal output composition
- multimodal values should be usable directly in `prompt` and `generate`
  expressions

Suggested repository additions:

- `multilingualprogramming/runtime/ai_runtime.py`
- `multilingualprogramming/runtime/ai_types.py`
- `multilingualprogramming/runtime/tool_runtime.py`
- `multilingualprogramming/runtime/retrieval_runtime.py`
- `multilingualprogramming/runtime/multimodal_runtime.py`
- `multilingualprogramming/runtime/semantic_match.py`

Suggested tests:

- `tests/core1/test_ai_semantics.py`
- `tests/core1/test_prompt_think_stream.py`
- `tests/core1/test_agent_tool.py`
- `tests/core1/test_semantic_match.py`
- `tests/core1/test_multimodal.py`

Exit criteria:

- the language can express typed AI workflows natively using language keywords,
  not library calls
- `@agent` + `@tool` programs are demonstrable in at least three surface
  languages
- multimodal pipelines are easy to demonstrate in a few lines of code
- `~=` semantic matching works across human-language input without manual
  embedding calls

## Phase 6: Reactive Web Platform

Goal:

- turn existing DOM support into a modern application model

Tasks:

- add `observe var` as a reactive mutable binding in the parser and semantic IR
- add `on <signal>.change` event handler syntax
- add declarative view composition via `canvas` blocks and `render` expressions
- add event handlers as first-class constructs
- support async UI updates driven by `stream<T>` values
- integrate AI streams with reactive state: a streaming `prompt` response
  should be bindable directly to a reactive view
- preserve low-level DOM access as an escape hatch

Suggested repository additions:

- `multilingualprogramming/runtime/reactive.py`
- `multilingualprogramming/codegen/ui_lowering.py`

Suggested tests:

- `tests/core1/test_reactive_ui.py`
- `tests/core1/test_observe_var.py`
- `tests/core1/test_stream_to_view.py`

Suggested demos:

- `examples/reactive_counter.ml`
- `examples/multilingual_dashboard.ml`
- `examples/streaming_chat_fr.ml`
- `examples/semantic_search_ja.ml`

Exit criteria:

- the primary web story is no longer raw imperative DOM manipulation
- users can build small interactive applications idiomatically
- a streaming AI response can update a reactive view in a single pipeline
  expression

## Phase 7: Tooling and Positioning

Goal:

- align the public interface and developer experience with the new language

Tasks:

- add CLI support for semantic IR inspection
- add legacy vs core execution modes
- improve playground messaging and examples
- add language-server and diagnostics goals to the roadmap
- reposition examples and docs around AI, multimodal, and reactive workflows

Suggested CLI additions:

- `multilingual ir`
- `multilingual explain`
- `multilingual ui-preview`
- `multilingual run --mode legacy|core`

Suggested repository targets:

- `multilingualprogramming/__main__.py`
- `docs/playground.md`
- `docs/demos.md`

Exit criteria:

- the project feels like a modern language platform rather than only a
  transpiler

## Recommended Near-Term Deliverables

The highest-value next steps are:

1. land the 1.0 vision and core spec documents (this phase is complete)
2. create semantic IR scaffolding in `multilingualprogramming/core/`
3. implement `fn`, `|>`, `?` and register them in the USM for all 17 languages
4. implement `let`/`var`, `enum`, records, and `result`/`option`
5. make pattern matching substantially stronger, add `~=` semantic match
6. define AI runtime abstractions (`prompt`, `think`, `stream`, `embed`,
   `@agent`, `@tool`) before any provider-specific integrations
7. build reactive UI with `observe var` on top of existing DOM groundwork

## Flagship Examples for 1.0

The first public examples of the new direction should include:

- a reactive counter app (`examples/reactive_counter.ml`)
- a multilingual tool-using assistant written in three languages showing
  identical semantics (`examples/agent_en.ml`, `examples/agent_fr.ml`,
  `examples/agent_ja.ml`)
- a typed invoice extractor from PDF using `generate` with a declared schema
- an image captioning pipeline using multimodal `prompt`
- a retrieval-based question-answering example using `embed` and `nearest`
- a streaming chat UI showing a `stream` expression bound to a reactive view
- a semantic intent classifier using `~=` across multilingual user input

These examples should become the public face of Multilingual 1.0.

The most compelling demo is the agent shown in three languages: it proves the
core claim that Multilingual is the only AI programming platform where the same
agent logic is idiomatic in any human language.
