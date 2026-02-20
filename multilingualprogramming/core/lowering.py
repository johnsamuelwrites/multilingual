#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Lowering boundary between language frontends and the shared core IR."""

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.parser.ast_nodes import Program


def lower_to_core_ir(program_ast, source_language, frontend_name="default"):
    """Lower a frontend AST into the typed core representation."""
    if not isinstance(program_ast, Program):
        raise TypeError("lower_to_core_ir expects a Program AST root")

    core = CoreIRProgram(
        ast=program_ast,
        source_language=source_language or "en",
        frontend_metadata={"frontend_name": frontend_name},
    )
    core.validate()
    return core
