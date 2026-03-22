#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core package for semantic internal representations."""

from multilingualprogramming.core.ir_nodes import IRBinding, IRFunction, IRProgram
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.validators import validate_semantic_ir

__all__ = [
    "IRBinding",
    "IRFunction",
    "IRProgram",
    "lower_to_semantic_ir",
    "validate_semantic_ir",
]
