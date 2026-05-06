#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for Core 1.0 example files in examples/core/.

Each source file in examples/core/ is discovered automatically.
The test pipeline for every example:
  1. Lex the source code (language-aware tokenisation)
  2. Parse the token stream into a surface AST
  3. Lower the AST to Core 1.0 semantic IR
  4. Run the minimal structural validator (validate_semantic_ir)
"""

import pathlib

import pytest

from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.validators import validate_semantic_ir
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.source_extensions import iter_source_files


_CORE_EXAMPLES_DIR = (
    pathlib.Path(__file__).parent.parent.parent / "examples" / "core"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_lang(path: pathlib.Path) -> str:
    """Infer language code from a filename like *_en.multi → 'en'."""
    stem = path.stem
    if "_" in stem:
        return stem.rsplit("_", 1)[-1]
    return "en"


def _lower(path: pathlib.Path):
    """Lex, parse, and lower a source example file to Core 1.0 IR."""
    lang = _detect_lang(path)
    source = path.read_text(encoding="utf-8")
    tokens = Lexer(source, language=lang).tokenize()
    ast = Parser(tokens, source_language=lang).parse()
    return lower_to_semantic_ir(ast, lang)


def _example_files():
    return iter_source_files(_CORE_EXAMPLES_DIR, "*")


# ---------------------------------------------------------------------------
# Parametrised tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_core_example_parses(path: pathlib.Path):
    """Every Core 1.0 example must tokenise and parse without raising."""
    lang = _detect_lang(path)
    source = path.read_text(encoding="utf-8")
    tokens = Lexer(source, language=lang).tokenize()
    program = Parser(tokens, source_language=lang).parse()
    assert program is not None
    assert len(program.body) > 0, f"{path.name} has an empty program body"


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_core_example_lowers_to_ir(path: pathlib.Path):
    """Every Core 1.0 example must lower to a valid IRProgram."""
    ir = _lower(path)
    assert ir is not None
    validate_semantic_ir(ir)
    assert ir.source_language != ""
    assert isinstance(ir.body, list)
    assert len(ir.body) > 0, f"{path.name}: IR body is empty after lowering"


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_core_example_language_detected(path: pathlib.Path):
    """Language code must be inferred correctly from the filename."""
    lang = _detect_lang(path)
    assert lang, f"Could not detect language for {path.name}"
    ir = _lower(path)
    assert ir.source_language == lang
