# Browser Demo

Run multilingual source code compiled to WebAssembly in the browser.
The WASM module only imports `wasi_snapshot_preview1.fd_write` — no custom
JavaScript host functions are required.

## Quick start (pre-built WASM)

```bash
# 1. Compile the demo source to WASM
python build.py                      # uses fibonacci_en.ml by default
python build.py path/to/program.ml   # any .ml file

# 2. Serve the directory (browsers block fetch() on file://)
python -m http.server 8080
# then open http://localhost:8080/examples/browser/
```

## What build.py produces

| File | Description |
|------|-------------|
| `app.wat` | WebAssembly Text format (human-readable) |
| `app.wasm` | Binary WASM module |
| `wasi_shim.js` | Minimal `wasi_snapshot_preview1.fd_write` polyfill |
| `renderer.js` | ABI manifest + `WebAssembly.instantiateStreaming` skeleton |

## Custom source

```bash
python build.py examples/arithmetics_fr.ml fr
python build.py examples/complete_features_de.ml de
```

## Memory management

Every generated module exports:

- **`__main`** — executes the top-level program
- **`__ml_reset`** — resets the heap and all free lists to their initial state

The browser demo calls `__ml_reset()` before each run so memory is fully
reclaimed between "Run" button presses.

The allocator (`$ml_alloc` / `$ml_free`) uses three segregated free lists for
blocks of ≤ 32 bytes, ≤ 64 bytes, and ≤ 256 bytes, with a bump-pointer
fallback for larger allocations.

## Architecture

```
fibonacci_en.ml
    │
    ▼  python build.py
WATCodeGenerator
    │
    ├─ app.wat  (WASM Text)
    │      │
    │      ▼  wasmtime.wat2wasm
    │   app.wasm
    │      │
    │      ▼  browser WebAssembly.instantiate
    │   instance.exports.__main()
    │      │
    │      ▼  WASI fd_write → makeWasiImports shim → <pre> element
    │   output displayed in page
    │
    ├─ wasi_shim.js   (generated)
    └─ renderer.js    (generated)
```
