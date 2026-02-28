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
```

## Manifest Shape

```json
{
  "abi_version": 1,
  "backend": "wat",
  "exports": [
    {
      "name": "compute",
      "arg_types": ["f64", "f64"],
      "return_type": "f64",
      "mode": "scalar_field"
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
