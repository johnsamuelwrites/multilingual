# Runtime Demos

The GitHub Pages site now showcases two different browser stories for `multilingual`.

## Two deployment models

### 1. Pyodide playground

Use the Pyodide-based playground when you want:

- live editing in the browser
- full interpreter behavior
- generated Python and WAT inspection
- an exploratory, teaching-friendly environment

**[Open the Pyodide Playground](playground.html){ .playground-link }**

### 2. Precompiled multilingual to WASM

Use the precompiled browser demo when you want:

- ahead-of-time compilation to `module.wasm`
- a minimal JavaScript host layer
- a deployment model closer to a production web app
- explicit WASI and DOM host-import bridging

**[Open the Browser WASM Demo Hub](browser/){ .playground-link }**

## What each demo proves

| Demo | Shows |
|---|---|
| Pyodide playground | `multilingual` can compile and execute interactively inside the browser |
| Browser WASM demo | `multilingual` programs can ship as prebuilt WebAssembly bundles and run with a small browser host runtime |

## Suggested narrative

If you are presenting the project, a good flow is:

1. Start with the playground to show multilingual authoring and instant feedback.
2. Switch to the browser WASM demo to show that the same project also supports ahead-of-time deployment with prebuilt artifacts.

