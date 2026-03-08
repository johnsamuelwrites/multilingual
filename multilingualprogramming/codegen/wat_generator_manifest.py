#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Manifest and frontend-template helpers for the WAT generator."""

from copy import deepcopy
import json

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.parser.ast_nodes import FunctionDef

from multilingualprogramming.codegen.wat_generator_support import (
    _STREAM_RENDER_MODES,
    _WAT_HOST_IMPORT_SIGNATURES,
    _extract_buffer_output,
    _extract_render_mode,
    _name,
    _real_params,
)


class WATGeneratorManifestMixin:
    """Frontend/ABI helpers for WATCodeGenerator."""

    def generate_abi_manifest(self, program) -> dict:
        """Generate ABI manifest metadata for frontend/runtime integration."""
        if isinstance(program, CoreIRProgram):
            program = program.ast

        funcs = [s for s in program.body if isinstance(s, FunctionDef)]
        top = [s for s in program.body if not isinstance(s, FunctionDef)]

        exports = []
        for func in funcs:
            params = _real_params(func)
            fname = _name(func.name)
            render_mode = _extract_render_mode(func)
            export_entry = {
                "name": fname,
                "arg_types": ["f64"] * len(params),
                "return_type": "f64",
                "mode": render_mode,
            }
            if render_mode in _STREAM_RENDER_MODES:
                output_kind = _extract_buffer_output(func)
                export_entry["stream_output"] = {
                    "kind": output_kind,
                    "count_export": f"{fname}_point_count",
                    "writer_export": f"{fname}_write_points",
                    "writer_signature": {
                        "arg_types": ["i32", "i32"],
                        "return_type": "i32",
                    },
                    "item_layout": {
                        "kind": "struct",
                        "stride_bytes": 16,
                        "fields": [
                            {"name": "x", "type": "f64", "offset_bytes": 0},
                            {"name": "y", "type": "f64", "offset_bytes": 8},
                        ],
                    },
                }
            exports.append(export_entry)

        if top:
            exports.append({
                "name": "__main",
                "arg_types": [],
                "return_type": "void",
                "mode": "scalar_field",
            })

        return {
            "abi_version": 1,
            "backend": "wat",
            "tuple_lowering": {
                "preferred": "out_params",
                "supported": ["multi_value", "out_params"],
                "out_params_memory_layout": {
                    "length_type": "i32",
                    "element_type": "f64",
                    "header_bytes": 4,
                    "element_size_bytes": 8,
                },
            },
            "exports": exports,
            "required_host_imports": deepcopy(_WAT_HOST_IMPORT_SIGNATURES),
            "memory_layout": {
                "primitive_types": {
                    "f64": {"size_bytes": 8, "alignment_bytes": 8},
                    "i32": {"size_bytes": 4, "alignment_bytes": 4},
                },
                "collections": {
                    "array<f64>": {
                        "element_type": "f64",
                        "element_size_bytes": 8,
                        "offset_formula": "base + index * 8",
                    }
                },
            },
        }

    def generate_js_host_shim(self, manifest: dict) -> str:
        """Generate a JavaScript host-import shim from an ABI manifest."""
        imports = manifest.get("required_host_imports", [])
        lines = [
            "// Auto-generated host shim from multilingual WASM ABI manifest",
            "export function createEnvHost(memoryRef = { current: null }) {",
            "  const textDecoder = new TextDecoder('utf-8');",
            "  function readUtf8(ptr, len) {",
            "    const memory = memoryRef.current;",
            "    if (!memory) return '';",
            "    const bytes = new Uint8Array(memory.buffer, ptr, len);",
            "    return textDecoder.decode(bytes);",
            "  }",
            "",
            "  return {",
            "    env: {",
        ]
        for entry in imports:
            name = entry["name"]
            if name == "print_str":
                lines.append("      print_str: (ptr, len) => { console.log(readUtf8(ptr, len)); },")
            elif name == "print_f64":
                lines.append("      print_f64: (value) => { console.log(value); },")
            elif name == "print_bool":
                lines.append("      print_bool: (value) => { console.log(Boolean(value)); },")
            elif name == "print_sep":
                lines.append("      print_sep: () => { /* spacing hook */ },")
            elif name == "print_newline":
                lines.append("      print_newline: () => { /* newline hook */ },")
            elif name == "pow_f64":
                lines.append("      pow_f64: (base, exp) => Math.pow(base, exp),")
            else:
                unhandled = (
                    f"      {name}: (...args) => "
                    f"{{ console.warn('Unhandled import {name}', args); }},"
                )
                lines.append(unhandled)
        lines.extend([
            "    },",
            "  };",
            "}",
        ])
        return "\n".join(lines)

    def generate_renderer_template(self, manifest: dict) -> str:
        """Generate a frontend renderer skeleton from ABI manifest metadata."""
        exports = manifest.get("exports", [])
        export_map_literal = json.dumps(
            {
                entry["name"]: {
                    "mode": entry.get("mode", "scalar_field"),
                    "stream_output": entry.get("stream_output"),
                }
                for entry in exports
            },
            indent=2,
        )
        lines = [
            "// Auto-generated renderer skeleton from multilingual WASM ABI manifest",
            "export const ABI_EXPORTS = " + export_map_literal + ";",
            "",
            "export async function loadWasmModule(url, importsFactory) {",
            "  const memoryRef = { current: null };",
            "  const imports = importsFactory(memoryRef);",
            "  const result = await WebAssembly.instantiateStreaming(fetch(url), imports);",
            "  const exports = result.instance.exports;",
            "  memoryRef.current = exports.memory || null;",
            "  return { instance: result.instance, exports, memoryRef };",
            "}",
            "",
            "export function renderByMode(ctx, abiName, exports, args = []) {",
            "  const abi = ABI_EXPORTS[abiName];",
            "  if (!abi) throw new Error(`Unknown ABI export: ${abiName}`);",
            "  if (abi.mode === 'scalar_field') {",
            "    return exports[abiName](...args);",
            "  }",
            "  if (abi.mode === 'point_stream' || abi.mode === 'polyline') {",
            "    const stream = abi.stream_output;",
            "    if (!stream) throw new Error(`Missing stream metadata for ${abiName}`);",
            "    const count = exports[stream.count_export]();",
            "    return { count, writer: stream.writer_export };",
            "  }",
            "  throw new Error(`Unsupported render mode: ${abi.mode}`);",
            "}",
        ]
        return "\n".join(lines)

    def _build_stream_buffer_helpers(self, func_name: str) -> str:
        """Emit stream helpers that write point pairs (x, y) into linear memory."""
        lines = [
            (
                f"  (func ${self._wat_symbol(func_name + '_point_count')} "
                f"(export \"{func_name}_point_count\")"
            ),
            "    (result i32)",
            "    i32.const 256",
            "  )",
            (
                f"  (func ${self._wat_symbol(func_name + '_write_points')} "
                f"(export \"{func_name}_write_points\")"
            ),
            "    (param $ptr i32)",
            "    (param $len i32)",
            "    (result i32)",
            "    (local $i i32)",
            "    (local $count i32)",
            "    local.get $len",
            "    i32.const 256",
            "    i32.lt_s",
            "    if (result i32)",
            "      local.get $len",
            "    else",
            "      i32.const 256",
            "    end",
            "    local.set $count",
            "    i32.const 0",
            "    local.set $i",
            "    block $done",
            "      loop $lp",
            "        local.get $i",
            "        local.get $count",
            "        i32.ge_s",
            "        br_if $done",
            "        local.get $ptr",
            "        local.get $i",
            "        i32.const 16",
            "        i32.mul",
            "        i32.add",
            "        local.get $i",
            "        f64.convert_i32_s",
            "        f64.store",
            "        local.get $ptr",
            "        local.get $i",
            "        i32.const 16",
            "        i32.mul",
            "        i32.add",
            "        i32.const 8",
            "        i32.add",
            "        local.get $i",
            "        f64.convert_i32_s",
            "        f64.const 0.5",
            "        f64.mul",
            "        f64.store",
            "        local.get $i",
            "        i32.const 1",
            "        i32.add",
            "        local.set $i",
            "        br $lp",
            "      end",
            "    end",
            "    local.get $count",
            "  )",
        ]
        return "\n".join(lines)
