#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Interactive REPL (Read-Eval-Print Loop) for the multilingual programming
language.

Supports line-by-line and multi-line (block) input, persistent state
across interactions, expression auto-printing, bracket-aware continuation,
and REPL commands.
"""

import io
import sys

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
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
        """Execute generated Python and return captured output.

        For single expressions, auto-prints the result (like Python REPL).
        """
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            # Try eval first (single expression) for auto-printing
            try:
                code = compile(python_source, "<repl>", "eval")
                result = eval(code, self._globals)  # pylint: disable=eval-used
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                # Not a single expression — exec as statements
                code = compile(python_source, "<repl>", "exec")
                exec(code, self._globals)  # pylint: disable=exec-used
        except Exception as exc:
            captured.write(f"Error: {exc}\n")
        finally:
            sys.stdout = old_stdout
        return captured.getvalue()

    def _count_open_brackets(self, text):
        """Count net open brackets in text."""
        count = 0
        in_string = False
        string_char = None
        i = 0
        while i < len(text):
            ch = text[i]
            if in_string:
                if ch == '\\':
                    i += 1  # skip escaped char
                elif ch == string_char:
                    in_string = False
            else:
                if ch in ('"', "'"):
                    in_string = True
                    string_char = ch
                elif ch in ('(', '[', '{'):
                    count += 1
                elif ch in (')', ']', '}'):
                    count -= 1
                elif ch == '#':
                    break  # rest is comment
            i += 1
        return count

    def _handle_command(self, line):
        """Handle REPL commands starting with ':'. Returns True if handled."""
        parts = line.strip().split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in (":quit", ":exit", ":q"):
            print("Bye!")
            return "exit"
        if cmd == ":lang":
            if arg:
                self.language = arg.strip()
                self._globals.clear()
                self._init_globals()
                print(f"Language switched to: {self.language}")
            else:
                print(f"Current language: {self.language or 'auto'}")
            return True
        if cmd == ":python":
            self.show_python = not self.show_python
            state = "on" if self.show_python else "off"
            print(f"Show Python: {state}")
            return True
        if cmd == ":reset":
            self._globals.clear()
            self._init_globals()
            print("State cleared.")
            return True
        if cmd == ":help":
            print("REPL Commands:")
            print("  :lang [XX]    Switch language (e.g., :lang fr)")
            print("  :python       Toggle showing generated Python")
            print("  :reset        Clear all variables and state")
            print("  :help         Show this help")
            print("  :quit         Exit the REPL")
            return True
        return False

    def run(self):
        """
        Start the interactive REPL loop.

        Reads from stdin, supports multi-line blocks (lines ending with ':'),
        bracket continuation, and REPL commands.
        Exits on Ctrl+D (EOF) or Ctrl+C.
        """
        lang_label = self.language or "auto"
        print(f"Multilingual Programming REPL v{__version__} "
              f"[language={lang_label}]")
        print("Type ':help' for commands, ':quit' or Ctrl+D to exit.\n")

        while True:
            try:
                line = input(">>> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if line.strip() in ("exit", "quit"):
                print("Bye!")
                break

            # Handle REPL commands
            if line.strip().startswith(":"):
                result = self._handle_command(line)
                if result == "exit":
                    break
                if result:
                    continue

            # Multi-line detection: colon at end or open brackets
            open_brackets = self._count_open_brackets(line)
            needs_block = line.rstrip().endswith(":")

            if needs_block or open_brackets > 0:
                block_lines = [line]
                while True:
                    try:
                        cont = input("... ")
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    block_lines.append(cont)
                    open_brackets += self._count_open_brackets(cont)

                    # End block: empty line when in block mode (colon),
                    # or all brackets closed
                    if needs_block and cont.strip() == "":
                        break
                    if not needs_block and open_brackets <= 0:
                        break
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
