# Multilingual 1.0 Vision

Multilingual 1.0 is a programming language for the age of human language, AI,
multimodal computing, and living interfaces.

It is built on a simple belief: programming should not force people to leave
their language, or their mode of expression behind. Code should
be semantically precise, globally portable, and natively fluent in the kinds of
systems people now build: intelligent agents, reactive applications, knowledge
systems, and multimodal workflows.

## New Identity

Multilingual 1.0 is:

- a human-language-first programming language
- an AI-native language with explicit semantics for models, tools, and retrieval
- a multimodal language for text, images, audio, video, and documents
- a reactive language for interfaces, events, and live state
- a portable language with one semantic core and many execution targets

## Why This Matters

Software no longer lives in a text-only world. It now spans:

- human-language interaction
- multimodal input and output
- reactive interfaces
- intelligent systems that plan, generate, extract, and act
- execution across browsers, devices, local systems, and cloud environments

Most programming languages were not designed for this world. Multilingual 1.0
is.

## Design Principles

### 1. Meaning comes before surface

The language is defined by its semantics, not by any single syntax. Different
human-language surfaces should express the same underlying program model.

### 2. Human language is a principal medium for programming

Programming should be accessible through natural human languages without losing
precision, rigor, or composability.

### 3. AI is part of the language

Generation, extraction, classification, transcription, embeddings, retrieval,
planning, and tool use should be language capabilities, not accidental library
patterns.

### 4. Structured data is central

Modern software is built on records, events, schemas, optional values, errors,
streams, and typed transformations. These should be principal concepts.

### 5. Interfaces should be reactive

The language should be excellent for building live systems with state, events,
views, and updates that respond naturally to change.

### 6. Portability is part of the language contract

Programs should move across runtimes, devices, and environments without losing
their identity. Semantics stay stable; execution adapts.

### 7. Capabilities should be explicit

Operations involving I/O, networking, time, user interfaces, and AI systems
should be visible in program semantics so they can be analyzed, tested, and
trusted.

## Language Pillars

Multilingual 1.0 is built around five pillars.

### 1. Shared semantic core

All frontends compile into one typed semantic representation.

### 2. Modern data model

The core language should support:

- immutable bindings by default
- mutable bindings when explicitly requested
- records
- tagged unions
- `option<T>`
- `result<T, E>`
- pattern matching
- async functions and streams

### 3. AI-native workflows

The language should provide principal semantics for:

- `generate`
- `extract`
- `classify`
- `transcribe`
- `embed`
- `plan`
- tool invocation
- retrieval over indexed knowledge

### 4. Multimodal programming

The language should treat text, image, audio, video, and document inputs as
principal values.

### 5. Reactive interfaces

The language should support:

- signals and state
- declarative views
- event handlers
- async UI updates
- low-level interoperability when needed

## Strategic Direction

Multilingual 1.0 stands for:

- one semantic programming model
- expression through human languages
- principal AI and multimodal computing
- reactive user experiences
- portable execution across environments

## Unique Differentiator

Multilingual's defining claim is this:

> The same program can live across human languages, interfaces, and intelligent
> systems without losing semantic identity.

This makes Multilingual more than a localized syntax project. It is a universal
programming platform for human expression and machine execution. Building with
models, tools, retrieval, events, and media should feel native to the language
itself.

## Syntax Direction

Multilingual 1.0 should adopt a modern surface designed for clarity,
composition, and intelligent systems.

Key decisions:

- `fn` for function declarations
- `let` for immutable bindings and `var` for mutable ones
- `|>` as the primary composition operator
- `?` for result propagation
- `enum` for tagged unions
- `~=` for semantic matching
- `@agent` and `@tool` as principal constructs
- `prompt`, `think`, `stream`, `embed`, `generate`, and `extract` as language
  primitives
- reactive bindings and view-oriented syntax for live interfaces

These constructs should be localized through the shared semantic vocabulary so
that the language grows through meaning first and surface second.

## Additional Principles

### 8. AI primitives are syntax, not wrappers

AI operations should appear in the semantic model as distinct language forms
with explicit behavior, costs, and capability boundaries.

### 9. Pipelines are the primary composition style

Programs should read as transformations of values, streams, events, and model
outputs rather than as long chains of incidental mutation.

### 10. Semantic matching belongs in the language

Modern programs often need approximate understanding rather than exact textual
equality. Semantic comparison and classification should be expressible as
principal language operations.

## Non-Goals

Multilingual 1.0 should not try to:

- become a vague natural-language execution engine without structure
- hide AI behavior behind implicit magic
- tie the language to one model provider or one runtime
- confuse surface flexibility with semantic ambiguity
