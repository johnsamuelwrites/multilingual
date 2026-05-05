#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
CLI entry point for the multilingual programming language.

Usage:
    python -m multilingualprogramming                     # Start REPL
    python -m multilingualprogramming <file>.multi       # Execute a source file
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
from multilingualprogramming.codegen.ui_lowering import lower_to_ui  # pylint: disable=unused-import
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir  # pylint: disable=unused-import
from multilingualprogramming.core.validators import validate_all  # pylint: disable=unused-import
from multilingualprogramming.keyword.language_pack_validator import (
    LanguagePackValidator,
)
from multilingualprogramming.exceptions import UnsupportedLanguageError
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.source_extensions import (
    find_package_init,
    has_source_extension,
)
from multilingualprogramming.version import __version__


def _emit_backend_report(result):
    """Write backend selection details to stderr."""
    report = result.backend_report()
    details = report.get("details", {})
    detail_pairs = [f"{key}={value}" for key, value in sorted(details.items())]
    detail_suffix = f" [{', '.join(detail_pairs)}]" if detail_pairs else ""
    print(
        f"[backend] {report['name']} ({report['reason']}){detail_suffix}",
        file=sys.stderr,
    )


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
    # Walk up from the file's directory while package initializer files exist;
    # that chain of directories forms the package name.  The directory
    # above the outermost package becomes the sys.path entry.
    resolved = Path(args.file).resolve()
    pkg_parts = []
    current = resolved.parent
    while find_package_init(current) is not None:
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

    mode = getattr(args, "mode", "legacy")
    if mode == "core":
        program_ast = _parse_program_from_file(args.file, args.lang)
        ir = lower_to_semantic_ir(program_ast, args.lang or "en")
        diags = validate_all(ir)
        if diags:
            for d in diags:
                print(f"[IR] {d}", file=sys.stderr)
            sys.exit(1)
        print(f"[core] IR validated: {len(ir.body)} top-level nodes", file=sys.stderr)

    result = executor.execute(source, globals_dict=run_globals or None)

    if result.output:
        sys.stdout.write(result.output)

    if getattr(args, "show_backend", False):
        _emit_backend_report(result)

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


def cmd_ir(args):
    """Lower a source file to semantic IR and print a summary."""
    program = _parse_program_from_file(args.file, args.lang)
    ir = lower_to_semantic_ir(program, args.lang or "en")

    if args.format == "json":
        _emit_ir_json(ir)
    else:
        _emit_ir_text(ir)


def _emit_ir_json(ir):
    """Emit a JSON representation of the semantic IR."""
    def _node_to_dict(node):
        if node is None:
            return None
        d = {"_type": type(node).__name__}
        for key, val in vars(node).items():
            if key.startswith("_"):
                continue
            if hasattr(val, "__dataclass_fields__"):
                d[key] = _node_to_dict(val)
            elif isinstance(val, list):
                d[key] = [
                    _node_to_dict(v) if hasattr(v, "__dataclass_fields__") else v
                    for v in val
                ]
            elif isinstance(val, tuple):
                d[key] = [
                    _node_to_dict(v) if hasattr(v, "__dataclass_fields__") else v
                    for v in val
                ]
            else:
                try:
                    json.dumps(val)
                    d[key] = val
                except (TypeError, ValueError):
                    d[key] = repr(val)
        return d

    print(json.dumps(_node_to_dict(ir), indent=2, ensure_ascii=False))


def _emit_ir_text(ir):
    """Emit a human-readable tree summary of the semantic IR."""
    print(f"IRProgram  language={ir.source_language!r}  nodes={len(ir.body)}")
    for i, node in enumerate(ir.body):
        _print_ir_node(node, prefix=f"  [{i}] ")


def _print_ir_node(node, prefix=""):
    if node is None:
        print(f"{prefix}(none)")
        return
    name_part = f"  name={node.name!r}" if hasattr(node, "name") and node.name else ""
    print(f"{prefix}{type(node).__name__}{name_part}")


def cmd_explain(args):
    """Explain the semantic structure of a source file in plain language."""
    program = _parse_program_from_file(args.file, args.lang)
    ir = lower_to_semantic_ir(program, args.lang or "en")
    _explain_ir(ir, args.file)


def _explain_ir(ir, filename):
    """Print a plain-English explanation of the semantic IR."""
    # pylint: disable=too-many-locals,too-many-branches
    # pylint: disable=too-many-statements,import-outside-toplevel
    from multilingualprogramming.core.ir_nodes import (
        IRBinding, IRFunction, IREnumDecl, IRTypeDecl,
        IRObserveBinding, IRAgentDecl, IRToolDecl,
    )

    print(f"File: {filename}")
    print(f"Language: {ir.source_language}")
    print(f"Top-level declarations: {len(ir.body)}")
    print()

    functions, bindings, enums, types_ = [], [], [], []
    observes, agents, tools, other = [], [], [], []
    for node in ir.body:
        if isinstance(node, IRFunction):
            functions.append(node)
        elif isinstance(node, IRBinding):
            bindings.append(node)
        elif isinstance(node, IREnumDecl):
            enums.append(node)
        elif isinstance(node, IRTypeDecl):
            types_.append(node)
        elif isinstance(node, IRObserveBinding):
            observes.append(node)
        elif isinstance(node, IRAgentDecl):
            agents.append(node)
        elif isinstance(node, IRToolDecl):
            tools.append(node)
        else:
            other.append(node)

    if functions:
        print("Functions:")
        for fn in functions:
            params = (
                ", ".join(p.name for p in fn.parameters)
                if fn.parameters else "(none)"
            )
            effects = fn.effects.names() if hasattr(fn, "effects") and fn.effects else []
            effect_str = f"  uses: {', '.join(sorted(effects))}" if effects else ""
            print(f"  fn {fn.name}({params}){effect_str}")
        print()

    if agents:
        print("Agents:")
        for a in agents:
            print(f"  @agent {a.name}  model={a.model}")
        print()

    if tools:
        print("Tools:")
        for t in tools:
            print(f"  @tool {t.name}  — {t.description}")
        print()

    if bindings:
        print("Bindings (let/var):")
        for b in bindings:
            mut = "var" if b.is_mutable else "let"
            print(f"  {mut} {b.name}")
        print()

    if observes:
        print("Reactive bindings (observe var):")
        for o in observes:
            print(f"  observe {o.name}")
        print()

    if enums:
        print("Enum declarations:")
        for e in enums:
            print(f"  enum {e.name}")
        print()

    if types_:
        print("Type declarations:")
        for t in types_:
            print(f"  type {t.name}")
        print()

    if other:
        print(f"Other nodes: {len(other)}")


def cmd_ui_preview(args):
    """Preview the reactive UI output (HTML + JS) for a source file."""
    program = _parse_program_from_file(args.file, args.lang)
    ir = lower_to_semantic_ir(program, args.lang or "en")
    result = lower_to_ui(ir)

    show_html = args.html or (not args.html and not args.js)
    show_js = args.js or (not args.html and not args.js)

    if show_html:
        html = result.emit_html()
        if html.strip():
            print("<!-- HTML -->")
            print(html)
        else:
            print("<!-- No HTML canvas blocks found -->")

    if show_js:
        js = result.emit_js()
        if js.strip():
            print("// JavaScript")
            print(js)

    if result.diagnostics:
        for diag in result.diagnostics:
            print(f"[WARN] {diag}", file=sys.stderr)


def _maybe_dispatch_direct_file_run(argv):
    """Dispatch `multilingual <file> [--lang XX]` to `cmd_run`."""
    if not argv:
        return False

    first = argv[0]
    if first.startswith("-"):
        return False
    if not has_source_extension(first):
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
    arg_parser.add_argument(
        "--show-backend", action="store_true",
        help="Report the selected execution backend to stderr",
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
            "pass <file>.multi or <file>.ml to run directly)"
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
    run_parser.add_argument(
        "--show-backend", action="store_true",
        help="Report the selected execution backend to stderr",
    )
    run_parser.add_argument(
        "--mode", default="legacy", choices=["legacy", "core"],
        help=(
            "Execution mode: 'legacy' (default) uses the Python/WAT backends; "
            "'core' validates the semantic IR first"
        ),
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

    # ir subcommand
    ir_parser = subparsers.add_parser(
        "ir", help="Show the semantic IR for a source file"
    )
    ir_parser.add_argument("file", help="Path to the source file")
    ir_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )
    ir_parser.add_argument(
        "--format", default="text", choices=["text", "json"],
        help="Output format: 'text' (default) or 'json'",
    )

    # explain subcommand
    explain_parser = subparsers.add_parser(
        "explain", help="Explain the semantic structure of a source file"
    )
    explain_parser.add_argument("file", help="Path to the source file")
    explain_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )

    # ui-preview subcommand
    ui_preview_parser = subparsers.add_parser(
        "ui-preview", help="Preview the reactive UI output (HTML + JS) for a source file"
    )
    ui_preview_parser.add_argument("file", help="Path to the source file")
    ui_preview_parser.add_argument(
        "--lang", default=None,
        help="Source language code (e.g., en, fr, hi). Auto-detect if omitted.",
    )
    ui_preview_parser.add_argument(
        "--html", action="store_true",
        help="Show only HTML output",
    )
    ui_preview_parser.add_argument(
        "--js", action="store_true",
        help="Show only JavaScript output",
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
    elif args.command == "ir":
        cmd_ir(args)
    elif args.command == "explain":
        cmd_explain(args)
    elif args.command == "ui-preview":
        cmd_ui_preview(args)
    else:
        # Default: start REPL
        args.lang = None
        args.show_python = False
        args.show_wat = False
        args.show_rust = False
        cmd_repl(args)


if __name__ == "__main__":
    main()
