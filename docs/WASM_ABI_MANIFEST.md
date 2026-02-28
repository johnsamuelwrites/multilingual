# WASM ABI Manifest

`WATCodeGenerator` now exposes `generate_abi_manifest(program)` to emit a
machine-readable ABI contract for generated WAT modules.

## Why

The manifest removes guesswork for frontends by declaring:

- exported function names
- argument and return types
- render mode metadata (`scalar_field`, `point_stream`, `polyline`)
- required host imports and signatures
- baseline linear-memory layout metadata for numeric arrays

## Python API

```python
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator

manifest = WATCodeGenerator().generate_abi_manifest(program_ast)
```

## CLI

```bash
multilingual wat-abi path/to/program.ml --lang en
multilingual wat-host-shim path/to/program.ml --lang en
multilingual wat-renderer-template path/to/program.ml --lang en
multilingual encoding-check-generated path/to/program.ml --lang en
multilingual build-wasm-bundle path/to/program.ml --lang en --out-dir build/wasm
```

## Manifest Shape

```json
{
  "abi_version": 1,
  "backend": "wat",
  "tuple_lowering": {
    "preferred": "out_params",
    "supported": ["multi_value", "out_params"],
    "out_params_memory_layout": {
      "length_type": "i32",
      "element_type": "f64",
      "header_bytes": 4,
      "element_size_bytes": 8
    }
  },
  "exports": [
    {
      "name": "compute",
      "arg_types": ["f64", "f64"],
      "return_type": "f64",
      "mode": "scalar_field"
    },
    {
      "name": "draw",
      "arg_types": ["f64"],
      "return_type": "f64",
      "mode": "point_stream",
      "stream_output": {
        "kind": "points",
        "count_export": "draw_point_count",
        "writer_export": "draw_write_points",
        "writer_signature": {"arg_types": ["i32", "i32"], "return_type": "i32"},
        "item_layout": {
          "kind": "struct",
          "stride_bytes": 16,
          "fields": [
            {"name": "x", "type": "f64", "offset_bytes": 0},
            {"name": "y", "type": "f64", "offset_bytes": 8}
          ]
        }
      }
    },
    {
      "name": "__main",
      "arg_types": [],
      "return_type": "void",
      "mode": "scalar_field"
    }
  ],
  "required_host_imports": [
    {"module": "env", "name": "print_str", "param_types": ["i32", "i32"], "return_type": "void"},
    {"module": "env", "name": "print_f64", "param_types": ["f64"], "return_type": "void"},
    {"module": "env", "name": "print_bool", "param_types": ["i32"], "return_type": "void"},
    {"module": "env", "name": "print_sep", "param_types": [], "return_type": "void"},
    {"module": "env", "name": "print_newline", "param_types": [], "return_type": "void"}
  ],
  "memory_layout": {
    "primitive_types": {
      "f64": {"size_bytes": 8, "alignment_bytes": 8},
      "i32": {"size_bytes": 4, "alignment_bytes": 4}
    },
    "collections": {
      "array<f64>": {
        "element_type": "f64",
        "element_size_bytes": 8,
        "offset_formula": "base + index * 8"
      }
    }
  }
}
```

## Render Mode Annotation

`generate_abi_manifest` reads function decorators:

```text
@render_mode("point_stream")
def draw(...):
    ...
```

If missing or invalid, mode defaults to `scalar_field`.

`point_stream` and `polyline` modes additionally expose stub buffer helpers:

- `<name>_point_count() -> i32`
- `<name>_write_points(ptr: i32, len: i32) -> i32`

These helper exports now write concrete `(x, y)` pairs (f64/f64, 16-byte stride)
into linear memory for up to 256 points and return the number of written points.

## Encoding Guard

Use `encoding-check-generated` to fail fast on replacement characters and common
mojibake markers in generated Python/WAT/ABI outputs.

## Deterministic Bundle Build

`build-wasm-bundle` is the authoritative build command for frontend integration.
It writes `module.wat`, `abi_manifest.json`, `host_shim.js`,
`renderer_template.js`, and `transpiled.py` with:

- lock-guarded build execution (`.multilingual-build.lock`)
- atomic writes (temp file + `os.replace`)
- deterministic JSON output (`sort_keys=True`)
- explicit build graph (`build_graph.json`) and lockfile (`build.lock.json`)

## Tuple Interop

The manifest includes canonical tuple lowering policy:

- `preferred: out_params`
- `supported: ["multi_value", "out_params"]`

Out-param tuple memory layout uses:

- `i32` element count header (4 bytes)
- followed by `f64` elements (8 bytes each)
