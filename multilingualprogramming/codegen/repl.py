#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Interactive REPL (Read-Eval-Print Loop) for the multilingual programming
language.

Supports line-by-line and multi-line (block) input, persistent state
across interactions, and optional display of generated Python source.
"""

import sys

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import SemanticAnalyzer
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.version import __version__


class REPL:
    """
    Interactive multilingual programming REPL.

    Usage:
        repl = REPL(language="fr")
        repl.run()   # starts interactive loop

    Or programmatically:
        repl = REPL(language="en")
        output = repl.eval_line("let x = 42")
        output = repl.eval_line("print(x)")  # "42\\n"
    """

    def __init__(self, language=None, show_python=False):
        """
        Initialize the REPL.

        Args:
            language: Source language code (e.g., "en", "fr").
                     If None, auto-detect from input.
            show_python: If True, display generated Python before execution.
        """
        self.language = language
        self.show_python = show_python
        self._globals = {}
        self._init_globals()

    def _init_globals(self):
        """Initialize the execution namespace with builtins."""
        lang = self.language or "en"
        builtins_ns = RuntimeBuiltins(lang).namespace()
        self._globals.update(builtins_ns)

    def eval_line(self, source):
        """
        Evaluate a single line or block of multilingual source code.

        Args:
            source: Source code string.

        Returns:
            Captured stdout output as a string, or error message.
        """
        import io
        if not source.strip():
            return ""

        try:
            # Tokenize
            lexer = Lexer(source, language=self.language)
            tokens = lexer.tokenize()
            detected_lang = lexer.language or self.language or "en"

            # Parse
            parser = Parser(tokens, source_language=detected_lang)
            program = parser.parse()

            # Generate Python
            generator = PythonCodeGenerator()
            python_source = generator.generate(program)

            if self.show_python:
                return f"[Python] {python_source.strip()}\n" + self._exec(
                    python_source
                )

            return self._exec(python_source)

        except Exception as exc:
            return f"Error: {exc}\n"

    def _exec(self, python_source):
        """Execute generated Python and return captured output."""
        import io
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            code = compile(python_source, "<repl>", "exec")
            exec(code, self._globals)  # pylint: disable=exec-used
        except Exception as exc:
            captured.write(f"Error: {exc}\n")
        finally:
            sys.stdout = old_stdout
        return captured.getvalue()

    def run(self):
        """
        Start the interactive REPL loop.

        Reads from stdin, supports multi-line blocks (lines ending with ':'),
        and exits on Ctrl+D (EOF) or Ctrl+C.
        """
        lang_label = self.language or "auto"
        print(f"Multilingual Programming REPL v{__version__} "
              f"[language={lang_label}]")
        print("Type 'exit' or Ctrl+D to quit. "
              "End block headers with ':' then indent.\n")

        while True:
            try:
                line = input(">>> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if line.strip() in ("exit", "quit"):
                print("Bye!")
                break

            # Check for multi-line block (line ends with ':')
            if line.rstrip().endswith(":"):
                block_lines = [line]
                while True:
                    try:
                        cont = input("... ")
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    if cont.strip() == "":
                        break
                    block_lines.append(cont)
                source = "\n".join(block_lines) + "\n"
            else:
                source = line + "\n"

            output = self.eval_line(source)
            if output:
                sys.stdout.write(output)

    def reset(self):
        """Clear the REPL state (variables, functions, etc.)."""
        self._globals.clear()
        self._init_globals()
