#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Lower parser AST into initial Core 1.0 semantic IR scaffolding."""

from multilingualprogramming.core.ir_nodes import IRProgram
from multilingualprogramming.parser.ast_nodes import Program


def lower_to_semantic_ir(program_ast: Program, source_language: str) -> IRProgram:
    """Create the initial semantic IR shell from a parsed program."""
    if not isinstance(program_ast, Program):
        raise TypeError("lower_to_semantic_ir expects a Program AST root")

    return IRProgram(
        body=[],
        source_language=source_language or "en",
        line=program_ast.line,
        column=program_ast.column,
    )
