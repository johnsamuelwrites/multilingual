#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Build the canonical browser-ready WASM bundle for the demo directory.

Usage:
    python build.py [source.ml [language]]

Defaults: fibonacci_en.ml  language=en

Outputs (all in the same directory as this script):
    module.wat
    module.wasm
    abi_manifest.json
    host_shim.js
    renderer_template.js
    transpiled.py
    build_graph.json
    build.lock.json
"""

from __future__ import annotations

import importlib
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent


def _load_multilingual_symbols():
    """Load project modules whether the script runs from repo root or this folder."""
    try:
        build_orchestrator = importlib.import_module(
            "multilingualprogramming.codegen.build_orchestrator"
        )
        lexer_module = importlib.import_module("multilingualprogramming.lexer.lexer")
        parser_module = importlib.import_module("multilingualprogramming.parser.parser")
    except ModuleNotFoundError:
        sys.path.insert(0, str(ROOT))
        build_orchestrator = importlib.import_module(
            "multilingualprogramming.codegen.build_orchestrator"
        )
        lexer_module = importlib.import_module("multilingualprogramming.lexer.lexer")
        parser_module = importlib.import_module("multilingualprogramming.parser.parser")
    return (
        build_orchestrator.BuildOrchestrator,
        lexer_module.Lexer,
        parser_module.Parser,
    )


def _detect_language(path: pathlib.Path) -> str:
    stem = path.stem
    if "_" in stem:
        return stem.rsplit("_", 1)[-1]
    return "en"


def _parse_program(source_path: pathlib.Path, language: str):
    """Parse a multilingual source file into an AST program."""
    _, lexer_cls, parser_cls = _load_multilingual_symbols()
    code = source_path.read_text(encoding="utf-8")
    tokens = lexer_cls(code, language=language).tokenize()
    return parser_cls(tokens, source_language=language).parse()


def build(source_path: pathlib.Path, language: str) -> None:
    """Build browser demo artifacts for the given source file."""
    build_orchestrator_cls, _, _ = _load_multilingual_symbols()
    outputs = build_orchestrator_cls(HERE).build_from_program(
        _parse_program(source_path, language)
    )
    print(f"  WAT  -> {outputs.wat}")
    if outputs.wasm.exists():
        print(f"  WASM -> {outputs.wasm}  ({outputs.wasm.stat().st_size:,} bytes)")
    else:
        print("  WASM -> skipped (install wasmtime to emit module.wasm)")
    print(f"  ABI  -> {outputs.abi_manifest}")
    print(f"  shim -> {outputs.host_shim_js}")
    print(f"  rend -> {outputs.renderer_template_js}")


def main() -> None:
    """Build the default or requested browser demo bundle."""
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
    print("Done - serve examples/browser/ over HTTP and open index.html.")


if __name__ == "__main__":
    main()
