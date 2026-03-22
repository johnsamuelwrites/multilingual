#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Module structure and ABI tests for the WAT code generator."""
# pylint: disable=duplicate-code

import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    CallExpr,
    ExpressionStatement,
    FunctionDef,
    Identifier,
    NumeralLiteral,
    Parameter,
    Program,
    ReturnStatement,
    StringLiteral,
    VariableDeclaration,
)


def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _gen(*stmts):
    """Generate WAT for the given top-level statements."""
    return WATCodeGenerator().generate(_prog(*stmts))


def _param(name: str) -> Parameter:
    """Create a Parameter with an Identifier name."""
    return Parameter(Identifier(name))


def _point_stream_fn() -> FunctionDef:
    """Create a function decorated with point_stream render mode."""
    return FunctionDef(
        Identifier("draw"),
        [_param("x")],
        [ReturnStatement(NumeralLiteral("0"))],
        decorators=[
            CallExpr(Identifier("render_mode"), [StringLiteral("point_stream")])
        ],
    )


class WATModuleStructureTestSuite(unittest.TestCase):
    """Verify that every WAT output is a well-formed module."""

    def test_empty_program_produces_module(self):
        wat = _gen()
        self.assertTrue(wat.strip().startswith("(module"))
        self.assertTrue(wat.strip().endswith(")"))

    def test_module_contains_wasi_imports(self):
        wat = _gen()
        self.assertIn('(import "wasi_snapshot_preview1" "fd_write"', wat)
        self.assertIn('(import "wasi_snapshot_preview1" "fd_read"', wat)
        self.assertIn('(import "wasi_snapshot_preview1" "args_sizes_get"', wat)
        self.assertIn('(import "wasi_snapshot_preview1" "args_get"', wat)
        self.assertNotIn('(import "env"', wat)

    def test_module_exports_memory(self):
        wat = _gen()
        self.assertIn('(memory (export "memory")', wat)

    def test_top_level_code_goes_into_main(self):
        wat = _gen(VariableDeclaration("x", NumeralLiteral("1")))
        self.assertIn('(func $__main (export "__main")', wat)

    def test_empty_program_has_no_main(self):
        wat = _gen()
        self.assertNotIn("__main", wat)

    def test_data_section_absent_when_no_strings(self):
        wat = _gen(VariableDeclaration("x", NumeralLiteral("5")))
        self.assertNotIn("(data", wat)

    def test_data_section_present_for_string_literal(self):
        wat = _gen(ExpressionStatement(CallExpr(Identifier("print"), [StringLiteral("hi")])))
        self.assertIn("(data", wat)

class WATABIManifestTestSuite(unittest.TestCase):
    """Validate ABI manifest emitted by WATCodeGenerator."""

    def test_manifest_contains_required_host_import_signatures(self):
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        imports = manifest["required_host_imports"]
        self.assertEqual(len(imports), 4)
        names = {i["name"] for i in imports}
        self.assertIn("fd_write", names)
        self.assertIn("fd_read", names)
        self.assertIn("args_sizes_get", names)
        self.assertIn("args_get", names)
        for imp in imports:
            self.assertEqual(imp["module"], "wasi_snapshot_preview1")

    def test_manifest_tracks_export_signatures(self):
        fn = FunctionDef(
            Identifier("compute"),
            [_param("x"), _param("y")],
            [ReturnStatement(NumeralLiteral("1"))],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        exports = manifest["exports"]
        self.assertEqual(len(exports), 1)
        self.assertEqual(exports[0]["name"], "compute")
        self.assertEqual(exports[0]["arg_types"], ["f64", "f64"])
        self.assertEqual(exports[0]["return_type"], "f64")
        self.assertEqual(exports[0]["mode"], "scalar_field")
        self.assertEqual(manifest["tuple_lowering"]["preferred"], "out_params")

    def test_manifest_extracts_render_mode_decorator(self):
        fn = _point_stream_fn()
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        export = manifest["exports"][0]
        self.assertEqual(export["name"], "draw")
        self.assertEqual(export["mode"], "point_stream")
        self.assertIn("stream_output", export)
        self.assertEqual(export["stream_output"]["writer_export"], "draw_write_points")
        self.assertEqual(export["stream_output"]["count_export"], "draw_point_count")

    def test_manifest_includes_main_for_top_level_statements(self):
        manifest = WATCodeGenerator().generate_abi_manifest(
            _prog(VariableDeclaration("x", NumeralLiteral("1")))
        )
        export_names = [entry["name"] for entry in manifest["exports"]]
        self.assertIn("__main", export_names)

    def test_manifest_extracts_buffer_output_kind(self):
        fn = FunctionDef(
            Identifier("draw"),
            [_param("x")],
            [ReturnStatement(NumeralLiteral("0"))],
            decorators=[
                CallExpr(Identifier("render_mode"), [StringLiteral("polyline")]),
                CallExpr(Identifier("buffer_output"), [StringLiteral("segments")]),
            ],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        export = manifest["exports"][0]
        self.assertEqual(export["mode"], "polyline")
        self.assertEqual(export["stream_output"]["kind"], "segments")


class WATStreamBufferExportsTestSuite(unittest.TestCase):
    """Verify stream helper exports are emitted for stream render modes."""

    def test_stream_render_mode_emits_buffer_helpers(self):
        fn = _point_stream_fn()
        wat = WATCodeGenerator().generate(_prog(fn))
        self.assertIn('(export "draw_point_count")', wat)
        self.assertIn('(export "draw_write_points")', wat)
        self.assertIn("(param $ptr i32)", wat)
        self.assertIn("(param $len i32)", wat)
        self.assertIn("f64.store", wat)


class WATFrontendTemplateTestSuite(unittest.TestCase):
    """Verify frontend template generation from ABI manifest."""

    def test_generate_js_host_shim_contains_all_wasi_stubs(self):
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        shim = WATCodeGenerator().generate_js_host_shim(manifest)
        self.assertIn("createWasiImports", shim)
        self.assertIn("fd_write", shim)
        self.assertIn("fd_read", shim)
        self.assertIn("args_sizes_get", shim)
        self.assertIn("args_get", shim)
        self.assertIn("wasi_snapshot_preview1", shim)

    def test_generate_js_host_shim_exports_dom_bridge(self):
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        shim = WATCodeGenerator().generate_js_host_shim(manifest)
        self.assertIn("export function createDomImports", shim)
        self.assertIn("ml_dom_get", shim)
        self.assertIn("ml_dom_set_text", shim)
        self.assertIn("ml_dom_get_value", shim)

    def test_generate_renderer_template_contains_mode_dispatch(self):
        fn = _point_stream_fn()
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("renderByMode", template)
        self.assertIn("point_stream", template)
        self.assertIn("draw_write_points", template)

    def test_renderer_template_exports_call_function_helper(self):
        """callFunction(exports, name, args) must be present in the renderer."""
        fn = FunctionDef(
            Identifier("fibonacci"),
            [Parameter(Identifier("n"))],
            [ReturnStatement(NumeralLiteral("0"))],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("export function callFunction", template)
        self.assertIn("exports[name]", template)

    def test_renderer_template_exposes_bundle_loader(self):
        """Renderer should load canonical build-wasm-bundle output directories."""
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("export async function loadWasmBundle", template)
        self.assertIn("new URL('module.wasm'", template)

    def test_renderer_template_includes_function_signatures(self):
        """Renderer must include a comment listing exported function signatures."""
        fn = FunctionDef(
            Identifier("add"),
            [Parameter(Identifier("x")), Parameter(Identifier("y"))],
            [ReturnStatement(NumeralLiteral("0"))],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("add(arg0: f64, arg1: f64) -> f64", template)

    def test_renderer_call_function_used_in_render_by_mode(self):
        """renderByMode must delegate to callFunction for scalar_field exports."""
        fn = FunctionDef(
            Identifier("compute"),
            [Parameter(Identifier("x"))],
            [ReturnStatement(NumeralLiteral("0"))],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("callFunction(exports, abiName, args)", template)
