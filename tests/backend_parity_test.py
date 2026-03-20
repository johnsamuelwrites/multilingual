#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Focused parity checks between Python execution and WAT/WASM execution."""

import importlib.util
import os
import tempfile
import unittest

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.wat_generator import (
    WATCodeGenerator,
    has_stub_calls,
)
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _parse_source(source: str, language: str = "en"):
    """Parse source text through the multilingual frontend."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    detected_language = lexer.language or language
    return Parser(tokens, source_language=detected_language).parse()


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for backend parity tests",
)
class BackendParityTestSuite(unittest.TestCase):
    """Compare Python executor output with WAT/WASM output for supported programs."""

    def _run_python(self, source: str, language: str = "en") -> str:
        result = ProgramExecutor(language=language).execute(source)
        self.assertTrue(result.success, result.errors)
        return result.output

    def _run_wat(self, source: str, language: str = "en") -> str:
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        program = _parse_source(source, language)
        wat = WATCodeGenerator().generate(program)
        self.assertFalse(has_stub_calls(wat), wat)

        engine = wasmtime.Engine()
        wasm_bytes = wasmtime.wat2wasm(wat)
        module = wasmtime.Module(engine, wasm_bytes)
        with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as tf:
            stdout_path = tf.name
        try:
            wasi_cfg = wasmtime.WasiConfig()
            wasi_cfg.stdout_file = stdout_path
            store = wasmtime.Store(engine)
            store.set_wasi(wasi_cfg)
            linker = wasmtime.Linker(engine)
            linker.define_wasi()
            instance = linker.instantiate(store, module)
            instance.exports(store)["__main"](store)
            with open(stdout_path, encoding="utf-8") as fh:
                return fh.read()
        finally:
            os.unlink(stdout_path)

    def _assert_backend_parity(self, source: str, language: str = "en") -> None:
        python_output = self._run_python(source, language)
        wat_output = self._run_wat(source, language)
        self.assertEqual(wat_output, python_output)

    def test_loop_arithmetic_parity(self):
        source = """\
let total = 0
for i in range(5):
    total = total + i
print(total)
"""
        self._assert_backend_parity(source)

    def test_string_concat_and_builtin_parity(self):
        source = """\
let message = "hello" + " " + "world"
print(message)
print(abs(-3))
print(min(5, 2, 8))
print(max(5, 2, 8))
"""
        self._assert_backend_parity(source)

    def test_list_and_comprehension_parity(self):
        source = """\
let nums = [i * 2 for i in range(4)]
print(len(nums))
print(nums[2])
"""
        self._assert_backend_parity(source)

    def test_string_index_and_slice_parity(self):
        source = """\
let s = "hello"
print(s[1])
print(s[1:4])
"""
        self._assert_backend_parity(source)

    def test_string_method_parity(self):
        source = """\
let s = "  hello world  "
print(s.strip())
print(s.find("world"))
"""
        self._assert_backend_parity(source)

    def test_fstring_parity(self):
        source = """\
let value = 3.14159
print(f"{value:.2f}")
print(f"{42!s}")
"""
        self._assert_backend_parity(source)

    def test_try_except_finally_parity(self):
        source = """\
try:
    raise ValueError
except ValueError as e:
    print("caught")
finally:
    print("done")
"""
        self._assert_backend_parity(source)

    def test_stateful_class_parity(self):
        source = """\
class Counter:
    def __init__(self):
        self.value = 1

    def bump(self):
        self.value = self.value + 2
        return self.value

let counter = Counter()
print(counter.bump())
print(counter.value)
"""
        self._assert_backend_parity(source)


if __name__ == "__main__":
    unittest.main()
