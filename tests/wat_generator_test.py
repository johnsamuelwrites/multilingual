#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the WAT (WebAssembly Text) code generator."""
# pylint: disable=duplicate-code, too-many-lines
# pylint: disable=mixed-line-endings

import unittest
import importlib.util

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
    AttributeAccess,
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
    ClassDef,
    Parameter,
    MatchStatement,
    CaseClause,
    ListLiteral,
    TupleLiteral,
    IndexAccess,
    AwaitExpr,
    ListComprehension,
    LambdaExpr,
    SliceExpr,
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
            {"print_str", "print_f64", "print_bool", "print_sep", "print_newline", "pow_f64"},
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

    def test_power(self):
        """Power operator lowers to call $pow_f64 host import."""
        wat = self._wat(BinaryOp(NumeralLiteral("2"), "**", NumeralLiteral("8")))
        self.assertIn("call $pow_f64", wat)
        self.assertNotIn("not natively supported", wat)

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

    def test_class_methods_lowered_to_wat_functions(self):
        """Top-level class methods should be lowered to standalone WAT functions."""
        wat = self._wat(
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
            )
        )
        self.assertIn('(func $Counter____init__ (export "Counter____init__")', wat)
        self.assertNotIn("unsupported statement: ClassDef", wat)

    def test_class_constructor_call_lowers_to_init_function(self):
        """ClassName(...) should lower to the class __init__ WAT function call."""
        wat = self._wat(
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
            ExpressionStatement(CallExpr(Identifier("Counter"), [NumeralLiteral("3")])),
        )
        self.assertIn("f64.const 0  ;; implicit self", wat)
        self.assertIn("call $Counter____init__", wat)

    def test_class_attribute_call_lowers_to_mangled_method(self):
        """Class.method(...) should lower to the mangled method function call."""
        wat = self._wat(
            ClassDef(
                "Math",
                [],
                [
                    FunctionDef(
                        "double",
                        [_param("x")],
                        [ReturnStatement(BinaryOp(Identifier("x"), "*", NumeralLiteral("2")))]
                    ),
                ],
            ),
            ExpressionStatement(
                CallExpr(
                    AttributeAccess(Identifier("Math"), "double"),
                    [NumeralLiteral("4")],
                )
            ),
        )
        self.assertIn("call $Math__double", wat)

    def test_instance_method_call_lowers_via_constructor_assignment(self):
        """obj = Class(...); obj.method(...) should lower using tracked class type."""
        wat = self._wat(
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
                CallExpr(AttributeAccess(Identifier("c"), "inc"), [NumeralLiteral("3")])
            ),
        )
        self.assertIn("call $Counter__inc", wat)

    def test_instance_method_call_stops_lowering_after_reassignment(self):
        """Reassigning obj to a non-instance value should clear class-method lowering."""
        wat = self._wat(
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
            Assignment(Identifier("c"), NumeralLiteral("0")),
            ExpressionStatement(
                CallExpr(AttributeAccess(Identifier("c"), "inc"), [NumeralLiteral("3")])
            ),
        )
        self.assertIn("unsupported call: c.inc(...)", wat)


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


class WATOopObjectModelTestSuite(unittest.TestCase):
    """Verify WAT OOP object model: field layout, f64.store/load, heap alloc."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _wat(self, *stmts):
        return self.gen.generate(_prog(*stmts))

    def _counter_class(self, extra_methods=None):
        """Counter class with self.value = start in __init__."""
        methods = [
            FunctionDef(
                "__init__",
                [_param("self"), _param("start")],
                [Assignment(
                    AttributeAccess(Identifier("self"), "value"),
                    Identifier("start"),
                )],
            ),
        ]
        if extra_methods:
            methods.extend(extra_methods)
        return ClassDef("Counter", [], methods)

    def test_self_attr_store_emits_f64_store(self):
        """self.value = start inside __init__ must emit f64.store."""
        wat = self._wat(self._counter_class())
        self.assertIn("f64.store", wat)

    def test_self_attr_load_emits_f64_load(self):
        """return self.value in a getter must emit f64.load."""
        getter = FunctionDef(
            "get",
            [_param("self")],
            [ReturnStatement(AttributeAccess(Identifier("self"), "value"))],
        )
        wat = self._wat(self._counter_class(extra_methods=[getter]))
        self.assertIn("f64.load", wat)

    def test_stateful_constructor_emits_heap_alloc(self):
        """Counter(10) for a stateful class must emit global.get $__heap_ptr."""
        wat = self._wat(
            self._counter_class(),
            VariableDeclaration(
                "c",
                CallExpr(Identifier("Counter"), [NumeralLiteral("10")]),
            ),
        )
        self.assertIn("global.get $__heap_ptr", wat)

    def test_stateless_class_keeps_old_behavior(self):
        """A class with no self.attr assignments keeps f64.const 0 as self."""
        stateless = ClassDef(
            "Math",
            [],
            [
                FunctionDef(
                    "__init__",
                    [_param("self")],
                    [ReturnStatement(NumeralLiteral("0"))],
                ),
            ],
        )
        wat = self._wat(
            stateless,
            ExpressionStatement(CallExpr(Identifier("Math"), [])),
        )
        self.assertIn("f64.const 0  ;; implicit self", wat)
        self.assertNotIn("global.get $__heap_ptr", wat)

    def test_field_byte_offset_correct(self):
        """Second field in a two-field class must use i32.const 8."""
        two_field = ClassDef(
            "Point",
            [],
            [
                FunctionDef(
                    "__init__",
                    [_param("self"), _param("x"), _param("y")],
                    [
                        Assignment(
                            AttributeAccess(Identifier("self"), "x"),
                            Identifier("x"),
                        ),
                        Assignment(
                            AttributeAccess(Identifier("self"), "y"),
                            Identifier("y"),
                        ),
                    ],
                ),
            ],
        )
        wat = self._wat(two_field)
        # First field (x) uses i32.const 0; second field (y) uses i32.const 8.
        self.assertIn("i32.const 0", wat)
        self.assertIn("i32.const 8", wat)

    def test_external_attr_read_emits_f64_load(self):
        """c.value in __main__ for a known class variable must emit f64.load."""
        wat = self._wat(
            self._counter_class(),
            VariableDeclaration(
                "c",
                CallExpr(Identifier("Counter"), [NumeralLiteral("10")]),
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("print"),
                    [AttributeAccess(Identifier("c"), "value")],
                )
            ),
        )
        self.assertIn("f64.load", wat)


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime not installed",
)
class WATClassWasmExecutionTestSuite(unittest.TestCase):
    """Compile generated WAT to WASM and execute class-related flows."""

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
                wasmtime.FuncType([wasmtime.ValType.f64(), wasmtime.ValType.f64()], [wasmtime.ValType.f64()]),
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
        """Counter(10).get() must return 10.0 via field store/load."""
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
        """Counter.increment (self.value += 1) must mutate the stored field."""
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
            ExpressionStatement(
                CallExpr(AttributeAccess(Identifier("c"), "increment"), [])
            ),
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
        """Two Counter instances must have independent memory regions."""
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


# ---------------------------------------------------------------------------
# Inheritance helpers + test suite
# ---------------------------------------------------------------------------

def _parse_en(source: str):
    """Parse an English-language multilingual source string via the full pipeline."""
    from multilingualprogramming.lexer.lexer import Lexer   # pylint: disable=import-outside-toplevel
    from multilingualprogramming.parser.parser import Parser  # pylint: disable=import-outside-toplevel
    tokens = Lexer(source, language="en").tokenize()
    return Parser(tokens, source_language="en").parse()


class WATInheritanceTestSuite(unittest.TestCase):
    """Verify compile-time inheritance: method name table, field layout, super()."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    # -- method name-table inheritance --

    def test_inherited_method_in_name_table(self):
        """Dog should have Animal.speak in its name table after lowering."""
        prog = _parse_en(
            "class Animal:\n"
            "    def speak(self):\n"
            "        print(0)\n"
            "class Dog(Animal):\n"
            "    pass\n"
        )
        self.gen.generate(prog)
        attr_call_names = getattr(self.gen, "_class_attr_call_names")
        self.assertIn("Dog.speak", attr_call_names)

    def test_overridden_method_not_inherited(self):
        """If Dog defines its own speak(), it must NOT be overwritten by Animal's."""
        prog = _parse_en(
            "class Animal:\n"
            "    def speak(self):\n"
            "        print(1)\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        print(2)\n"
        )
        self.gen.generate(prog)
        # Dog.speak should point to Dog__speak, not Animal__speak
        attr_call_names = getattr(self.gen, "_class_attr_call_names")
        self.assertEqual(attr_call_names["Dog.speak"], "Dog__speak")

    # -- field layout inheritance --

    def test_parent_field_at_offset_zero(self):
        """Inherited parent field must appear at offset 0 in the child layout."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def __init__(self):\n"
            "        self.name = 0\n"
        )
        self.gen.generate(prog)
        class_field_layouts = getattr(self.gen, "_class_field_layouts")
        layout = class_field_layouts["Dog"]
        self.assertIn("legs", layout)
        self.assertIn("name", layout)
        self.assertEqual(layout["legs"], 0)   # parent field first
        self.assertEqual(layout["name"], 8)   # child field after

    def test_subclass_obj_size_includes_parent_fields(self):
        """Dog with one parent field + one own field must have obj_size == 16."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def __init__(self):\n"
            "        self.name = 0\n"
        )
        self.gen.generate(prog)
        class_obj_sizes = getattr(self.gen, "_class_obj_sizes")
        self.assertEqual(class_obj_sizes["Dog"], 16)

    # -- super() lowering --

    def test_super_init_emits_parent_call(self):
        """super().__init__() must emit a call to Animal____init__."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.name = 0\n"
        )
        wat = self.gen.generate(prog)
        self.assertIn("call $Animal____init__", wat)

    def test_super_method_emits_parent_call(self):
        """super().speak() inside Dog.bark must emit a call to Animal__speak."""
        prog = _parse_en(
            "class Animal:\n"
            "    def speak(self):\n"
            "        print(1)\n"
            "class Dog(Animal):\n"
            "    def bark(self):\n"
            "        super().speak()\n"
        )
        wat = self.gen.generate(prog)
        self.assertIn("call $Animal__speak", wat)

    def test_subclass_without_own_init_inherits_ctor(self):
        """A subclass with no __init__ must inherit the parent's constructor entry."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def bark(self):\n"
            "        print(self.legs)\n"
        )
        self.gen.generate(prog)
        class_ctor_names = getattr(self.gen, "_class_ctor_names")
        self.assertIn("Dog", class_ctor_names)
        self.assertEqual(
            class_ctor_names["Dog"],
            class_ctor_names["Animal"],
        )


@unittest.skipUnless(
    importlib.util.find_spec("wasmtime") is not None,
    "wasmtime not installed",
)
class WATInheritanceWasmExecutionTestSuite(unittest.TestCase):
    """Execute WAT-compiled inheritance programs via wasmtime."""

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
        linker.allow_shadowing = True

        def _print_f64(val):
            printed.append(val)

        def _print_str(_ptr, _length):
            pass  # string printing not tested here

        def _print_bool(val):
            printed.append(bool(val))

        def _print_sep():
            pass

        def _print_newline():
            pass

        linker.define_func("env", "print_f64",
                           wasmtime.FuncType([wasmtime.ValType.f64()], []), _print_f64)
        linker.define_func("env", "print_str",
                           wasmtime.FuncType([wasmtime.ValType.i32(), wasmtime.ValType.i32()], []),
                           _print_str)
        linker.define_func("env", "print_bool",
                           wasmtime.FuncType([wasmtime.ValType.i32()], []), _print_bool)
        linker.define_func("env", "print_sep",
                           wasmtime.FuncType([], []), _print_sep)
        linker.define_func("env", "print_newline",
                           wasmtime.FuncType([], []), _print_newline)
        linker.define_func("env", "pow_f64",
                           wasmtime.FuncType([wasmtime.ValType.f64(), wasmtime.ValType.f64()],
                                             [wasmtime.ValType.f64()]),
                           lambda base, exp: base ** exp)

        instance = linker.instantiate(store, module)
        instance.exports(store)["__main"](store)
        return printed

    def test_inherited_method_called_on_subclass(self):
        """Dog() uses Animal's constructor; d.get_legs() returns the Animal field."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "    def get_legs(self):\n"
            "        return self.legs\n"
            "class Dog(Animal):\n"
            "    pass\n"
            "d = Dog()\n"
            "print(d.get_legs())\n"
        )
        self.assertEqual(self._run_main(prog), [4.0])

    def test_super_init_sets_parent_field(self):
        """super().__init__() in Dog.__init__ correctly sets self.legs."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.name = 9\n"
            "    def get_legs(self):\n"
            "        return self.legs\n"
            "d = Dog()\n"
            "print(d.get_legs())\n"
        )
        self.assertEqual(self._run_main(prog), [4.0])

    def test_subclass_own_and_inherited_fields(self):
        """Dog can access both inherited self.legs and its own self.name."""
        prog = _parse_en(
            "class Animal:\n"
            "    def __init__(self):\n"
            "        self.legs = 4\n"
            "class Dog(Animal):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.name = 99\n"
            "    def get_both(self):\n"
            "        return self.legs + self.name\n"
            "d = Dog()\n"
            "print(d.get_both())\n"
        )
        self.assertEqual(self._run_main(prog), [103.0])


# ---------------------------------------------------------------------------
# New feature tests — items 1–5
# ---------------------------------------------------------------------------

class WATMatchCaseTestSuite(unittest.TestCase):
    """WAT lowering for match/case statements."""

    def test_match_numeric_case_generates_block(self):
        """match with numeric literal cases produces block + f64.eq + if."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(NumeralLiteral("1"), [PassStatement()], is_default=False),
                CaseClause(NumeralLiteral("2"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("block $", wat)
        self.assertIn("f64.eq", wat)
        self.assertIn("if", wat)
        self.assertIn("br $", wat)

    def test_match_default_case_emits_body(self):
        """A default case emits its body without a condition check."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(None, [PassStatement()], is_default=True),
            ],
        )
        wat = _gen(stmt)
        self.assertIn(";; case _: (default)", wat)
        self.assertIn("br $", wat)

    def test_match_boolean_case(self):
        """Boolean literal case emits f64.const 1.0 / 0.0 + f64.eq."""
        stmt = MatchStatement(
            subject=Identifier("flag"),
            cases=[
                CaseClause(BooleanLiteral(True), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 1.0", wat)
        self.assertIn("f64.eq", wat)

    def test_match_string_case_lowers_to_f64_eq(self):
        """String pattern is lowered via interned offset comparison (f64.eq)."""
        stmt = MatchStatement(
            subject=Identifier("s"),
            cases=[
                CaseClause(
                    StringLiteral("hello"), [PassStatement()], is_default=False
                ),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("f64.eq", wat)
        self.assertIn("f64.const", wat)
        self.assertNotIn("string patterns not comparable", wat)
        self.assertNotIn("unsupported call: string_pattern_match", wat)

    def test_match_string_case_same_string_matches(self):
        """Two identical string literals intern to the same offset, so the match fires."""
        # Declare s = "world", then match s: case "world": x = 1; case "other": x = 2
        prog = _gen(
            VariableDeclaration(Identifier("s"), StringLiteral("world")),
            MatchStatement(
                subject=Identifier("s"),
                cases=[
                    CaseClause(StringLiteral("world"), [
                        VariableDeclaration(Identifier("x"), NumeralLiteral("1")),
                    ], is_default=False),
                    CaseClause(StringLiteral("other"), [
                        VariableDeclaration(Identifier("x"), NumeralLiteral("2")),
                    ], is_default=False),
                ],
            ),
        )
        # Both patterns lower to f64.eq comparisons against interned offsets.
        self.assertIn("f64.eq", prog)
        self.assertNotIn("unsupported call:", prog)


class WATAugmentedAssignTestSuite(unittest.TestCase):
    """WAT lowering for augmented assignment operators."""

    def _gen_aug(self, op: str) -> str:
        """Generate WAT for ``x = 0; x op= 3``."""
        return _gen(
            VariableDeclaration(Identifier("x"), NumeralLiteral("0")),
            Assignment(Identifier("x"), NumeralLiteral("3"), op=op),
        )

    def test_add_assign(self):
        self.assertIn("f64.add", self._gen_aug("+="))

    def test_sub_assign(self):
        self.assertIn("f64.sub", self._gen_aug("-="))

    def test_mul_assign(self):
        self.assertIn("f64.mul", self._gen_aug("*="))

    def test_div_assign(self):
        self.assertIn("f64.div", self._gen_aug("/="))

    def test_floor_div_assign(self):
        wat = self._gen_aug("//=")
        self.assertIn("f64.div", wat)
        self.assertIn("f64.floor", wat)

    def test_mod_assign(self):
        wat = self._gen_aug("%=")
        self.assertIn("f64.div", wat)
        self.assertIn("f64.floor", wat)
        self.assertIn("f64.neg", wat)
        self.assertIn("f64.add", wat)

    def test_power_assign(self):
        wat = self._gen_aug("**=")
        self.assertIn("call $pow_f64", wat)
        self.assertNotIn("not natively supported", wat)

    def test_bitwise_and_assign(self):
        wat = self._gen_aug("&=")
        self.assertIn("i32.trunc_f64_s", wat)
        self.assertIn("i32.and", wat)
        self.assertIn("f64.convert_i32_s", wat)

    def test_bitwise_or_assign(self):
        wat = self._gen_aug("|=")
        self.assertIn("i32.or", wat)

    def test_bitwise_xor_assign(self):
        wat = self._gen_aug("^=")
        self.assertIn("i32.xor", wat)

    def test_shl_assign(self):
        wat = self._gen_aug("<<=")
        self.assertIn("i32.shl", wat)

    def test_shr_assign(self):
        wat = self._gen_aug(">>=")
        self.assertIn("i32.shr_s", wat)


class WATStringLenTestSuite(unittest.TestCase):
    """WAT len() lowering for string literals and string variables."""

    def test_len_of_string_literal(self):
        """len("hello") → f64.const 5.0 (byte length)."""
        stmt = ExpressionStatement(
            CallExpr(Identifier("len"), [StringLiteral("hello")])
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 5.0", wat)

    def test_len_of_string_variable(self):
        """let s = "hi"; len(s) → local.get of the strlen local."""
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hi")),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("s")])),
        ]
        wat = _gen(*stmts)
        # strlen local must be declared and used
        self.assertIn("s_strlen", wat)
        self.assertIn("f64.const 2.0", wat)  # "hi" = 2 bytes

    def test_len_string_reassign(self):
        """Re-assigning a string variable updates the strlen local."""
        stmts = [
            VariableDeclaration(Identifier("t"), StringLiteral("abc")),
            Assignment(Identifier("t"), StringLiteral("wxyz"), op="="),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("t")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.const 4.0", wat)  # "wxyz" = 4 bytes

    def test_len_localized_fr(self):
        """longueur() is recognized as len() in WAT."""
        stmt = ExpressionStatement(
            CallExpr(Identifier("longueur"), [StringLiteral("bonjour")])
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 7.0", wat)


class WATListSupportTestSuite(unittest.TestCase):
    """WAT lowering for list literals, indexing, and len()."""

    def test_list_alloc_emits_heap_global(self):
        """A list literal triggers emission of $__heap_ptr."""
        stmt = VariableDeclaration(Identifier("a"), ListLiteral([NumeralLiteral("1")]))
        wat = _gen(stmt)
        self.assertIn("$__heap_ptr", wat)

    def test_list_alloc_stores_length_header(self):
        """[1, 2, 3] stores f64.const 3.0 as the length header."""
        stmt = VariableDeclaration(
            Identifier("a"),
            ListLiteral([NumeralLiteral("1"), NumeralLiteral("2"), NumeralLiteral("3")]),
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 3.0", wat)
        self.assertIn("f64.store", wat)

    def test_list_len(self):
        """len(a) for a list variable emits f64.load at offset 0."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20")]),
            ),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("a")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.load", wat)
        self.assertIn(";; list length from header", wat)

    def test_list_index_access(self):
        """a[1] for a list variable emits the correct offset arithmetic."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20")]),
            ),
            ExpressionStatement(
                IndexAccess(Identifier("a"), NumeralLiteral("1"))
            ),
        ]
        wat = _gen(*stmts)
        # Offset arithmetic: i32.const 8 * index (element 1 → offset 8 from data start)
        self.assertIn("i32.const 8", wat)
        self.assertIn("i32.mul", wat)
        self.assertIn("f64.load", wat)

    def test_tuple_alloc(self):
        """Tuple literal (1, 2) is allocated like a list."""
        stmt = VariableDeclaration(
            Identifier("t"),
            TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
        )
        wat = _gen(stmt)
        self.assertIn("$__heap_ptr", wat)
        self.assertIn("f64.const 2.0", wat)


class WATAsyncAwaitTestSuite(unittest.TestCase):
    """WAT lowering for async/await — best-effort synchronous evaluation."""

    def test_await_expr_evaluates_operand(self):
        """await f() in WAT is lowered by simply evaluating f() (no async stub)."""
        func = FunctionDef(
            Identifier("work"),
            params=[],
            body=[ReturnStatement(NumeralLiteral("42"))],
        )
        stmt = ExpressionStatement(
            AwaitExpr(CallExpr(Identifier("work"), []))
        )
        wat = _gen(func, stmt)
        # The call to $work must appear; no "unsupported expr: AwaitExpr" stub.
        self.assertIn("call $work", wat)
        self.assertNotIn("unsupported expr: AwaitExpr", wat)

    def test_async_def_lowers_as_regular_function(self):
        """async def f() is emitted as a normal WAT function."""
        func = FunctionDef(
            Identifier("f"),
            params=[],
            body=[ReturnStatement(NumeralLiteral("1"))],
            is_async=True,
        )
        wat = _gen(func)
        self.assertIn('(func $f', wat)
        self.assertIn('(export "f")', wat)


class WATForListTestSuite(unittest.TestCase):
    """WAT lowering for for-loops over list/tuple variables."""

    def test_for_loop_over_list_var_emits_index_loop(self):
        """for x in a (list var) → index-based loop using list header."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20"), NumeralLiteral("30")]),
            ),
            ForLoop(
                target=Identifier("x"),
                iterable=Identifier("a"),
                body=[ExpressionStatement(Identifier("x"))],
            ),
        ]
        wat = _gen(*stmts)
        # Should emit list-iteration pattern: load length, index loop, f64.load element.
        self.assertIn("i32.const 8", wat)   # element stride
        self.assertIn("i32.mul", wat)
        self.assertIn("f64.load", wat)
        self.assertIn("f64.ge", wat)        # exit condition (idx >= len)
        self.assertNotIn("not supported in WAT", wat)

    def test_for_loop_over_non_tracked_var_emits_comment(self):
        """for x in unknown_var → unsupported comment (not a tracked list)."""
        stmt = ForLoop(
            target=Identifier("x"),
            iterable=Identifier("unknown"),
            body=[PassStatement()],
        )
        wat = _gen(stmt)
        self.assertIn("not supported in WAT", wat)

    def test_async_for_over_list_var_works(self):
        """async for x in a (list var) is lowered identically to sync for."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
            ),
            ForLoop(
                target=Identifier("x"),
                iterable=Identifier("a"),
                body=[PassStatement()],
                is_async=True,
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("i32.mul", wat)
        self.assertNotIn("not supported in WAT", wat)


class WATListComprehensionTestSuite(unittest.TestCase):
    """WAT lowering for comprehensions over list variables."""

    def test_listcomp_over_list_var(self):
        """[x for x in a] over a list variable lowers to an index-based loop."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("1"), NumeralLiteral("2"), NumeralLiteral("3")]),
            ),
            ExpressionStatement(
                ListComprehension(
                    element=Identifier("x"),
                    target=Identifier("x"),
                    iterable=Identifier("a"),
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("listcomp over list variable", wat)
        self.assertIn("f64.load", wat)
        self.assertIn("i32.mul", wat)
        self.assertNotIn("collections not representable as f64", wat)


class WATMatchCaseExtendedTestSuite(unittest.TestCase):
    """WAT lowering for additional match/case pattern types."""

    def test_match_none_pattern(self):
        """case None: lowers to f64.eq with f64.const 0."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(NoneLiteral(), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("case None:", wat)
        self.assertIn("f64.const 0", wat)
        self.assertIn("f64.eq", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_match_identifier_capture(self):
        """case y: (capture variable) binds subject value to y and always matches."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(Identifier("y"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("capture variable", wat)
        self.assertIn("local.set", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_match_mixed_patterns(self):
        """Numeric, string, None, and capture cases all lower without stubs."""
        stmt = MatchStatement(
            subject=Identifier("v"),
            cases=[
                CaseClause(NumeralLiteral("1"), [PassStatement()], is_default=False),
                CaseClause(StringLiteral("ok"), [PassStatement()], is_default=False),
                CaseClause(NoneLiteral(), [PassStatement()], is_default=False),
                CaseClause(Identifier("other"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertNotIn("complex pattern not lowerable", wat)
        self.assertNotIn("unsupported call: string_pattern_match", wat)


class WATTupleMatchPatternTestSuite(unittest.TestCase):
    """WAT match/case lowering for tuple/list literal patterns."""

    def test_tuple_pattern_emits_length_and_element_checks(self):
        """case (1, 2): checks length == 2 AND elem[0] == 1.0 AND elem[1] == 2.0."""
        stmts = [
            VariableDeclaration(
                Identifier("t"),
                TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
            ),
            MatchStatement(
                subject=Identifier("t"),
                cases=[
                    CaseClause(
                        TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
                        [PassStatement()],
                        is_default=False,
                    ),
                ],
            ),
        ]
        wat = _gen(*stmts)
        # Length check: f64.const 2.0 from the pattern tuple
        self.assertIn("f64.const 2.0", wat)
        # Element-wise: each element comparison uses f64.eq + i32.and
        self.assertGreaterEqual(wat.count("f64.eq"), 3)  # len + 2 elements
        self.assertIn("i32.and", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_tuple_pattern_requires_list_subject(self):
        """Tuple pattern against a non-list subject falls back to stub."""
        stmt = MatchStatement(
            subject=Identifier("x"),   # x is not a list local
            cases=[
                CaseClause(
                    TupleLiteral([NumeralLiteral("1")]),
                    [PassStatement()],
                    is_default=False,
                ),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("complex pattern not lowerable", wat)


class WATStringOpsTestSuite(unittest.TestCase):
    """WAT lowering for string concatenation, indexing, and slicing."""

    def test_compile_time_string_concat(self):
        """StringLiteral + StringLiteral interns the concatenated result at compile time."""
        stmt = VariableDeclaration(
            Identifier("s"),
            BinaryOp(StringLiteral("hello"), "+", StringLiteral(" world")),
        )
        wat = _gen(stmt)
        self.assertIn("str concat (compile-time)", wat)
        # No runtime helper needed.
        self.assertNotIn("call $__str_concat", wat)

    def test_runtime_string_concat_calls_helper(self):
        """str_var + StringLiteral emits call $__str_concat and the helper func."""
        stmts = [
            VariableDeclaration(Identifier("a"), StringLiteral("hi")),
            VariableDeclaration(
                Identifier("b"),
                BinaryOp(Identifier("a"), "+", StringLiteral("!")),
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_concat", wat)
        self.assertIn("str concat (runtime)", wat)

    def test_string_index_emits_byte_load(self):
        """s[i] on a string variable emits i32.load8_u + f64.convert_i32_u."""
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(IndexAccess(Identifier("s"), NumeralLiteral("0"))),
        ]
        wat = _gen(*stmts)
        self.assertIn("i32.load8_u", wat)
        self.assertIn("f64.convert_i32_u", wat)
        self.assertIn("string byte access", wat)

    def test_string_slice_calls_helper(self):
        """s[1:3] on a string variable emits call $__str_slice and the helper."""
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(
                IndexAccess(Identifier("s"), SliceExpr(NumeralLiteral("1"), NumeralLiteral("3")))
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_slice", wat)
        self.assertIn("string slice", wat)

    def test_string_slice_no_start_uses_zero(self):
        """s[:3] defaults start to 0."""
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hello")),
            ExpressionStatement(
                IndexAccess(Identifier("s"), SliceExpr(stop=NumeralLiteral("3")))
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("call $__str_slice", wat)
        self.assertIn("f64.const 0", wat)


class WATLambdaTableTestSuite(unittest.TestCase):
    """WAT lambda function pointers via WAT table + call_indirect."""

    def test_lambda_emits_table_and_index(self):
        """let f = lambda x: x emits a lambda table entry and f64.const index."""
        stmt = VariableDeclaration(
            Identifier("f"),
            LambdaExpr(
                params=[Parameter(Identifier("x"))],
                body=Identifier("x"),
            ),
        )
        wat = _gen(stmt)
        self.assertIn("(table", wat)
        self.assertIn("(elem", wat)
        self.assertIn("f64.const 0.0", wat)  # table index 0

    def test_lambda_call_emits_call_indirect(self):
        """f(42) on a lambda local emits call_indirect via lambda_table."""
        stmts = [
            VariableDeclaration(
                Identifier("f"),
                LambdaExpr(
                    params=[Parameter(Identifier("x"))],
                    body=Identifier("x"),
                ),
            ),
            ExpressionStatement(CallExpr(Identifier("f"), [NumeralLiteral("42")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("call_indirect", wat)
        self.assertIn("(table", wat)

    def test_two_lambdas_get_distinct_table_indices(self):
        """Two lambdas get indices 0 and 1 in the table."""
        stmts = [
            VariableDeclaration(
                Identifier("f"),
                LambdaExpr(params=[Parameter(Identifier("x"))], body=Identifier("x")),
            ),
            VariableDeclaration(
                Identifier("g"),
                LambdaExpr(params=[Parameter(Identifier("y"))], body=Identifier("y")),
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.const 0.0", wat)
        self.assertIn("f64.const 1.0", wat)


if __name__ == "__main__":
    unittest.main()
