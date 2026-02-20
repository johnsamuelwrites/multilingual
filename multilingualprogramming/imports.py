#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Import hook for loading `.ml` modules/packages."""

import importlib.abc
import importlib.util
import sys
from pathlib import Path

from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.core.lowering import lower_to_core_ir
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import SemanticAnalyzer


class _MLLoader(importlib.abc.Loader):
    """Loader that transpiles and executes `.ml` source modules."""

    _CODE_CACHE = {}

    def __init__(self, source_path, is_package=False):
        self.source_path = Path(source_path)
        self._is_package = is_package

    def is_package(self, fullname):
        del fullname
        return self._is_package

    def _build_code_object(self):
        stat = self.source_path.stat()
        cache_key = str(self.source_path.resolve())
        cache_entry = self._CODE_CACHE.get(cache_key)
        stamp = (stat.st_mtime_ns, stat.st_size)
        if cache_entry and cache_entry["stamp"] == stamp:
            return cache_entry["code"], cache_entry["language"]

        with open(self.source_path, "r", encoding="utf-8") as handle:
            source = handle.read()

        lexer = Lexer(source, language=None)
        tokens = lexer.tokenize()
        detected_language = lexer.language or "en"

        parser = Parser(tokens, source_language=detected_language)
        program = parser.parse()
        core_program = lower_to_core_ir(
            program, detected_language, frontend_name="lexer_parser"
        )

        analyzer = SemanticAnalyzer(source_language=detected_language)
        builtins_ns = RuntimeBuiltins(detected_language).namespace()
        for name in builtins_ns:
            analyzer.symbol_table.define(name, "variable", line=0, column=0)

        semantic_errors = analyzer.analyze(core_program.ast)
        if semantic_errors:
            rendered = "; ".join(str(err) for err in semantic_errors)
            raise ImportError(
                f"Semantic checks failed for {self.source_path}: {rendered}"
            )

        python_source = PythonCodeGenerator().generate(core_program)
        code_obj = compile(python_source, str(self.source_path), "exec")

        self._CODE_CACHE[cache_key] = {
            "stamp": stamp,
            "code": code_obj,
            "language": detected_language,
        }
        return code_obj, detected_language

    def exec_module(self, module):
        code_obj, language = self._build_code_object()
        for name, builtin_obj in RuntimeBuiltins(language).namespace().items():
            module.__dict__.setdefault(name, builtin_obj)
        exec(code_obj, module.__dict__)  # pylint: disable=exec-used


class _MLFinder(importlib.abc.MetaPathFinder):
    """Meta-path finder for `.ml` modules and packages."""

    @staticmethod
    def _candidate_spec(fullname, base_dir):
        module_name = fullname.rsplit(".", 1)[-1]
        package_dir = Path(base_dir) / module_name
        package_init = package_dir / "__init__.ml"
        if package_init.is_file():
            loader = _MLLoader(package_init, is_package=True)
            return importlib.util.spec_from_file_location(
                fullname,
                package_init,
                loader=loader,
                submodule_search_locations=[str(package_dir)],
            )

        module_file = Path(base_dir) / f"{module_name}.ml"
        if module_file.is_file():
            loader = _MLLoader(module_file, is_package=False)
            return importlib.util.spec_from_file_location(
                fullname,
                module_file,
                loader=loader,
            )
        return None

    def find_spec(self, fullname, path=None, target=None):
        del target
        search_paths = path if path is not None else sys.path
        for base in search_paths:
            if not base:
                base = "."
            try:
                spec = self._candidate_spec(fullname, base)
            except OSError:
                continue
            if spec is not None:
                return spec
        return None


_FINDER = None


def enable_multilingual_imports():
    """Enable import of `.ml` modules in the active Python process."""
    global _FINDER  # pylint: disable=global-statement
    if _FINDER is not None and _FINDER in sys.meta_path:
        return _FINDER
    finder = _MLFinder()
    sys.meta_path.insert(0, finder)
    _FINDER = finder
    return finder


def disable_multilingual_imports():
    """Disable import of `.ml` modules in the active Python process."""
    global _FINDER  # pylint: disable=global-statement
    if _FINDER is not None and _FINDER in sys.meta_path:
        sys.meta_path.remove(_FINDER)
    _FINDER = None
