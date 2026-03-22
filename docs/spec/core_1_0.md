# Multilingual Core 1.0

This document defines the semantic blueprint of Multilingual 1.0.

Core 1.0 is the stable center of the language. Human-language frontends,
interactive tools, AI systems, and execution targets all meet here.

The purpose of this document is to define what the language is, not merely how
it is currently implemented.

## Purpose

Core 1.0 exists to give Multilingual:

- one precise semantic identity
- one shared foundation across human-language surfaces
- one language model for code, data, AI, concurrency, and interaction
- one portable representation that can move across execution environments
- one semantic basis for distributed and long-running programs

Detailed specifications for AI, multimodal, reactive UI, concurrency, and
distribution layers may grow into companion documents, but Core 1.0 defines
the semantic ground they stand on.

## Semantic Model

Every program in Multilingual 1.0 is understood in three layers:

1. a human-language surface
2. a shared semantic representation
3. an execution form

The surface may vary. The execution target may vary. The semantics do not.

This is the central contract of the language.

## Values

Core 1.0 includes these foundational value families:

- `none`
- `bool`
- `int`
- `float`
- `decimal`
- `string`
- `bytes`
- `list<T>`
- `set<T>`
- `map<K, V>`
- `tuple<...>`
- `record`
- `option<T>`
- `result<T, E>`
- `range`
- `function`
- `stream<T>`
- `signal<T>`

Core 1.0 is also designed to host these first-class capability-oriented values:

- `image`
- `audio`
- `video`
- `document`
- `embedding`
- `prompt`
- `model`
- `tool`
- `resource`
- `future<T>`
- `channel<T>`
- `memory`

These are not second-class library conventions. They belong to the language
model.

## Bindings and Mutability

Bindings are explicit about mutability.

- `let` creates an immutable binding
- `var` creates a mutable binding

```text
let name = "Amina"
var count = 0
```

Rebinding an immutable name is a semantic error.

Core 1.0 distinguishes between:

- mutation of a binding
- mutation of a value

That distinction should remain visible in the semantic representation and in
diagnostics.

## Data Model

Structured data is a first-class part of the language.

### Records

Records are named-field values.

```text
type User = {
  id: int
  name: string
  email: option<string>
}
```

### Tagged unions

Tagged unions represent well-typed alternatives.

```text
enum FetchState =
  | Idle
  | Loading
  | Loaded { user: User }
  | Failed { message: string }
```

### Result and absence

Core 1.0 treats absence and failure as explicit data shapes:

- `option<T>` expresses presence or absence
- `result<T, E>` expresses success or expected failure

These constructs are central to control flow, API design, and AI output
handling.

## Type System

Core 1.0 uses gradual typing with inference.

Its goals are:

- clarity without excessive ceremony
- strong structure for records, unions, and schemas
- useful inference for common code
- enough type information for tooling, optimization, and validation

Type information should be preserved in the semantic representation even when
it is partly inferred.

## Functions

Functions are first-class values and are declared with `fn`.

Core 1.0 supports:

- named functions
- anonymous functions
- closures
- typed parameters and return values
- async functions
- explicit capability annotations

```text
fn greet(name: string) -> string:
  "Hello, {name}!"

let double = fn(x: int): x * 2
```

## Composition

Composition is a language-level concern, not a stylistic accident.

### Pipe operator

The `|>` operator threads a value through transformations.

```text
let result = names
  |> filter(fn(n): n.length > 3)
  |> map(fn(n): n.upper())
  |> join(", ")
```

This style should work equally well for data pipelines, event streams, and AI
workflows.

### Result propagation

The `?` operator propagates failure from a `result<T, E>`.

```text
fn parse_user(data: string) -> result<User, ParseError>:
  let json = parse_json(data)?
  let name = json["name"]?
  ok(User(name: name))
```

## Pattern Matching

Pattern matching is a central Core 1.0 construct.

It should support:

- literal patterns
- identifier capture
- wildcards
- tuple and list destructuring
- record destructuring
- tagged union cases
- optional guards

```text
match state
  case Loaded { user }:
    show(user.name)
  case Failed { message }:
    show(message)
  case _:
    show("waiting")
```

Exhaustiveness checking for well-defined union types is part of the long-term
language contract.

## Control Flow

Core 1.0 supports:

- conditional execution
- loops
- matching
- early return
- async suspension
- stream iteration

Control flow should lower cleanly into multiple execution environments without
giving up semantic clarity.

## Async and Streams

Asynchrony is a first-class part of the language.

Core 1.0 supports:

- `async fn`
- `await`
- `for await`
- `stream<T>`

`stream<T>` is the standard representation for incrementally produced values,
including event sources, generated tokens, and long-lived computations.

## Structured Concurrency and Parallelism

Concurrent and parallel execution are first-class semantic properties.

Core 1.0 provides:

### Parallel fan-out

`par` runs a fixed set of expressions simultaneously and collects their results
as a tuple. All branches must complete before execution continues.

```text
let (summary, tags, sentiment) = par [
  summarize(doc),
  extract_tags(doc),
  classify_sentiment(doc)
]
```

This is the primary idiom for running multiple AI operations in parallel.

### Spawning concurrent tasks

`spawn` launches a task that runs concurrently and returns a `future<T>`. The
result is retrieved with `await`.

```text
let task = spawn long_computation(input)
let result = await task
```

### Typed channels

`channel<T>` is a typed conduit between concurrent tasks. Channels are
directional, buffered or unbounded, and composable with `stream<T>`.

```text
let ch: channel<string> = channel()
spawn producer(ch)
for await msg in ch:
  handle(msg)
```

### Scope-bounded concurrency

All concurrent work should have a bounded scope. Tasks spawned within a block
are joined before the block exits. This prevents leaking concurrent work across
semantic boundaries and makes programs easier to reason about.

### Parallel pipelines

`|>` composes values sequentially. When fan-out is needed, `par` provides an
explicit parallel step that integrates naturally into pipeline style:

```text
let result = doc
  |> preprocess()
  |> par [ summarize, translate, embed ]
  |> store_all()
```

## AI-Native Semantics

AI operations are language forms.

They are not wrappers around external APIs. They appear as explicit semantic
constructs with visible capability requirements, typed inputs, and typed
results.

Core operations include:

- `prompt`
- `generate`
- `think`
- `stream`
- `embed`
- `classify`
- `extract`
- `plan`

### Prompting

```text
let answer = prompt @claude-sonnet:
  "Explain {topic} simply."
```

### Structured generation

```text
let invoice: Invoice = generate @gpt-4o:
  "Extract invoice fields from: {text}"
```

### Reasoning

```text
let analysis = think @claude-sonnet:
  "Step through the tradeoffs of: {proposal}"
```

### Streaming output

```text
let tokens: stream<string> = stream @claude-sonnet:
  "Write a poem about {subject}"
```

### Embeddings

```text
let vec: vector<float> = embed @text-embedding-3-small: query
```

### Tools and agents

Agents and tools are first-class language concepts.

```text
@tool(description: "Search a knowledge base")
fn search(query: string) -> list<string> uses net:
  ...

@agent(model: @claude-sonnet)
fn researcher(question: string) -> Report uses ai, net:
  let sources = search(question)
  let body = think @claude-sonnet:
    "Synthesize: {sources}"
  Report(content: body.conclusion)
```

### Multi-agent coordination

`@swarm` declares a coordinated group of agents that share tools, memory, and
communication channels. Agents within a swarm can delegate tasks to each other
and communicate through typed channels.

```text
@swarm(coordinator: @lead_agent)
let research_team = swarm {
  @agent(model: @claude-sonnet) fn lead_agent(goal: string) -> Report uses ai, net: ...
  @agent(model: @claude-sonnet) fn web_searcher(query: string) -> list<string> uses net: ...
  @agent(model: @claude-sonnet) fn summarizer(docs: list<string>) -> string uses ai: ...
}
```

Agents in a swarm can run in parallel and pass results through the coordinator
without manual orchestration code.

## Semantic Matching

Core 1.0 includes semantic comparison as a language capability.

The `~=` operator expresses approximate understanding rather than exact textual
equality.

```text
match user_input ~=:
  "yes": proceed()
  "cancel": abort()
  "help": show_help()
```

Semantic matching makes fuzzy classification and intent handling part of the
language itself.

## Effects and Capabilities

Programs should declare important external capabilities explicitly.

Initial capability families include:

- `ai`
- `ui`
- `net`
- `fs`
- `time`
- `process`

```text
fn render(user: User) -> none uses ui
fn load_users() -> list<User> uses net
```

Capability information should remain visible in the semantic representation so
that tooling, diagnostics, testing, and optimization can reason about it.

## Reactive State

Reactivity is a first-class part of the language model.

Core forms should support:

- reactive bindings
- derived values
- event handlers
- live views

```text
observe var count: int = 0

fn increment():
  count = count + 1

on count.change:
  render(view_counter(count))
```

The same reactive semantics should be able to power interfaces, event-driven
systems, and live agent workflows.

## Observability and Provenance

Programs that delegate to AI models, run concurrently, or span distributed
environments should be observable by design.

Core 1.0 provides observability primitives that attach to AI expressions:

- `trace expr` — captures the model, inputs, and outputs of an AI operation
- `cost expr` — returns the token or compute cost of an AI operation
- `explain expr` — requests a natural-language explanation of the result

```text
let analysis = trace think @claude-sonnet:
  "Evaluate the risks in: {proposal}"

let c = cost embed @text-embedding-3-small: query
```

Provenance values carry the full context of a decision: which model, which
inputs, which output, and when. They should be storable, queryable, and
renderable.

## Distribution and Placement

Programs should be able to declare where computation runs without writing
manual coordination code.

### Placement annotations

Functions and agents can be annotated with placement hints:

- `@local` — run on the user's device
- `@edge` — run in a nearby compute node
- `@cloud` — run in a remote cloud environment

```text
@local
fn preprocess(img: image) -> image: ...

@cloud
@agent(model: @claude-sonnet)
fn analyze(img: image) -> Report uses ai: ...
```

The runtime honors placement annotations and manages data transfer. Semantics
are preserved regardless of where execution happens.

### Long-running programs and memory

Agents and programs that span sessions need persistent state. `memory` is a
named, typed, queryable store accessible across invocations.

```text
let kb: memory<string> = memory("user-notes")
kb.store("preference", "prefers short answers")
let pref = kb.retrieve("preference")
```

Memory should support: named stores, typed values, time-scoped retrieval, and
embedding-based semantic search over stored content.

## Modules and Packages

Core 1.0 includes explicit module boundaries and package metadata.

Packages should be able to describe:

- dependencies
- targets
- capabilities
- exported interfaces
- versioning

This lets the language scale from small scripts to portable applications and
shared ecosystems.

## Semantic Representation Requirements

The shared semantic representation should model at least:

- bindings and mutability
- structured types
- union cases and patterns
- `option` and `result`
- functions and closures
- effects and capabilities
- AI-native constructs
- reactive constructs
- async and stream semantics
- concurrent constructs: `par`, `spawn`, `channel`, `future`
- multi-agent coordination: `@swarm`, delegation, message passing
- observability: `trace`, `cost`, `explain` annotations
- distribution: placement annotations, `memory` stores
- backend-neutral calls and data flow

This representation is the defining boundary of the language.

## Localization Contract

Every language construct in Core 1.0 should be part of a shared semantic
vocabulary so that it can be expressed across human-language surfaces without
changing meaning.

Localization belongs to the surface. Semantics belong to the core.

## Initial Priorities

The highest-value implementation priorities for Core 1.0 are:

1. typed semantic representation
2. `let` and `var`
3. `fn`, `|>`, and `?`
4. records and `enum`
5. `option` and `result`
6. stronger pattern matching
7. explicit capabilities
8. AI-native constructs
9. semantic matching
10. reactive bindings and event forms
11. async and stream consistency
12. `par` and `spawn` for structured concurrency
13. `channel<T>` and `future<T>` as principal values
14. multi-agent coordination via `@swarm`
15. observability primitives: `trace`, `cost`, `explain`
16. placement annotations and `memory` stores

