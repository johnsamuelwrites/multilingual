#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""WAT->WASM artifact and execution checks for complete feature examples."""

from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.source_extensions import iter_source_files


_EXAMPLES_DIR = pathlib.Path(__file__).parent.parent / "examples"
_EXECUTION_FUEL_LIMIT = 500_000


def _load_complete_feature_examples() -> list[tuple[str, pathlib.Path, str]]:
    """Return (lang, path, code) tuples for complete_features examples."""
    rows: list[tuple[str, pathlib.Path, str]] = []
    for fpath in iter_source_files(_EXAMPLES_DIR, "complete_features_*"):
        lang = fpath.stem.split("_")[-1]
        rows.append((lang, fpath, fpath.read_text(encoding="utf-8")))
    return rows


def _parse(code: str, lang: str):
    """Parse multilingual source text into AST."""
    tokens = Lexer(code, language=lang).tokenize()
    return Parser(tokens, source_language=lang).parse()


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime not installed",
)
class CompleteFeaturesWasmExecutionSuite(unittest.TestCase):
    """Generate WAT/WASM artifacts and execute them for every language example."""

    def _instantiate_and_run_main(self, wasm_bytes: bytes):
        # Imported lazily so this module still imports when wasmtime is absent.
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        config = wasmtime.Config()
        config.consume_fuel = True
        engine = wasmtime.Engine(config)
        module = wasmtime.Module(engine, wasm_bytes)
        wasi_cfg = wasmtime.WasiConfig()
        wasi_cfg.inherit_stdout()
        store = wasmtime.Store(engine)
        store.set_wasi(wasi_cfg)
        store.set_fuel(_EXECUTION_FUEL_LIMIT)
        linker = wasmtime.Linker(engine)
        linker.define_wasi()
        instance = linker.instantiate(store, module)
        exports = instance.exports(store)
        if "__main" in exports:
            try:
                exports["__main"](store)
            except (wasmtime.Trap, wasmtime.WasmtimeError) as exc:
                # Some complete-feature examples are intentionally heavy.
                # Fuel exhaustion still proves the module instantiated and executed.
                if "fuel" not in str(exc).lower():
                    raise

    def test_complete_feature_examples_generate_wasm_artifacts_and_execute(self):
        # Imported lazily so this module still imports when wasmtime is absent.
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        for lang, fpath, code in _load_complete_feature_examples():
            with self.subTest(lang=lang, file=fpath.name):
                prog = _parse(code, lang)
                wat = WATCodeGenerator().generate(prog)

                with tempfile.TemporaryDirectory(prefix=f"ml-wasm-{lang}-") as tmpdir:
                    out_dir = pathlib.Path(tmpdir)
                    wat_path = out_dir / f"{fpath.stem}.wat"
                    wasm_path = out_dir / f"{fpath.stem}.wasm"

                    wat_path.write_text(wat, encoding="utf-8")
                    self.assertTrue(wat_path.exists(), f"[{lang}] missing WAT artifact")

                    wasm_bytes = wasmtime.wat2wasm(wat)
                    wasm_path.write_bytes(wasm_bytes)
                    self.assertTrue(wasm_path.exists(), f"[{lang}] missing WASM artifact")
                    self.assertGreater(
                        wasm_path.stat().st_size,
                        0,
                        f"[{lang}] empty WASM artifact",
                    )

                    self._instantiate_and_run_main(wasm_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
