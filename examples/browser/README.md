# Browser Demo

Run a prebuilt multilingual WebAssembly bundle in the browser.
The generated module only imports `wasi_snapshot_preview1.fd_write` and
`fd_read` through the generated `host_shim.js` runtime.

## Quick start

```bash
# 1. Build the canonical browser bundle
python build.py
# or
python -m multilingualprogramming build-wasm-bundle fibonacci_en.multi --lang en --out-dir examples/browser

# 2. Serve the directory
python -m http.server 8080
# then open http://localhost:8080/examples/browser/
```

## What `build.py` produces

| File | Description |
|------|-------------|
| `module.wat` | WebAssembly Text format |
| `module.wasm` | Browser-ready WASM binary |
| `abi_manifest.json` | Export/import ABI metadata |
| `host_shim.js` | Generated WASI browser shim |
| `renderer_template.js` | Generated bundle loader helpers |
| `browser_runtime.js` | Thin demo wrapper around generated helpers |

## Deployment model

This example now matches the production browser flow:

1. Compile `.multi` source ahead of time.
2. Ship `module.wasm` plus the generated JS shim/template.
3. Load the bundle in the browser with minimal JavaScript.

The page does not compile source in-browser. Edit the template, rerun
`python build.py`, then reload the page.
