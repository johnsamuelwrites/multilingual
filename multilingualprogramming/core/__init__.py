#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Core IR package for language-agnostic internal representations."""

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.core.lowering import lower_to_core_ir

__all__ = ["CoreIRProgram", "lower_to_core_ir"]
