#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Integration tests for `.ml` import support across languages."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.imports import (
    disable_multilingual_imports,
    enable_multilingual_imports,
)


class MultilingualImportTestSuite(unittest.TestCase):
    """Validate importing multilingual modules and packages."""

    def setUp(self):
        disable_multilingual_imports()

    def tearDown(self):
        disable_multilingual_imports()

    def _write_file(self, root, relative_path, content):
        path = Path(root) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _with_sys_path(self, root):
        original_path = list(sys.path)
        sys.path.insert(0, root)
        return original_path

    def _restore_sys_path(self, original):
        sys.path[:] = original

    def _purge_modules(self, names):
        for name in names:
            sys.modules.pop(name, None)

    def test_english_program_imports_french_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "module_fr.ml",
                "soit valeur = 41\n"
                "def incremente(x):\n"
                "    retour x + 1\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["module_fr"])
            try:
                source = (
                    "import module_fr\n"
                    "print(module_fr.incremente(module_fr.valeur))\n"
                )
                result = ProgramExecutor(language="en").execute(source)
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["module_fr"])

            self.assertTrue(result.success, result.errors)
            self.assertEqual(result.output.strip(), "42")

    def test_french_program_from_imports_english_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "module_en.ml",
                "def add(a, b):\n"
                "    return a + b\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["module_en"])
            try:
                source = (
                    "depuis module_en importer add comme addition\n"
                    "afficher(addition(20, 22))\n"
                )
                result = ProgramExecutor(language="fr").execute(source)
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["module_en"])

            self.assertTrue(result.success, result.errors)
            self.assertEqual(result.output.strip(), "42")

    def test_package_import_from_ml_init_and_submodule(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(tmp, "pkg/__init__.ml", "let default_value = 5\n")
            self._write_file(
                tmp,
                "pkg/tools.ml",
                "def double(x):\n"
                "    return x * 2\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["pkg", "pkg.tools"])
            try:
                source = (
                    "from pkg import default_value\n"
                    "from pkg import tools\n"
                    "print(tools.double(default_value))\n"
                )
                result = ProgramExecutor(language="en").execute(source)
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["pkg", "pkg.tools"])

            self.assertTrue(result.success, result.errors)
            self.assertEqual(result.output.strip(), "10")

    def test_manual_enable_disable_for_direct_python_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "module_direct.ml",
                "let value = 7\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["module_direct"])
            try:
                disable_multilingual_imports()
                with self.assertRaises(ModuleNotFoundError):
                    importlib.import_module("module_direct")

                enable_multilingual_imports()
                module = importlib.import_module("module_direct")
                self.assertEqual(module.value, 7)
            finally:
                disable_multilingual_imports()
                self._restore_sys_path(original_path)
                self._purge_modules(["module_direct"])
