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
class ListLiteral(ASTNode):
    """List literal [a, b, c]."""
    def __init__(self, elements, line=0, column=0):
        super().__init__(line, column)
        self.elements = elements
class DictLiteral(ASTNode):
    """Dict literal {key: value, ...}."""
    def __init__(self, entries, line=0, column=0):
        super().__init__(line, column)
        self.entries = entries
        # Backward compatibility for code that expects key/value pairs only.
        self.pairs = [
            entry for entry in entries
            if isinstance(entry, tuple) and len(entry) == 2
        ]
class SetLiteral(ASTNode):
    """Set literal {a, b, c}."""
    def __init__(self, elements, line=0, column=0):
        super().__init__(line, column)
        self.elements = elements
class DictUnpackEntry(ASTNode):
    """Dictionary unpacking entry: **expr."""
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value
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
    """Yield expression: yield [from] value."""
    def __init__(self, value=None, is_from=False, line=0, column=0):
        super().__init__(line, column)
        self.value = value
        self.is_from = is_from
class AwaitExpr(ASTNode):
    """Await expression: await value."""
    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = value
class NamedExpr(ASTNode):
    """Named expression (walrus): target := value."""
    def __init__(self, target, value, line=0, column=0):
        super().__init__(line, column)
        self.target = target
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
class AnnAssignment(ASTNode):
    """Annotated assignment: x: T [= value]."""
    def __init__(self, target, annotation, value=None, line=0, column=0):
        super().__init__(line, column)
        self.target = target
        self.annotation = annotation
        self.value = value
class ExpressionStatement(ASTNode):
    """A bare expression used as a statement."""
    def __init__(self, expression, line=0, column=0):
        super().__init__(line, column)
        self.expression = expression
class PassStatement(ASTNode):
    """Pass/no-op statement."""
class ReturnStatement(ASTNode):
    """Return statement: return value."""
    def __init__(self, value=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value
class BreakStatement(ASTNode):
    """Break statement."""
class ContinueStatement(ASTNode):
    """Continue statement."""
class RaiseStatement(ASTNode):
    """Raise statement: raise expression [from cause]."""
    def __init__(self, value=None, cause=None, line=0, column=0):
        super().__init__(line, column)
        self.value = value
        self.cause = cause
class DelStatement(ASTNode):
    """Delete statement: del target."""
    def __init__(self, target, line=0, column=0):
        super().__init__(line, column)
        self.target = target
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
    """Yield as a statement: yield [from] value."""
    def __init__(self, value=None, is_from=False, line=0, column=0):
        super().__init__(line, column)
        self.value = value
        self.is_from = is_from
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
    """While loop: while condition: body [else: else_body]."""
    def __init__(self, condition, body, else_body=None, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body
        self.else_body = else_body
class ForLoop(ASTNode):
    """For loop: for target in iterable: body [else: else_body]."""
    def __init__(self, target, iterable, body, is_async=False,
                 else_body=None, line=0, column=0):
        super().__init__(line, column)
        self.target = target
        self.iterable = iterable
        self.body = body
        self.is_async = is_async
        self.else_body = else_body
class FunctionDef(ASTNode):
    """Function definition: def name(params): body."""
    def __init__(self, name, params, body, decorators=None,
                 return_annotation=None, is_async=False, **kwargs):
        line = kwargs.get("line", 0)
        column = kwargs.get("column", 0)
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body
        self.decorators = decorators or []
        self.return_annotation = return_annotation
        self.is_async = is_async
class ClassDef(ASTNode):
    """Class definition: class Name(bases): body."""
    def __init__(self, name, bases, body, decorators=None,
                 line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.bases = bases
        self.body = body
        self.decorators = decorators or []
class TryStatement(ASTNode):
    """Try/except/else/finally block."""
    def __init__(self, body, handlers=None, else_body=None, finally_body=None,
                 line=0, column=0):
        super().__init__(line, column)
        self.body = body
        self.handlers = handlers or []
        self.else_body = else_body
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
    """Single case or default clause with optional guard."""
    def __init__(self, pattern=None, body=None, is_default=False,
                 guard=None, line=0, column=0):
        super().__init__(line, column)
        self.pattern = pattern
        self.body = body or []
        self.is_default = is_default
        self.guard = guard
class WithStatement(ASTNode):
    """With statement: with expr as name, ...: body."""
    def __init__(self, items, name=None, body=None, is_async=False, line=0, column=0):
        super().__init__(line, column)
        # Backward compatibility: WithStatement(expr, name=..., body=...)
        if not isinstance(items, list):
            items = [(items, name)]
        self.items = items
        # Backward compatibility with old single-item attributes.
        self.context_expr = items[0][0] if items else None
        self.name = items[0][1] if items else None
        self.body = body or []
        self.is_async = is_async
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
# ---------------------------------------------------------------------------
# Extended expression nodes
# ---------------------------------------------------------------------------
class SliceExpr(ASTNode):
    """Slice expression: start:stop or start:stop:step."""
    def __init__(self, start=None, stop=None, step=None, line=0, column=0):
        super().__init__(line, column)
        self.start = start
        self.stop = stop
        self.step = step
class Parameter(ASTNode):
    """Function parameter with optional default, *args, **kwargs."""
    def __init__(self, name, default=None, is_vararg=False,
                 is_kwarg=False, annotation=None, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.default = default
        self.is_vararg = is_vararg
        self.is_kwarg = is_kwarg
        self.annotation = annotation
class StarredExpr(ASTNode):
    """Starred expression in call: *args or **kwargs."""
    def __init__(self, value, is_double=False, line=0, column=0):
        super().__init__(line, column)
        self.value = value
        self.is_double = is_double
class TupleLiteral(ASTNode):
    """Tuple literal or tuple unpacking target: a, b, c."""
    def __init__(self, elements, line=0, column=0):
        super().__init__(line, column)
        self.elements = elements
class ComprehensionClause(ASTNode):
    """Single comprehension clause: for target in iterable [if cond]..."""
    def __init__(self, target, iterable, conditions=None, line=0, column=0):
        super().__init__(line, column)
        self.target = target
        self.iterable = iterable
        self.conditions = conditions or []
class ListComprehension(ASTNode):
    """List comprehension: [expr for target in iterable if cond]."""
    def __init__(self, element, target, iterable, conditions=None,
                 clauses=None, line=0, column=0):
        super().__init__(line, column)
        self.element = element
        self.clauses = clauses or [
            ComprehensionClause(
                target, iterable, conditions or [], line=line, column=column
            )
        ]
        first = self.clauses[0]
        # Backward compatibility: expose first-clause fields.
        self.target = first.target
        self.iterable = first.iterable
        self.conditions = first.conditions
class DictComprehension(ASTNode):
    """Dict comprehension: {key: val for target in iterable if cond}."""
    def __init__(self, key, value, target, iterable, conditions=None,
                 clauses=None, **kwargs):
        line = kwargs.pop("line", 0)
        column = kwargs.pop("column", 0)
        if kwargs:
            extra = ", ".join(sorted(kwargs.keys()))
            raise TypeError(f"Unexpected keyword argument(s): {extra}")
        super().__init__(line, column)
        self.key = key
        self.value = value
        self.clauses = clauses or [
            ComprehensionClause(
                target, iterable, conditions or [], line=line, column=column
            )
        ]
        first = self.clauses[0]
        # Backward compatibility: expose first-clause fields.
        self.target = first.target
        self.iterable = first.iterable
        self.conditions = first.conditions
class GeneratorExpr(ASTNode):
    """Generator expression: (expr for target in iterable if cond)."""
    def __init__(self, element, target, iterable, conditions=None,
                 clauses=None, line=0, column=0):
        super().__init__(line, column)
        self.element = element
        self.clauses = clauses or [
            ComprehensionClause(
                target, iterable, conditions or [], line=line, column=column
            )
        ]
        first = self.clauses[0]
        # Backward compatibility: expose first-clause fields.
        self.target = first.target
        self.iterable = first.iterable
        self.conditions = first.conditions
class SetComprehension(ASTNode):
    """Set comprehension: {expr for target in iterable if cond}."""
    def __init__(self, element, target, iterable, conditions=None,
                 clauses=None, line=0, column=0):
        super().__init__(line, column)
        self.element = element
        self.clauses = clauses or [
            ComprehensionClause(
                target, iterable, conditions or [], line=line, column=column
            )
        ]
        first = self.clauses[0]
        self.target = first.target
        self.iterable = first.iterable
        self.conditions = first.conditions
class FStringLiteral(ASTNode):
    """F-string with interpolated expressions: f"text {expr} text"."""
    def __init__(self, parts, line=0, column=0):
        super().__init__(line, column)
        # parts: list of (str | ASTNode) alternating text and expressions
        self.parts = parts
class AssertStatement(ASTNode):
    """Assert statement: assert test [, msg]."""
    def __init__(self, test, msg=None, line=0, column=0):
        super().__init__(line, column)
        self.test = test
        self.msg = msg
class ChainedAssignment(ASTNode):
    """Chained assignment: a = b = c = value."""
    def __init__(self, targets, value, line=0, column=0):
        super().__init__(line, column)
        self.targets = targets
        self.value = value
