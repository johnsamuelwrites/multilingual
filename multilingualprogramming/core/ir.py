#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Typed core IR containers shared by all language frontends."""

from dataclasses import dataclass, field
from typing import Any

from multilingualprogramming.parser.ast_nodes import Program


@dataclass
class CoreIRProgram:
    """Language-agnostic, forward-only lowered program representation."""

    ast: Program
    source_language: str
    core_version: str = "0.1"
    frontend_metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self):
        """Validate minimal structural constraints of the core object."""
        if not isinstance(self.ast, Program):
            raise TypeError("CoreIRProgram.ast must be a Program AST node")
        if not isinstance(self.source_language, str) or not self.source_language:
            raise ValueError("CoreIRProgram.source_language must be a non-empty string")
