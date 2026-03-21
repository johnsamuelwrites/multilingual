#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Reactive UI IR and lowering tests.

Tests that:
- IRCanvasBlock, IRRenderExpr, IRViewBinding exist in ir_nodes
- UILoweringPass produces correct JS/HTML output
- observe var lowers to a JS signal declaration
- on_change lowers to a handler registration
"""
# pylint: disable=missing-class-docstring

from multilingualprogramming.core.ir_nodes import (
    IRCanvasBlock,
    IRIdentifier,
    IRLiteral,
    IRObserveBinding,
    IROnChange,
    IRProgram,
    IRRenderExpr,
    IRViewBinding,
)
from multilingualprogramming.codegen.ui_lowering import UILoweringPass, lower_to_ui
from multilingualprogramming.core.types import INT_TYPE, STRING_TYPE


def _prog(*nodes):
    return IRProgram(body=list(nodes), source_language="en")


# ===========================================================================
# IRCanvasBlock
# ===========================================================================

class TestIRCanvasBlock:
    def test_canvas_block_instantiates(self):
        canvas = IRCanvasBlock(name="main")
        assert canvas.name == "main"
        assert canvas.children == []

    def test_canvas_block_with_children(self):
        child = IRLiteral(value="hello", kind="string")
        canvas = IRCanvasBlock(name="chat", children=[child])
        assert len(canvas.children) == 1


# ===========================================================================
# IRRenderExpr
# ===========================================================================

class TestIRRenderExpr:
    def test_render_expr_instantiates(self):
        target = IRIdentifier(name="my_canvas")
        value = IRLiteral(value="hello", kind="string")
        render = IRRenderExpr(target=target, value=value)
        assert render.target is target
        assert render.value is value


# ===========================================================================
# IRViewBinding
# ===========================================================================

class TestIRViewBinding:
    def test_view_binding_instantiates(self):
        signal = IRIdentifier(name="chat_output")
        target = IRIdentifier(name="chat_view")
        binding = IRViewBinding(signal=signal, target=target)
        assert binding.signal is signal
        assert binding.target is target


# ===========================================================================
# UILoweringPass: observe var
# ===========================================================================

class TestUILoweringObserve:
    def test_observe_emits_signal_declaration(self):
        node = IRObserveBinding(
            name="count",
            value=IRLiteral(value=0, kind="int", inferred_type=INT_TYPE),
        )
        result = lower_to_ui(_prog(node))
        assert any("count" in s for s in result.js_signals)

    def test_signal_uses_initial_value(self):
        node = IRObserveBinding(
            name="score",
            value=IRLiteral(value=100, kind="int", inferred_type=INT_TYPE),
        )
        result = lower_to_ui(_prog(node))
        signal_js = "\n".join(result.js_signals)
        assert "100" in signal_js

    def test_observe_string_signal(self):
        node = IRObserveBinding(
            name="message",
            value=IRLiteral(value="", kind="string", inferred_type=STRING_TYPE),
        )
        result = lower_to_ui(_prog(node))
        assert any("message" in s for s in result.js_signals)


# ===========================================================================
# UILoweringPass: on_change
# ===========================================================================

class TestUILoweringOnChange:
    def test_on_change_emits_handler(self):
        node = IROnChange(signal=IRIdentifier(name="count"))
        result = lower_to_ui(_prog(node))
        handler_js = "\n".join(result.js_handlers)
        assert "count" in handler_js
        assert "on_change" in handler_js

    def test_on_change_uses_arrow_function(self):
        node = IROnChange(signal=IRIdentifier(name="x"))
        result = lower_to_ui(_prog(node))
        handler_js = "\n".join(result.js_handlers)
        assert "=>" in handler_js


# ===========================================================================
# UILoweringPass: canvas block
# ===========================================================================

class TestUILoweringCanvas:
    def test_canvas_emits_html_element(self):
        node = IRCanvasBlock(name="main")
        result = lower_to_ui(_prog(node))
        html = result.emit_html()
        assert "main" in html
        assert "<div" in html

    def test_canvas_has_class_ml_canvas(self):
        node = IRCanvasBlock(name="chat")
        result = lower_to_ui(_prog(node))
        assert "ml-canvas" in result.emit_html()


# ===========================================================================
# UILoweringPass: view binding
# ===========================================================================

class TestUILoweringViewBinding:
    def test_view_binding_emits_js(self):
        node = IRViewBinding(
            signal=IRIdentifier(name="response"),
            target=IRIdentifier(name="chat_view"),
        )
        result = lower_to_ui(_prog(node))
        binding_js = "\n".join(result.js_bindings)
        assert "streamToView" in binding_js
        assert "response" in binding_js

    def test_emit_js_combines_all_sections(self):
        observe = IRObserveBinding(
            name="msg",
            value=IRLiteral(value="", kind="string", inferred_type=STRING_TYPE),
        )
        canvas = IRCanvasBlock(name="view")
        js = lower_to_ui(_prog(observe, canvas)).emit_js()
        assert "msg" in js
        assert "_engine" in js


# ===========================================================================
# UILoweringResult helpers
# ===========================================================================

class TestUILoweringResult:
    def test_emit_js_includes_preamble(self):
        result = lower_to_ui(_prog())
        js = result.emit_js()
        assert "ReactiveEngine" in js

    def test_empty_program_no_diagnostics(self):
        result = lower_to_ui(_prog())
        assert result.diagnostics == []
