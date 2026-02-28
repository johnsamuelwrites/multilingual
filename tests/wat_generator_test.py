#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the WAT (WebAssembly Text) code generator."""
# pylint: disable=duplicate-code

import unittest

from multilingualprogramming.parser.ast_nodes import (
    Program,
    NumeralLiteral,
    StringLiteral,
    BooleanLiteral,
    NoneLiteral,
    Identifier,
    BinaryOp,
    UnaryOp,
    BooleanOp,
    CompareOp,
    CallExpr,
    VariableDeclaration,
    Assignment,
    ExpressionStatement,
    PassStatement,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    GlobalStatement,
    LocalStatement,
    IfStatement,
    WhileLoop,
    ForLoop,
    FunctionDef,
    Parameter,
)
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.core.ir import CoreIRProgram


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _gen(*stmts):
    """Generate WAT for the given top-level statements."""
    return WATCodeGenerator().generate(_prog(*stmts))


def _param(name: str) -> Parameter:
    """Create a Parameter with an Identifier name."""
    return Parameter(Identifier(name))


# ---------------------------------------------------------------------------
# Module structure
# ---------------------------------------------------------------------------

class WATModuleStructureTestSuite(unittest.TestCase):
    """Verify that every WAT output is a well-formed module."""

    def test_empty_program_produces_module(self):
        """An empty program should still produce a (module ...) wrapper."""
        wat = _gen()
        self.assertTrue(wat.strip().startswith("(module"))
        self.assertTrue(wat.strip().endswith(")"))

    def test_module_contains_required_imports(self):
        """All five host imports must appear in every generated module."""
        wat = _gen()
        self.assertIn('(import "env" "print_str"', wat)
        self.assertIn('(import "env" "print_f64"', wat)
        self.assertIn('(import "env" "print_bool"', wat)
        self.assertIn('(import "env" "print_sep"', wat)
        self.assertIn('(import "env" "print_newline"', wat)

    def test_module_exports_memory(self):
        """Linear memory must be declared and exported."""
        wat = _gen()
        self.assertIn('(memory (export "memory") 1)', wat)

    def test_top_level_code_goes_into_main(self):
        """Top-level statements must be inside the __main function."""
        wat = _gen(VariableDeclaration("x", NumeralLiteral("1")))
        self.assertIn('(func $__main (export "__main")', wat)

    def test_empty_program_has_no_main(self):
        """With no statements, no __main should be emitted."""
        wat = _gen()
        self.assertNotIn("__main", wat)

    def test_data_section_absent_when_no_strings(self):
        """Data section must not appear when there are no string literals."""
        wat = _gen(VariableDeclaration("x", NumeralLiteral("5")))
        self.assertNotIn("(data", wat)

    def test_data_section_present_for_string_literal(self):
        """A string literal in a print call must add a data section."""
        wat = _gen(
            ExpressionStatement(
                CallExpr(Identifier("print"), [StringLiteral("hi")])
            )
        )
        self.assertIn("(data", wat)

    def test_generate_accepts_core_ir_program(self):
        """WATCodeGenerator must accept a CoreIRProgram as input."""
        prog = _prog(VariableDeclaration("x", NumeralLiteral("1")))
        core = CoreIRProgram(ast=prog, source_language="en")
        wat = WATCodeGenerator().generate(core)
        self.assertIn("(module", wat)
        self.assertIn("$x", wat)


class WATABIManifestTestSuite(unittest.TestCase):
    """Validate ABI manifest emitted by WATCodeGenerator."""

    def test_manifest_contains_required_host_import_signatures(self):
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        imports = manifest["required_host_imports"]
        names = {entry["name"] for entry in imports}
        self.assertEqual(
            names,
            {"print_str", "print_f64", "print_bool", "print_sep", "print_newline"},
        )

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
        fn = FunctionDef(
            Identifier("draw"),
            [_param("x")],
            [ReturnStatement(NumeralLiteral("0"))],
            decorators=[
                CallExpr(Identifier("render_mode"), [StringLiteral("point_stream")])
            ],
        )
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
        fn = FunctionDef(
            Identifier("draw"),
            [_param("x")],
            [ReturnStatement(NumeralLiteral("0"))],
            decorators=[
                CallExpr(Identifier("render_mode"), [StringLiteral("point_stream")])
            ],
        )
        wat = WATCodeGenerator().generate(_prog(fn))
        self.assertIn('(export "draw_point_count")', wat)
        self.assertIn('(export "draw_write_points")', wat)
        self.assertIn("(param $ptr i32)", wat)
        self.assertIn("(param $len i32)", wat)
        self.assertIn("f64.store", wat)


class WATFrontendTemplateTestSuite(unittest.TestCase):
    """Verify frontend template generation from ABI manifest."""

    def test_generate_js_host_shim_contains_env_imports(self):
        manifest = WATCodeGenerator().generate_abi_manifest(_prog())
        shim = WATCodeGenerator().generate_js_host_shim(manifest)
        self.assertIn("createEnvHost", shim)
        self.assertIn("print_str", shim)
        self.assertIn("print_f64", shim)

    def test_generate_renderer_template_contains_mode_dispatch(self):
        fn = FunctionDef(
            Identifier("draw"),
            [_param("x")],
            [ReturnStatement(NumeralLiteral("0"))],
            decorators=[
                CallExpr(Identifier("render_mode"), [StringLiteral("point_stream")])
            ],
        )
        manifest = WATCodeGenerator().generate_abi_manifest(_prog(fn))
        template = WATCodeGenerator().generate_renderer_template(manifest)
        self.assertIn("renderByMode", template)
        self.assertIn("point_stream", template)
        self.assertIn("draw_write_points", template)


# ---------------------------------------------------------------------------
# Expression generation
# ---------------------------------------------------------------------------

class WATExpressionTestSuite(unittest.TestCase):
    """Verify that individual expressions produce correct WAT instructions."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, expr):
        """Generate WAT for a single expression in a variable declaration."""
        return self.gen.generate(_prog(VariableDeclaration("_r", expr)))

    def test_integer_numeral(self):
        wat = self._wat(NumeralLiteral("42"))
        self.assertIn("f64.const 42.0", wat)

    def test_float_numeral(self):
        wat = self._wat(NumeralLiteral("3.14"))
        self.assertIn("f64.const 3.14", wat)

    def test_devanagari_numeral(self):
        """Hindi numerals (Devanagari) must be converted to f64."""
        wat = self._wat(NumeralLiteral("१०"))
        self.assertIn("f64.const 10.0", wat)

    def test_arabic_indic_numeral(self):
        """Arabic-Indic numerals must be converted to f64."""
        wat = self._wat(NumeralLiteral("٧"))
        self.assertIn("f64.const 7.0", wat)

    def test_boolean_true(self):
        wat = self._wat(BooleanLiteral(True))
        self.assertIn("i32.const 1", wat)
        self.assertIn("f64.convert_i32_s", wat)

    def test_boolean_false(self):
        wat = self._wat(BooleanLiteral(False))
        self.assertIn("i32.const 0", wat)
        self.assertIn("f64.convert_i32_s", wat)

    def test_none_literal(self):
        wat = self._wat(NoneLiteral())
        self.assertIn("f64.const 0", wat)

    def test_identifier(self):
        wat = self.gen.generate(_prog(
            VariableDeclaration("a", NumeralLiteral("1")),
            VariableDeclaration("b", Identifier("a")),
        ))
        self.assertIn("local.get $a", wat)

    def test_binary_add(self):
        wat = self._wat(BinaryOp(NumeralLiteral("3"), "+", NumeralLiteral("4")))
        self.assertIn("f64.add", wat)

    def test_binary_sub(self):
        wat = self._wat(BinaryOp(NumeralLiteral("9"), "-", NumeralLiteral("5")))
        self.assertIn("f64.sub", wat)

    def test_binary_mul(self):
        wat = self._wat(BinaryOp(NumeralLiteral("2"), "*", NumeralLiteral("6")))
        self.assertIn("f64.mul", wat)

    def test_binary_div(self):
        wat = self._wat(BinaryOp(NumeralLiteral("8"), "/", NumeralLiteral("2")))
        self.assertIn("f64.div", wat)

    def test_floor_division(self):
        """Floor division emits f64.div followed by f64.floor."""
        wat = self._wat(BinaryOp(NumeralLiteral("7"), "//", NumeralLiteral("2")))
        self.assertIn("f64.div", wat)
        self.assertIn("f64.floor", wat)

    def test_modulo(self):
        """Modulo uses the floor-based pattern."""
        wat = self._wat(BinaryOp(NumeralLiteral("7"), "%", NumeralLiteral("3")))
        self.assertIn("f64.floor", wat)
        self.assertIn("f64.sub", wat)

    def test_unary_neg(self):
        wat = self._wat(UnaryOp("-", NumeralLiteral("5")))
        self.assertIn("f64.neg", wat)

    def test_unary_plus(self):
        """Unary + is identity — just emits the operand."""
        wat = self._wat(UnaryOp("+", NumeralLiteral("5")))
        self.assertIn("f64.const 5.0", wat)
        self.assertNotIn("f64.neg", wat)

    def test_unary_not(self):
        wat = self._wat(UnaryOp("not", BooleanLiteral(True)))
        self.assertIn("i32.eqz", wat)

    def test_compare_eq(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [("==", NumeralLiteral("0"))])
        )
        self.assertIn("f64.eq", wat)

    def test_compare_ne(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [("!=", NumeralLiteral("0"))])
        )
        self.assertIn("f64.ne", wat)

    def test_compare_lt(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [("<", NumeralLiteral("10"))])
        )
        self.assertIn("f64.lt", wat)

    def test_compare_le(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [("<=", NumeralLiteral("10"))])
        )
        self.assertIn("f64.le", wat)

    def test_compare_gt(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [(">", NumeralLiteral("0"))])
        )
        self.assertIn("f64.gt", wat)

    def test_compare_ge(self):
        wat = self._wat(
            CompareOp(Identifier("x"), [(">=", NumeralLiteral("0"))])
        )
        self.assertIn("f64.ge", wat)

    def test_compare_result_converted_to_f64(self):
        """CompareOp in an expression context must be converted from i32 to f64."""
        wat = self._wat(
            CompareOp(Identifier("x"), [("<", NumeralLiteral("5"))])
        )
        self.assertIn("f64.convert_i32_s", wat)

    def test_boolean_op_and(self):
        wat = self._wat(
            BooleanOp("and", [BooleanLiteral(True), BooleanLiteral(False)])
        )
        self.assertIn("i32.and", wat)

    def test_boolean_op_or(self):
        wat = self._wat(
            BooleanOp("or", [BooleanLiteral(True), BooleanLiteral(False)])
        )
        self.assertIn("i32.or", wat)

    def test_call_user_function(self):
        """Calling a user function emits call $fname — function must be defined in the module."""
        wat = self.gen.generate(_prog(
            FunctionDef("double", [Parameter("x")], [
                ReturnStatement(BinaryOp(Identifier("x"), "*", NumeralLiteral("2")))
            ]),
            ExpressionStatement(
                CallExpr(Identifier("double"), [NumeralLiteral("3")])
            )
        ))
        self.assertIn("call $double", wat)


# ---------------------------------------------------------------------------
# Statement generation
# ---------------------------------------------------------------------------

class WATStatementTestSuite(unittest.TestCase):
    """Verify individual statements produce correct WAT."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, *stmts):
        return self.gen.generate(_prog(*stmts))

    def test_variable_declaration_local(self):
        """A VariableDeclaration must declare a local and store the value."""
        wat = self._wat(VariableDeclaration("x", NumeralLiteral("10")))
        self.assertIn("(local $x f64)", wat)
        self.assertIn("local.set $x", wat)

    def test_variable_declaration_comment(self):
        """A VariableDeclaration should emit a comment."""
        wat = self._wat(VariableDeclaration("y", NumeralLiteral("5")))
        self.assertIn(";; let y = ...", wat)

    def test_simple_assignment(self):
        """Plain assignment (=) must emit local.set."""
        wat = self._wat(
            VariableDeclaration("n", NumeralLiteral("0")),
            Assignment(Identifier("n"), NumeralLiteral("7")),
        )
        self.assertIn("local.set $n", wat)

    def test_compound_assignment_add(self):
        """Augmented += must emit local.get, value, f64.add, local.set."""
        wat = self._wat(
            VariableDeclaration("s", NumeralLiteral("0")),
            Assignment(Identifier("s"), NumeralLiteral("1"), op="+="),
        )
        self.assertIn("local.get $s", wat)
        self.assertIn("f64.add", wat)
        self.assertIn("local.set $s", wat)

    def test_compound_assignment_sub(self):
        wat = self._wat(
            VariableDeclaration("v", NumeralLiteral("10")),
            Assignment(Identifier("v"), NumeralLiteral("3"), op="-="),
        )
        self.assertIn("f64.sub", wat)

    def test_compound_assignment_mul(self):
        wat = self._wat(
            VariableDeclaration("v", NumeralLiteral("2")),
            Assignment(Identifier("v"), NumeralLiteral("5"), op="*="),
        )
        self.assertIn("f64.mul", wat)

    def test_compound_assignment_div(self):
        wat = self._wat(
            VariableDeclaration("v", NumeralLiteral("10")),
            Assignment(Identifier("v"), NumeralLiteral("2"), op="/="),
        )
        self.assertIn("f64.div", wat)

    def test_pass_statement(self):
        """PassStatement must emit nop."""
        wat = self._wat(PassStatement())
        self.assertIn("nop", wat)

    def test_return_with_value(self):
        """ReturnStatement inside a function must emit the value then return."""
        prog = _prog(
            FunctionDef(
                "one",
                [],
                [ReturnStatement(NumeralLiteral("1"))]
            )
        )
        wat = self.gen.generate(prog)
        self.assertIn("f64.const 1.0", wat)
        self.assertIn("return", wat)

    def test_return_bare(self):
        """ReturnStatement with no value emits f64.const 0 then return."""
        prog = _prog(
            FunctionDef("noop", [], [ReturnStatement()])
        )
        wat = self.gen.generate(prog)
        self.assertIn("f64.const 0", wat)
        self.assertIn("return", wat)

    def test_global_statement_emits_comment(self):
        """GlobalStatement emits a nop comment (not supported in WAT)."""
        wat = self._wat(GlobalStatement(["g"]))
        self.assertIn("GlobalStatement", wat)

    def test_local_statement_emits_comment(self):
        """LocalStatement emits a nop comment."""
        wat = self._wat(LocalStatement(["lv"]))
        self.assertIn("LocalStatement", wat)

    def test_expression_statement_non_print(self):
        """An expression statement calling a WAT function must be evaluated and dropped."""
        # compute() must be defined in the same module for WAT call emission
        wat = self.gen.generate(_prog(
            FunctionDef("compute", [Parameter("n")], [
                ReturnStatement(Identifier("n"))
            ]),
            ExpressionStatement(
                CallExpr(Identifier("compute"), [NumeralLiteral("1")])
            )
        ))
        self.assertIn("call $compute", wat)
        self.assertIn("drop", wat)

    def test_break_emits_branch(self):
        """break inside a while loop must emit br $while_blk_N."""
        wat = self._wat(
            WhileLoop(
                BooleanLiteral(True),
                [BreakStatement()]
            )
        )
        self.assertIn("br $while_blk_", wat)

    def test_continue_emits_branch(self):
        """continue inside a while loop must emit br $while_lp_N."""
        wat = self._wat(
            WhileLoop(
                BooleanLiteral(True),
                [ContinueStatement()]
            )
        )
        self.assertIn("br $while_lp_", wat)

    def test_break_outside_loop_emits_comment(self):
        """break outside any loop must emit a comment, not crash."""
        wat = self._wat(BreakStatement())
        self.assertIn(";; break (no enclosing loop)", wat)

    def test_continue_outside_loop_emits_comment(self):
        """continue outside any loop must emit a comment, not crash."""
        wat = self._wat(ContinueStatement())
        self.assertIn(";; continue (no enclosing loop)", wat)


# ---------------------------------------------------------------------------
# Print call generation
# ---------------------------------------------------------------------------

class WATPrintTestSuite(unittest.TestCase):
    """Verify that print calls produce the correct WAT import calls."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, *stmts):
        return self.gen.generate(_prog(*stmts))

    def _print(self, *args):
        return ExpressionStatement(
            CallExpr(Identifier("print"), list(args))
        )

    def test_print_string_calls_print_str(self):
        wat = self._wat(self._print(StringLiteral("hello")))
        self.assertIn("call $print_str", wat)
        self.assertIn("call $print_newline", wat)

    def test_print_number_calls_print_f64(self):
        wat = self._wat(self._print(NumeralLiteral("42")))
        self.assertIn("call $print_f64", wat)
        self.assertIn("call $print_newline", wat)

    def test_print_bool_calls_print_bool(self):
        wat = self._wat(self._print(BooleanLiteral(True)))
        self.assertIn("call $print_bool", wat)

    def test_print_multiple_args_inserts_separator(self):
        wat = self._wat(
            self._print(StringLiteral("a"), NumeralLiteral("1"))
        )
        self.assertIn("call $print_sep", wat)

    def test_print_single_arg_no_separator(self):
        wat = self._wat(self._print(NumeralLiteral("5")))
        self.assertNotIn("call $print_sep", wat)

    def test_string_stored_in_data_section(self):
        """The string bytes must appear in the data section."""
        wat = self._wat(self._print(StringLiteral("ok")))
        self.assertIn("(data", wat)
        # "ok" encodes as 6f 6b
        self.assertIn("\\6f\\6b", wat)

    def test_string_ptr_and_len_emitted(self):
        """i32.const for ptr and len must be emitted for print_str."""
        wat = self._wat(self._print(StringLiteral("hi")))
        self.assertIn("i32.const 0   ;; str ptr", wat)
        self.assertIn("i32.const 2   ;; str len", wat)

    def test_string_deduplication(self):
        """The same string literal should not be interned twice."""
        wat = self._wat(
            self._print(StringLiteral("x")),
            self._print(StringLiteral("x")),
        )
        # Data section should contain "x" (1 byte) only once → total data = 1 byte
        # Both print calls should reference offset 0
        self.assertEqual(wat.count("i32.const 0   ;; str ptr"), 2)

    def test_print_emits_comment(self):
        wat = self._wat(self._print(NumeralLiteral("1")))
        self.assertIn(";; print(...)", wat)

    # Localised print variants
    def test_french_afficher(self):
        wat = self._wat(
            ExpressionStatement(
                CallExpr(Identifier("afficher"), [StringLiteral("bonjour")])
            )
        )
        self.assertIn("call $print_str", wat)

    def test_german_ausgeben(self):
        wat = self._wat(
            ExpressionStatement(
                CallExpr(Identifier("ausgeben"), [NumeralLiteral("1")])
            )
        )
        self.assertIn("call $print_f64", wat)

    def test_japanese_hyoji(self):
        wat = self._wat(
            ExpressionStatement(
                CallExpr(Identifier("表示"), [NumeralLiteral("7")])
            )
        )
        self.assertIn("call $print_f64", wat)

    def test_hindi_chhapo(self):
        wat = self._wat(
            ExpressionStatement(
                CallExpr(Identifier("छापो"), [StringLiteral("नमस्ते")])
            )
        )
        self.assertIn("call $print_str", wat)


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------

class WATControlFlowTestSuite(unittest.TestCase):
    """Verify if / while / for control flow generation."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, *stmts):
        return self.gen.generate(_prog(*stmts))

    # --- if ---

    def test_if_only(self):
        """Simple if with no else."""
        wat = self._wat(
            IfStatement(
                CompareOp(Identifier("x"), [(">", NumeralLiteral("0"))]),
                [PassStatement()]
            )
        )
        self.assertIn(";; if ...", wat)
        self.assertIn("if", wat)
        self.assertIn("end  ;; if", wat)

    def test_if_else(self):
        """if / else should emit an else branch."""
        wat = self._wat(
            IfStatement(
                BooleanLiteral(True),
                [PassStatement()],
                else_body=[PassStatement()]
            )
        )
        self.assertIn("if", wat)
        self.assertIn("else", wat)
        self.assertIn("end  ;; if", wat)

    def test_if_elif(self):
        """if / elif should emit nested if inside else."""
        wat = self._wat(
            IfStatement(
                CompareOp(Identifier("x"), [("==", NumeralLiteral("1"))]),
                [PassStatement()],
                elif_clauses=[
                    (CompareOp(Identifier("x"), [("==", NumeralLiteral("2"))]),
                     [PassStatement()])
                ]
            )
        )
        self.assertIn(";; elif ...", wat)

    def test_if_elif_else(self):
        """if / elif / else should emit full chained structure."""
        wat = self._wat(
            IfStatement(
                CompareOp(Identifier("x"), [("==", NumeralLiteral("1"))]),
                [PassStatement()],
                elif_clauses=[
                    (CompareOp(Identifier("x"), [("==", NumeralLiteral("2"))]),
                     [PassStatement()])
                ],
                else_body=[PassStatement()]
            )
        )
        self.assertIn(";; elif ...", wat)
        self.assertIn("else", wat)

    # --- while ---

    def test_while_loop_structure(self):
        """While loop must emit block + loop with exit check."""
        wat = self._wat(
            WhileLoop(
                CompareOp(Identifier("i"), [("<", NumeralLiteral("10"))]),
                [PassStatement()]
            )
        )
        self.assertIn(";; while ...", wat)
        self.assertIn("block $while_blk_", wat)
        self.assertIn("loop $while_lp_", wat)
        self.assertIn("i32.eqz", wat)
        self.assertIn("br_if $while_blk_", wat)
        self.assertIn("br $while_lp_", wat)
        self.assertIn("end  ;; loop", wat)
        self.assertIn("end  ;; block (while)", wat)

    def test_nested_while_unique_labels(self):
        """Nested while loops must use distinct labels."""
        wat = self._wat(
            WhileLoop(
                BooleanLiteral(True),
                [WhileLoop(BooleanLiteral(True), [BreakStatement()])]
            )
        )
        self.assertIn("$while_blk_1", wat)
        self.assertIn("$while_blk_2", wat)
        self.assertIn("$while_lp_1", wat)
        self.assertIn("$while_lp_2", wat)

    # --- for ---

    def test_for_range_one_arg(self):
        """for i in range(5) must iterate from 0 to 5."""
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("range"), [NumeralLiteral("5")]),
                [PassStatement()]
            )
        )
        self.assertIn(";; for i in range(...)", wat)
        self.assertIn("block $for_blk_", wat)
        self.assertIn("loop $for_lp_", wat)
        self.assertIn("f64.ge", wat)          # loop exit condition
        self.assertIn("br_if $for_blk_", wat)
        self.assertIn("br $for_lp_", wat)
        # Initialise iter var from 0
        self.assertIn("f64.const 0.0", wat)
        self.assertIn("local.set $i", wat)

    def test_for_range_two_args(self):
        """for i in range(2, 8) must use the start value."""
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(
                    Identifier("range"),
                    [NumeralLiteral("2"), NumeralLiteral("8")]
                ),
                [PassStatement()]
            )
        )
        self.assertIn("f64.const 2.0", wat)   # start
        self.assertIn("f64.const 8.0", wat)   # end

    def test_for_loop_increments_by_one(self):
        """The loop variable must be incremented by 1 each iteration."""
        wat = self._wat(
            ForLoop(
                Identifier("k"),
                CallExpr(Identifier("range"), [NumeralLiteral("3")]),
                [PassStatement()]
            )
        )
        self.assertIn("f64.const 1", wat)
        self.assertIn("f64.add", wat)
        self.assertIn("local.set $k", wat)

    def test_for_loop_end_stored_in_local(self):
        """Range end must be stored in a __reN local to avoid re-evaluation."""
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("range"), [NumeralLiteral("10")]),
                [PassStatement()]
            )
        )
        self.assertIn("local.set $__re", wat)
        self.assertIn("local.get $__re", wat)

    def test_for_non_range_emits_comment(self):
        """for over non-range iterables emits an unsupported comment."""
        wat = self._wat(
            ForLoop(
                Identifier("item"),
                Identifier("my_list"),
                [PassStatement()]
            )
        )
        self.assertIn("not supported in WAT", wat)

    # Localised range() variants
    def test_french_intervalle(self):
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("intervalle"), [NumeralLiteral("5")]),
                [PassStatement()]
            )
        )
        self.assertIn(";; for i in range(...)", wat)

    def test_german_bereich(self):
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("bereich"), [NumeralLiteral("3")]),
                [PassStatement()]
            )
        )
        self.assertIn(";; for i in range(...)", wat)

    def test_japanese_hani(self):
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("範囲"), [NumeralLiteral("4")]),
                [PassStatement()]
            )
        )
        self.assertIn(";; for i in range(...)", wat)

    def test_arabic_mada(self):
        wat = self._wat(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("مدى"), [NumeralLiteral("6")]),
                [PassStatement()]
            )
        )
        self.assertIn(";; for i in range(...)", wat)


# ---------------------------------------------------------------------------
# Function definitions
# ---------------------------------------------------------------------------

class WATFunctionTestSuite(unittest.TestCase):
    """Verify function definition code generation."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, *stmts):
        return self.gen.generate(_prog(*stmts))

    def test_function_is_exported(self):
        """Every function must be exported with its own name."""
        wat = self._wat(FunctionDef("greet", [], [PassStatement()]))
        self.assertIn('(func $greet (export "greet")', wat)

    def test_function_with_params(self):
        """Parameters must appear as (param $name f64) in the WAT."""
        wat = self._wat(
            FunctionDef(
                "add",
                [_param("a"), _param("b")],
                [ReturnStatement(
                    BinaryOp(Identifier("a"), "+", Identifier("b"))
                )]
            )
        )
        self.assertIn("(param $a f64)", wat)
        self.assertIn("(param $b f64)", wat)

    def test_function_result_type(self):
        """Functions must declare (result f64)."""
        wat = self._wat(FunctionDef("f", [], [PassStatement()]))
        self.assertIn("(result f64)", wat)

    def test_function_implicit_return(self):
        """Functions without an explicit return must end with f64.const 0."""
        wat = self._wat(FunctionDef("noop", [], [PassStatement()]))
        self.assertIn("f64.const 0  ;; implicit return", wat)

    def test_function_local_var_declared(self):
        """Locals used inside a function body must appear as (local $name f64)."""
        wat = self._wat(
            FunctionDef(
                "compute",
                [],
                [VariableDeclaration("tmp", NumeralLiteral("7"))]
            )
        )
        self.assertIn("(local $tmp f64)", wat)

    def test_param_not_redeclared_as_local(self):
        """Parameters must not appear in the locals list."""
        wat = self._wat(
            FunctionDef(
                "square",
                [_param("x")],
                [ReturnStatement(
                    BinaryOp(Identifier("x"), "*", Identifier("x"))
                )]
            )
        )
        self.assertIn("(param $x f64)", wat)
        # The param should NOT also appear as a local
        self.assertNotIn("(local $x f64)", wat)

    def test_multiple_functions(self):
        """Multiple top-level functions must all be included."""
        wat = self._wat(
            FunctionDef("alpha", [], [PassStatement()]),
            FunctionDef("beta", [], [PassStatement()]),
        )
        self.assertIn("$alpha", wat)
        self.assertIn("$beta", wat)

    def test_function_and_main_coexist(self):
        """Functions and top-level code must coexist in the same module."""
        wat = self._wat(
            FunctionDef("helper", [], [PassStatement()]),
            VariableDeclaration("x", NumeralLiteral("1")),
        )
        self.assertIn("$helper", wat)
        self.assertIn("$__main", wat)

    def test_function_call_from_main(self):
        """A call to a user function in top-level code must emit call $name."""
        wat = self._wat(
            FunctionDef("triple", [_param("n")],
                        [ReturnStatement(
                            BinaryOp(NumeralLiteral("3"), "*", Identifier("n"))
                        )]),
            ExpressionStatement(
                CallExpr(Identifier("triple"), [NumeralLiteral("5")])
            )
        )
        self.assertIn("call $triple", wat)


# ---------------------------------------------------------------------------
# String interning
# ---------------------------------------------------------------------------

class WATStringInternTestSuite(unittest.TestCase):
    """Verify the WAT linear memory string interning mechanism."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _print_stmt(self, text):
        return ExpressionStatement(
            CallExpr(Identifier("print"), [StringLiteral(text)])
        )

    def test_ascii_string_hex_encoded(self):
        """ASCII strings must be hex-encoded in the data section."""
        wat = self.gen.generate(_prog(self._print_stmt("AB")))
        # 'A' = 0x41, 'B' = 0x42
        self.assertIn("\\41\\42", wat)

    def test_utf8_multibyte_string(self):
        """Multi-byte UTF-8 strings must be hex-encoded correctly."""
        wat = self.gen.generate(_prog(self._print_stmt("é")))
        # 'é' encodes as 0xc3 0xa9
        self.assertIn("\\c3\\a9", wat)

    def test_second_string_offset_follows_first(self):
        """Consecutive strings must be laid out sequentially in memory."""
        wat = self.gen.generate(_prog(
            self._print_stmt("hi"),     # offset 0, len 2
            self._print_stmt("world"),  # offset 2, len 5
        ))
        # First string: ptr=0, len=2
        self.assertIn("i32.const 0   ;; str ptr", wat)
        self.assertIn("i32.const 2   ;; str len", wat)
        # Second string: ptr=2, len=5
        self.assertIn("i32.const 2   ;; str ptr", wat)
        self.assertIn("i32.const 5   ;; str len", wat)

    def test_same_string_reuses_offset(self):
        """Identical string literals must share the same data segment."""
        wat = self.gen.generate(_prog(
            self._print_stmt("dup"),
            self._print_stmt("dup"),
        ))
        # Both calls reference offset 0
        self.assertEqual(wat.count("i32.const 0   ;; str ptr"), 2)

    def test_empty_string_has_zero_length(self):
        """Empty string literal must use length 0."""
        wat = self.gen.generate(_prog(self._print_stmt("")))
        self.assertIn("i32.const 0   ;; str len", wat)

    def test_generator_state_reset_between_calls(self):
        """Calling generate() twice must reset the data section."""
        gen = WATCodeGenerator()
        gen.generate(_prog(self._print_stmt("first")))
        wat2 = gen.generate(_prog(self._print_stmt("second")))
        # After reset, "second" should start at offset 0
        self.assertIn("i32.const 0   ;; str ptr", wat2)


# ---------------------------------------------------------------------------
# Multilingual numerals
# ---------------------------------------------------------------------------

class WATMultilingualNumeralTestSuite(unittest.TestCase):
    """Verify that Unicode script numerals are correctly converted to f64."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, numeral_str):
        return self.gen.generate(
            _prog(VariableDeclaration("r", NumeralLiteral(numeral_str)))
        )

    def test_bengali_numeral(self):
        """Bengali numerals ৪৫ = 45."""
        wat = self._wat("৪৫")
        self.assertIn("f64.const 45.0", wat)

    def test_tamil_numeral(self):
        """Tamil numerals ௧௨ = 12."""
        wat = self._wat("௧௨")
        self.assertIn("f64.const 12.0", wat)

    def test_chinese_numeral_unsupported_falls_back(self):
        """Chinese ideograph numerals (三, etc.) are not Unicode decimal digits;
        MPNumeral does not support them, so _to_f64 must fall back to 0.0."""
        wat = self._wat("三")
        self.assertIn("f64.const 0.0", wat)

    def test_roman_numeral(self):
        """Roman numeral X = 10."""
        wat = self._wat("X")
        self.assertIn("f64.const 10.0", wat)

    def test_invalid_numeral_defaults_to_zero(self):
        """An unrecognised numeral string must safely fall back to 0.0."""
        wat = self._wat("???")
        self.assertIn("f64.const 0.0", wat)


# ---------------------------------------------------------------------------
# Integration: complete programs
# ---------------------------------------------------------------------------

class WATIntegrationTestSuite(unittest.TestCase):
    """End-to-end WAT generation for realistic mini-programs."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def test_sum_loop(self):
        """
        let s = 0
        for i in range(5):
            s += i
        print(s)
        """
        prog = _prog(
            VariableDeclaration("s", NumeralLiteral("0")),
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("range"), [NumeralLiteral("5")]),
                [Assignment(Identifier("s"), Identifier("i"), op="+=")]
            ),
            ExpressionStatement(
                CallExpr(Identifier("print"), [Identifier("s")])
            )
        )
        wat = self.gen.generate(prog)
        # Structural sanity
        self.assertIn("(module", wat)
        self.assertIn("$__main", wat)
        self.assertIn("$s", wat)
        self.assertIn("$i", wat)
        self.assertIn("call $print_f64", wat)

    def test_factorial_function(self):
        """
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        """
        prog = _prog(
            FunctionDef(
                "factorial",
                [_param("n")],
                [
                    IfStatement(
                        CompareOp(Identifier("n"), [("<=", NumeralLiteral("1"))]),
                        [ReturnStatement(NumeralLiteral("1"))]
                    ),
                    ReturnStatement(
                        BinaryOp(
                            Identifier("n"), "*",
                            CallExpr(
                                Identifier("factorial"),
                                [BinaryOp(Identifier("n"), "-", NumeralLiteral("1"))]
                            )
                        )
                    )
                ]
            )
        )
        wat = self.gen.generate(prog)
        self.assertIn('(func $factorial (export "factorial")', wat)
        self.assertIn("(param $n f64)", wat)
        self.assertIn("f64.le", wat)
        self.assertIn("call $factorial", wat)
        self.assertIn("f64.mul", wat)

    def test_french_for_loop_program(self):
        """
        French: pour i dans intervalle(3): afficher(i)
        """
        prog = _prog(
            ForLoop(
                Identifier("i"),
                CallExpr(Identifier("intervalle"), [NumeralLiteral("3")]),
                [ExpressionStatement(
                    CallExpr(Identifier("afficher"), [Identifier("i")])
                )]
            )
        )
        wat = self.gen.generate(prog)
        self.assertIn(";; for i in range(...)", wat)
        self.assertIn("call $print_f64", wat)

    def test_while_with_break(self):
        """
        let i = 0
        while i < 10:
            if i == 5:
                break
            i += 1
        """
        prog = _prog(
            VariableDeclaration("i", NumeralLiteral("0")),
            WhileLoop(
                CompareOp(Identifier("i"), [("<", NumeralLiteral("10"))]),
                [
                    IfStatement(
                        CompareOp(Identifier("i"), [("==", NumeralLiteral("5"))]),
                        [BreakStatement()]
                    ),
                    Assignment(Identifier("i"), NumeralLiteral("1"), op="+=")
                ]
            )
        )
        wat = self.gen.generate(prog)
        self.assertIn("block $while_blk_", wat)
        self.assertIn("br $while_blk_", wat)   # break branch
        self.assertIn("f64.eq", wat)

    def test_print_multiple_types(self):
        """print(42, True, "hello") — three different arg types."""
        prog = _prog(
            ExpressionStatement(
                CallExpr(Identifier("print"), [
                    NumeralLiteral("42"),
                    BooleanLiteral(True),
                    StringLiteral("hello"),
                ])
            )
        )
        wat = self.gen.generate(prog)
        self.assertIn("call $print_f64", wat)
        self.assertIn("call $print_bool", wat)
        self.assertIn("call $print_str", wat)
        # Two separators between three args
        self.assertEqual(wat.count("call $print_sep"), 2)


if __name__ == "__main__":
    unittest.main()
