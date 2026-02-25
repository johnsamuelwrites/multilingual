#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Integration tests for `.ml` import support across languages."""

import importlib
import subprocess
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


class RelativeImportTestSuite(unittest.TestCase):
    """Validate relative imports (depuis . / depuis ..) in French .ml packages."""

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

    def _run_fr(self, source, extra_path=None):
        """Execute French source, optionally with an extra sys.path entry."""
        original_path = list(sys.path)
        if extra_path:
            sys.path.insert(0, extra_path)
        try:
            return ProgramExecutor(language="fr").execute(
                source, globals_dict={"__package__": None}
            )
        finally:
            sys.path[:] = original_path

    def test_relative_import_same_package(self):
        """depuis . importer module  (level=1, module name given)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(tmp, "paquet/__init__.ml", "")
            self._write_file(
                tmp,
                "paquet/utilitaires.ml",
                "déf multiplier(a, b):\n    retour a * b\n",
            )
            self._write_file(
                tmp,
                "paquet/calcul.ml",
                "depuis .utilitaires importer multiplier\n"
                "afficher(multiplier(6, 7))\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["paquet", "paquet.utilitaires", "paquet.calcul"])
            try:
                source = "depuis paquet importer calcul"
                result = ProgramExecutor(language="fr").execute(
                    source,
                    globals_dict={"__package__": None},
                )
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["paquet", "paquet.utilitaires", "paquet.calcul"])

        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "42")

    def test_relative_import_bare_dot(self):
        """depuis . importer nom  (level=1, no module name — imports a name from __init__)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "paquet/__init__.ml",
                "soit CONSTANTE = 99\n",
            )
            self._write_file(
                tmp,
                "paquet/lecteur.ml",
                "depuis . importer CONSTANTE\n"
                "afficher(CONSTANTE)\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["paquet", "paquet.lecteur"])
            try:
                source = "depuis paquet importer lecteur"
                result = ProgramExecutor(language="fr").execute(
                    source,
                    globals_dict={"__package__": None},
                )
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["paquet", "paquet.lecteur"])

        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "99")

    def test_relative_import_parent_package(self):
        """depuis .. importer module  (level=2, cross subpackage boundary)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(tmp, "lib/__init__.ml", "")
            self._write_file(
                tmp,
                "lib/maths.ml",
                "déf carre(x):\n    retour x * x\n",
            )
            self._write_file(tmp, "lib/sous/__init__.ml", "")
            self._write_file(
                tmp,
                "lib/sous/application.ml",
                "depuis .. importer maths\n"
                "afficher(maths.carre(9))\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(
                ["lib", "lib.maths", "lib.sous", "lib.sous.application"]
            )
            try:
                source = "depuis lib.sous importer application"
                result = ProgramExecutor(language="fr").execute(
                    source,
                    globals_dict={"__package__": None},
                )
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(
                    ["lib", "lib.maths", "lib.sous", "lib.sous.application"]
                )

        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "81")

    def test_relative_import_dotmodule_name(self):
        """depuis .module importer Classe  (level=1, explicit sub-module)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(tmp, "pkg/__init__.ml", "")
            self._write_file(
                tmp,
                "pkg/formes.ml",
                "classe Carre:\n"
                "    déf __init__(soi, cote):\n"
                "        soi.cote = cote\n"
                "    déf surface(soi):\n"
                "        retour soi.cote * soi.cote\n",
            )
            self._write_file(
                tmp,
                "pkg/mesures.ml",
                "depuis .formes importer Carre\n"
                "soit c = Carre(7)\n"
                "afficher(c.surface())\n",
            )

            original_path = self._with_sys_path(tmp)
            self._purge_modules(["pkg", "pkg.formes", "pkg.mesures"])
            try:
                source = "depuis pkg importer mesures"
                result = ProgramExecutor(language="fr").execute(
                    source,
                    globals_dict={"__package__": None},
                )
            finally:
                self._restore_sys_path(original_path)
                self._purge_modules(["pkg", "pkg.formes", "pkg.mesures"])

        self.assertTrue(result.success, result.errors)
        self.assertEqual(result.output.strip(), "49")

    def test_imports_fr_example_package(self):
        """End-to-end: run examples/imports_fr via absolute package imports."""
        examples_root = Path(__file__).parent.parent / "examples"
        modules_to_purge = [
            "imports_fr",
            "imports_fr.geometrie",
            "imports_fr.geometrie.formes",
            "imports_fr.geometrie.mesures",
            "imports_fr.statistiques",
            "imports_fr.statistiques.descriptif",
        ]
        original_path = self._with_sys_path(str(examples_root))
        self._purge_modules(modules_to_purge)
        try:
            source = (
                "depuis imports_fr.geometrie.formes importer Cercle, Rectangle\n"
                "depuis imports_fr.geometrie.mesures importer calcul_surface\n"
                "depuis imports_fr.statistiques.descriptif importer moyenne\n"
                "soit formes = [Cercle(1.0), Rectangle(2.0, 3.0)]\n"
                "soit surfaces = [calcul_surface(f) pour f dans formes]\n"
                "afficher(round(moyenne(surfaces), 4))\n"
            )
            result = ProgramExecutor(language="fr").execute(
                source,
                globals_dict={"__package__": None},
            )
        finally:
            self._restore_sys_path(original_path)
            self._purge_modules(modules_to_purge)

        self.assertTrue(result.success, result.errors)
        # Cercle(1.0).surface ≈ π ≈ 3.1416; Rectangle(2,3).surface = 6.0
        # moyenne ≈ (3.1416 + 6.0) / 2 ≈ 4.5708
        output = float(result.output.strip())
        self.assertAlmostEqual(output, 4.5708, places=3)


class CLIImportTestSuite(unittest.TestCase):
    """Validate that `multilingual run` correctly resolves local .ml imports."""

    def _write_file(self, root, relative_path, content):
        path = Path(root) / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _run_cli(self, file_path):
        return subprocess.run(
            [sys.executable, "-m", "multilingualprogramming", "run",
             str(file_path), "--lang", "fr"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cli_run_resolves_sibling_module(self):
        """multilingual run principal.ml finds utilitaires.ml in same directory."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "utilitaires.ml",
                "déf ajouter(a, b):\n    retour a + b\n",
            )
            self._write_file(
                tmp,
                "principal.ml",
                "importer utilitaires\n"
                "afficher(utilitaires.ajouter(19, 23))\n",
            )
            proc = self._run_cli(Path(tmp) / "principal.ml")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "42")

    def test_cli_run_resolves_package_import(self):
        """multilingual run principal.ml finds a local package with __init__.ml."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(tmp, "outils/__init__.ml", "")
            self._write_file(
                tmp,
                "outils/calcul.ml",
                "déf tripler(x):\n    retour x * 3\n",
            )
            self._write_file(
                tmp,
                "principal.ml",
                "depuis outils importer calcul\n"
                "afficher(calcul.tripler(14))\n",
            )
            proc = self._run_cli(Path(tmp) / "principal.ml")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "42")

    def test_cli_run_resolves_relative_import_inside_package(self):
        """multilingual run on a file inside a package resolves relative imports."""
        with tempfile.TemporaryDirectory() as tmp:
            self._write_file(
                tmp,
                "monpac/__init__.ml",
                "",
            )
            self._write_file(
                tmp,
                "monpac/utilitaires.ml",
                "déf doubler(x):\n    retour x * 2\n",
            )
            self._write_file(
                tmp,
                "monpac/calcul.ml",
                "depuis . importer utilitaires\n"
                "afficher(utilitaires.doubler(21))\n",
            )
            proc = self._run_cli(Path(tmp) / "monpac" / "calcul.ml")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "42")
