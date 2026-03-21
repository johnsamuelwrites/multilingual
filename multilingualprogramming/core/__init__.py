#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core package for language-agnostic and semantic internal representations."""

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.core.lowering import lower_to_core_ir
from multilingualprogramming.core.ir_nodes import IRProgram
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.validators import validate_semantic_ir

__all__ = [
    "CoreIRProgram",
    "IRProgram",
    "lower_to_core_ir",
    "lower_to_semantic_ir",
    "validate_semantic_ir",
]
