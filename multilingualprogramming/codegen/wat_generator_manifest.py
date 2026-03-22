#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Manifest and frontend-template helpers for the WAT generator."""

from copy import deepcopy
import json

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.core.ir_nodes import IRProgram
from multilingualprogramming.core.runtime_lowering import lower_ir_to_runtime_ast
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
        elif isinstance(program, IRProgram):
            program = lower_ir_to_runtime_ast(program)

        funcs = [s for s in program.body if isinstance(s, FunctionDef)]
        top = [s for s in program.body if not isinstance(s, FunctionDef)]

        exports = []
        for func in funcs:
            params = _real_params(func)
            fname = _name(func.name)
            render_mode = _extract_render_mode(func)
            is_str_return = fname in getattr(self, "_string_return_funcs", set())
            export_entry = {
                "name": fname,
                "arg_types": ["f64"] * len(params),
                "return_type": "str" if is_str_return else "f64",
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

    def generate_js_host_shim(self, _manifest: dict) -> str:
        """Generate a JavaScript WASI shim for browser execution.

        The generated module imports ``wasi_snapshot_preview1.{fd_write, fd_read,
        args_sizes_get, args_get}``.  Browser stubs for fd_read (returns EOF) and
        args_get (returns empty argv) are included.  Use a full WASI polyfill
        (e.g. ``@bjorn3/browser_wasi_shim``) for full WASI compatibility.
        """
        lines = [
            "// Auto-generated WASI shim from multilingual WASM ABI manifest",
            "//",
            "// Requires: wasi_snapshot_preview1.{fd_write, fd_read}",
            "// For production use, prefer a full WASI polyfill such as:",
            "//   npm install @bjorn3/browser_wasi_shim",
            "//",
            "// Minimal inline shim (line-buffers stdout; fd_read returns EOF in browser):",
            "export function createWasiImports(",
            "  memoryRef = { current: null },",
            "  outputCallback = (line) => console.log(line),",
            "  inputProvider = null,",
            ") {",
            "  const textDecoder = new TextDecoder('utf-8');",
            "  const textEncoder = new TextEncoder();",
            "  let stdoutBuf = '';",
            "  function flushLine() {",
            "    let nl;",
            "    while ((nl = stdoutBuf.indexOf('\\n')) !== -1) {",
            "      outputCallback(stdoutBuf.slice(0, nl));",
            "      stdoutBuf = stdoutBuf.slice(nl + 1);",
            "    }",
            "  }",
            "  const wasi_snapshot_preview1 = {",
            "    fd_write(fd, iovsPtr, iovsLen, nwrittenPtr) {",
            "      if (fd !== 1 && fd !== 2) return 8;",
            "      const mem = memoryRef.current;",
            "      if (!mem) return 8;",
            "      const view = new DataView(mem.buffer);",
            "      let written = 0;",
            "      for (let i = 0; i < iovsLen; i++) {",
            "        const ptr = view.getUint32(iovsPtr + i * 8, true);",
            "        const len = view.getUint32(iovsPtr + i * 8 + 4, true);",
            "        stdoutBuf += textDecoder.decode(new Uint8Array(mem.buffer, ptr, len));",
            "        written += len;",
            "      }",
            "      flushLine();",
            "      view.setUint32(nwrittenPtr, written, true);",
            "      return 0;",
            "    },",
            "    fd_read(fd, iovsPtr, iovsLen, nreadPtr) {",
            "      // Browser: uses inputProvider() if set, falls back to window.prompt, else EOF.",
            "      if (fd !== 0) return 8;",
            "      const mem = memoryRef.current;",
            "      if (!mem) { new DataView(mem.buffer).setUint32(nreadPtr, 0, true); return 0; }",
            "      const provider = inputProvider",
            "        ?? (typeof window !== 'undefined' && typeof window.prompt === 'function'",
            "            ? () => window.prompt('Input:') ?? ''",
            "            : null);",
            "      if (!provider) {",
            "        new DataView(mem.buffer).setUint32(nreadPtr, 0, true);",
            "        return 0;",
            "      }",
            "      const line = (provider() ?? '') + '\\n';",
            "      const encoded = textEncoder.encode(line);",
            "      const view = new DataView(mem.buffer);",
            "      const ptr = view.getUint32(iovsPtr, true);",
            "      const len = view.getUint32(iovsPtr + 4, true);",
            "      const nread = Math.min(encoded.length, len);",
            "      new Uint8Array(mem.buffer, ptr, nread).set(encoded.subarray(0, nread));",
            "      view.setUint32(nreadPtr, nread, true);",
            "      return 0;",
            "    },",
            "    args_sizes_get(argcPtr, argvBufSizePtr) {",
            "      // Browser stub: reports 0 arguments.",
            "      if (!memoryRef.current) return 8;",
            "      const view = new DataView(memoryRef.current.buffer);",
            "      view.setUint32(argcPtr, 0, true);",
            "      view.setUint32(argvBufSizePtr, 0, true);",
            "      return 0;",
            "    },",
            "    args_get(_argvPtr, _argvBufPtr) { return 0; },",
            "  };",
            "  return { wasi_snapshot_preview1, memoryRef };",
            "}",
            "",
            "// Minimal DOM bridge for the WAT env.ml_dom_* host imports used by",
            "// the browser demo. Element references are stored in a JS-side handle",
            "// table; WAT receives opaque numeric handles as f64 values.",
            (
                "export function createDomImports("
                "memoryRef = { current: null }, exportsRef = { current: null }) {"
            ),
            "  const textDecoder = new TextDecoder('utf-8');",
            "  const textEncoder = new TextEncoder();",
            "  const handles = new Map();",
            "  let nextHandle = 1;",
            "",
            "  function readUtf8(ptr, len) {",
            "    const mem = memoryRef.current;",
            "    if (!mem || len <= 0) return '';",
            "    return textDecoder.decode(new Uint8Array(mem.buffer, ptr, len));",
            "  }",
            "",
            "  function writeUtf8(ptr, len, value) {",
            "    const mem = memoryRef.current;",
            "    if (!mem || len <= 0) return 0;",
            "    const bytes = textEncoder.encode(value ?? '');",
            "    const written = Math.min(bytes.length, len);",
            "    new Uint8Array(mem.buffer, ptr, written).set(bytes.subarray(0, written));",
            "    return written;",
            "  }",
            "",
            "  function registerElement(element) {",
            "    if (!element) return 0;",
            "    const handle = nextHandle++;",
            "    handles.set(handle, element);",
            "    return handle;",
            "  }",
            "",
            "  function getElement(handle) {",
            "    return handles.get(Math.trunc(handle)) || null;",
            "  }",
            "",
            "  const env = {",
            "    ml_dom_get(idPtr, idLen) {",
            "      return registerElement(document.getElementById(readUtf8(idPtr, idLen)));",
            "    },",
            "    ml_dom_set_text(handle, ptr, len) {",
            "      const element = getElement(handle);",
            "      if (element) element.textContent = readUtf8(ptr, len);",
            "    },",
            "    ml_dom_set_html(handle, ptr, len) {",
            "      const element = getElement(handle);",
            "      if (element) element.innerHTML = readUtf8(ptr, len);",
            "    },",
            "    ml_dom_get_value(handle, bufPtr, bufLen) {",
            "      const element = getElement(handle);",
            "      if (!element) return 0;",
            "      const value = 'value' in element",
            "        ? element.value",
            "        : (element.textContent ?? '');",
            "      return writeUtf8(bufPtr, bufLen, value);",
            "    },",
            "    ml_dom_set_attr(handle, namePtr, nameLen, valuePtr, valueLen) {",
            "      const element = getElement(handle);",
            "      if (element) {",
            "        element.setAttribute(",
            "          readUtf8(namePtr, nameLen),",
            "          readUtf8(valuePtr, valueLen),",
            "        );",
            "      }",
            "    },",
            "    ml_dom_create(tagPtr, tagLen) {",
            "      return registerElement(",
            "        document.createElement(readUtf8(tagPtr, tagLen))",
            "      );",
            "    },",
            "    ml_dom_append(parentHandle, childHandle) {",
            "      const parent = getElement(parentHandle);",
            "      const child = getElement(childHandle);",
            "      if (parent && child) parent.appendChild(child);",
            "    },",
            "    ml_dom_style(handle, propPtr, propLen, valuePtr, valueLen) {",
            "      const element = getElement(handle);",
            "      if (element) {",
            "        element.style[readUtf8(propPtr, propLen)] = readUtf8(valuePtr, valueLen);",
            "      }",
            "    },",
            "    ml_dom_remove(handle) {",
            "      const element = getElement(handle);",
            "      if (element) element.remove();",
            "    },",
            "    ml_dom_set_class(handle, ptr, len) {",
            "      const element = getElement(handle);",
            "      if (element) element.className = readUtf8(ptr, len);",
            "    },",
            "    ml_dom_on(handle, evtPtr, evtLen, funcIdx) {",
            "      const element = getElement(handle);",
            "      if (!element) return;",
            "      const eventName = readUtf8(evtPtr, evtLen);",
            "      element.addEventListener(eventName, () => {",
            "        if (exportsRef.current && exportsRef.current.__dom_dispatch) {",
            "          exportsRef.current.__dom_dispatch(funcIdx);",
            "        }",
            "      });",
            "    },",
            "  };",
            "",
            "  return { env, memoryRef };",
            "}",
            "",
            "// Read a UTF-8 string returned by a string-valued export.",
            "// Call immediately after the export; ptrF64 is its f64 return value.",
            "// Example:",
            "//   const ptrF64 = exports.greet(42);",
            "//   const str = readStringResult(exports, ptrF64);",
            "export function readStringResult(exports, ptrF64) {",
            "  const ptr = Math.trunc(ptrF64);",
            "  const len = exports.__ml_str_len ? exports.__ml_str_len() : 0;",
            "  if (!exports.memory || len === 0) return '';",
            "  return new TextDecoder('utf-8').decode(",
            "    new Uint8Array(exports.memory.buffer, ptr, len)",
            "  );",
            "}",
        ]
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
        # Build a per-function signature comment block for the caller's reference.
        sig_lines = []
        for entry in exports:
            name = entry["name"]
            arg_types = entry.get("arg_types", [])
            ret = entry.get("return_type", "void")
            args_str = ", ".join(f"arg{i}: {t}" for i, t in enumerate(arg_types))
            note = "  // use readStringResult(exports, result)" if ret == "str" else ""
            sig_lines.append(f"//   {name}({args_str}) -> {ret}{note}")
        sig_comment = "\n".join(sig_lines) if sig_lines else "//   (no exports)"

        lines = [
            "// Auto-generated renderer skeleton from multilingual WASM ABI manifest",
            "//",
            "// Exported functions (all numeric args/returns are f64):",
            sig_comment,
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
            "// Load the canonical bundle emitted by `build-wasm-bundle` from a directory URL.",
            "export async function loadWasmBundle(baseUrl, importsFactory) {",
            "  const bundleUrl = new URL('module.wasm', new URL(baseUrl, import.meta.url));",
            "  return loadWasmModule(bundleUrl, importsFactory);",
            "}",
            "",
            "// Call any exported numeric function by name.",
            "// args: array of numbers (f64).  Returns the f64 result, or undefined for void.",
            "// Example: callFunction(exports, 'fibonacci', [10]) // => 55",
            "export function callFunction(exports, name, args = []) {",
            "  const fn = exports[name];",
            "  if (!fn) throw new Error(`No export named '${name}'`);",
            "  return fn(...args);",
            "}",
            "",
            "export function renderByMode(ctx, abiName, exports, args = []) {",
            "  const abi = ABI_EXPORTS[abiName];",
            "  if (!abi) throw new Error(`Unknown ABI export: ${abiName}`);",
            "  if (abi.mode === 'scalar_field') {",
            "    return callFunction(exports, abiName, args);",
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
