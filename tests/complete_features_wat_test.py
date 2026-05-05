#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Regression tests for all complete_features source example files.

Each complete_features_<lang> source file exercises every feature of the
multilingual language for that human language.  These tests verify:

  1. Parsing  — each file must parse without error.
  2. Execution — ProgramExecutor must succeed and produce output.
  3. WAT generation — WATCodeGenerator must not raise an exception.
  4. WAT module structure — the output must be a well-formed (module …).
  5. WAT symbol validity — no undefined call $name or undeclared local refs
     that would cause wabt / the browser WASM engine to reject the module.
  6. WAT content — expected structural elements (imports, memory, __main).

Tests are parameterised over all 17 languages via unittest.subTest so every
failure is reported with its language code.
"""

import re
import pathlib
import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.source_extensions import iter_source_files


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"

# The five host functions the generated WAT module imports from the browser.
_WAT_RUNTIME_FUNCS = frozenset({
    "print_str",
    "print_f64",
    "print_bool",
    "print_sep",
    "print_newline",
})


def _load_examples():
    """Return a sorted list of (lang_code, source_code) for every example file."""
    pairs = []
    for fpath in iter_source_files(_EXAMPLES_DIR, "complete_features_*"):
        lang = fpath.stem.split("_")[-1]
        pairs.append((lang, fpath.read_text(encoding="utf-8")))
    return pairs


def _parse(code: str, lang: str):
    """Lex + parse *code* with the given language.  Returns a Program node."""
    lex = Lexer(code, language=lang)
    return Parser(lex.tokenize(), source_language=lang).parse()


def _generate_wat(code: str, lang: str) -> str:
    """Parse *code* and generate WAT.  Returns the WAT string."""
    return WATCodeGenerator().generate(_parse(code, lang))


def _wat_validity_errors(wat: str) -> list:
    """
    Return a list of validity problems found in *wat*.

    Checks two invariants that must hold for the generated WAT to be
    accepted by wabt / the browser WASM engine:

    * Every ``call $name`` must reference a function defined in the module
      (via ``(func $name …)``) or one of the five host imports.
    * Every ``local.get $name`` / ``local.set $name`` within a function must
      reference a name declared as ``(param $name …)`` or ``(local $name …)``
      in that function's signature / body.
    """
    errs = []

    # Collect all function names defined or imported in the module
    defined = set(re.findall(r'\(func \$(\w+)', wat))
    allowed_calls = defined | _WAT_RUNTIME_FUNCS

    # Check for calls to undefined symbols
    for call_target in re.findall(r'call \$(\w+)', wat):
        if call_target not in allowed_calls:
            errs.append(f"undefined call: ${call_target}")

    # Check per-function local declarations vs references
    # Split on the opening of each func definition (the leading \n  is consumed
    # by the split, so each chunk starts at '$funcname')
    for chunk in re.split(r'\n  \(func ', wat)[1:]:
        fname_m = re.match(r'\$(\w+)', chunk)
        fname = fname_m.group(1) if fname_m else "?"
        declared = set(re.findall(r'\((?:param|local) \$(\w+)', chunk))
        for ref in re.findall(r'local\.(?:get|set) \$(\w+)', chunk):
            if ref not in declared:
                errs.append(f"undeclared local in ${fname}: ${ref}")

    return errs


# ---------------------------------------------------------------------------
# 1. Parsing
# ---------------------------------------------------------------------------

class CompleteFeaturesParseSuite(unittest.TestCase):
    """Parsing every complete_features source file must succeed."""

    def test_all_files_parse_without_error(self):
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                prog = _parse(code, lang)
                self.assertIsNotNone(prog,
                                     f"[{lang}] Parser returned None")
                self.assertGreater(
                    len(prog.body), 0,
                    f"[{lang}] Parsed program body is empty"
                )

    def test_all_files_parse_with_expected_node_count(self):
        """Each complete features file should parse into a non-trivial AST."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                prog = _parse(code, lang)
                # Complete feature files have many top-level statements;
                # require at least 10 to catch silent truncation.
                self.assertGreaterEqual(
                    len(prog.body), 10,
                    f"[{lang}] Only {len(prog.body)} top-level statements parsed "
                    f"(expected ≥ 10 for a complete-features file)"
                )


# ---------------------------------------------------------------------------
# 2. Execution
# ---------------------------------------------------------------------------

class CompleteFeaturesExecutionSuite(unittest.TestCase):
    """Executing every complete_features source file must succeed."""

    def test_all_files_execute_without_error(self):
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                result = ProgramExecutor(language=lang).execute(code)
                self.assertTrue(
                    result.success,
                    f"[{lang}] Execution failed: {result.errors}"
                )

    def test_all_files_produce_output(self):
        """Every complete-features program must print at least one line."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                result = ProgramExecutor(language=lang).execute(code)
                self.assertTrue(result.success,
                                f"[{lang}] Execution failed: {result.errors}")
                self.assertTrue(
                    result.output.strip(),
                    f"[{lang}] Program produced no output"
                )

    def test_all_files_generate_python_source(self):
        """The executor must produce a Python transpilation for every file."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                result = ProgramExecutor(language=lang).execute(code)
                self.assertTrue(result.success,
                                f"[{lang}] Execution failed: {result.errors}")
                self.assertTrue(
                    result.python_source and result.python_source.strip(),
                    f"[{lang}] No Python source was generated"
                )


# ---------------------------------------------------------------------------
# 3 & 4. WAT generation and module structure
# ---------------------------------------------------------------------------

class CompleteFeaturesWATGenerationSuite(unittest.TestCase):
    """WAT generation for every complete_features source file must succeed."""

    def test_all_files_wat_generation_no_exception(self):
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                try:
                    wat = _generate_wat(code, lang)
                    self.assertIsInstance(wat, str,
                                         f"[{lang}] generate() did not return a str")
                except Exception as exc:  # pylint: disable=broad-except
                    self.fail(f"[{lang}] WATCodeGenerator raised: {exc}")

    def test_all_wat_starts_with_module(self):
        """Every generated WAT must open with the (module keyword."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                self.assertTrue(
                    wat.strip().startswith("(module"),
                    f"[{lang}] WAT does not start with '(module': {wat[:50]!r}"
                )

    def test_all_wat_ends_with_closing_paren(self):
        """Every generated WAT must be closed with a matching ')'."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                self.assertTrue(
                    wat.strip().endswith(")"),
                    f"[{lang}] WAT does not end with ')'"
                )

    def test_all_wat_non_empty(self):
        """Generated WAT must contain more than just the module wrapper."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                lines = [ln for ln in wat.splitlines() if ln.strip()]
                self.assertGreater(
                    len(lines), 5,
                    f"[{lang}] WAT has only {len(lines)} non-empty lines"
                )


# ---------------------------------------------------------------------------
# 5. WAT symbol validity (the core regression gate)
# ---------------------------------------------------------------------------

class CompleteFeaturesWATValiditySuite(unittest.TestCase):
    """
    Generated WAT must contain no undefined symbols.

    Undefined symbols cause wabt / browser WASM engines to reject the binary,
    producing the 'WAT contains unresolved symbols' error seen in the playground.
    """

    def test_no_undefined_function_calls(self):
        """
        Every ``call $name`` in the generated WAT must reference either:
        - a function defined in the same module (``(func $name …)``), or
        - one of the five host imports (print_str / print_f64 / …).
        """
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                errs = [e for e in _wat_validity_errors(wat)
                        if e.startswith("undefined call")]
                self.assertFalse(
                    errs,
                    f"[{lang}] WAT has undefined function calls: {errs}"
                )

    def test_no_undeclared_local_references(self):
        """
        Every ``local.get $x`` / ``local.set $x`` inside a WAT function must
        reference a name declared as ``(param $x …)`` or ``(local $x …)``
        in that function.  Undeclared local references make the WAT invalid.
        """
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                errs = [e for e in _wat_validity_errors(wat)
                        if e.startswith("undeclared")]
                self.assertFalse(
                    errs,
                    f"[{lang}] WAT has undeclared local references: {errs}"
                )

    def test_all_wat_symbols_valid_combined(self):
        """Combined gate: no undefined calls AND no undeclared locals."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                errs = _wat_validity_errors(wat)
                self.assertFalse(
                    errs,
                    f"[{lang}] WAT has {len(errs)} validity error(s): {errs[:5]}"
                )


# ---------------------------------------------------------------------------
# 6. WAT content — structural elements
# ---------------------------------------------------------------------------

class CompleteFeaturesWATContentSuite(unittest.TestCase):
    """Generated WAT must contain the structural elements expected by the runtime."""

    def test_all_wat_defines_wasi_runtime_functions(self):
        """Every WAT module must define the five print runtime functions internally."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                for fn in sorted(_WAT_RUNTIME_FUNCS):
                    self.assertIn(
                        f"${fn}",
                        wat,
                        f"[{lang}] Missing runtime function: {fn}"
                    )

    def test_all_wat_exports_linear_memory(self):
        """WAT must export a linear memory page for string data."""
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                self.assertIn(
                    "(memory", wat,
                    f"[{lang}] WAT is missing (memory …) declaration"
                )

    def test_all_wat_exports_main_entrypoint(self):
        """
        Every complete_features program has top-level statements, so WAT must
        contain and export the ``__main`` entry-point function.
        """
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                self.assertIn(
                    '"__main"', wat,
                    f"[{lang}] WAT does not export __main entry point"
                )

    def test_all_wat_has_main_local_declarations(self):
        """
        __main must declare its locals with (local $name f64).
        Complete-features files always have local variables.
        """
        for lang, code in _load_examples():
            with self.subTest(lang=lang):
                wat = _generate_wat(code, lang)
                # Locate the __main func block
                main_match = re.search(
                    r'\(func \$__main.*?(?=\n  \(func |\n\)$)',
                    wat, re.DOTALL
                )
                self.assertIsNotNone(
                    main_match,
                    f"[{lang}] Could not locate $__main function in WAT"
                )
                self.assertIn(
                    "(local $", main_match.group(),
                    f"[{lang}] $__main has no (local …) declarations"
                )


if __name__ == "__main__":
    unittest.main()
