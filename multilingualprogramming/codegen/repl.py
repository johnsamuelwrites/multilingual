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
import json
import os
import sys
from pathlib import Path

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.exceptions import UnsupportedLanguageError
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

    _COMMAND_CATALOG = None
    _OPERATOR_CATALOG = None

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

    @classmethod
    def _load_command_catalog(cls):
        """Load command aliases and help text from resources."""
        if cls._COMMAND_CATALOG is not None:
            return cls._COMMAND_CATALOG

        path = (
            Path(__file__).resolve().parent.parent
            / "resources" / "repl" / "commands.json"
        )
        with open(path, "r", encoding="utf-8-sig") as handle:
            cls._COMMAND_CATALOG = json.load(handle)
        return cls._COMMAND_CATALOG

    def _language_code(self):
        """Return normalized active language code."""
        return (self.language or "en").lower()

    @classmethod
    def _load_operator_catalog(cls):
        """Load operator and symbol metadata from resources."""
        if cls._OPERATOR_CATALOG is not None:
            return cls._OPERATOR_CATALOG

        path = (
            Path(__file__).resolve().parent.parent
            / "resources" / "usm" / "operators.json"
        )
        with open(path, "r", encoding="utf-8-sig") as handle:
            cls._OPERATOR_CATALOG = json.load(handle)
        return cls._OPERATOR_CATALOG

    def _aliases_for(self, canonical, lang):
        """Return ordered aliases for a command in active language."""
        catalog = self._load_command_catalog()
        commands = catalog.get("commands", {})
        default_lang = catalog.get("default_language", "en")
        meta = commands.get(canonical, {})
        aliases_by_lang = meta.get("aliases", {})

        aliases = []
        aliases.extend(aliases_by_lang.get(default_lang, []))
        if lang != default_lang:
            aliases.extend(aliases_by_lang.get(lang, []))

        seen = set()
        ordered = []
        for alias in aliases:
            key = alias.casefold()
            if key not in seen:
                seen.add(key)
                ordered.append(alias)
        return ordered

    def _message(self, key, ui_lang, **kwargs):
        """Get localized REPL message template from command catalog."""
        catalog = self._load_command_catalog()
        default_lang = catalog.get("default_language", "en")
        messages = catalog.get("messages", {})
        template = messages.get(key, {}).get(
            ui_lang,
            messages.get(key, {}).get(default_lang, ""),
        )
        return template.format(**kwargs) if template else ""

    def _command_alias_map(self, lang):
        """Map canonical command names to casefolded aliases."""
        catalog = self._load_command_catalog()
        commands = catalog.get("commands", {})
        result = {}
        for canonical in commands:
            aliases = self._aliases_for(canonical, lang)
            result[canonical] = {
                canonical.casefold(), *(alias.casefold() for alias in aliases)
            }
        return result

    def _print_help(self):
        """Print localized REPL help from command catalog."""
        catalog = self._load_command_catalog()
        lang = self._language_code()
        default_lang = catalog.get("default_language", "en")
        commands = catalog.get("commands", {})

        title = catalog.get("help_titles", {}).get(
            lang,
            catalog.get("help_titles", {}).get(default_lang, "REPL Commands:"),
        )
        order = catalog.get("help_order", list(commands.keys()))

        print(title)
        for canonical in order:
            meta = commands.get(canonical, {})
            aliases = self._aliases_for(canonical, lang)
            display = aliases[-1] if aliases else canonical
            arg_hint = meta.get("arg_hint", "")
            description = meta.get("descriptions", {}).get(
                lang,
                meta.get("descriptions", {}).get(default_lang, ""),
            )
            print(f"  :{display}{arg_hint}  {description}")

    def _resolve_listing_language(self, arg):
        """Resolve and validate the language used for keyword/symbol listings."""
        lang = arg.strip().lower() if arg.strip() else self._language_code()
        registry = KeywordRegistry()
        registry.check_language(lang)
        return lang

    def _print_keywords(self, arg):
        """Print available keywords for a given language."""
        active_lang = self._language_code()
        try:
            lang = self._resolve_listing_language(arg)
        except UnsupportedLanguageError:
            label = arg.strip() or self._language_code()
            print(self._message("unsupported_language", active_lang, lang=label))
            return

        keywords = KeywordRegistry().get_all_keywords(lang)
        print(self._message("keywords_title", active_lang, lang=lang, count=len(keywords)))
        for concept_id, keyword in sorted(
            keywords.items(),
            key=lambda item: (item[1].casefold(), item[0]),
        ):
            print(f"  {keyword} -> {concept_id}")

    def _print_symbols(self, arg):
        """Print available operator and symbol mappings."""
        active_lang = self._language_code()
        try:
            lang = self._resolve_listing_language(arg)
        except UnsupportedLanguageError:
            label = arg.strip() or self._language_code()
            print(self._message("unsupported_language", active_lang, lang=label))
            return

        catalog = self._load_operator_catalog()
        default_lang = catalog.get("default_language", "en")
        print(self._message("symbols_title", active_lang, lang=lang))
        for category, operators in catalog.items():
            if not isinstance(operators, dict):
                continue
            print(f"{category}:")
            for name, meta in operators.items():
                if not isinstance(meta, dict):
                    continue
                symbols = meta.get("symbols", [])
                unicode_alt = meta.get("unicode_alt", [])
                pairs = meta.get("pairs", [])
                if pairs:
                    primary = f"{pairs[0]} {pairs[1]}"
                elif symbols:
                    primary = ", ".join(symbols)
                else:
                    primary = ""

                line = f"  {name}: {primary}"
                if unicode_alt:
                    line += f" | alt: {', '.join(unicode_alt)}"

                descriptions = meta.get("description", {})
                if isinstance(descriptions, dict):
                    desc = descriptions.get(lang, descriptions.get(default_lang))
                    if desc:
                        line += f" ({desc})"
                print(line)

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
            lexer = Lexer(source, language=self.language)
            tokens = lexer.tokenize()
            detected_lang = lexer.language or self.language or "en"

            parser = Parser(tokens, source_language=detected_lang)
            program = parser.parse()

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
            try:
                code = compile(python_source, "<repl>", "eval")
                result = eval(code, self._globals)  # pylint: disable=eval-used
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                code = compile(python_source, "<repl>", "exec")
                exec(code, self._globals)  # pylint: disable=exec-used
        except Exception as exc:
            captured.write(f"Error: {exc}\n")
        finally:
            sys.stdout = old_stdout
        return captured.getvalue()

    def _continuation_state(self, text):
        """Return (open_brackets, has_unclosed_string) for continuation."""
        count = 0
        string_char = None
        is_triple = False
        i = 0
        while i < len(text):
            ch = text[i]

            if string_char is not None:
                if is_triple:
                    if text[i:i+3] == string_char * 3:
                        string_char = None
                        is_triple = False
                        i += 3
                        continue
                else:
                    if ch == '\\':
                        i += 2
                        continue
                    if ch == string_char:
                        string_char = None
                        i += 1
                        continue
                i += 1
                continue

            if ch == '#':
                # Comment until end of line (outside strings)
                while i < len(text) and text[i] != '\n':
                    i += 1
                continue

            if ch in ('"', "'"):
                if text[i:i+3] == ch * 3:
                    string_char = ch
                    is_triple = True
                    i += 3
                    continue
                string_char = ch
                is_triple = False
                i += 1
                continue

            if ch in ('(', '[', '{'):
                count += 1
            elif ch in (')', ']', '}'):
                count -= 1

            i += 1

        return count, string_char is not None

    def _count_open_brackets(self, text):
        """Count net open brackets in text."""
        count, _has_unclosed_string = self._continuation_state(text)
        return count

    def _resolve_command(self, line):
        """Resolve REPL command aliases to canonical command names."""
        text = line.strip()
        if not text:
            return None, ""

        if text.startswith(":"):
            text = text[1:].lstrip()
            if not text:
                return None, ""

        parts = text.split(None, 1)
        cmd = parts[0].casefold()
        arg = parts[1] if len(parts) > 1 else ""

        alias_map = self._command_alias_map(self._language_code())
        for canonical, words in alias_map.items():
            if cmd in words:
                return canonical, arg
        return None, ""

    def _handle_command(self, line):
        """Handle REPL commands. Returns True if handled."""
        cmd, arg = self._resolve_command(line)
        if cmd is None:
            return False

        if cmd == "quit":
            print("Bye!")
            return "exit"
        if cmd == "lang":
            if arg:
                self.language = arg.strip()
                self._globals.clear()
                self._init_globals()
                print(f"Language switched to: {self.language}")
            else:
                print(f"Current language: {self.language or 'auto'}")
            return True
        if cmd == "python":
            self.show_python = not self.show_python
            state = "on" if self.show_python else "off"
            print(f"Show Python: {state}")
            return True
        if cmd == "reset":
            self._globals.clear()
            self._init_globals()
            print("State cleared.")
            return True
        if cmd == "help":
            self._print_help()
            return True
        if cmd == "keywords":
            self._print_keywords(arg)
            return True
        if cmd == "symbols":
            self._print_symbols(arg)
            return True
        return False

    def run(self):
        """
        Start the interactive REPL loop.

        Reads from stdin, supports multi-line blocks (lines ending with ':'),
        bracket continuation, and REPL commands.
        Exits on EOF (Ctrl+D on Unix, Ctrl+Z then Enter on Windows) or Ctrl+C.
        """
        lang_label = self.language or "auto"
        eof_hint = "Ctrl+Z then Enter" if os.name == "nt" else "Ctrl+D"
        print(f"Multilingual Programming REPL v{__version__} "
              f"[language={lang_label}]")
        print(
            f"Type ':help' for commands. Use ':quit' (or Ctrl+C) to exit. "
            f"EOF key is terminal-dependent ({eof_hint}).\n"
        )

        while True:
            try:
                line = input(">>> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if line.strip() in ("exit", "quit", "\x04", "\x1a"):
                print("Bye!")
                break

            result = self._handle_command(line)
            if result == "exit":
                break
            if result:
                continue

            open_brackets, has_unclosed_string = self._continuation_state(line)
            needs_block = line.rstrip().endswith(":")

            if needs_block or open_brackets > 0 or has_unclosed_string:
                block_lines = [line]
                while True:
                    try:
                        cont = input("... ")
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    if cont.strip() in ("\x04", "\x1a"):
                        print("Bye!")
                        return
                    block_lines.append(cont)
                    full_text = "\n".join(block_lines)
                    open_brackets, has_unclosed_string = (
                        self._continuation_state(full_text)
                    )

                    if needs_block and cont.strip() == "" \
                            and open_brackets <= 0 and not has_unclosed_string:
                        break
                    if not needs_block and open_brackets <= 0 \
                            and not has_unclosed_string:
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
