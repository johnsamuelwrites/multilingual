#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for deterministic, atomic WAT build orchestration."""

import shutil
import unittest
from pathlib import Path

from multilingualprogramming.codegen.build_orchestrator import BuildOrchestrator, wasmtime
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _parse(source: str, lang: str = "en"):
    lexer = Lexer(source, language=lang)
    parser = Parser(lexer.tokenize(), source_language=lang)
    return parser.parse()


class BuildOrchestratorTestSuite(unittest.TestCase):
    """Validate bundle generation and deterministic outputs."""

    @staticmethod
    def _tmpdir(test_name: str) -> Path:
        path = Path("tests") / ".tmp_build_orchestrator" / test_name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def test_build_generates_expected_artifacts(self):
        source = "def f(x):\n    return x + 1\nprint(f(2))\n"
        program = _parse(source)
        out = self._tmpdir("artifacts")
        try:
            outputs = BuildOrchestrator(out).build_from_program(program)
            self.assertTrue(outputs.transpiled_python.exists())
            self.assertTrue(outputs.wat.exists())
            self.assertEqual(outputs.wasm.exists(), wasmtime is not None)
            self.assertTrue(outputs.abi_manifest.exists())
            self.assertTrue(outputs.host_shim_js.exists())
            self.assertTrue(outputs.renderer_template_js.exists())
            self.assertTrue(outputs.build_graph.exists())
            self.assertTrue(outputs.build_lockfile.exists())
        finally:
            shutil.rmtree(out)

    def test_build_is_deterministic_for_same_input(self):
        source = "def f(x):\n    return x + 1\nprint(f(2))\n"
        program = _parse(source)
        out = self._tmpdir("deterministic")
        try:
            orchestrator = BuildOrchestrator(out)
            first = orchestrator.build_from_program(program)
            first_manifest = first.abi_manifest.read_text(encoding="utf-8")
            first_lock = first.build_lockfile.read_text(encoding="utf-8")
            second = orchestrator.build_from_program(program)
            second_manifest = second.abi_manifest.read_text(encoding="utf-8")
            second_lock = second.build_lockfile.read_text(encoding="utf-8")
            self.assertEqual(first_manifest, second_manifest)
            self.assertEqual(first_lock, second_lock)
        finally:
            shutil.rmtree(out)


if __name__ == "__main__":
    unittest.main()
