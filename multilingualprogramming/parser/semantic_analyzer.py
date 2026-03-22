#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Semantic analyzer for the multilingual programming language AST and IR."""

from multilingualprogramming.core import ir_nodes as ir
from multilingualprogramming.parser.ast_nodes import (
    Identifier, TupleLiteral, StarredExpr,
)
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
    Walks the AST or semantic IR and performs semantic analysis:
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
        """Analyze an AST or IR program. Returns list of SemanticError."""
        self.errors = []
        self._visit(program)
        return self.errors

    def _visit(self, node):
        """Visit an AST or IR node using dynamic dispatch."""
        if node is None:
            return None
        if hasattr(node, "accept"):
            return node.accept(self)
        method = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        return method(node)

    def _visit_all(self, nodes):
        """Visit each node from *nodes* in order."""
        for node in nodes:
            self._visit(node)

    def _validate_parameters(self, params):
        """Validate Python-like parameter ordering and uniqueness."""
        seen_names = set()
        seen_default = False
        seen_vararg = False
        seen_kwarg = False

        for param in params:
            if isinstance(param, str):
                continue

            name = param.name
            if name in seen_names:
                self._report("DUPLICATE_DEFINITION", param, name=name)
            seen_names.add(name)

            if param.is_kwarg:
                if seen_kwarg or param.default is not None:
                    self._report("UNEXPECTED_TOKEN", param,
                                 token=f"invalid parameter '{name}'")
                seen_kwarg = True
                continue

            if param.is_vararg:
                if seen_vararg or seen_kwarg or param.default is not None:
                    self._report("UNEXPECTED_TOKEN", param,
                                 token=f"invalid parameter '{name}'")
                seen_vararg = True
                continue

            if seen_kwarg:
                self._report("UNEXPECTED_TOKEN", param,
                             token=f"parameter '{name}' after **kwargs")

            # Python allows required keyword-only params after *args.
            if not seen_vararg:
                if param.default is None and seen_default:
                    self._report("UNEXPECTED_TOKEN", param,
                                 token=f"non-default parameter '{name}' follows default parameter")
                if param.default is not None:
                    seen_default = True

    def _report(self, message_key, node, **kwargs):
        """Record a semantic error."""
        kwargs.setdefault("line", node.line)
        kwargs.setdefault("column", node.column)
        msg = self._error_registry.format(
            message_key, self.source_language, **kwargs
        )
        self.errors.append(SemanticError(msg, node.line, node.column))

    @staticmethod
    def _is_identifier(node):
        return isinstance(node, (Identifier, ir.IRIdentifier))

    @staticmethod
    def _is_tuple_target(node):
        return isinstance(node, (TupleLiteral, ir.IRTupleLiteral))

    @staticmethod
    def _is_starred_target(node):
        return isinstance(node, (StarredExpr, ir.IRStarredExpr))

    @staticmethod
    def _target_name(node):
        return getattr(node, "name", None)

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def visit_Program(self, node):
        self._visit_all(node.body)

    def visit_IRProgram(self, node):
        self._visit_all(node.body)

    def visit_VariableDeclaration(self, node):
        self._visit(node.value)
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name, "variable", is_const=node.is_const,
            line=node.line, column=node.column
        )

    def visit_IRBinding(self, node):
        self._visit(node.value)
        self._visit(node.annotation)
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name,
            "variable",
            is_const=(getattr(node, "binding_kind", "let") == "const"),
            line=node.line,
            column=node.column,
        )

    def visit_IRObserveBinding(self, node):
        self._visit(node.value)
        self._visit(node.annotation)
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name, "variable", line=node.line, column=node.column
        )

    def visit_Assignment(self, node):
        self._visit(node.value)
        # Tuple unpacking: define targets instead of looking them up
        if self._is_tuple_target(node.target):
            self._define_assignment_target(node.target)
        elif self._is_identifier(node.target):
            # Plain assignment (=) defines the variable if it does not yet exist.
            # Augmented assignment (+=, -= etc.) is read-modify-write, so the
            # variable must already be defined — report UNDEFINED_NAME if not.
            sym = self.symbol_table.lookup(node.target.name)
            if sym is None:
                if getattr(node, "op", "=") != "=":
                    # Augmented assignment requires the variable to exist first.
                    self._report("UNDEFINED_NAME", node.target, name=node.target.name)
                else:
                    self.symbol_table.define(
                        node.target.name, "variable",
                        line=node.target.line, column=node.target.column,
                    )
            elif sym.is_const:
                self._report("CONST_REASSIGNMENT", node, name=node.target.name)
        else:
            self._visit(node.target)
            # Check const reassignment for non-Identifier targets that carry a name
            if hasattr(node.target, 'name'):
                sym = self.symbol_table.lookup(node.target.name)
                if sym and sym.is_const:
                    self._report("CONST_REASSIGNMENT", node,
                                 name=node.target.name)

    def visit_IRAssignment(self, node):
        chain_targets = getattr(node, "chain_targets", None)
        if chain_targets:
            self._visit(node.value)
            for target in chain_targets:
                if self._is_identifier(target):
                    existing = self.symbol_table.lookup(target.name)
                    if existing is None:
                        self.symbol_table.define(
                            target.name,
                            "variable",
                            line=target.line,
                            column=target.column,
                        )
                    elif existing.is_const:
                        self._report(
                            "CONST_REASSIGNMENT", node, name=target.name
                        )
                elif self._is_tuple_target(target):
                    self._define_assignment_target(target)
                else:
                    self._visit(target)
            return
        self.visit_Assignment(node)

    def visit_AnnAssignment(self, node):
        if node.annotation:
            self._visit(node.annotation)
        if node.value:
            self._visit(node.value)
        if self._is_identifier(node.target):
            existing = self.symbol_table.lookup(node.target.name)
            if existing is None:
                self.symbol_table.define(
                    node.target.name, "variable",
                    line=node.target.line, column=node.target.column
                )
        else:
            self._visit(node.target)

    def _define_assignment_target(self, target):
        """Define variables in a tuple unpacking assignment target."""
        if self._is_identifier(target):
            existing = self.symbol_table.lookup(target.name)
            if existing is None:
                self.symbol_table.define(
                    target.name, "variable",
                    line=target.line, column=target.column
                )
        elif self._is_starred_target(target):
            self._define_assignment_target(target.value)
        elif self._is_tuple_target(target):
            for elem in target.elements:
                self._define_assignment_target(elem)
        else:
            self._visit(target)

    def visit_ExpressionStatement(self, node):
        self._visit(node.expression)

    def visit_IRExprStatement(self, node):
        self._visit(node.expression)

    def visit_Identifier(self, node):
        sym = self.symbol_table.lookup(node.name)
        if sym is None:
            self._report("UNDEFINED_NAME", node, name=node.name)

    def visit_IRIdentifier(self, node):
        self.visit_Identifier(node)

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

    def visit_IRLiteral(self, _node):
        pass

    def visit_ListLiteral(self, node):
        self._visit_all(node.elements)

    def visit_IRListLiteral(self, node):
        self._visit_all(node.elements)

    def visit_DictLiteral(self, node):
        for entry in node.entries:
            if isinstance(entry, tuple):
                key, value = entry
                self._visit(key)
                self._visit(value)
            else:
                self._visit(entry)

    def visit_IRDictLiteral(self, node):
        self.visit_DictLiteral(node)

    def visit_SetLiteral(self, node):
        self._visit_all(node.elements)

    def visit_IRSetLiteral(self, node):
        self._visit_all(node.elements)

    def visit_DictUnpackEntry(self, node):
        self._visit(node.value)

    def visit_BinaryOp(self, node):
        self._visit(node.left)
        self._visit(node.right)

    def visit_IRBinaryOp(self, node):
        self.visit_BinaryOp(node)

    def visit_UnaryOp(self, node):
        self._visit(node.operand)

    def visit_IRUnaryOp(self, node):
        self.visit_UnaryOp(node)

    def visit_BooleanOp(self, node):
        self._visit_all(node.values)

    def visit_IRBooleanOp(self, node):
        self._visit_all(node.values)

    def visit_CompareOp(self, node):
        self._visit(node.left)
        for _op, right in node.comparators:
            self._visit(right)

    def visit_IRCompareOp(self, node):
        self.visit_CompareOp(node)

    def visit_CallExpr(self, node):
        self._visit(node.func)
        for arg in node.args:
            self._visit(arg)
        for _name, val in node.keywords:
            self._visit(val)

    def visit_IRCallExpr(self, node):
        self.visit_CallExpr(node)

    def visit_AttributeAccess(self, node):
        self._visit(node.obj)

    def visit_IRAttributeAccess(self, node):
        self.visit_AttributeAccess(node)

    def visit_IndexAccess(self, node):
        self._visit(node.obj)
        self._visit(node.index)

    def visit_IRIndexAccess(self, node):
        self.visit_IndexAccess(node)

    def visit_SliceExpr(self, node):
        self._visit(node.start)
        self._visit(node.stop)
        self._visit(node.step)

    def visit_IRSliceExpr(self, node):
        self.visit_SliceExpr(node)

    def visit_StarredExpr(self, node):
        self._visit(node.value)

    def visit_IRStarredExpr(self, node):
        self.visit_StarredExpr(node)

    def visit_TupleLiteral(self, node):
        self._visit_all(node.elements)

    def visit_IRTupleLiteral(self, node):
        self._visit_all(node.elements)

    def visit_IRFStringLiteral(self, node):
        self.visit_FStringLiteral(node)

    def visit_LambdaExpr(self, node):
        self.symbol_table.enter_scope("lambda", "function")
        self._in_function += 1
        params = getattr(node, "params", getattr(node, "parameters", []))
        self._validate_parameters(params)
        for param in params:
            if isinstance(param, str):
                self.symbol_table.define(
                    param, "parameter", line=node.line, column=node.column
                )
            else:
                if param.default:
                    self._visit(param.default)
                self.symbol_table.define(
                    param.name, "parameter",
                    line=param.line, column=param.column
                )
        self._visit(node.body)
        self._in_function -= 1
        self.symbol_table.exit_scope()

    def visit_IRLambdaExpr(self, node):
        self.visit_LambdaExpr(node)

    def visit_YieldExpr(self, node):
        if self._in_function == 0:
            self._report("YIELD_OUTSIDE_FUNCTION", node)
        if node.value:
            self._visit(node.value)

    def visit_IRYieldExpr(self, node):
        self.visit_YieldExpr(node)

    def visit_AwaitExpr(self, node):
        if self._in_async_function == 0:
            self._report("UNEXPECTED_TOKEN", node, token="await")
        self._visit(node.value)

    def visit_IRAwaitExpr(self, node):
        self.visit_AwaitExpr(node)

    def visit_NamedExpr(self, node):
        self._visit(node.value)
        if self._is_identifier(node.target):
            existing = self.symbol_table.lookup(node.target.name)
            if existing is None:
                self.symbol_table.define(
                    node.target.name, "variable",
                    line=node.target.line, column=node.target.column
                )
        else:
            self._visit(node.target)

    def visit_IRNamedExpr(self, node):
        if isinstance(node.target, str):
            target = ir.IRIdentifier(
                name=node.target, line=node.line, column=node.column
            )
            self.visit_NamedExpr(
                ir.IRNamedExpr(
                    target=target, value=node.value, line=node.line, column=node.column
                )
            )
            return
        self.visit_NamedExpr(node)

    def visit_ConditionalExpr(self, node):
        self._visit(node.condition)
        self._visit(node.true_expr)
        self._visit(node.false_expr)

    def visit_IRConditionalExpr(self, node):
        self.visit_ConditionalExpr(node)

    # -- Simple statements --

    def visit_PassStatement(self, _node):
        pass

    def visit_IRPassStatement(self, _node):
        pass

    def visit_ReturnStatement(self, node):
        if self._in_function == 0:
            self._report("RETURN_OUTSIDE_FUNCTION", node)
        if node.value:
            self._visit(node.value)

    def visit_IRReturnStatement(self, node):
        self.visit_ReturnStatement(node)

    def visit_BreakStatement(self, node):
        if self._in_loop == 0:
            self._report("BREAK_OUTSIDE_LOOP", node)

    def visit_IRBreakStatement(self, node):
        self.visit_BreakStatement(node)

    def visit_ContinueStatement(self, node):
        if self._in_loop == 0:
            self._report("CONTINUE_OUTSIDE_LOOP", node)

    def visit_IRContinueStatement(self, node):
        self.visit_ContinueStatement(node)

    def visit_RaiseStatement(self, node):
        if node.value:
            self._visit(node.value)
        if getattr(node, "cause", None):
            self._visit(node.cause)

    def visit_IRRaiseStatement(self, node):
        self.visit_RaiseStatement(node)

    def visit_DelStatement(self, node):
        self._visit(node.target)

    def visit_IRDelStatement(self, node):
        self.visit_DelStatement(node)

    def visit_AssertStatement(self, node):
        self._visit(node.test)
        if node.msg:
            self._visit(node.msg)

    def visit_IRAssertStatement(self, node):
        self.visit_AssertStatement(node)

    def visit_ChainedAssignment(self, node):
        self._visit(node.value)
        for target in node.targets:
            if self._is_identifier(target):
                existing = self.symbol_table.lookup(target.name)
                if existing is None:
                    self.symbol_table.define(
                        target.name, "variable",
                        line=target.line, column=target.column
                    )
            elif self._is_tuple_target(target):
                self._define_assignment_target(target)
            else:
                self._visit(target)

    def visit_GlobalStatement(self, node):
        for name in node.names:
            # Define in current scope so references don't trigger "undefined"
            self.symbol_table.define(
                name, "variable", line=node.line, column=node.column
            )

    def visit_IRGlobalStatement(self, node):
        self.visit_GlobalStatement(node)

    def visit_LocalStatement(self, node):
        for name in node.names:
            # Define in current scope so references don't trigger "undefined"
            self.symbol_table.define(
                name, "variable", line=node.line, column=node.column
            )

    def visit_IRNonlocalStatement(self, node):
        self.visit_LocalStatement(node)

    def visit_YieldStatement(self, node):
        if self._in_function == 0:
            self._report("YIELD_OUTSIDE_FUNCTION", node)
        if node.value:
            self._visit(node.value)

    def visit_IRYieldStatement(self, node):
        self.visit_YieldStatement(node)

    # -- Compound statements --

    def visit_IfStatement(self, node):
        self._visit(node.condition)
        self._visit_all(node.body)
        for elif_cond, elif_body in node.elif_clauses:
            self._visit(elif_cond)
            self._visit_all(elif_body)
        if node.else_body:
            self._visit_all(node.else_body)

    def visit_IRIfStatement(self, node):
        self._visit(node.condition)
        self._visit_all(node.body)
        for clause in node.elif_clauses:
            self._visit(clause.condition)
            self._visit_all(clause.body)
        self._visit_all(node.else_body)

    def visit_WhileLoop(self, node):
        self._visit(node.condition)
        self._in_loop += 1
        self._visit_all(node.body)
        self._in_loop -= 1
        if node.else_body:
            self._visit_all(node.else_body)

    def visit_IRWhileLoop(self, node):
        self.visit_WhileLoop(node)

    def visit_ForLoop(self, node):
        if getattr(node, "is_async", False) and self._in_async_function == 0:
            self._report("UNEXPECTED_TOKEN", node, token="async for")
        self._visit(node.iterable)
        self._define_for_target(node.target)
        self._in_loop += 1
        self._visit_all(node.body)
        self._in_loop -= 1
        if getattr(node, "else_body", None):
            self._visit_all(node.else_body)

    def visit_IRForLoop(self, node):
        self.visit_ForLoop(node)

    def _define_for_target(self, target):
        """Define for-loop target variable(s) in the current scope."""
        if self._is_tuple_target(target):
            for elem in target.elements:
                self._define_for_target(elem)
        elif self._is_starred_target(target):
            self._define_for_target(target.value)
        else:
            self.symbol_table.define(
                target.name, "variable",
                line=target.line, column=target.column
            )

    def visit_FunctionDef(self, node):
        # Visit decorators
        for dec in getattr(node, 'decorators', []):
            self._visit(dec)
        params = getattr(node, "params", getattr(node, "parameters", []))
        self.symbol_table.define(
            node.name, "function", line=node.line, column=node.column
        )
        self.symbol_table.enter_scope(node.name, "function")
        self._in_function += 1
        if getattr(node, "is_async", False):
            self._in_async_function += 1
        self._validate_parameters(params)
        for param in params:
            if isinstance(param, str):
                self.symbol_table.define(
                    param, "parameter", line=node.line, column=node.column
                )
            else:
                # Parameter node
                if getattr(param, "annotation", None):
                    self._visit(param.annotation)
                if param.default:
                    self._visit(param.default)
                self.symbol_table.define(
                    param.name, "parameter",
                    line=param.line, column=param.column
                )
        if getattr(node, "return_annotation", None):
            self._visit(node.return_annotation)
        self._visit_all(node.body)
        if getattr(node, "is_async", False):
            self._in_async_function -= 1
        self._in_function -= 1
        self.symbol_table.exit_scope()

    def visit_IRFunction(self, node):
        self.visit_FunctionDef(node)

    def visit_IRAgentDecl(self, node):
        self._visit(node.model)
        self.visit_FunctionDef(node)

    def visit_IRToolDecl(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        # Visit decorators
        for dec in getattr(node, 'decorators', []):
            self._visit(dec)
        self.symbol_table.define(
            node.name, "class", line=node.line, column=node.column
        )
        self.symbol_table.enter_scope(node.name, "class")
        for base in node.bases:
            self._visit(base)
        self._visit_all(node.body)
        self.symbol_table.exit_scope()

    def visit_IRClassDecl(self, node):
        self.visit_ClassDef(node)

    def visit_IRTypeDecl(self, node):
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name, "class", line=node.line, column=node.column
        )

    def visit_IREnumDecl(self, node):
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._report("DUPLICATE_DEFINITION", node, name=node.name)
        self.symbol_table.define(
            node.name, "class", line=node.line, column=node.column
        )

    def visit_TryStatement(self, node):
        self._visit_all(node.body)
        for handler in node.handlers:
            self._visit(handler)
        if node.else_body:
            self._visit_all(node.else_body)
        if node.finally_body:
            self._visit_all(node.finally_body)

    def visit_IRTryStatement(self, node):
        self.visit_TryStatement(node)

    def visit_ExceptHandler(self, node):
        self.symbol_table.enter_scope("except", "block")
        if node.exc_type:
            self._visit(node.exc_type)
        if node.name:
            self.symbol_table.define(
                node.name, "variable",
                line=node.line, column=node.column
            )
        self._visit_all(node.body)
        self.symbol_table.exit_scope()

    def visit_IRExceptHandler(self, node):
        self.visit_ExceptHandler(node)

    def visit_MatchStatement(self, node):
        self._visit(node.subject)
        for case in node.cases:
            self._visit(case)

    def visit_IRMatchStatement(self, node):
        self._visit(node.subject)
        for case in node.cases:
            self._visit(case)

    def visit_CaseClause(self, node):
        if node.pattern:
            self._visit(node.pattern)
        if getattr(node, "guard", None):
            self._visit(node.guard)
        self._visit_all(node.body)

    def visit_IRMatchCase(self, node):
        self.symbol_table.enter_scope("case", "block")
        if node.pattern:
            self._visit(node.pattern)
        self._visit_all(node.body)
        self.symbol_table.exit_scope()

    def visit_WithStatement(self, node):
        if getattr(node, "is_async", False) and self._in_async_function == 0:
            self._report("UNEXPECTED_TOKEN", node, token="async with")
        for context_expr, _name in node.items:
            self._visit(context_expr)
        self.symbol_table.enter_scope("with", "block")
        for _context_expr, name in node.items:
            if name:
                self.symbol_table.define(
                    name, "variable",
                    line=node.line, column=node.column
                )
        self._visit_all(node.body)
        self.symbol_table.exit_scope()

    def visit_IRWithStatement(self, node):
        self.visit_WithStatement(node)

    def visit_ListComprehension(self, node):
        self.symbol_table.enter_scope("listcomp", "block")
        for clause in getattr(node, "clauses", [node]):
            self._visit(clause.iterable)
            if isinstance(clause.target, str):
                self.symbol_table.define(
                    clause.target, "variable",
                    line=node.line, column=node.column
                )
            else:
                self._define_comp_target(clause.target, node)
            for cond in clause.conditions:
                self._visit(cond)
        self._visit(node.element)
        self.symbol_table.exit_scope()

    def visit_IRListComp(self, node):
        self.visit_ListComprehension(node)

    def visit_DictComprehension(self, node):
        self.symbol_table.enter_scope("dictcomp", "block")
        for clause in getattr(node, "clauses", [node]):
            self._visit(clause.iterable)
            if isinstance(clause.target, str):
                self.symbol_table.define(
                    clause.target, "variable",
                    line=node.line, column=node.column
                )
            else:
                self._define_comp_target(clause.target, node)
            for cond in clause.conditions:
                self._visit(cond)
        self._visit(node.key)
        self._visit(node.value)
        self.symbol_table.exit_scope()

    def visit_IRDictComp(self, node):
        self.visit_DictComprehension(node)

    def visit_GeneratorExpr(self, node):
        self.symbol_table.enter_scope("genexpr", "block")
        for clause in getattr(node, "clauses", [node]):
            self._visit(clause.iterable)
            if isinstance(clause.target, str):
                self.symbol_table.define(
                    clause.target, "variable",
                    line=node.line, column=node.column
                )
            else:
                self._define_comp_target(clause.target, node)
            for cond in clause.conditions:
                self._visit(cond)
        self._visit(node.element)
        self.symbol_table.exit_scope()

    def visit_IRGeneratorExpr(self, node):
        self.visit_GeneratorExpr(node)

    def visit_SetComprehension(self, node):
        self.symbol_table.enter_scope("setcomp", "block")
        for clause in getattr(node, "clauses", [node]):
            self._visit(clause.iterable)
            if isinstance(clause.target, str):
                self.symbol_table.define(
                    clause.target, "variable",
                    line=node.line, column=node.column
                )
            else:
                self._define_comp_target(clause.target, node)
            for cond in clause.conditions:
                self._visit(cond)
        self._visit(node.element)
        self.symbol_table.exit_scope()

    def visit_IRSetComp(self, node):
        self.visit_SetComprehension(node)

    def _define_comp_target(self, target, node):
        """Define comprehension target variable(s) in current scope."""
        if self._is_identifier(target):
            self.symbol_table.define(
                target.name, "variable",
                line=target.line, column=target.column
            )
        elif self._is_starred_target(target):
            self._define_comp_target(target.value, node)
        elif self._is_tuple_target(target):
            for elem in target.elements:
                self._define_comp_target(elem, node)

    def visit_FStringLiteral(self, node):
        for part in node.parts:
            if not isinstance(part, str):
                self._visit(part)

    def visit_ImportStatement(self, node):
        name = node.alias or node.module
        self.symbol_table.define(
            name, "variable", line=node.line, column=node.column
        )

    def visit_IRImportStatement(self, node):
        self.visit_ImportStatement(node)

    def visit_FromImportStatement(self, node):
        for name, alias in node.names:
            sym_name = alias or name
            self.symbol_table.define(
                sym_name, "variable", line=node.line, column=node.column
            )

    def visit_IRFromImportStatement(self, node):
        self.visit_FromImportStatement(node)

    def visit_IRModelRef(self, _node):
        pass

    def visit_IRPromptExpr(self, node):
        self._visit(node.model)
        self._visit(node.template)

    def visit_IRGenerateExpr(self, node):
        self._visit(node.model)
        self._visit(node.template)

    def visit_IRThinkExpr(self, node):
        self._visit(node.model)
        self._visit(node.template)

    def visit_IRStreamExpr(self, node):
        self._visit(node.model)
        self._visit(node.template)

    def visit_IREmbedExpr(self, node):
        self._visit(node.model)
        self._visit(node.value)

    def visit_IRExtractExpr(self, node):
        self._visit(node.model)
        self._visit(node.source)

    def visit_IRClassifyExpr(self, node):
        self._visit(node.model)
        self._visit(node.subject)
        self._visit_all(node.categories)

    def visit_IRPlanExpr(self, node):
        self._visit(node.model)
        self._visit(node.goal)

    def visit_IRTranscribeExpr(self, node):
        self._visit(node.model)
        self._visit(node.source)

    def visit_IRRetrieveExpr(self, node):
        self._visit(node.index)
        self._visit(node.query)
        self._visit(node.model)

    def visit_IRSemanticMatchOp(self, node):
        self._visit(node.left)
        self._visit(node.right)
        self._visit(node.model)

    def visit_IRPipeExpr(self, node):
        self._visit(node.left)
        self._visit(node.right)

    def visit_IRResultPropagation(self, node):
        self._visit(node.operand)

    def visit_IROnChange(self, node):
        self._visit(node.signal)
        self._visit_all(node.body)

    def visit_IRCanvasBlock(self, node):
        self._visit_all(node.children)

    def visit_IRRenderExpr(self, node):
        self._visit(node.target)
        self._visit(node.value)

    def visit_IRViewBinding(self, node):
        self._visit(node.signal)
        self._visit(node.target)

    def visit_IRLiteralPattern(self, node):
        self._visit(node.value)

    def visit_IRCapturePattern(self, node):
        if self.symbol_table.lookup_local(node.name) is None:
            self.symbol_table.define(
                node.name, "variable", line=node.line, column=node.column
            )

    def visit_IRWildcardPattern(self, _node):
        pass

    def visit_IROrPattern(self, node):
        for alternative in node.alternatives:
            self._visit(alternative)

    def visit_IRSequencePattern(self, node):
        self._visit_all(node.elements)

    def visit_IRRecordPattern(self, node):
        for value in node.fields.values():
            self._visit(value)

    def visit_IRGuardedPattern(self, node):
        self._visit(node.pattern)
        self._visit(node.guard)

    def visit_IRAsPattern(self, node):
        self._visit(node.pattern)
        if self.symbol_table.lookup_local(node.name) is None:
            self.symbol_table.define(
                node.name, "variable", line=node.line, column=node.column
            )

    def visit_IRSemanticPattern(self, node):
        self._visit(node.template)

    def generic_visit(self, _node):
        """Ignore unsupported nodes during semantic traversal."""
        return None
