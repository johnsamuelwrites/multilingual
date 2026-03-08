#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""WASM execution tests for the WAT generator's class lowering."""
# pylint: disable=duplicate-code

import importlib.util
import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    Assignment,
    AttributeAccess,
    BinaryOp,
    CallExpr,
    ClassDef,
    ExpressionStatement,
    FunctionDef,
    Identifier,
    NumeralLiteral,
    Parameter,
    Program,
    ReturnStatement,
    VariableDeclaration,
)


def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _param(name: str) -> Parameter:
    """Create a Parameter with an Identifier name."""
    return Parameter(Identifier(name))


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
        store = wasmtime.Store(engine)
        printed = []
        linker = wasmtime.Linker(engine)

        def _noop():
            return None

        def _noop_print_str(_ptr, _length):
            return None

        def _capture_f64(value):
            printed.append(value)

        def _capture_bool(value):
            printed.append(bool(value))

        linker.define(
            store,
            "env",
            "print_str",
            wasmtime.Func(
                store,
                wasmtime.FuncType([wasmtime.ValType.i32(), wasmtime.ValType.i32()], []),
                _noop_print_str,
            ),
        )
        linker.define(
            store,
            "env",
            "print_f64",
            wasmtime.Func(
                store,
                wasmtime.FuncType([wasmtime.ValType.f64()], []),
                _capture_f64,
            ),
        )
        linker.define(
            store,
            "env",
            "print_bool",
            wasmtime.Func(
                store,
                wasmtime.FuncType([wasmtime.ValType.i32()], []),
                _capture_bool,
            ),
        )
        linker.define(
            store,
            "env",
            "print_sep",
            wasmtime.Func(store, wasmtime.FuncType([], []), _noop),
        )
        linker.define(
            store,
            "env",
            "print_newline",
            wasmtime.Func(store, wasmtime.FuncType([], []), _noop),
        )
        linker.define(
            store,
            "env",
            "pow_f64",
            wasmtime.Func(
                store,
                wasmtime.FuncType(
                    [wasmtime.ValType.f64(), wasmtime.ValType.f64()],
                    [wasmtime.ValType.f64()],
                ),
                lambda base, exp: base ** exp,
            ),
        )
        instance = linker.instantiate(store, module)
        instance.exports(store)["__main"](store)
        return printed

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


if __name__ == "__main__":
    unittest.main()
