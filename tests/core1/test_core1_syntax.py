#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core 1.0 syntax tests.

Covers: fn, var, let, |>, ?, ~=, enum, type (record), observe var.
Each test parses a source snippet and checks that the correct AST node
or IR node is produced.
"""
# pylint: disable=missing-class-docstring

from multilingualprogramming.core.effects import Effect, EffectSet
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_nodes import (
    BinaryOp,
    EnumDecl,
    FunctionDef,
    ObserveDeclaration,
    RecordDecl,
    UnaryOp,
    VariableDeclaration,
)
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.ir_nodes import (
    IRBinding,
    IREnumDecl,
    IRFunction,
    IRLiteral,
    IRObserveBinding,
    IRPipeExpr,
    IRProgram,
    IRSemanticMatchOp,
    IRTypeDecl,
)
from multilingualprogramming.core.types import INT_TYPE
from multilingualprogramming.core.validators import validate_all, validate_semantic_ir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(source: str, language: str = "en"):
    """Parse source into the surface AST."""
    tokens = Lexer(source, language=language).tokenize()
    return Parser(tokens, source_language=language).parse()


def lower(source: str, language: str = "en"):
    """Lower source into semantic IR."""
    tree = parse(source, language)
    return lower_to_semantic_ir(tree, language)


# ===========================================================================
# fn keyword
# ===========================================================================

class TestFnKeyword:
    def test_fn_parses_as_func_def(self):
        program = parse("fn add(x, y):\n    return x + y\n")
        assert len(program.body) == 1
        node = program.body[0]
        assert isinstance(node, FunctionDef)
        assert node.name == "add"
        assert node.syntax_keyword == "fn"

    def test_fn_lowers_to_ir_function(self):
        ir = lower("fn greet(name):\n    return name\n")
        node = ir.body[0]
        assert isinstance(node, IRFunction)
        assert node.name == "greet"
        assert node.syntax_keyword == "fn"

    def test_fn_parameters_preserved(self):
        ir = lower("fn f(a, b, c):\n    pass\n")
        fn = ir.body[0]
        assert isinstance(fn, IRFunction)
        assert [p.name for p in fn.parameters] == ["a", "b", "c"]


# ===========================================================================
# var / let mutability
# ===========================================================================

class TestVarLet:
    def test_let_is_immutable(self):
        program = parse("let x = 1\n")
        node = program.body[0]
        assert isinstance(node, VariableDeclaration)
        assert node.declaration_kind == "let"
        assert not node.is_mutable

    def test_var_is_mutable(self):
        program = parse("var count = 0\n")
        node = program.body[0]
        assert isinstance(node, VariableDeclaration)
        assert node.declaration_kind == "var"
        assert node.is_mutable

    def test_let_lowers_to_immutable_binding(self):
        ir = lower("let name = \"Alice\"\n")
        node = ir.body[0]
        assert isinstance(node, IRBinding)
        assert not node.is_mutable
        assert node.name == "name"

    def test_var_lowers_to_mutable_binding(self):
        ir = lower("var score = 0\n")
        node = ir.body[0]
        assert isinstance(node, IRBinding)
        assert node.is_mutable
        assert node.name == "score"


# ===========================================================================
# |> pipe operator
# ===========================================================================

class TestPipeOperator:
    def test_pipe_produces_binary_op(self):
        program = parse("x |> f\n")
        node = program.body[0].expression
        assert isinstance(node, BinaryOp)
        assert node.op == "|>"

    def test_pipe_lowers_to_ir_pipe_expr(self):
        ir = lower("let result = items |> sort\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IRPipeExpr)

    def test_pipe_is_left_associative(self):
        # a |> f |> g  must parse as  (a |> f) |> g
        program = parse("a |> f |> g\n")
        outer = program.body[0].expression
        assert isinstance(outer, BinaryOp)
        assert outer.op == "|>"
        assert isinstance(outer.left, BinaryOp)
        assert outer.left.op == "|>"

    def test_pipe_in_pipeline(self):
        src = "let out = names |> filter(active) |> map(upper) |> join\n"
        ir = lower(src)
        binding = ir.body[0]
        assert isinstance(binding.value, IRPipeExpr)


# ===========================================================================
# ? result propagation operator
# ===========================================================================

class TestResultPropagation:
    def test_question_mark_produces_unary_op(self):
        program = parse("fn f():\n    let x = parse(data)?\n    return x\n")
        fn = program.body[0]
        body_stmt = fn.body[0]
        # The ? is on the value of the let declaration
        assert isinstance(body_stmt, VariableDeclaration)
        value = body_stmt.value
        assert isinstance(value, UnaryOp)
        assert value.op == "?"

    def test_chained_propagation(self):
        program = parse("fn f():\n    let x = a()?.b()?\n    return x\n")
        fn = program.body[0]
        value = fn.body[0].value
        # Outermost ? wraps the chained call
        assert isinstance(value, UnaryOp)
        assert value.op == "?"


# ===========================================================================
# ~= semantic match operator
# ===========================================================================

class TestSemanticMatch:
    def test_semantic_match_produces_binary_op(self):
        program = parse("if x ~= \"yes\":\n    pass\n")
        cond = program.body[0].condition
        assert isinstance(cond, BinaryOp)
        assert cond.op == "~="

    def test_semantic_match_lowers_to_semantic_match_op(self):
        ir = lower("let ok = answer ~= \"yes\"\n")
        binding = ir.body[0]
        assert isinstance(binding.value, IRSemanticMatchOp)


# ===========================================================================
# enum declarations
# ===========================================================================

class TestEnumDeclaration:
    def test_enum_parses(self):
        src = "enum Color = | Red | Green | Blue\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, EnumDecl)
        assert node.name == "Color"
        assert len(node.variants) == 3
        assert [v.name for v in node.variants] == ["Red", "Green", "Blue"]

    def test_enum_with_fields_parses(self):
        src = "enum Shape = | Circle { radius: float } | Rect { width: float, height: float }\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, EnumDecl)
        assert node.name == "Shape"
        circle = node.variants[0]
        assert circle.name == "Circle"
        assert len(circle.fields) == 1
        assert circle.fields[0][0] == "radius"

    def test_enum_lowers_to_ir_enum_decl(self):
        ir = lower("enum Status = | Ok | Err\n")
        node = ir.body[0]
        assert isinstance(node, IREnumDecl)
        assert node.name == "Status"
        assert node.declared_type is not None


# ===========================================================================
# type (record) declarations
# ===========================================================================

class TestTypeDeclaration:
    def test_type_parses(self):
        src = "type Point = { x: float, y: float }\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, RecordDecl)
        assert node.name == "Point"
        assert len(node.fields) == 2
        assert node.fields[0].name == "x"
        assert node.fields[1].name == "y"

    def test_type_lowers_to_ir_type_decl(self):
        ir = lower("type Point = { x: float, y: float }\n")
        node = ir.body[0]
        assert isinstance(node, IRTypeDecl)
        assert node.name == "Point"
        assert node.declared_type is not None

    def test_type_with_option_field(self):
        src = "type User = { id: int, email: str }\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, RecordDecl)
        assert node.name == "User"


# ===========================================================================
# observe var (reactive bindings)
# ===========================================================================

class TestObserveDeclaration:
    def test_observe_parses(self):
        src = "observe var count = 0\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, ObserveDeclaration)
        assert node.name == "count"

    def test_observe_with_annotation(self):
        src = "observe var score: int = 0\n"
        program = parse(src)
        node = program.body[0]
        assert isinstance(node, ObserveDeclaration)
        assert node.annotation is not None

    def test_observe_lowers_to_ir_observe_binding(self):
        ir = lower("observe var count = 0\n")
        node = ir.body[0]
        assert isinstance(node, IRObserveBinding)
        assert node.name == "count"
        assert node.value is not None


# ===========================================================================
# Validator
# ===========================================================================

class TestValidator:
    def test_valid_program_has_no_diagnostics(self):
        ir = lower("let x = 1\nfn f(a):\n    return a\n")
        diags = validate_all(ir)
        assert not diags

    def test_validate_semantic_ir_accepts_valid(self):
        ir = lower("let x = 42\n")
        validate_semantic_ir(ir)  # must not raise

    def test_empty_binding_name_reported(self):
        program = IRProgram(
            body=[IRBinding(name="", value=IRLiteral(value=1, kind="int",
                                                     inferred_type=INT_TYPE))],
            source_language="en",
        )
        diags = validate_all(program)
        assert any("empty name" in d for d in diags)

    def test_observe_without_value_reported(self):
        program = IRProgram(
            body=[IRObserveBinding(name="x", value=None)],
            source_language="en",
        )
        diags = validate_all(program)
        assert any("no initial value" in d for d in diags)

    def test_unknown_effect_reported(self):
        fn = IRFunction(
            name="f",
            effects=EffectSet(effects=(Effect("unknown_capability"),)),
        )
        program = IRProgram(body=[fn], source_language="en")
        diags = validate_all(program)
        assert any("unknown capability" in d for d in diags)


# ===========================================================================
# uses capability syntax
# ===========================================================================

class TestUsesSyntax:
    def test_uses_sets_effects_on_function(self):
        src = "fn fetch(url) -> str uses net:\n    pass\n"
        program = parse(src)
        fn = program.body[0]
        assert isinstance(fn, FunctionDef)
        assert "net" in fn.uses

    def test_multiple_uses_capabilities(self):
        src = "fn ai_fn(x) uses ai, net:\n    pass\n"
        program = parse(src)
        fn = program.body[0]
        assert set(fn.uses) == {"ai", "net"}

    def test_uses_flows_into_ir_effects(self):
        ir = lower("fn f() uses ai:\n    pass\n")
        fn = ir.body[0]
        assert isinstance(fn, IRFunction)
        assert "ai" in fn.effects.names()
