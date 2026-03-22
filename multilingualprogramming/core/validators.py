#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Validation passes for Core 1.0 semantic IR.

Each validator accepts an IRProgram and raises ValueError with a descriptive
message on the first structural violation it finds.  They are designed to be
composed:

    validate_semantic_ir(program)   # structural checks
    validate_bindings(program)      # mutability and declaration checks
    validate_effects(program)       # capability annotation checks

All validators are also available through the single ``validate_all`` entry
point which runs every pass in sequence.
"""

from __future__ import annotations

from multilingualprogramming.core.ir_nodes import (
    IRAgentDecl,
    IRBinding,
    IRCanvasBlock,
    IRClassifyExpr,
    IREnumDecl,
    IREmbedExpr,
    IRExtractExpr,
    IRFunction,
    IRGenerateExpr,
    IRMatchStatement,
    IRNode,
    IRObserveBinding,
    IROnChange,
    IRPlanExpr,
    IRProgram,
    IRPromptExpr,
    IRRenderExpr,
    IRRetrieveExpr,
    IRSemanticMatchOp,
    IRStreamExpr,
    IRThinkExpr,
    IRToolDecl,
    IRTranscribeExpr,
    IRTypeDecl,
    IRViewBinding,
)


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def validate_all(program: IRProgram) -> list[str]:
    """Run all validation passes and return a list of diagnostic messages.

    Returns an empty list when the program is valid.
    Collects all diagnostics rather than stopping at the first error.
    """
    diagnostics: list[str] = []
    for fn in (
        _check_program_root,
        _check_bindings,
        _check_declarations,
        _check_effects,
        _check_effect_completeness,
        _check_match_statements,
    ):
        fn(program, diagnostics)
    return diagnostics


def validate_semantic_ir(program: IRProgram) -> None:
    """Validate minimal structural requirements.  Raises on first violation."""
    if not isinstance(program, IRProgram):
        raise TypeError("validate_semantic_ir expects an IRProgram")
    if not isinstance(program.source_language, str) or not program.source_language:
        raise ValueError("IRProgram.source_language must be a non-empty string")
    if not isinstance(program.body, list):
        raise ValueError("IRProgram.body must be a list")


def validate_bindings(program: IRProgram) -> None:
    """Check binding and declaration structural constraints."""
    diags: list[str] = []
    _check_bindings(program, diags)
    _check_declarations(program, diags)
    if diags:
        raise ValueError("\n".join(diags))


def validate_effects(program: IRProgram) -> None:
    """Check that effect annotations are well-formed."""
    diags: list[str] = []
    _check_effects(program, diags)
    if diags:
        raise ValueError("\n".join(diags))


# ---------------------------------------------------------------------------
# Internal check functions
# ---------------------------------------------------------------------------

_KNOWN_EFFECTS = frozenset({"ai", "ui", "net", "fs", "time", "process"})

# IR node types that require each capability effect
_AI_NODE_TYPES = (
    IRPromptExpr, IRGenerateExpr, IRThinkExpr, IRStreamExpr, IREmbedExpr,
    IRExtractExpr, IRClassifyExpr, IRPlanExpr, IRTranscribeExpr, IRRetrieveExpr,
    IRSemanticMatchOp,
)
_UI_NODE_TYPES = (
    IRCanvasBlock, IROnChange, IRRenderExpr, IRViewBinding,
)


def _check_program_root(program: IRProgram, diags: list[str]) -> None:
    if not isinstance(program.source_language, str) or not program.source_language:
        diags.append("IRProgram.source_language must be a non-empty string")
    if not isinstance(program.body, list):
        diags.append("IRProgram.body must be a list")
        return
    for i, node in enumerate(program.body):
        if not isinstance(node, IRNode):
            diags.append(f"IRProgram.body[{i}] is not an IRNode: {type(node).__name__!r}")


def _check_bindings(program: IRProgram, diags: list[str]) -> None:
    for node in _walk(program):
        if isinstance(node, IRBinding):
            if not node.name:
                diags.append(
                    f"IRBinding at {node.line}:{node.column} has an empty name"
                )
        if isinstance(node, IRObserveBinding):
            if not node.name:
                diags.append(
                    f"IRObserveBinding at {node.line}:{node.column} has an empty name"
                )
            if node.value is None:
                diags.append(
                    f"IRObserveBinding {node.name!r} at {node.line}:{node.column} "
                    f"has no initial value"
                )


def _check_declarations(program: IRProgram, diags: list[str]) -> None:
    for node in _walk(program):
        if isinstance(node, (IRFunction, IRAgentDecl, IRToolDecl)):
            if not node.name:
                diags.append(
                    f"{type(node).__name__} at {node.line}:{node.column} "
                    f"has an empty name"
                )
        if isinstance(node, IREnumDecl):
            if not node.name:
                diags.append(
                    f"IREnumDecl at {node.line}:{node.column} has an empty name"
                )
            if node.declared_type is None:
                diags.append(
                    f"IREnumDecl {node.name!r} has no declared type"
                )
        if isinstance(node, IRTypeDecl):
            if not node.name:
                diags.append(
                    f"IRTypeDecl at {node.line}:{node.column} has an empty name"
                )
        if isinstance(node, IRAgentDecl):
            if node.model is None:
                diags.append(
                    f"IRAgentDecl {node.name!r} at {node.line}:{node.column} "
                    f"has no model — @agent requires a model parameter"
                )
        if isinstance(node, IRToolDecl):
            if not node.description:
                diags.append(
                    f"IRToolDecl {node.name!r} at {node.line}:{node.column} "
                    f"has no description — @tool requires a description parameter"
                )


def _check_effects(program: IRProgram, diags: list[str]) -> None:
    for node in _walk(program):
        if isinstance(node, (IRFunction, IRAgentDecl, IRToolDecl)):
            for effect in node.effects.effects:
                if effect.name not in _KNOWN_EFFECTS:
                    diags.append(
                        f"{type(node).__name__} {node.name!r}: "
                        f"unknown capability {effect.name!r} "
                        f"(known: {sorted(_KNOWN_EFFECTS)})"
                    )


def _check_effect_completeness(program: IRProgram, diags: list[str]) -> None:
    """Check that every function/agent/tool declares the effects it actually uses.

    Walks each callable body and reports any capability that is used but not
    declared.  Also checks top-level statements against program-level effects.
    """
    # Collect callables (function/agent/tool) plus the program root itself
    callables: list[tuple[str, object, list[IRNode]]] = []
    for node in _walk(program):
        if isinstance(node, (IRFunction, IRAgentDecl, IRToolDecl)):
            callables.append((
                f"{type(node).__name__} {node.name!r}",
                node.effects,
                node.body,
            ))

    # Also check top-level statements against program-level effects
    callables.append(("module level", program.effects, program.body))

    for label, effects, body in callables:
        declared = {e.name for e in effects.effects}
        needs_ai = any(isinstance(n, _AI_NODE_TYPES) for n in _walk_list(body))
        needs_ui = any(isinstance(n, _UI_NODE_TYPES) for n in _walk_list(body))

        if needs_ai and "ai" not in declared:
            diags.append(
                f"{label} uses AI operations (prompt/generate/embed/…) "
                f"but does not declare 'uses ai'"
            )
        if needs_ui and "ui" not in declared:
            diags.append(
                f"{label} uses UI/reactive operations (canvas/on-change/render/…) "
                f"but does not declare 'uses ui'"
            )


def _check_match_statements(program: IRProgram, diags: list[str]) -> None:
    for node in _walk(program):
        if isinstance(node, IRMatchStatement):
            if node.subject is None:
                diags.append(
                    f"IRMatchStatement at {node.line}:{node.column} has no subject"
                )
            if not node.cases:
                diags.append(
                    f"IRMatchStatement at {node.line}:{node.column} has no cases"
                )


# ---------------------------------------------------------------------------
# Walk helper — yields every IRNode in the tree (depth-first, no recursion
# into non-IRNode values)
# ---------------------------------------------------------------------------

def _walk(node: IRNode):
    """Yield node and all IR descendant nodes depth-first."""
    yield node
    for field_value in vars(node).values():
        if isinstance(field_value, IRNode):
            yield from _walk(field_value)
        elif isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, IRNode):
                    yield from _walk(item)
        elif isinstance(field_value, tuple):
            for item in field_value:
                if isinstance(item, IRNode):
                    yield from _walk(item)


def _walk_list(nodes: list[IRNode]):
    """Yield all IR nodes reachable from a list of root nodes, depth-first.

    Does not descend into nested function/agent/tool bodies — those are
    checked separately as their own callables in _check_effect_completeness.
    """
    _callable_types = (IRFunction, IRAgentDecl, IRToolDecl)
    for node in nodes:
        if not isinstance(node, IRNode):
            continue
        yield node
        # Stop recursion at callable boundaries: a nested fn's body is covered
        # by its own entry in the callables list.
        if isinstance(node, _callable_types):
            continue
        for field_value in vars(node).values():
            if isinstance(field_value, IRNode):
                yield from _walk_list([field_value])
            elif isinstance(field_value, list):
                yield from _walk_list([i for i in field_value if isinstance(i, IRNode)])
            elif isinstance(field_value, tuple):
                yield from _walk_list([i for i in field_value if isinstance(i, IRNode)])
