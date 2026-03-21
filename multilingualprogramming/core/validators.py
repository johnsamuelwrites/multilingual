#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Validation helpers for Core 1.0 semantic IR."""

from multilingualprogramming.core.ir_nodes import IRProgram


def validate_semantic_ir(program: IRProgram) -> None:
    """Validate minimal structural requirements for semantic IR."""
    if not isinstance(program, IRProgram):
        raise TypeError("validate_semantic_ir expects an IRProgram")
    if not isinstance(program.source_language, str) or not program.source_language:
        raise ValueError("IRProgram.source_language must be a non-empty string")
