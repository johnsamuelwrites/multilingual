#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Build script: compile a multilingual source file to a self-contained WASM bundle.

Usage:
    python build.py [source.ml [language]]

Defaults: fibonacci_en.ml  language=en

Outputs (all in the same directory as this script):
    app.wat          — WebAssembly Text format
    app.wasm         — binary WASM module
    wasi_shim.js     — minimal WASI fd_write polyfill for browsers
    renderer.js      — ABI manifest + WebAssembly loader skeleton

The generated WASM exports:
    __main           — runs the top-level program
    __ml_reset       — resets heap to initial state (call before re-running)
    memory           — linear memory (required by the WASI shim)
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent

# Allow running without installing the package.
sys.path.insert(0, str(ROOT))

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator  # noqa: E402
from multilingualprogramming.lexer.lexer import Lexer  # noqa: E402
from multilingualprogramming.parser.parser import Parser  # noqa: E402


def _detect_language(path: pathlib.Path) -> str:
    """Infer language code from filename suffix like _en, _fr, etc."""
    stem = path.stem
    if "_" in stem:
        return stem.rsplit("_", 1)[-1]
    return "en"


def build(source_path: pathlib.Path, language: str) -> None:
    code = source_path.read_text(encoding="utf-8")
    tokens = Lexer(code, language=language).tokenize()
    prog = Parser(tokens, source_language=language).parse()

    gen = WATCodeGenerator()
    wat = gen.generate(prog)
    manifest = gen.generate_abi_manifest(prog)

    wat_path = HERE / "app.wat"
    wat_path.write_text(wat, encoding="utf-8")
    print(f"  WAT  -> {wat_path}")

    try:
        import wasmtime  # type: ignore
        wasm_bytes = wasmtime.wat2wasm(wat)
        wasm_path = HERE / "app.wasm"
        wasm_path.write_bytes(wasm_bytes)
        print(f"  WASM -> {wasm_path}  ({len(wasm_bytes):,} bytes)")
    except ImportError:
        print("  WASM -> skipped (wasmtime not installed; compile app.wat manually)")

    shim_path = HERE / "wasi_shim.js"
    shim_path.write_text(gen.generate_js_host_shim(manifest), encoding="utf-8")
    print(f"  shim -> {shim_path}")

    renderer_path = HERE / "renderer.js"
    renderer_path.write_text(gen.generate_renderer_template(manifest), encoding="utf-8")
    print(f"  rend -> {renderer_path}")


def main() -> None:
    args = sys.argv[1:]
    if args:
        source_path = pathlib.Path(args[0])
        language = args[1] if len(args) > 1 else _detect_language(source_path)
    else:
        source_path = HERE / "fibonacci_en.ml"
        language = "en"

    if not source_path.exists():
        sys.exit(f"Error: {source_path} not found")

    print(f"Building {source_path.name}  (language={language})")
    build(source_path, language)
    print("Done — open index.html with a local HTTP server to run the demo.")


if __name__ == "__main__":
    main()
