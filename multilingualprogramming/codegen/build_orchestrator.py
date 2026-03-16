#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Deterministic build orchestration for WAT artifact bundles."""

import json
import os
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

try:
    import wasmtime  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    wasmtime = None

from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator


@dataclass
class BuildOutputs:  # pylint: disable=too-many-instance-attributes
    """Resolved output file paths for build artifacts."""

    wat: Path
    wasm: Path
    abi_manifest: Path
    host_shim_js: Path
    renderer_template_js: Path
    transpiled_python: Path
    build_graph: Path
    build_lockfile: Path
    build_lock: Path


class BuildOrchestrator:  # pylint: disable=too-many-instance-attributes
    """Atomic, lock-guarded, deterministic artifact build."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.outputs = BuildOutputs(
            wat=self.output_dir / "module.wat",
            wasm=self.output_dir / "module.wasm",
            abi_manifest=self.output_dir / "abi_manifest.json",
            host_shim_js=self.output_dir / "host_shim.js",
            renderer_template_js=self.output_dir / "renderer_template.js",
            transpiled_python=self.output_dir / "transpiled.py",
            build_graph=self.output_dir / "build_graph.json",
            build_lockfile=self.output_dir / "build.lock.json",
            build_lock=self.output_dir / ".multilingual-build.lock",
        )

    def _acquire_lock(self, timeout_seconds: float = 10.0, poll_interval: float = 0.05):
        start = time.perf_counter()
        while True:
            try:
                fd = os.open(
                    self.outputs.build_lock,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                os.close(fd)
                return
            except FileExistsError:
                if (time.perf_counter() - start) >= timeout_seconds:
                    raise TimeoutError(
                        f"Timeout acquiring build lock: {self.outputs.build_lock}"
                    ) from None
                time.sleep(poll_interval)

    def _release_lock(self):
        try:
            self.outputs.build_lock.unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def _atomic_write_text(path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)

    @staticmethod
    def _atomic_write_bytes(path: Path, content: bytes):
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("wb", delete=False, dir=path.parent) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)

    @staticmethod
    def _compile_wasm_bytes(wat_source: str) -> bytes | None:
        if wasmtime is None:
            return None
        return wasmtime.wat2wasm(wat_source)

    def build_from_program(self, program) -> BuildOutputs:
        """Generate and atomically write all build artifacts from parsed Program."""
        self._acquire_lock()
        try:
            wat_generator = WATCodeGenerator()
            python_source = PythonCodeGenerator().generate(program)
            wat_source = wat_generator.generate(program)
            wasm_bytes = self._compile_wasm_bytes(wat_source)
            manifest = wat_generator.generate_abi_manifest(program)
            host_shim = wat_generator.generate_js_host_shim(manifest)
            renderer_template = wat_generator.generate_renderer_template(manifest)
            source_digest = hashlib.sha256(python_source.encode("utf-8")).hexdigest()

            build_graph = {
                "version": 1,
                "nodes": {
                    "program": [],
                    "transpiled_python": ["program"],
                    "module_wat": ["program"],
                    "module_wasm": ["module_wat"],
                    "abi_manifest": ["program", "module_wat"],
                    "host_shim_js": ["abi_manifest"],
                    "renderer_template_js": ["abi_manifest"],
                },
            }
            build_lockfile = {
                "version": 1,
                "source_digest_sha256": source_digest,
                "artifacts": {
                    "transpiled_python": self.outputs.transpiled_python.name,
                    "module_wat": self.outputs.wat.name,
                    "module_wasm": self.outputs.wasm.name,
                    "abi_manifest": self.outputs.abi_manifest.name,
                    "host_shim_js": self.outputs.host_shim_js.name,
                    "renderer_template_js": self.outputs.renderer_template_js.name,
                    "build_graph": self.outputs.build_graph.name,
                },
            }

            self._atomic_write_text(self.outputs.transpiled_python, python_source)
            self._atomic_write_text(self.outputs.wat, wat_source)
            if wasm_bytes is not None:
                self._atomic_write_bytes(self.outputs.wasm, wasm_bytes)
            self._atomic_write_text(
                self.outputs.abi_manifest,
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
            )
            self._atomic_write_text(self.outputs.host_shim_js, host_shim)
            self._atomic_write_text(self.outputs.renderer_template_js, renderer_template)
            self._atomic_write_text(
                self.outputs.build_graph,
                json.dumps(build_graph, ensure_ascii=False, indent=2, sort_keys=True),
            )
            self._atomic_write_text(
                self.outputs.build_lockfile,
                json.dumps(build_lockfile, ensure_ascii=False, indent=2, sort_keys=True),
            )
            return self.outputs
        finally:
            self._release_lock()
