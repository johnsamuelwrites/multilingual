#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Compiler boundary and new primitive regression tests."""

from unittest.mock import patch

from multilingualprogramming.codegen.executor import ProgramExecutor
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.core.ir_nodes import (
    IRCanvasBlock,
    IROnChange,
    IRPlanExpr,
    IRRenderExpr,
    IRRetrieveExpr,
    IRTranscribeExpr,
    IRViewBinding,
)
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


def _lower(source: str, language: str = "en"):
    tokens = Lexer(source, language=language).tokenize()
    program = Parser(tokens, source_language=language).parse()
    return lower_to_semantic_ir(program, language)


class TestNewCorePrimitives:
    """Dedicated Core 1.0 primitive lowering coverage."""

    def test_plan_lowers_to_dedicated_ir_node(self):
        ir = _lower('let p = plan @planner: "Ship release"\n')
        assert isinstance(ir.body[0].value, IRPlanExpr)

    def test_transcribe_lowers_to_dedicated_ir_node(self):
        ir = _lower("let text = transcribe @whisper: audio_blob\n")
        assert isinstance(ir.body[0].value, IRTranscribeExpr)

    def test_retrieve_lowers_to_dedicated_ir_node(self):
        ir = _lower('let hits = retrieve kb: "hello"\n')
        assert isinstance(ir.body[0].value, IRRetrieveExpr)


class TestReactiveForms:
    """Reactive syntax should preserve semantic IR nodes."""

    def test_on_change_lowers_to_dedicated_ir_node(self):
        ir = _lower("on count.change:\n    pass\n")
        assert isinstance(ir.body[0], IROnChange)

    def test_canvas_lowers_to_dedicated_ir_node(self):
        ir = _lower("canvas main:\n    pass\n")
        assert isinstance(ir.body[0], IRCanvasBlock)

    def test_render_lowers_to_dedicated_ir_node(self):
        ir = _lower('render panel with "hello"\n')
        assert isinstance(ir.body[0], IRRenderExpr)

    def test_bind_lowers_to_dedicated_ir_node(self):
        ir = _lower("bind output -> panel\n")
        assert isinstance(ir.body[0], IRViewBinding)


class TestCompilerBoundary:
    """Backends and executor should accept semantic IR programs directly."""

    def test_python_generator_accepts_semantic_ir(self):
        ir = _lower("let x = 1\nprint(x)\n")
        code = PythonCodeGenerator().generate(ir)
        assert "x = 1" in code
        assert "print(x)" in code

    def test_python_generator_uses_native_ir_path(self):
        ir = _lower("let x = 1\nprint(x)\n")
        with patch(
            "multilingualprogramming.codegen.python_generator."
            "lower_ir_to_runtime_ast",
            side_effect=AssertionError("legacy bridge should not run"),
            create=True,
        ):
            code = PythonCodeGenerator().generate(ir)
        assert "x = 1" in code
        assert "print(x)" in code

    def test_executor_uses_semantic_ir_boundary(self):
        result = ProgramExecutor(language="en").execute("let x = 2\nprint(x)\n")
        assert result.success, result.errors
        assert result.output.strip() == "2"

    def test_wat_generator_accepts_semantic_ir(self):
        ir = _lower("let x = 1\nprint(x)\n")
        wat = WATCodeGenerator().generate(ir)
        assert isinstance(wat, str)
        assert "(module" in wat
