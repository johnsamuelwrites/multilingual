#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Compatibility wrapper for the canonical semantic analyzer in core/."""

from multilingualprogramming.core.semantic_analyzer import (
    Scope,
    SemanticAnalyzer,
    Symbol,
    SymbolTable,
)

__all__ = [
    "Symbol",
    "Scope",
    "SymbolTable",
    "SemanticAnalyzer",
]
