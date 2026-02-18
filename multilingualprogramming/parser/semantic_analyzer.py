#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Semantic analyzer for the multilingual programming language AST."""

from multilingualprogramming.parser.ast_nodes import Identifier, TupleLiteral
from multilingualprogramming.parser.error_messages import ErrorMessageRegistry
from multilingualprogramming.exceptions import SemanticError


class Symbol:
    """Represents a declared name in a scope."""

    def __init__(self, name, symbol_type, is_const=False,
                 data_type=None, line=0, column=0):
        self.name = name
        self.symbol_type = symbol_type  # "variable", "function", "class", "parameter"
        self.is_const = is_const
        self.data_type = data_type
        self.line = line
        self.column = column

    def __repr__(self):
        return (f"Symbol({self.name!r}, {self.symbol_type!r}, "
                f"const={self.is_const}, type={self.data_type!r})")


class Scope:
    """A single scope level in the scope chain."""

    def __init__(self, name, scope_type, parent=None):
        self.name = name
        self.scope_type = scope_type  # "global", "function", "class", "block"
        self.parent = parent
        self.symbols = {}

    def define(self, symbol):
        """Define a symbol in this scope."""
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        """Look up a symbol, searching parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name):
        """Look up in this scope only."""
        return self.symbols.get(name)


class SymbolTable:
    """Manages the scope chain during semantic analysis."""

    def __init__(self):
        self.global_scope = Scope("global", "global")
        self.current_scope = self.global_scope

    def enter_scope(self, name, scope_type):
        """Push a new scope."""
        new_scope = Scope(name, scope_type, parent=self.current_scope)
        self.current_scope = new_scope
        return new_scope

    def exit_scope(self):
        """Pop back to the parent scope."""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent

    def define(self, name, symbol_type, is_const=False,
               data_type=None, line=0, column=0):
        """Define a symbol in the current scope."""
        symbol = Symbol(name, symbol_type, is_const, data_type, line, column)
        self.current_scope.define(symbol)
        return symbol

    def lookup(self, name):
        """Look up from current scope upward."""
        return self.current_scope.lookup(name)

    def lookup_local(self, name):
        """Look up in current scope only."""
        return self.current_scope.lookup_local(name)


# pylint: disable=too-many-public-methods
class SemanticAnalyzer:
    """
    Walks the AST and performs semantic analysis:
    - Scope resolution
    - Constant reassignment detection
    - Break/continue/return context validation
    - Basic type inference
    """

    def __init__(self, source_language="en"):
        self.symbol_table = SymbolTable()
        self.source_language = source_language
        self.errors = []
        self._in_loop = 0
        self._in_function = 0
        self._in_async_function = 0
        self._error_registry = ErrorMessageRegistry()

    def analyze(self, program):
        """Analyze the AST. Returns list of SemanticError."""
        self.errors = []
        program.accept(self)
        return self.errors

    def _report(self, message_key, node, **kwargs):
        """Record a semantic error."""
        kwargs.setdefault("line", node.line)
        kwargs.setdefault("column", node.column)
        msg = self._error_registry.format(
            message_key, self.source_language, **kwargs
        )
        self.errors.append(SemanticError(msg, node.line, node.column))

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def visit_Program(self, node):
        for stmt in node.body:
            stmt.accept(self)

    def visit_VariableDeclaration(self, node):
        node.value.accept(self)
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name, "variable", is_const=node.is_const,
            line=node.line, column=node.column
        )

    def visit_Assignment(self, node):
        node.value.accept(self)
        # Tuple unpacking: define targets instead of looking them up
        if isinstance(node.target, TupleLiteral):
            self._define_assignment_target(node.target)
        else:
            node.target.accept(self)
        # Check const reassignment
        if hasattr(node.target, 'name'):
            sym = self.symbol_table.lookup(node.target.name)
            if sym and sym.is_const:
                self._report("CONST_REASSIGNMENT", node,
                             name=node.target.name)

    def visit_AnnAssignment(self, node):
        if node.annotation:
            node.annotation.accept(self)
        if node.value:
            node.value.accept(self)
        if isinstance(node.target, Identifier):
            existing = self.symbol_table.lookup(node.target.name)
            if existing is None:
                self.symbol_table.define(
                    node.target.name, "variable",
                    line=node.target.line, column=node.target.column
                )
        else:
            node.target.accept(self)

    def _define_assignment_target(self, target):
        """Define variables in a tuple unpacking assignment target."""
        if isinstance(target, Identifier):
            existing = self.symbol_table.lookup(target.name)
            if existing is None:
                self.symbol_table.define(
                    target.name, "variable",
                    line=target.line, column=target.column
                )
        elif isinstance(target, TupleLiteral):
            for elem in target.elements:
                self._define_assignment_target(elem)
        else:
            target.accept(self)

    def visit_ExpressionStatement(self, node):
        node.expression.accept(self)

    def visit_Identifier(self, node):
        sym = self.symbol_table.lookup(node.name)
        if sym is None:
            self._report("UNDEFINED_NAME", node, name=node.name)

    def visit_NumeralLiteral(self, _node):
        pass

    def visit_StringLiteral(self, _node):
        pass

    def visit_DateLiteral(self, _node):
        pass

    def visit_BooleanLiteral(self, _node):
        pass

    def visit_NoneLiteral(self, _node):
        pass

    def visit_ListLiteral(self, node):
        for elem in node.elements:
            elem.accept(self)

    def visit_DictLiteral(self, node):
        for entry in node.entries:
            if isinstance(entry, tuple):
                key, value = entry
                key.accept(self)
                value.accept(self)
            else:
                entry.accept(self)

    def visit_SetLiteral(self, node):
        for elem in node.elements:
            elem.accept(self)

    def visit_DictUnpackEntry(self, node):
        node.value.accept(self)

    def visit_BinaryOp(self, node):
        node.left.accept(self)
        node.right.accept(self)

    def visit_UnaryOp(self, node):
        node.operand.accept(self)

    def visit_BooleanOp(self, node):
        for val in node.values:
            val.accept(self)

    def visit_CompareOp(self, node):
        node.left.accept(self)
        for _op, right in node.comparators:
            right.accept(self)

    def visit_CallExpr(self, node):
        node.func.accept(self)
        for arg in node.args:
            arg.accept(self)
        for _name, val in node.keywords:
            val.accept(self)

    def visit_AttributeAccess(self, node):
        node.obj.accept(self)

    def visit_IndexAccess(self, node):
        node.obj.accept(self)
        node.index.accept(self)

    def visit_SliceExpr(self, node):
        if node.start:
            node.start.accept(self)
        if node.stop:
            node.stop.accept(self)
        if node.step:
            node.step.accept(self)

    def visit_StarredExpr(self, node):
        node.value.accept(self)

    def visit_TupleLiteral(self, node):
        for elem in node.elements:
            elem.accept(self)

    def visit_LambdaExpr(self, node):
        self.symbol_table.enter_scope("lambda", "function")
        self._in_function += 1
        for param in node.params:
            if isinstance(param, str):
                self.symbol_table.define(
                    param, "parameter", line=node.line, column=node.column
                )
            else:
                if param.default:
                    param.default.accept(self)
                self.symbol_table.define(
                    param.name, "parameter",
                    line=param.line, column=param.column
                )
        node.body.accept(self)
        self._in_function -= 1
        self.symbol_table.exit_scope()

    def visit_YieldExpr(self, node):
        if self._in_function == 0:
            self._report("YIELD_OUTSIDE_FUNCTION", node)
        if node.value:
            node.value.accept(self)

    def visit_AwaitExpr(self, node):
        if self._in_async_function == 0:
            self._report("UNEXPECTED_TOKEN", node, token="await")
        node.value.accept(self)

    def visit_NamedExpr(self, node):
        node.value.accept(self)
        if isinstance(node.target, Identifier):
            existing = self.symbol_table.lookup(node.target.name)
            if existing is None:
                self.symbol_table.define(
                    node.target.name, "variable",
                    line=node.target.line, column=node.target.column
                )
        else:
            node.target.accept(self)

    def visit_ConditionalExpr(self, node):
        node.condition.accept(self)
        node.true_expr.accept(self)
        node.false_expr.accept(self)

    # -- Simple statements --

    def visit_PassStatement(self, _node):
        pass

    def visit_ReturnStatement(self, node):
        if self._in_function == 0:
            self._report("RETURN_OUTSIDE_FUNCTION", node)
        if node.value:
            node.value.accept(self)

    def visit_BreakStatement(self, node):
        if self._in_loop == 0:
            self._report("BREAK_OUTSIDE_LOOP", node)

    def visit_ContinueStatement(self, node):
        if self._in_loop == 0:
            self._report("CONTINUE_OUTSIDE_LOOP", node)

    def visit_RaiseStatement(self, node):
        if node.value:
            node.value.accept(self)

    def visit_AssertStatement(self, node):
        node.test.accept(self)
        if node.msg:
            node.msg.accept(self)

    def visit_ChainedAssignment(self, node):
        node.value.accept(self)
        for target in node.targets:
            if isinstance(target, Identifier):
                existing = self.symbol_table.lookup(target.name)
                if existing is None:
                    self.symbol_table.define(
                        target.name, "variable",
                        line=target.line, column=target.column
                    )
            elif isinstance(target, TupleLiteral):
                self._define_assignment_target(target)
            else:
                target.accept(self)

    def visit_GlobalStatement(self, _node):
        pass

    def visit_LocalStatement(self, _node):
        pass

    def visit_YieldStatement(self, node):
        if self._in_function == 0:
            self._report("YIELD_OUTSIDE_FUNCTION", node)
        if node.value:
            node.value.accept(self)

    # -- Compound statements --

    def visit_IfStatement(self, node):
        node.condition.accept(self)
        for stmt in node.body:
            stmt.accept(self)
        for elif_cond, elif_body in node.elif_clauses:
            elif_cond.accept(self)
            for stmt in elif_body:
                stmt.accept(self)
        if node.else_body:
            for stmt in node.else_body:
                stmt.accept(self)

    def visit_WhileLoop(self, node):
        node.condition.accept(self)
        self._in_loop += 1
        for stmt in node.body:
            stmt.accept(self)
        self._in_loop -= 1

    def visit_ForLoop(self, node):
        node.iterable.accept(self)
        self._define_for_target(node.target)
        self._in_loop += 1
        for stmt in node.body:
            stmt.accept(self)
        self._in_loop -= 1

    def _define_for_target(self, target):
        """Define for-loop target variable(s) in the current scope."""
        if isinstance(target, TupleLiteral):
            for elem in target.elements:
                self._define_for_target(elem)
        else:
            self.symbol_table.define(
                target.name, "variable",
                line=target.line, column=target.column
            )

    def visit_FunctionDef(self, node):
        # Visit decorators
        for dec in getattr(node, 'decorators', []):
            dec.accept(self)
        self.symbol_table.define(
            node.name, "function", line=node.line, column=node.column
        )
        self.symbol_table.enter_scope(node.name, "function")
        self._in_function += 1
        if getattr(node, "is_async", False):
            self._in_async_function += 1
        for param in node.params:
            if isinstance(param, str):
                self.symbol_table.define(
                    param, "parameter", line=node.line, column=node.column
                )
            else:
                # Parameter node
                if getattr(param, "annotation", None):
                    param.annotation.accept(self)
                if param.default:
                    param.default.accept(self)
                self.symbol_table.define(
                    param.name, "parameter",
                    line=param.line, column=param.column
                )
        if getattr(node, "return_annotation", None):
            node.return_annotation.accept(self)
        for stmt in node.body:
            stmt.accept(self)
        if getattr(node, "is_async", False):
            self._in_async_function -= 1
        self._in_function -= 1
        self.symbol_table.exit_scope()

    def visit_ClassDef(self, node):
        # Visit decorators
        for dec in getattr(node, 'decorators', []):
            dec.accept(self)
        self.symbol_table.define(
            node.name, "class", line=node.line, column=node.column
        )
        self.symbol_table.enter_scope(node.name, "class")
        for base in node.bases:
            base.accept(self)
        for stmt in node.body:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_TryStatement(self, node):
        for stmt in node.body:
            stmt.accept(self)
        for handler in node.handlers:
            handler.accept(self)
        if node.finally_body:
            for stmt in node.finally_body:
                stmt.accept(self)

    def visit_ExceptHandler(self, node):
        self.symbol_table.enter_scope("except", "block")
        if node.exc_type:
            node.exc_type.accept(self)
        if node.name:
            self.symbol_table.define(
                node.name, "variable",
                line=node.line, column=node.column
            )
        for stmt in node.body:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_MatchStatement(self, node):
        node.subject.accept(self)
        for case in node.cases:
            case.accept(self)

    def visit_CaseClause(self, node):
        if node.pattern:
            node.pattern.accept(self)
        for stmt in node.body:
            stmt.accept(self)

    def visit_WithStatement(self, node):
        for context_expr, _name in node.items:
            context_expr.accept(self)
        self.symbol_table.enter_scope("with", "block")
        for _context_expr, name in node.items:
            if name:
                self.symbol_table.define(
                    name, "variable",
                    line=node.line, column=node.column
                )
        for stmt in node.body:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_ListComprehension(self, node):
        self.symbol_table.enter_scope("listcomp", "block")
        node.iterable.accept(self)
        if isinstance(node.target, str):
            self.symbol_table.define(
                node.target, "variable",
                line=node.line, column=node.column
            )
        else:
            self._define_comp_target(node.target, node)
        node.element.accept(self)
        for cond in node.conditions:
            cond.accept(self)
        self.symbol_table.exit_scope()

    def visit_DictComprehension(self, node):
        self.symbol_table.enter_scope("dictcomp", "block")
        node.iterable.accept(self)
        if isinstance(node.target, str):
            self.symbol_table.define(
                node.target, "variable",
                line=node.line, column=node.column
            )
        else:
            self._define_comp_target(node.target, node)
        node.key.accept(self)
        node.value.accept(self)
        for cond in node.conditions:
            cond.accept(self)
        self.symbol_table.exit_scope()

    def visit_GeneratorExpr(self, node):
        self.symbol_table.enter_scope("genexpr", "block")
        node.iterable.accept(self)
        if isinstance(node.target, str):
            self.symbol_table.define(
                node.target, "variable",
                line=node.line, column=node.column
            )
        else:
            self._define_comp_target(node.target, node)
        node.element.accept(self)
        for cond in node.conditions:
            cond.accept(self)
        self.symbol_table.exit_scope()

    def _define_comp_target(self, target, node):
        """Define comprehension target variable(s) in current scope."""
        if isinstance(target, Identifier):
            self.symbol_table.define(
                target.name, "variable",
                line=target.line, column=target.column
            )
        elif isinstance(target, TupleLiteral):
            for elem in target.elements:
                self._define_comp_target(elem, node)

    def visit_FStringLiteral(self, node):
        for part in node.parts:
            if not isinstance(part, str):
                part.accept(self)

    def visit_ImportStatement(self, node):
        name = node.alias or node.module
        self.symbol_table.define(
            name, "variable", line=node.line, column=node.column
        )

    def visit_FromImportStatement(self, node):
        for name, alias in node.names:
            sym_name = alias or name
            self.symbol_table.define(
                sym_name, "variable", line=node.line, column=node.column
            )

    def generic_visit(self, _node):
        """Ignore unsupported nodes during semantic traversal."""
        return None
