#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
CLI entry point for the multilingual programming language.

Usage:
    python -m multilingualprogramming                     # Start REPL
    python -m multilingualprogramming run <file>           # Execute a file
    python -m multilingualprogramming repl [--lang XX]     # Start REPL
    python -m multilingualprogramming compile <file>       # Show generated Python
    python -m multilingualprogramming smoke --lang fr      # Validate one language pack
    python -m multilingualprogramming smoke --all          # Validate all language packs
"""

import argparse
import sys

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.repl import REPL
from multilingualprogramming.keyword.language_pack_validator import (
    LanguagePackValidator,
)
from multilingualprogramming.exceptions import UnsupportedLanguageError
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.version import __version__


def cmd_run(args):
    """Execute a multilingual source file."""

    try:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    executor = ProgramExecutor(language=args.lang)
    result = executor.execute(source)

    if result.output:
        sys.stdout.write(result.output)

    if not result.success:
        for err in result.errors:
            print(err, file=sys.stderr)
        sys.exit(1)


def cmd_repl(args):
    """Start the interactive REPL."""
    repl = REPL(language=args.lang, show_python=args.show_python)
    repl.run()


def cmd_compile(args):
    """Compile a source file and print the generated Python."""

    try:
        with open(args.file, encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    lang = args.lang
    lexer = Lexer(source, language=lang)
    tokens = lexer.tokenize()
    detected_lang = lexer.language or lang or "en"

    parser = Parser(tokens, source_language=detected_lang)
    program = parser.parse()

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


def main():
    """Run the CLI entry point and dispatch subcommands."""
    parser = argparse.ArgumentParser(
        prog="multilingual",
        description="Multilingual Programming Language CLI",
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

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "repl":
        cmd_repl(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "smoke":
        cmd_smoke(args)
    else:
        # Default: start REPL
        args.lang = None
        args.show_python = False
        cmd_repl(args)


if __name__ == "__main__":
    main()
