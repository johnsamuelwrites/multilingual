#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""@agent and @tool decorator runtime tests."""
# pylint: disable=missing-class-docstring,import-error

import ast

import pytest

from multilingualprogramming.runtime.ai_runtime import AIRuntime, MockProvider
from multilingualprogramming.runtime.ai_types import ModelRef, Plan, ToolCall
from multilingualprogramming.runtime.tool_runtime import (
    AgentLoop,
    ToolRegistry,
    tool,
)


@pytest.fixture(autouse=True)
def reset():
    """Reset the shared AI runtime around each test."""
    AIRuntime.reset()
    yield
    AIRuntime.reset()


# ===========================================================================
# ToolRegistry
# ===========================================================================

class TestToolRegistry:
    def test_register_and_call(self):
        reg = ToolRegistry()

        def add(a: int, b: int) -> int:
            return a + b

        reg.register(add, description="Add two numbers")
        result = reg.call(ToolCall(name="add", arguments={"a": 2, "b": 3}))
        assert result.success
        assert result.output == 5

    def test_names_lists_all_tools(self):
        reg = ToolRegistry()

        def alpha():
            return "a"

        def beta():
            return "b"

        reg.register(alpha, description="A")
        reg.register(beta, description="B")
        assert set(reg.names()) == {"alpha", "beta"}

    def test_descriptions_returns_descriptions(self):
        reg = ToolRegistry()

        def mul(a, b):
            return a * b

        reg.register(mul, description="Multiply numbers")
        descs = reg.descriptions()
        assert "mul" in descs
        assert "Multiply numbers" in descs

    def test_call_missing_tool_returns_error(self):
        reg = ToolRegistry()
        result = reg.call(ToolCall(name="nonexistent", arguments={}))
        assert not result.success
        assert "nonexistent" in result.error


# ===========================================================================
# @tool decorator
# ===========================================================================

class TestToolDecorator:
    def test_tool_decorator_callable(self):
        @tool(description="Say hello")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert greet("World") == "Hello, World!"

    def test_tool_preserves_function(self):
        @tool(description="Square a number")
        def square(x: int) -> int:
            return x * x

        assert square(4) == 16

    def test_tool_marked_with_dunder(self):
        @tool(description="test")
        def my_tool():
            pass

        assert getattr(my_tool, "__tool__", False)


# ===========================================================================
# AgentLoop
# ===========================================================================

class TestAgentLoop:
    def test_agent_loop_runs_single_turn(self):
        provider = MockProvider()
        provider.add_response("The answer is 42.")
        AIRuntime.register(provider)

        reg = ToolRegistry()
        loop = AgentLoop(model=ModelRef("claude-sonnet"), registry=reg)
        result = loop.run("What is 6 times 7?")
        assert "42" in result

    def test_agent_loop_with_tool_call(self):
        reg = ToolRegistry()

        def multiply(a: int, b: int) -> int:
            return a * b

        reg.register(multiply, description="Multiply two numbers")

        provider = MockProvider()
        provider.add_response(
            '{"tool": "multiply", "arguments": {"a": 6, "b": 7}}'
        )
        provider.add_response("The result is 42.")
        AIRuntime.register(provider)

        loop = AgentLoop(model=ModelRef("claude-sonnet"), registry=reg)
        result = loop.run("What is 6 times 7?")
        assert result is not None

    def test_agent_loop_history_records_tool(self):
        reg = ToolRegistry()

        def calc(expr: str) -> int:
            """Evaluate a simple integer arithmetic expression for the test."""
            node = ast.parse(expr, mode="eval")
            assert isinstance(node.body, ast.BinOp)
            assert isinstance(node.body.op, ast.Mult)
            assert isinstance(node.body.left, ast.Constant)
            assert isinstance(node.body.right, ast.Constant)
            return int(node.body.left.value) * int(node.body.right.value)

        reg.register(calc, description="Calculate expression", name="calc")

        provider = MockProvider()
        provider.add_response('{"tool": "calc", "arguments": {"expr": "6*7"}}')
        provider.add_response("The result is 42.")
        AIRuntime.register(provider)

        loop = AgentLoop(model=ModelRef("m"), registry=reg)
        loop.run("What is 6*7?")
        assert loop.history[0]["tool"] == "calc"


# ===========================================================================
# Plan primitive
# ===========================================================================

class TestPlan:
    def test_plan_add_steps(self):
        p = Plan(goal="Write a report")
        p.add_step("Gather data")
        p.add_step("Analyse data")
        p.add_step("Write draft")
        assert len(p.steps) == 3

    def test_pending_steps(self):
        p = Plan(goal="Do things")
        p.add_step("Step A")
        p.add_step("Step B")
        p.steps[0].status = "done"
        pending = p.pending_steps()
        assert len(pending) == 1
        assert pending[0].description == "Step B"

    def test_completed_steps(self):
        p = Plan(goal="Do things")
        s = p.add_step("Step A")
        s.status = "done"
        p.add_step("Step B")
        assert len(p.completed_steps()) == 1

    def test_is_complete_all_done(self):
        p = Plan(goal="Done")
        s1 = p.add_step("A")
        s2 = p.add_step("B")
        assert not p.is_complete()
        s1.status = "done"
        s2.status = "done"
        assert p.is_complete()

    def test_summary_contains_goal(self):
        p = Plan(goal="Build something")
        p.add_step("Design")
        summary = p.summary()
        assert "Build something" in summary
        assert "Design" in summary

    def test_plan_step_index(self):
        p = Plan(goal="Steps")
        s0 = p.add_step("First")
        s1 = p.add_step("Second")
        assert s0.index == 0
        assert s1.index == 1
