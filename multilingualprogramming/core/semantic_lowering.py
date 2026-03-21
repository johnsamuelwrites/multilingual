#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Lower parser AST into initial Core 1.0 semantic IR scaffolding."""

from multilingualprogramming.core.ir_nodes import (
    IRBinding,
    IRExpression,
    IRFunction,
    IRProgram,
)
from multilingualprogramming.core.types import NamedType
from multilingualprogramming.parser.ast_nodes import FunctionDef, Identifier, Program, VariableDeclaration


def lower_to_semantic_ir(program_ast: Program, source_language: str) -> IRProgram:
    """Create the initial semantic IR shell from a parsed program."""
    if not isinstance(program_ast, Program):
        raise TypeError("lower_to_semantic_ir expects a Program AST root")

    return IRProgram(
        body=[_lower_node(node) for node in program_ast.body],
        source_language=source_language or "en",
        line=program_ast.line,
        column=program_ast.column,
    )


def _lower_node(node):
    """Lower a parser AST node into the initial semantic IR."""
    if isinstance(node, VariableDeclaration):
        return IRBinding(
            name=node.name,
            value=IRExpression(line=node.line, column=node.column),
            is_mutable=node.is_mutable,
            annotation=None,
            line=node.line,
            column=node.column,
        )
    if isinstance(node, FunctionDef):
        return IRFunction(
            name=node.name,
            parameters=[param.name for param in node.params],
            body=[_lower_node(stmt) for stmt in node.body],
            return_type=_lower_annotation(node.return_annotation),
            is_async=node.is_async,
            syntax_keyword=node.syntax_keyword,
            line=node.line,
            column=node.column,
        )
    return IRExpression(line=getattr(node, "line", 0), column=getattr(node, "column", 0))


def _lower_annotation(annotation):
    """Lower a narrow subset of annotation nodes into semantic types."""
    if annotation is None:
        return None
    if isinstance(annotation, Identifier):
        return NamedType(annotation.name)
    return NamedType(type(annotation).__name__)
