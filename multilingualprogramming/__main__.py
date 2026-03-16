#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
CLI entry point for the multilingual programming language.

Usage:
    python -m multilingualprogramming                     # Start REPL
    python -m multilingualprogramming <file>.ml          # Execute a source file
    python -m multilingualprogramming run <file>           # Execute a file
    python -m multilingualprogramming repl [--lang XX]     # Start REPL
    python -m multilingualprogramming compile <file>       # Show generated Python
    python -m multilingualprogramming build-wasm-bundle <file>  # Build WAT/ABI bundle
    python -m multilingualprogramming smoke --lang fr      # Validate one language pack
    python -m multilingualprogramming smoke --all          # Validate all language packs
"""
# pylint: disable=mixed-line-endings

import argparse
import json
import sys
from pathlib import Path

from multilingualprogramming.codegen.encoding_guard import (
    assert_clean_utf8_file,
    assert_clean_text_encoding,
)
from multilingualprogramming.codegen.build_orchestrator import BuildOrchestrator
from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.repl import REPL
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.keyword.language_pack_validator import (
    LanguagePackValidator,
)
from multilingualprogramming.exceptions import UnsupportedLanguageError
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.version import __version__


def _read_source_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _parse_program_from_file(path: str, lang: str | None):
    source = _read_source_file(path)
    lexer = Lexer(source, language=lang)
    tokens = lexer.tokenize()
    detected_lang = lexer.language or lang or "en"
    parser = Parser(tokens, source_language=detected_lang)
    return parser.parse()


def cmd_run(args):
    """Execute a multilingual source file."""
    source = _read_source_file(args.file)

    # Determine package context so that relative imports work.
    # Walk up from the file's directory while __init__.ml files exist;
    # that chain of directories forms the package name.  The directory
    # above the outermost package becomes the sys.path entry.
    resolved = Path(args.file).resolve()
    pkg_parts = []
    current = resolved.parent
    while (current / "__init__.ml").is_file():
        pkg_parts.append(current.name)
        current = current.parent
    pkg_parts.reverse()
    package_name = ".".join(pkg_parts) if pkg_parts else None

    # The path entry is either the package root (when inside a package)
    # or the script's own directory (top-level script).
    path_entry = str(current if pkg_parts else resolved.parent)
    if path_entry not in sys.path:
        sys.path.insert(0, path_entry)

    # Pass __package__ so the import system can resolve relative imports.
    run_globals = {"__package__": package_name} if package_name else {}

    executor = ProgramExecutor(language=args.lang)
    result = executor.execute(source, globals_dict=run_globals or None)

    if result.output:
        sys.stdout.write(result.output)

    if not result.success:
        for err in result.errors:
            print(err, file=sys.stderr)
        sys.exit(1)


def cmd_repl(args):
    """Start the interactive REPL."""
    repl = REPL(
        language=args.lang,
        show_python=args.show_python,
        show_wat=args.show_wat,
        show_rust=args.show_rust,
    )
    repl.run()


def cmd_compile(args):
    """Compile a source file and print the generated Python."""
    program = _parse_program_from_file(args.file, args.lang)

    generator = PythonCodeGenerator()
    python_source = generator.generate(program)
    print(python_source)


def cmd_smoke(args):
    """Run language-pack smoke validation checks."""
    registry_validator = LanguagePackValidator()
    languages = (
        sorted(registry_validator.get_supported_languages())
        if args.all
        else [args.lang]
    )

    failed = False
    for language in languages:
        try:
            errors = registry_validator.validate(language)
        except UnsupportedLanguageError as exc:
            failed = True
            print(f"[FAIL] {language}: {exc}", file=sys.stderr)
            continue

        if errors:
            failed = True
            print(f"[FAIL] {language}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"[PASS] {language}")

    if failed:
        sys.exit(1)


def cmd_wat_abi(args):
    """Parse source and emit the generated WAT ABI manifest JSON."""
    program = _parse_program_from_file(args.file, args.lang)
    manifest = WATCodeGenerator().generate_abi_manifest(program)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def cmd_wat_host_shim(args):
    """Emit JS host-import shim from generated WAT ABI manifest."""
    program = _parse_program_from_file(args.file, args.lang)
    generator = WATCodeGenerator()
    manifest = generator.generate_abi_manifest(program)
    print(generator.generate_js_host_shim(manifest))


def cmd_wat_renderer_template(args):
    """Emit JS renderer skeleton from generated WAT ABI manifest."""
    program = _parse_program_from_file(args.file, args.lang)
    generator = WATCodeGenerator()
    manifest = generator.generate_abi_manifest(program)
    print(generator.generate_renderer_template(manifest))


def cmd_encoding_check(args):
    """Validate UTF-8/no-mojibake policy for provided files."""
    failed = False
    for fpath in args.files:
        try:
            assert_clean_utf8_file(fpath)
            print(f"[PASS] {fpath}")
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            failed = True
            print(f"[FAIL] {fpath}: {exc}", file=sys.stderr)
    if failed:
        sys.exit(1)


def cmd_encoding_check_generated(args):
    """Validate generated compiler outputs for encoding regressions."""
    program = _parse_program_from_file(args.file, args.lang)
    wat_generator = WATCodeGenerator()
    py_source = PythonCodeGenerator().generate(program)
    wat_source = wat_generator.generate(program)
    abi_json = json.dumps(
        wat_generator.generate_abi_manifest(program), ensure_ascii=False, indent=2
    )

    assert_clean_text_encoding("generated_python", py_source)
    assert_clean_text_encoding("generated_wat", wat_source)
    assert_clean_text_encoding("generated_abi_json", abi_json)
    print("[PASS] generated_python")
    print("[PASS] generated_wat")
    print("[PASS] generated_abi_json")


def cmd_build_wasm_bundle(args):
    """Build deterministic browser-ready WAT/WASM artifact bundle."""
    program = _parse_program_from_file(args.file, args.lang)
    wasm_target = getattr(args, "wasm_target", "browser")
    orchestrator = BuildOrchestrator(args.out_dir)
    outputs = orchestrator.build_from_program(program, wasm_target=wasm_target)
    print(f"[PASS] {outputs.transpiled_python}")
    print(f"[PASS] {outputs.wat}")
    if outputs.wasm.exists():
        print(f"[PASS] {outputs.wasm}")
    else:
        print(f"[WARN] {outputs.wasm} (wasmtime not installed; WAT only)")
    print(f"[PASS] {outputs.abi_manifest}")
    print(f"[PASS] {outputs.host_shim_js}")
    print(f"[PASS] {outputs.renderer_template_js}")
    print(f"[PASS] {outputs.build_graph}")
    print(f"[PASS] {outputs.build_lockfile}")


def _maybe_dispatch_direct_file_run(argv):
    """Dispatch `multilingual <file>.ml [--lang XX]` to `cmd_run`."""
    if not argv:
        return False

    first = argv[0]
    if first.startswith("-"):
        return False
    if not first.lower().endswith(".ml"):
        return False

    arg_parser = argparse.ArgumentParser(
        prog="multilingual",
        description="Execute a multilingual source file",
    )
    arg_parser.add_argument("file", help="Path to the source file")
    arg_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )
    args = arg_parser.parse_args(argv)
    cmd_run(args)
    return True


def main():  # pylint: disable=too-many-statements
    """Run the CLI entry point and dispatch subcommands."""
    argv = sys.argv[1:]
    if _maybe_dispatch_direct_file_run(argv):
        return

    parser = argparse.ArgumentParser(
        prog="multilingual",
        description=(
            "Multilingual Programming Language CLI "
            "(default command starts interactive REPL; "
            "pass <file>.ml to run directly)"
        ),
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # run subcommand
    run_parser = subparsers.add_parser("run", help="Execute a source file")
    run_parser.add_argument("file", help="Path to the source file")
    run_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    # repl subcommand
    repl_parser = subparsers.add_parser("repl", help="Start interactive REPL")
    repl_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )
    repl_parser.add_argument(
        "--show-python", action="store_true",
        help="Display generated Python code before execution",
    )
    repl_parser.add_argument(
        "--show-wat", action="store_true",
        help="Display generated WAT (WebAssembly Text) code before execution",
    )
    repl_parser.add_argument(
        "--show-rust", action="store_true",
        help="Display generated Rust/Wasmtime bridge code before execution",
    )

    # compile subcommand
    compile_parser = subparsers.add_parser(
        "compile", help="Show generated Python code"
    )
    compile_parser.add_argument("file", help="Path to the source file")
    compile_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    # smoke subcommand
    smoke_parser = subparsers.add_parser(
        "smoke", help="Validate language pack(s)"
    )
    smoke_parser.add_argument(
        "--lang", default="en",
        help="Language code to validate (default: en)",
    )
    smoke_parser.add_argument(
        "--all", action="store_true",
        help="Validate all supported languages",
    )

    wat_abi_parser = subparsers.add_parser(
        "wat-abi", help="Emit WAT ABI manifest JSON for a source file"
    )
    wat_abi_parser.add_argument("file", help="Path to the source file")
    wat_abi_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    wat_host_parser = subparsers.add_parser(
        "wat-host-shim",
        help="Emit JS host shim from WAT ABI manifest for a source file",
    )
    wat_host_parser.add_argument("file", help="Path to the source file")
    wat_host_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    wat_renderer_parser = subparsers.add_parser(
        "wat-renderer-template",
        help="Emit JS renderer skeleton from WAT ABI manifest for a source file",
    )
    wat_renderer_parser.add_argument("file", help="Path to the source file")
    wat_renderer_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    encoding_check_parser = subparsers.add_parser(
        "encoding-check",
        help="Validate UTF-8 and no-mojibake markers for files",
    )
    encoding_check_parser.add_argument("files", nargs="+", help="Files to validate")

    encoding_generated_parser = subparsers.add_parser(
        "encoding-check-generated",
        help="Validate generated Python/WAT/ABI outputs for a source file",
    )
    encoding_generated_parser.add_argument("file", help="Path to the source file")
    encoding_generated_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    build_bundle_parser = subparsers.add_parser(
        "build-wasm-bundle",
        help="Build deterministic browser-ready WAT/WASM artifacts",
    )
    build_bundle_parser.add_argument("file", help="Path to the source file")
    build_bundle_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )
    build_bundle_parser.add_argument(
        "--out-dir", default="build/wasm",
        help="Output directory for generated artifacts (default: build/wasm)",
    )
    build_bundle_parser.add_argument(
        "--wasm-target", default="browser", choices=["browser", "wasi"],
        help=(
            "Compilation target: 'browser' (default) includes DOM host imports; "
            "'wasi' omits them for native wasmtime/WASI execution."
        ),
    )

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "repl":
        cmd_repl(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "smoke":
        cmd_smoke(args)
    elif args.command == "wat-abi":
        cmd_wat_abi(args)
    elif args.command == "wat-host-shim":
        cmd_wat_host_shim(args)
    elif args.command == "wat-renderer-template":
        cmd_wat_renderer_template(args)
    elif args.command == "encoding-check":
        cmd_encoding_check(args)
    elif args.command == "encoding-check-generated":
        cmd_encoding_check_generated(args)
    elif args.command == "build-wasm-bundle":
        cmd_build_wasm_bundle(args)
    else:
        # Default: start REPL
        args.lang = None
        args.show_python = False
        args.show_wat = False
        args.show_rust = False
        cmd_repl(args)


if __name__ == "__main__":
    main()
