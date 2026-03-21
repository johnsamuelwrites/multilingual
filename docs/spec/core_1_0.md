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
- one language model for code, data, AI, and interaction
- one portable representation that can move across execution environments

Detailed specifications for AI, multimodal, and reactive UI layers may grow
into companion documents, but Core 1.0 defines the semantic ground they stand
on.

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

