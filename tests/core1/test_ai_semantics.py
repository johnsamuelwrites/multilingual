#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""AI-semantics IR lowering tests.

Verifies that prompt/think/stream/embed/generate expressions lower to the
correct IR node types.
"""
# pylint: disable=missing-class-docstring

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.ir_nodes import (
    IRAgentDecl,
    IRBinding,
    IRModelRef,
    IRFunction,
    IRProgram,
    IRPromptExpr,
    IRThinkExpr,
    IRStreamExpr,
    IREmbedExpr,
    IRGenerateExpr,
)


def parse(source: str, language: str = "en"):
    tokens = Lexer(source, language=language).tokenize()
    return Parser(tokens, source_language=language).parse()


def lower(source: str, language: str = "en"):
    tree = parse(source, language)
    return lower_to_semantic_ir(tree, language)


def _find(ir: IRProgram, cls):
    """Return the first top-level node of the given class."""
    for node in ir.body:
        if isinstance(node, cls):
            return node
    return None


# ===========================================================================
# prompt
# ===========================================================================

class TestPromptLowering:
    def test_prompt_call_lowers_to_ir_prompt(self):
        ir = lower("let r = prompt(\"hello\")\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IRPromptExpr)

    def test_prompt_in_function_body(self):
        src = "fn ask(q):\n    let r = prompt(q)\n    return r\n"
        ir = lower(src)
        fn = ir.body[0]
        assert isinstance(fn, IRFunction)
        body_binding = fn.body[0]
        assert isinstance(body_binding, IRBinding)
        assert isinstance(body_binding.value, IRPromptExpr)

    def test_native_prompt_syntax_lowers_model_ref(self):
        ir = lower("let r = prompt @claude-sonnet: \"hello\"\n")
        binding = ir.body[0]
        assert isinstance(binding.value, IRPromptExpr)
        assert isinstance(binding.value.model, IRModelRef)
        assert binding.value.model.model_name == "claude-sonnet"


# ===========================================================================
# think
# ===========================================================================

class TestThinkLowering:
    def test_think_call_lowers_to_ir_think(self):
        ir = lower("let r = think(\"reason about this\")\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IRThinkExpr)


# ===========================================================================
# stream
# ===========================================================================

class TestStreamLowering:
    def test_stream_call_lowers_to_ir_stream(self):
        ir = lower("let s = stream(\"tell me a story\")\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IRStreamExpr)


# ===========================================================================
# embed
# ===========================================================================

class TestEmbedLowering:
    def test_embed_call_lowers_to_ir_embed(self):
        ir = lower("let v = embed(\"some text\")\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IREmbedExpr)


# ===========================================================================
# generate
# ===========================================================================

class TestGenerateLowering:
    def test_generate_call_lowers_to_ir_generate(self):
        ir = lower("let doc = generate(\"make a summary\")\n")
        binding = ir.body[0]
        assert isinstance(binding, IRBinding)
        assert isinstance(binding.value, IRGenerateExpr)

    def test_native_generate_target_type_is_preserved(self):
        ir = lower("let doc = generate @gpt-4o: \"make a summary\" -> Invoice\n")
        binding = ir.body[0]
        assert isinstance(binding.value, IRGenerateExpr)
        assert binding.value.target_type is not None
        assert binding.value.target_type.name == "Invoice"


class TestAgentDecoratorLowering:
    def test_agent_model_ref_colon_syntax_lowers(self):
        src = "@agent(model: @claude-sonnet)\nfn ask(q):\n    return prompt @claude-sonnet: q\n"
        ir = lower(src)
        node = ir.body[0]
        assert isinstance(node, IRAgentDecl)
        assert isinstance(node.model, IRModelRef)
        assert node.model.model_name == "claude-sonnet"
