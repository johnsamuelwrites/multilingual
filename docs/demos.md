# Demos

Multilingual 1.0 showcases a new kind of AI-native, reactive, multilingual
programming platform.

## Core 1.0 flagship demos

### Multilingual AI agent (3 languages)

The most compelling demo: the same agent logic written in English, French, and
Japanese, running identically.  Proves that Multilingual is the only AI
programming platform where agent code is idiomatic in any human language.

- `examples/agent_en.ml` — English
- `examples/agent_fr.ml` — French
- `examples/agent_ja.ml` — Japanese

### Reactive counter

`observe var` + `on .change` + `canvas` — the simplest reactive web app.

- `examples/reactive_counter.ml`

### Streaming chat (French)

A streaming AI response bound to a reactive view, written in French.

- `examples/streaming_chat_fr.ml`

### Semantic search (Japanese)

`embed` + `nearest` + `~=` semantic match across Japanese user input.

- `examples/semantic_search_ja.ml`

### Multilingual AI dashboard

`@agent`, reactive state, streaming output, and canvas composition.

- `examples/multilingual_dashboard.ml`

## CLI tools for Core 1.0

### Inspect the semantic IR

```
multilingual ir my_program.ml
multilingual ir my_program.ml --format json
```

### Explain a program's structure

```
multilingual explain my_program.ml
```

Output: a plain-English summary of all declared functions, agents, tools,
reactive bindings, effects, and type declarations.

### Preview reactive UI output

```
multilingual ui-preview my_program.ml
multilingual ui-preview my_program.ml --html
multilingual ui-preview my_program.ml --js
```

### Validate with Core IR before running

```
multilingual run my_program.ml --mode core
```

Validates the semantic IR (checks capabilities, binding names, match
statement completeness) before executing.

## Browser deployment models

### 1. Pyodide playground

Use for live editing, full interpreter behavior, IR inspection, and teaching.

**[Open the Pyodide Playground](playground.html)**

### 2. Precompiled Multilingual to WASM

Use for ahead-of-time compilation to `module.wasm` and minimal JavaScript host.

**[Open the Browser WASM Demo Hub](../browser/)**

## What each demo proves

| Demo | Shows |
|------|-------|
| Multilingual agent (3 languages) | Agent logic is idiomatic in any human language |
| Reactive counter | `observe var` + `on .change` + `canvas` reactive model |
| Streaming chat (French) | AI stream bound to reactive view in French |
| Semantic search (Japanese) | `~=` and `embed` across multilingual input |
| Pyodide playground | Live browser compilation and IR inspection |
| Browser WASM demo | Production-ready prebuilt artifact deployment |
