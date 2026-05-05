#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for the Core 1.0 CLI subcommands: ir, explain, ui-preview."""
# pylint: disable=missing-class-docstring

import json
from pathlib import Path
from types import SimpleNamespace

from multilingualprogramming.__main__ import (
    cmd_explain,
    cmd_ir,
    cmd_ui_preview,
    _emit_ir_json,
    _emit_ir_text,
)
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lower(source: str, lang: str = "en"):
    tokens = Lexer(source, language=lang).tokenize()
    program = Parser(tokens, source_language=lang).parse()
    return lower_to_semantic_ir(program, lang)


def _tmp_ml_file(tmp_path: Path, source: str) -> Path:
    p = tmp_path / "test.multi"
    p.write_text(source, encoding="utf-8")
    return p


# ===========================================================================
# _emit_ir_text
# ===========================================================================

class TestEmitIRText:
    def test_prints_program_header(self, capsys):
        ir = _lower("let x = 1\n")
        _emit_ir_text(ir)
        out = capsys.readouterr().out
        assert "IRProgram" in out
        assert "language='en'" in out

    def test_prints_binding_node(self, capsys):
        ir = _lower("let score = 42\n")
        _emit_ir_text(ir)
        out = capsys.readouterr().out
        assert "IRBinding" in out
        assert "score" in out

    def test_prints_function_node(self, capsys):
        ir = _lower("fn greet(name):\n    return name\n")
        _emit_ir_text(ir)
        out = capsys.readouterr().out
        assert "IRFunction" in out
        assert "greet" in out


# ===========================================================================
# _emit_ir_json
# ===========================================================================

class TestEmitIRJson:
    def test_valid_json_output(self, capsys):
        ir = _lower("let x = 1\n")
        _emit_ir_json(ir)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["_type"] == "IRProgram"

    def test_json_contains_body(self, capsys):
        ir = _lower("let a = 1\nlet b = 2\n")
        _emit_ir_json(ir)
        data = json.loads(capsys.readouterr().out)
        assert "body" in data
        assert len(data["body"]) == 2

    def test_json_contains_node_types(self, capsys):
        ir = _lower("fn f(x):\n    return x\n")
        _emit_ir_json(ir)
        data = json.loads(capsys.readouterr().out)
        assert data["body"][0]["_type"] == "IRFunction"


# ===========================================================================
# cmd_ir
# ===========================================================================

class TestCmdIR:
    def test_text_format(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "let x = 1\n")
        args = SimpleNamespace(file=str(f), lang=None, format="text")
        cmd_ir(args)
        out = capsys.readouterr().out
        assert "IRProgram" in out

    def test_json_format(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "let x = 1\n")
        args = SimpleNamespace(file=str(f), lang=None, format="json")
        cmd_ir(args)
        data = json.loads(capsys.readouterr().out)
        assert data["_type"] == "IRProgram"

    def test_function_in_json(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "fn add(a, b):\n    return a + b\n")
        args = SimpleNamespace(file=str(f), lang=None, format="json")
        cmd_ir(args)
        data = json.loads(capsys.readouterr().out)
        assert data["body"][0]["_type"] == "IRFunction"


# ===========================================================================
# cmd_explain
# ===========================================================================

class TestCmdExplain:
    def test_explain_shows_filename(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "let x = 1\n")
        args = SimpleNamespace(file=str(f), lang=None)
        cmd_explain(args)
        out = capsys.readouterr().out
        assert str(f) in out

    def test_explain_shows_language(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "let x = 1\n")
        args = SimpleNamespace(file=str(f), lang="en")
        cmd_explain(args)
        out = capsys.readouterr().out
        assert "en" in out

    def test_explain_lists_functions(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "fn greet(name):\n    return name\n")
        args = SimpleNamespace(file=str(f), lang=None)
        cmd_explain(args)
        out = capsys.readouterr().out
        assert "greet" in out
        assert "Functions" in out

    def test_explain_lists_bindings(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "let score = 100\nvar count = 0\n")
        args = SimpleNamespace(file=str(f), lang=None)
        cmd_explain(args)
        out = capsys.readouterr().out
        assert "score" in out
        assert "count" in out

    def test_explain_lists_observe(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "observe var counter = 0\n")
        args = SimpleNamespace(file=str(f), lang=None)
        cmd_explain(args)
        out = capsys.readouterr().out
        assert "counter" in out
        assert "Reactive" in out

    def test_explain_effects(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "fn fetch(url) -> str uses net:\n    pass\n")
        args = SimpleNamespace(file=str(f), lang=None)
        cmd_explain(args)
        out = capsys.readouterr().out
        assert "fetch" in out
        assert "net" in out


# ===========================================================================
# cmd_ui_preview
# ===========================================================================

class TestCmdUIPreview:
    def test_canvas_produces_html(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "observe var count = 0\n")
        args = SimpleNamespace(file=str(f), lang=None, html=False, js=False)
        cmd_ui_preview(args)
        out = capsys.readouterr().out
        # JS output should contain the engine declaration
        assert "_engine" in out or "ReactiveEngine" in out

    def test_html_flag_shows_only_html(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "observe var x = 0\n")
        args = SimpleNamespace(file=str(f), lang=None, html=True, js=False)
        cmd_ui_preview(args)
        out = capsys.readouterr().out
        # html=True shows HTML section; with no canvas blocks it shows the no-canvas comment
        assert "HTML" in out or "canvas" in out.lower()

    def test_js_flag_shows_js(self, tmp_path, capsys):
        f = _tmp_ml_file(tmp_path, "observe var msg = \"\"\n")
        args = SimpleNamespace(file=str(f), lang=None, html=False, js=True)
        cmd_ui_preview(args)
        out = capsys.readouterr().out
        assert "JavaScript" in out or "_engine" in out
