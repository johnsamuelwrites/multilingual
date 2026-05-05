# multilingual
Not yet another programming language. A multilingual one.

> **One semantic core. Many human languages.**
>  
> Build software through human-language-first syntax with native support for AI,
> multimodal workflows, reactive interfaces, and portable execution.

## Vision

`multilingual` is becoming a programming language for the age of human
language, AI, multimodal computing, and living interfaces.

Its purpose is bigger than keyword translation. The goal is to make it possible
to express the same precise program semantics across human languages while also
making modern software primitives feel native:

- structured data and pattern matching
- AI generation, extraction, planning, and tool use
- multimodal input and output
- reactive state and interfaces
- portable execution across environments

Read the language direction here:

- Vision: [docs/vision.md](docs/vision.md)
- Core 1.0: [docs/spec/core_1_0.md](docs/spec/core_1_0.md)
- 1.0 roadmap: [docs/roadmaps/multilingual_1_0.md](docs/roadmaps/multilingual_1_0.md)

## Strategic Direction

The project is moving toward a clearer identity:

- one semantic programming model expressed through many human languages
- first-class semantics for AI, retrieval, tools, and multimodal workflows
- structured concurrency, observability, memory, and agent coordination
- reactive and distributed programs that span browser, device, edge, and cloud
- portable execution where semantics stay stable while backends adapt

The repository already contains early pieces of that future, but the current
implementation is still a transitional platform between the historical
multilingual compiler pipeline and the fuller Core 1.0 language model.

## What Multilingual Is

- a human-language-first programming language
- a shared semantic model expressed through multiple language surfaces
- an AI-native language platform, not just a syntax experiment
- a research and implementation space for multilingual programming systems

## Why Multilingual

- **Human-language-first programming**: code should not force people to abandon
  their language or mode of expression.
- **Shared semantics**: different human-language surfaces should express the
  same underlying program.
- **AI-native direction**: models, tools, retrieval, and semantic workflows are
  becoming first-class language concepts.
- **Portable architecture**: one language should move across runtimes and
  environments without losing meaning.

### Pipeline Illustration

![Multilingual pipeline with surface normalization](docs/assets/multilingual_pipeline_surface.svg)

## Current Platform

Today the repository already provides:

- multilingual frontends driven by the USM keyword model
- a shared parser, AST, and semantic-IR direction
- semantic analysis plus Python and WAT/WASM code generation
- Python execution support
- WAT/WASM generation and backend selection
- browser demos and DOM-oriented workflows

This is an active language platform in motion, not just a whitepaper.

## Current Limitations

- the current semantic core is still thinner than the long-term Core 1.0 model
- some localized surfaces still feel less natural than they should
- parts of the implementation still reflect the historical compiler pipeline
  more than the future language experience
- AI-native, multimodal, reactive, concurrent, and distributed constructs are
  in mixed stages of design, prototyping, and rollout
- documentation still needs ongoing migration from "current compiler" wording
  toward "future language platform" wording

Details:

- Word order and naturalness: [docs/word_order_and_naturalness.md](docs/word_order_and_naturalness.md)
- Controlled language scope: [docs/cnl_scope.md](docs/cnl_scope.md)
- Current compatibility matrix: [docs/compatibility_matrix.md](docs/compatibility_matrix.md)

## Quick Start

Source files now prefer the `.multi` extension. The legacy `.ml` extension
remains fully supported for compatibility. Running the current implementation
requires Python 3.12 or newer.

### Try The Playground

You can try `multilingual` directly in your browser:

- Playground: https://johnsamuel.info/multilingual/playground.html

The playground lets you:

- write code in supported human languages
- run execution in Pyodide
- inspect generated Python
- inspect generated WAT/WASM output
- inspect generated Wasmtime bridge code

## Install

PyPI package: https://pypi.org/project/multilingualprogramming/

Option 1:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install multilingualprogramming
```

Option 2:

```bash
pipx install multilingualprogramming
```

For local development from source:

```bash
pip install -r requirements.txt
pip install .
```

## Hello World

```text
# English
print("Hello world")

# French
afficher("Bonjour le monde")

# Spanish
imprimir("Hola mundo")
```

## Use the REPL

```bash
multilingual
multilingual repl
multilingual repl --lang fr
multilingual repl --show-python
multilingual repl --show-wat
multilingual repl --show-rust
```

REPL commands:

- `:help` show commands
- `:language <code>` switch language
- `:python` toggle generated Python display
- `:wat` toggle generated WAT display
- `:rust` toggle generated Wasmtime bridge display
- `:reset` clear session state
- `:kw [XX]` show language keywords
- `:ops [XX]` show operators and symbols
- `:q` exit

## Run a Program

```bash
multilingual hello_en.multi
multilingual run hello_en.multi
multilingual run hello_fr.multi --lang fr
multilingual run hello_en.multi --show-backend
```

## Cross-Language Module Imports

You can import `.multi` and `.ml` modules across language surfaces in one program.

`module_fr.multi`:

```text
soit valeur = 41
def incremente(x):
    retour x + 1
```

`main_en.multi`:

```text
import module_fr
print(module_fr.incremente(module_fr.valeur))
```

Run:

```bash
multilingual run main_en.multi --lang en
```

## Roadmap

Near-term priorities:

- stabilize the Core 1.0 semantic model
- strengthen the semantic IR and capability-aware analysis pipeline
- ship more unmistakable language features such as `fn`, `var`, `enum`, `|>`,
  `par`, `spawn`, `memory`, and observability primitives
- continue building AI-native, multimodal, reactive, and distributed features
  on top of that core

See:

- [docs/roadmaps/multilingual_1_0.md](docs/roadmaps/multilingual_1_0.md)

## More Documentation

- Usage examples: [USAGE.md](USAGE.md)
- Language design overview: [docs/design.md](docs/design.md)
- Frontend contracts: [docs/frontend_contracts.md](docs/frontend_contracts.md)
- Core spec draft: [docs/spec/core_1_0.md](docs/spec/core_1_0.md)

## Architect and Creator
- John Samuel
