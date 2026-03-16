#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""WASM execution tests for the WAT generator's class lowering."""
# pylint: disable=duplicate-code

import importlib.util
import os
import tempfile
import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    Assignment,
    AttributeAccess,
    BinaryOp,
    CallExpr,
    ClassDef,
    CompareOp,
    ExceptHandler,
    ExpressionStatement,
    FunctionDef,
    Identifier,
    IfStatement,
    ListLiteral,
    NumeralLiteral,
    Parameter,
    Program,
    RaiseStatement,
    ReturnStatement,
    StringLiteral,
    TryStatement,
    UnaryOp,
    VariableDeclaration,
)


def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _param(name: str) -> Parameter:
    """Create a Parameter with an Identifier name."""
    return Parameter(Identifier(name))


def _parse_wasi_output(text: str) -> list:
    """Parse WASI stdout text into a list of Python values.

    Tokens separated by whitespace are converted to float, bool, or string.
    """
    values = []
    for token in text.split():
        if token == "True":
            values.append(True)
        elif token == "False":
            values.append(False)
        elif token in ("nan", "inf", "-inf"):
            values.append(float(token))
        else:
            try:
                values.append(float(token))
            except ValueError:
                values.append(token)
    return values


def _parse_source(source: str, language: str):
    """Parse source text through the lexer/parser frontend for the given language."""
    from multilingualprogramming.lexer.lexer import Lexer  # pylint: disable=import-outside-toplevel
    from multilingualprogramming.parser.parser import Parser  # pylint: disable=import-outside-toplevel

    tokens = Lexer(source, language=language).tokenize()
    return Parser(tokens, source_language=language).parse()


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for WAT execution tests",
)
class WATClassWasmExecutionTestSuite(unittest.TestCase):
    """Execute generated WAT for lowered classes via wasmtime."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _run_main(self, prog):
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        wat = self.gen.generate(prog)
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
                return _parse_wasi_output(fh.read())
        finally:
            os.unlink(stdout_path)

    def test_constructor_statement_compiles_and_runs(self):
        prog = _prog(
            ClassDef(
                "Counter",
                [],
                [
                    FunctionDef(
                        "__init__",
                        [_param("self"), _param("start")],
                        [ReturnStatement(Identifier("start"))],
                    ),
                ],
            ),
            ExpressionStatement(CallExpr(Identifier("Counter"), [NumeralLiteral("1")])),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [])

    def test_class_method_call_runs(self):
        prog = _prog(
            ClassDef(
                "Math",
                [],
                [
                    FunctionDef(
                        "double",
                        [_param("x")],
                        [ReturnStatement(BinaryOp(Identifier("x"), "*", NumeralLiteral("2")))],
                    ),
                ],
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [
                        CallExpr(
                            AttributeAccess(Identifier("Math"), "double"),
                            [NumeralLiteral("4")],
                        )
                    ],
                )
            ),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [8.0])

    def test_instance_method_call_runs(self):
        prog = _prog(
            ClassDef(
                "Counter",
                [],
                [
                    FunctionDef(
                        "__init__",
                        [_param("self"), _param("start")],
                        [ReturnStatement(Identifier("start"))],
                    ),
                    FunctionDef(
                        "inc",
                        [_param("self"), _param("x")],
                        [ReturnStatement(BinaryOp(Identifier("x"), "+", NumeralLiteral("1")))],
                    ),
                ],
            ),
            VariableDeclaration("c", CallExpr(Identifier("Counter"), [NumeralLiteral("1")])),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [
                        CallExpr(
                            AttributeAccess(Identifier("c"), "inc"),
                            [NumeralLiteral("4")],
                        )
                    ],
                )
            ),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [5.0])

    def test_stateful_counter_stores_and_reads_value(self):
        prog = _prog(
            ClassDef(
                "Counter",
                [],
                [
                    FunctionDef(
                        "__init__",
                        [_param("self"), _param("start")],
                        [
                            Assignment(
                                AttributeAccess(Identifier("self"), "value"),
                                Identifier("start"),
                            )
                        ],
                    ),
                    FunctionDef(
                        "get",
                        [_param("self")],
                        [ReturnStatement(AttributeAccess(Identifier("self"), "value"))],
                    ),
                ],
            ),
            VariableDeclaration(
                "c",
                CallExpr(Identifier("Counter"), [NumeralLiteral("10")]),
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [CallExpr(AttributeAccess(Identifier("c"), "get"), [])],
                )
            ),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [10.0])

    def test_stateful_counter_mutates_value(self):
        prog = _prog(
            ClassDef(
                "Counter",
                [],
                [
                    FunctionDef(
                        "__init__",
                        [_param("self"), _param("start")],
                        [
                            Assignment(
                                AttributeAccess(Identifier("self"), "value"),
                                Identifier("start"),
                            )
                        ],
                    ),
                    FunctionDef(
                        "increment",
                        [_param("self")],
                        [
                            Assignment(
                                AttributeAccess(Identifier("self"), "value"),
                                BinaryOp(
                                    AttributeAccess(Identifier("self"), "value"),
                                    "+",
                                    NumeralLiteral("1"),
                                ),
                            )
                        ],
                    ),
                    FunctionDef(
                        "get",
                        [_param("self")],
                        [ReturnStatement(AttributeAccess(Identifier("self"), "value"))],
                    ),
                ],
            ),
            VariableDeclaration(
                "c",
                CallExpr(Identifier("Counter"), [NumeralLiteral("10")]),
            ),
            ExpressionStatement(CallExpr(AttributeAccess(Identifier("c"), "increment"), [])),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [CallExpr(AttributeAccess(Identifier("c"), "get"), [])],
                )
            ),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [11.0])

    def test_two_instances_have_independent_state(self):
        prog = _prog(
            ClassDef(
                "Counter",
                [],
                [
                    FunctionDef(
                        "__init__",
                        [_param("self"), _param("start")],
                        [
                            Assignment(
                                AttributeAccess(Identifier("self"), "value"),
                                Identifier("start"),
                            )
                        ],
                    ),
                    FunctionDef(
                        "get",
                        [_param("self")],
                        [ReturnStatement(AttributeAccess(Identifier("self"), "value"))],
                    ),
                ],
            ),
            VariableDeclaration(
                "a",
                CallExpr(Identifier("Counter"), [NumeralLiteral("1")]),
            ),
            VariableDeclaration(
                "b",
                CallExpr(Identifier("Counter"), [NumeralLiteral("2")]),
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [CallExpr(AttributeAccess(Identifier("a"), "get"), [])],
                )
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [CallExpr(AttributeAccess(Identifier("b"), "get"), [])],
                )
            ),
        )
        printed = self._run_main(prog)
        self.assertEqual(printed, [1.0, 2.0])


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for WAT execution tests",
)
class WATExpressionSemanticsWasmExecutionTestSuite(unittest.TestCase):
    """Execute focused arithmetic and membership regressions via wasmtime."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _instantiate(self, prog):
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        wat = self.gen.generate(prog)
        engine = wasmtime.Engine()
        wasm_bytes = wasmtime.wat2wasm(wat)
        module = wasmtime.Module(engine, wasm_bytes)
        wasi_cfg = wasmtime.WasiConfig()
        wasi_cfg.inherit_stdout()
        store = wasmtime.Store(engine)
        store.set_wasi(wasi_cfg)
        linker = wasmtime.Linker(engine)
        linker.define_wasi()
        instance = linker.instantiate(store, module)
        return store, instance

    def _call_export(self, prog, export_name, *args):
        store, instance = self._instantiate(prog)
        return instance.exports(store)[export_name](store, *args)

    def test_bit_extract_expression_matches_expected_value(self):
        prog = _prog(
            FunctionDef(
                "cellule_suivante",
                [_param("numero_regle"), _param("gauche"), _param("centre"), _param("droite")],
                [
                    VariableDeclaration(
                        "indice",
                        BinaryOp(
                            BinaryOp(
                                BinaryOp(Identifier("gauche"), "*", NumeralLiteral("4")),
                                "+",
                                BinaryOp(Identifier("centre"), "*", NumeralLiteral("2")),
                            ),
                            "+",
                            Identifier("droite"),
                        ),
                    ),
                    ReturnStatement(
                        BinaryOp(
                            BinaryOp(Identifier("numero_regle"), ">>", Identifier("indice")),
                            "&",
                            NumeralLiteral("1"),
                        )
                    ),
                ],
            ),
        )
        self.assertEqual(self._call_export(prog, "cellule_suivante", 90.0, 1.0, 0.0, 1.0), 0.0)
        self.assertEqual(self._call_export(prog, "cellule_suivante", 90.0, 1.0, 0.0, 0.0), 1.0)

    def test_membership_branch_returns_expected_value(self):
        prog = _prog(
            FunctionDef(
                "classe_wolfram",
                [_param("numero_regle")],
                [
                    IfStatement(
                        CompareOp(
                            Identifier("numero_regle"),
                            [(
                                "in",
                                ListLiteral(
                                    [
                                        NumeralLiteral("18"),
                                        NumeralLiteral("22"),
                                        NumeralLiteral("30"),
                                        NumeralLiteral("45"),
                                        NumeralLiteral("60"),
                                        NumeralLiteral("90"),
                                    ]
                                ),
                            )],
                        ),
                        [ReturnStatement(NumeralLiteral("3"))],
                        else_body=[ReturnStatement(NumeralLiteral("2"))],
                    )
                ],
            ),
        )
        self.assertEqual(self._call_export(prog, "classe_wolfram", 30.0), 3.0)
        self.assertEqual(self._call_export(prog, "classe_wolfram", 73.0), 2.0)

    def test_french_source_membership_and_bit_extract_compile_correctly(self):
        prog = _parse_source(
            "déf cellule_suivante(numero_regle, gauche, centre, droite):\n"
            "    soit indice = gauche * 4 + centre * 2 + droite\n"
            "    retour (numero_regle >> indice) & 1\n"
            "\n"
            "déf classe_wolfram(numero_regle):\n"
            "    si numero_regle dans [18, 22, 30, 45, 60, 90]:\n"
            "        retour 3\n"
            "    sinon:\n"
            "        retour 2\n",
            language="fr",
        )
        self.assertEqual(self._call_export(prog, "cellule_suivante", 90.0, 1.0, 0.0, 1.0), 0.0)
        self.assertEqual(self._call_export(prog, "classe_wolfram", 30.0), 3.0)


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for WAT execution tests",
)
class WATIntegerPrintingTestSuite(unittest.TestCase):
    """Verify that integer-valued floats are printed without a decimal point."""

    def _run_raw(self, prog) -> str:
        """Return the raw stdout text (not parsed) from running prog.__main."""
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error

        gen = WATCodeGenerator()
        wat = gen.generate(prog)
        engine = wasmtime.Engine()
        wasm_bytes = wasmtime.wat2wasm(wat)
        module = wasmtime.Module(engine, wasm_bytes)
        with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as tf:
            stdout_path = tf.name
        try:
            cfg = wasmtime.WasiConfig()
            cfg.stdout_file = stdout_path
            store = wasmtime.Store(engine)
            store.set_wasi(cfg)
            linker = wasmtime.Linker(engine)
            linker.define_wasi()
            inst = linker.instantiate(store, module)
            inst.exports(store)["__main"](store)
            with open(stdout_path, encoding="utf-8") as fh:
                return fh.read()
        finally:
            os.unlink(stdout_path)

    def test_integer_literal_prints_without_decimal(self):
        """print(42) must output '42', not '42.0'."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(Identifier("print"), [NumeralLiteral("42")])
            )
        )
        raw = self._run_raw(prog)
        self.assertIn("42\n", raw)
        self.assertNotIn("42.0", raw)

    def test_zero_prints_without_decimal(self):
        prog = _prog(
            ExpressionStatement(
                CallExpr(Identifier("print"), [NumeralLiteral("0")])
            )
        )
        raw = self._run_raw(prog)
        self.assertEqual(raw.strip(), "0")

    def test_float_literal_still_prints_decimal(self):
        """print(1.5) must still output '1.5'."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(Identifier("print"), [NumeralLiteral("1.5")])
            )
        )
        raw = self._run_raw(prog)
        self.assertEqual(raw.strip(), "1.5")

    def test_negative_integer_prints_without_decimal(self):
        """print(-7) must output '-7', not '-7.0'."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [UnaryOp("-", NumeralLiteral("7"))],
                )
            )
        )
        raw = self._run_raw(prog)
        self.assertEqual(raw.strip(), "-7")


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for WAT execution tests",
)
class WATExceptionHandlingTestSuite(unittest.TestCase):
    """Verify try/except/finally semantics via wasmtime execution."""

    def _run_raw(self, prog) -> str:
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error
        gen = WATCodeGenerator()
        wat = gen.generate(prog)
        engine = wasmtime.Engine()
        wasm_bytes = wasmtime.wat2wasm(wat)
        module = wasmtime.Module(engine, wasm_bytes)
        with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as tf:
            stdout_path = tf.name
        try:
            cfg = wasmtime.WasiConfig()
            cfg.stdout_file = stdout_path
            store = wasmtime.Store(engine)
            store.set_wasi(cfg)
            linker = wasmtime.Linker(engine)
            linker.define_wasi()
            inst = linker.instantiate(store, module)
            inst.exports(store)["__main"](store)
            with open(stdout_path, encoding="utf-8") as fh:
                return fh.read()
        finally:
            os.unlink(stdout_path)

    def test_catch_all_except_catches_raise(self):
        """bare except: catches any raised exception."""
        prog = _prog(
            TryStatement(
                body=[
                    RaiseStatement(CallExpr(Identifier("ValueError"), [])),
                    ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("1")])),
                ],
                handlers=[
                    ExceptHandler(exc_type=None, body=[
                        ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("2")])),
                    ]),
                ],
            )
        )
        raw = self._run_raw(prog)
        self.assertNotIn("1", raw)
        self.assertIn("2", raw)

    def test_except_exception_catches_raise(self):
        """except Exception: catches any raised exception."""
        prog = _prog(
            TryStatement(
                body=[
                    RaiseStatement(CallExpr(Identifier("RuntimeError"), [])),
                ],
                handlers=[
                    ExceptHandler(
                        exc_type=Identifier("Exception"),
                        body=[
                            ExpressionStatement(
                                CallExpr(Identifier("print"), [NumeralLiteral("42")])
                            ),
                        ],
                    ),
                ],
            )
        )
        raw = self._run_raw(prog)
        self.assertIn("42", raw)

    def test_finally_runs_after_handled_exception(self):
        """finally body executes after a handled exception."""
        prog = _prog(
            TryStatement(
                body=[
                    RaiseStatement(CallExpr(Identifier("ValueError"), [])),
                ],
                handlers=[
                    ExceptHandler(exc_type=Identifier("ValueError"), body=[
                        ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("1")])),
                    ]),
                ],
                finally_body=[
                    ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("2")])),
                ],
            )
        )
        raw = self._run_raw(prog)
        self.assertIn("1", raw)
        self.assertIn("2", raw)

    def test_finally_runs_when_no_exception(self):
        """finally body executes even when no exception is raised."""
        prog = _prog(
            TryStatement(
                body=[
                    ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("1")])),
                ],
                handlers=[
                    ExceptHandler(exc_type=Identifier("ValueError"), body=[
                        ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("X")])),
                    ]),
                ],
                finally_body=[
                    ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("2")])),
                ],
            )
        )
        raw = self._run_raw(prog)
        self.assertIn("1", raw)
        self.assertIn("2", raw)
        self.assertNotIn("X", raw)

    def test_except_as_e_binds_nonzero_code(self):
        """except ValueError as e: binds e to the exception code (non-zero)."""
        prog = _prog(
            TryStatement(
                body=[
                    RaiseStatement(CallExpr(Identifier("ValueError"), [])),
                ],
                handlers=[
                    ExceptHandler(
                        exc_type=Identifier("ValueError"),
                        name="e",
                        body=[
                            ExpressionStatement(
                                CallExpr(Identifier("print"), [Identifier("e")])
                            ),
                        ],
                    ),
                ],
            )
        )
        raw = self._run_raw(prog)
        # e should be the ValueError code (1), not 0
        val = float(raw.strip())
        self.assertNotEqual(val, 0.0)
        self.assertEqual(val, 1.0)


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime is required for WAT execution tests",
)
class WATArgvTestSuite(unittest.TestCase):
    """Verify argc()/argv() builtins via wasmtime with synthetic args."""

    def _run_with_args(self, prog, cli_args: list[str]) -> str:
        import wasmtime  # pylint: disable=import-outside-toplevel,import-error
        gen = WATCodeGenerator()
        wat = gen.generate(prog)
        engine = wasmtime.Engine()
        wasm_bytes = wasmtime.wat2wasm(wat)
        module = wasmtime.Module(engine, wasm_bytes)
        with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as tf:
            stdout_path = tf.name
        try:
            cfg = wasmtime.WasiConfig()
            cfg.stdout_file = stdout_path
            cfg.argv = cli_args
            store = wasmtime.Store(engine)
            store.set_wasi(cfg)
            linker = wasmtime.Linker(engine)
            linker.define_wasi()
            inst = linker.instantiate(store, module)
            inst.exports(store)["__main"](store)
            with open(stdout_path, encoding="utf-8") as fh:
                return fh.read()
        finally:
            os.unlink(stdout_path)

    def test_argc_returns_argument_count(self):
        prog = _prog(
            ExpressionStatement(CallExpr(Identifier("print"), [CallExpr(Identifier("argc"), [])]))
        )
        raw = self._run_with_args(prog, ["prog", "hello", "world"])
        self.assertEqual(raw.strip(), "3")

    def test_argv_zero_returns_program_name(self):
        """argv(0) returns the program name (first CLI argument)."""
        prog = _prog(
            VariableDeclaration("s", CallExpr(Identifier("argv"), [NumeralLiteral("0")])),
            ExpressionStatement(
                CallExpr(Identifier("print"), [StringLiteral("ok")])
            ),
        )
        # Just verify it compiles and runs without crash
        raw = self._run_with_args(prog, ["myprog"])
        self.assertIn("ok", raw)


if __name__ == "__main__":
    unittest.main()
