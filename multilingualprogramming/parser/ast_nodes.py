#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""AST node classes for the multilingual programming language."""


class ASTNode:
    """Base class for all AST nodes."""

    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column

    def accept(self, visitor):
        """Visitor pattern dispatch."""
        method_name = f"visit_{type(self).__name__}"
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# ---------------------------------------------------------------------------
# Program root
# ---------------------------------------------------------------------------

class Program(ASTNode):
    """Root node containing a list of top-level statements."""

    def __init__(self, body, line=0, column=0):
        super().__init__(line, column)
        self.body = body


# ---------------------------------------------------------------------------
# Literal nodes
# ---------------------------------------------------------------------------

class NumeralLiteral(ASTNode):
    """Number literal (raw string from NUMERAL token)."""

    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class StringLiteral(ASTNode):
    """String literal (content without delimiters)."""

    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class DateLiteral(ASTNode):
    """Date literal from special delimiters."""

    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class BooleanLiteral(ASTNode):
    """TRUE or FALSE keyword as a literal value."""

    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class NoneLiteral(ASTNode):
    """NONE keyword as a literal value."""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)


class ListLiteral(ASTNode):
    """List literal [a, b, c]."""

    def __init__(self, elements, line=0, column=0):
        super().__init__(line, column)
        self.elements = elements


class DictLiteral(ASTNode):
    """Dict literal {key: value, ...}."""

    def __init__(self, pairs, line=0, column=0):
        super().__init__(line, column)
        self.pairs = pairs


# ---------------------------------------------------------------------------
# Expression nodes
# ---------------------------------------------------------------------------

class Identifier(ASTNode):
    """Variable or name reference."""

    def __init__(self, name, line=0, column=0):
        super().__init__(line, column)
        self.name = name


class BinaryOp(ASTNode):
    """Binary operation: left op right."""

    def __init__(self, left, op, right, line=0, column=0):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    """Unary operation: op operand."""

    def __init__(self, op, operand, line=0, column=0):
        super().__init__(line, column)
        self.op = op
        self.operand = operand


class BooleanOp(ASTNode):
    """Logical AND / OR with short-circuit semantics."""

    def __init__(self, op, values, line=0, column=0):
        super().__init__(line, column)
        self.op = op
        self.values = values


class CompareOp(ASTNode):
    """Chained comparison: a < b < c."""

    def __init__(self, left, comparators, line=0, column=0):
        super().__init__(line, column)
        self.left = left
        self.comparators = comparators


class CallExpr(ASTNode):
    """Function or method call: func(args)."""

    def __init__(self, func, args, keywords=None, line=0, column=0):
        super().__init__(line, column)
        self.func = func
        self.args = args
        self.keywords = keywords or []


class AttributeAccess(ASTNode):
    """Attribute access: obj.attr."""

    def __init__(self, obj, attr, line=0, column=0):
        super().__init__(line, column)
        self.obj = obj
        self.attr = attr


class IndexAccess(ASTNode):
    """Index/subscript access: obj[index]."""

    def __init__(self, obj, index, line=0, column=0):
        super().__init__(line, column)
        self.obj = obj
        self.index = index


class LambdaExpr(ASTNode):
    """Lambda expression: lambda params: body."""

    def __init__(self, params, body, line=0, column=0):
        super().__init__(line, column)
        self.params = params
        self.body = body


class YieldExpr(ASTNode):
    """Yield expression: yield value."""

    def __init__(self, value=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class ConditionalExpr(ASTNode):
    """Ternary conditional: true_expr if condition else false_expr."""

    def __init__(self, condition, true_expr, false_expr, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr


# ---------------------------------------------------------------------------
# Simple statement nodes
# ---------------------------------------------------------------------------

class VariableDeclaration(ASTNode):
    """Variable declaration: let x = expr / const PI = 3.14."""

    def __init__(self, name, value, is_const=False, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.value = value
        self.is_const = is_const


class Assignment(ASTNode):
    """Assignment: target = value (also +=, -=, *=, /=)."""

    def __init__(self, target, value, op="=", line=0, column=0):
        super().__init__(line, column)
        self.target = target
        self.value = value
        self.op = op


class ExpressionStatement(ASTNode):
    """A bare expression used as a statement."""

    def __init__(self, expression, line=0, column=0):
        super().__init__(line, column)
        self.expression = expression


class PassStatement(ASTNode):
    """Pass/no-op statement."""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)


class ReturnStatement(ASTNode):
    """Return statement: return value."""

    def __init__(self, value=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class BreakStatement(ASTNode):
    """Break statement."""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)


class ContinueStatement(ASTNode):
    """Continue statement."""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)


class RaiseStatement(ASTNode):
    """Raise statement: raise expression."""

    def __init__(self, value=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value


class GlobalStatement(ASTNode):
    """Global declaration: global x, y."""

    def __init__(self, names, line=0, column=0):
        super().__init__(line, column)
        self.names = names


class LocalStatement(ASTNode):
    """Local (nonlocal) declaration: local x, y."""

    def __init__(self, names, line=0, column=0):
        super().__init__(line, column)
        self.names = names


class YieldStatement(ASTNode):
    """Yield as a statement."""

    def __init__(self, value=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value


# ---------------------------------------------------------------------------
# Compound statement nodes
# ---------------------------------------------------------------------------

class IfStatement(ASTNode):
    """If/elif/else block."""

    def __init__(self, condition, body, elif_clauses=None,
                 else_body=None, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body
        self.elif_clauses = elif_clauses or []
        self.else_body = else_body


class WhileLoop(ASTNode):
    """While loop: while condition: body."""

    def __init__(self, condition, body, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body


class ForLoop(ASTNode):
    """For loop: for target in iterable: body."""

    def __init__(self, target, iterable, body, line=0, column=0):
        super().__init__(line, column)
        self.target = target
        self.iterable = iterable
        self.body = body


class FunctionDef(ASTNode):
    """Function definition: def name(params): body."""

    def __init__(self, name, params, body, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body


class ClassDef(ASTNode):
    """Class definition: class Name(bases): body."""

    def __init__(self, name, bases, body, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.bases = bases
        self.body = body


class TryStatement(ASTNode):
    """Try/except/finally block."""

    def __init__(self, body, handlers=None, finally_body=None,
                 line=0, column=0):
        super().__init__(line, column)
        self.body = body
        self.handlers = handlers or []
        self.finally_body = finally_body


class ExceptHandler(ASTNode):
    """Single except clause: except Type as name: body."""

    def __init__(self, exc_type=None, name=None, body=None,
                 line=0, column=0):
        super().__init__(line, column)
        self.exc_type = exc_type
        self.name = name
        self.body = body or []


class MatchStatement(ASTNode):
    """Match/case block."""

    def __init__(self, subject, cases, line=0, column=0):
        super().__init__(line, column)
        self.subject = subject
        self.cases = cases


class CaseClause(ASTNode):
    """Single case or default clause."""

    def __init__(self, pattern=None, body=None, is_default=False,
                 line=0, column=0):
        super().__init__(line, column)
        self.pattern = pattern
        self.body = body or []
        self.is_default = is_default


class WithStatement(ASTNode):
    """With statement: with expr as name: body."""

    def __init__(self, context_expr, name=None, body=None,
                 line=0, column=0):
        super().__init__(line, column)
        self.context_expr = context_expr
        self.name = name
        self.body = body or []


# ---------------------------------------------------------------------------
# Import nodes
# ---------------------------------------------------------------------------

class ImportStatement(ASTNode):
    """Simple import: import module as alias."""

    def __init__(self, module, alias=None, line=0, column=0):
        super().__init__(line, column)
        self.module = module
        self.alias = alias


class FromImportStatement(ASTNode):
    """From-import: from module import name1 as alias1, name2."""

    def __init__(self, module, names, line=0, column=0):
        super().__init__(line, column)
        self.module = module
        self.names = names
