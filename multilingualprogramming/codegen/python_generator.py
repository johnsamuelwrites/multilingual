#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Python code generator: transpiles the multilingual AST to valid Python source."""

from multilingualprogramming.exceptions import CodeGenerationError
from multilingualprogramming.numeral.mp_numeral import MPNumeral


class PythonCodeGenerator:
    """
    Visitor-based transpiler that converts a multilingual AST into
    valid Python 3 source code.

    NumeralLiteral values in any Unicode script are converted to Python
    numeric literals via MPNumeral.to_decimal().

    Usage:
        gen = PythonCodeGenerator()
        python_source = gen.generate(ast_program)
    """

    def __init__(self, indent_str="    "):
        self.indent_str = indent_str
        self._depth = 0
        self._lines = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, node):
        """Generate Python source from the AST root node."""
        self._depth = 0
        self._lines = []
        node.accept(self)
        return "\n".join(self._lines) + "\n"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _emit(self, text):
        """Add a line at the current indentation level."""
        self._lines.append(self.indent_str * self._depth + text)

    def _indent(self):
        self._depth += 1

    def _dedent(self):
        self._depth -= 1

    def _emit_body(self, body):
        """Emit a list of statements as an indented block."""
        self._indent()
        if not body:
            self._emit("pass")
        else:
            for stmt in body:
                stmt.accept(self)
        self._dedent()

    def _expr(self, node):
        """Generate the expression string for a node.

        Uses a sub-generator so expression visitors can return strings
        rather than emitting lines.
        """
        sub = _ExpressionGenerator()
        return node.accept(sub)

    def _error(self, message, node):
        """Raise a CodeGenerationError with source location."""
        raise CodeGenerationError(message, node.line, node.column)

    # ------------------------------------------------------------------
    # Statement visitors (emit lines)
    # ------------------------------------------------------------------

    def visit_Program(self, node):
        for stmt in node.body:
            stmt.accept(self)

    def visit_VariableDeclaration(self, node):
        val = self._expr(node.value)
        self._emit(f"{node.name} = {val}")

    def visit_Assignment(self, node):
        target = self._expr(node.target)
        val = self._expr(node.value)
        self._emit(f"{target} {node.op} {val}")

    def visit_ExpressionStatement(self, node):
        expr = self._expr(node.expression)
        self._emit(expr)

    def visit_PassStatement(self, _node):
        self._emit("pass")

    def visit_ReturnStatement(self, node):
        if node.value:
            val = self._expr(node.value)
            self._emit(f"return {val}")
        else:
            self._emit("return")

    def visit_BreakStatement(self, _node):
        self._emit("break")

    def visit_ContinueStatement(self, _node):
        self._emit("continue")

    def visit_RaiseStatement(self, node):
        if node.value:
            val = self._expr(node.value)
            self._emit(f"raise {val}")
        else:
            self._emit("raise")

    def visit_AssertStatement(self, node):
        test = self._expr(node.test)
        if node.msg:
            msg = self._expr(node.msg)
            self._emit(f"assert {test}, {msg}")
        else:
            self._emit(f"assert {test}")

    def visit_ChainedAssignment(self, node):
        targets = " = ".join(self._expr(t) for t in node.targets)
        value = self._expr(node.value)
        self._emit(f"{targets} = {value}")

    def visit_GlobalStatement(self, node):
        names = ", ".join(node.names)
        self._emit(f"global {names}")

    def visit_LocalStatement(self, node):
        names = ", ".join(node.names)
        self._emit(f"nonlocal {names}")

    def visit_YieldStatement(self, node):
        if node.value:
            val = self._expr(node.value)
            self._emit(f"yield {val}")
        else:
            self._emit("yield")

    # -- Compound statements --

    def visit_IfStatement(self, node):
        cond = self._expr(node.condition)
        self._emit(f"if {cond}:")
        self._emit_body(node.body)
        for elif_cond, elif_body in node.elif_clauses:
            econd = self._expr(elif_cond)
            self._emit(f"elif {econd}:")
            self._emit_body(elif_body)
        if node.else_body:
            self._emit("else:")
            self._emit_body(node.else_body)

    def visit_WhileLoop(self, node):
        cond = self._expr(node.condition)
        self._emit(f"while {cond}:")
        self._emit_body(node.body)

    def visit_ForLoop(self, node):
        target = self._expr(node.target)
        iterable = self._expr(node.iterable)
        self._emit(f"for {target} in {iterable}:")
        self._emit_body(node.body)

    def visit_FunctionDef(self, node):
        # Emit decorators
        for dec in getattr(node, 'decorators', []):
            dec_expr = self._expr(dec)
            self._emit(f"@{dec_expr}")
        # Build parameter list
        param_strs = []
        for param in node.params:
            if isinstance(param, str):
                param_strs.append(param)
            else:
                param_strs.append(self._expr(param))
        params = ", ".join(param_strs)
        self._emit(f"def {node.name}({params}):")
        self._emit_body(node.body)

    def visit_ClassDef(self, node):
        # Emit decorators
        for dec in getattr(node, 'decorators', []):
            dec_expr = self._expr(dec)
            self._emit(f"@{dec_expr}")
        if node.bases:
            bases = ", ".join(self._expr(b) for b in node.bases)
            self._emit(f"class {node.name}({bases}):")
        else:
            self._emit(f"class {node.name}:")
        self._emit_body(node.body)

    def visit_TryStatement(self, node):
        self._emit("try:")
        self._emit_body(node.body)
        for handler in node.handlers:
            handler.accept(self)
        if node.finally_body:
            self._emit("finally:")
            self._emit_body(node.finally_body)

    def visit_ExceptHandler(self, node):
        if node.exc_type:
            exc = self._expr(node.exc_type)
            if node.name:
                self._emit(f"except {exc} as {node.name}:")
            else:
                self._emit(f"except {exc}:")
        else:
            self._emit("except:")
        self._emit_body(node.body)

    def visit_MatchStatement(self, node):
        subject = self._expr(node.subject)
        self._emit(f"match {subject}:")
        self._indent()
        for case in node.cases:
            case.accept(self)
        self._dedent()

    def visit_CaseClause(self, node):
        if node.is_default:
            self._emit("case _:")
        else:
            pattern = self._expr(node.pattern)
            self._emit(f"case {pattern}:")
        self._emit_body(node.body)

    def visit_WithStatement(self, node):
        ctx = self._expr(node.context_expr)
        if node.name:
            self._emit(f"with {ctx} as {node.name}:")
        else:
            self._emit(f"with {ctx}:")
        self._emit_body(node.body)

    def visit_ImportStatement(self, node):
        if node.alias:
            self._emit(f"import {node.module} as {node.alias}")
        else:
            self._emit(f"import {node.module}")

    def visit_FromImportStatement(self, node):
        parts = []
        for name, alias in node.names:
            if alias:
                parts.append(f"{name} as {alias}")
            else:
                parts.append(name)
        names = ", ".join(parts)
        self._emit(f"from {node.module} import {names}")

    def generic_visit(self, node):
        self._error(
            f"Unsupported AST node type: {type(node).__name__}", node
        )


# ======================================================================
# Expression sub-generator (returns strings instead of emitting lines)
# ======================================================================

class _ExpressionGenerator:
    """Visitor that returns Python expression strings."""

    def _expr(self, node):
        """Recursively generate an expression string."""
        return node.accept(self)

    def _convert_numeral(self, raw_value):
        """Convert a multilingual numeral string to a Python numeric literal."""
        try:
            num = MPNumeral(raw_value)
            decimal = num.to_decimal()
            # Preserve integer vs float
            if isinstance(decimal, float):
                return repr(decimal)
            return str(decimal)
        except Exception:
            # If MPNumeral can't parse it, try as a raw Python number
            try:
                val = int(raw_value)
                return str(val)
            except ValueError:
                try:
                    val = float(raw_value)
                    return repr(val)
                except ValueError:
                    return raw_value

    # -- Literals --

    def visit_NumeralLiteral(self, node):
        return self._convert_numeral(node.value)

    def visit_StringLiteral(self, node):
        return repr(node.value)

    def visit_DateLiteral(self, node):
        # Emit as a string for runtime parsing
        return repr(node.value)

    def visit_BooleanLiteral(self, node):
        return "True" if node.value else "False"

    def visit_NoneLiteral(self, _node):
        return "None"

    def visit_ListLiteral(self, node):
        elems = ", ".join(self._expr(e) for e in node.elements)
        return f"[{elems}]"

    def visit_DictLiteral(self, node):
        pairs = ", ".join(
            f"{self._expr(k)}: {self._expr(v)}" for k, v in node.pairs
        )
        return "{" + pairs + "}"

    # -- Expressions --

    def visit_Identifier(self, node):
        return node.name

    def visit_BinaryOp(self, node):
        left = self._expr(node.left)
        right = self._expr(node.right)
        return f"({left} {node.op} {right})"

    def visit_UnaryOp(self, node):
        operand = self._expr(node.operand)
        if node.op == "NOT":
            return f"(not {operand})"
        if node.op == "~":
            return f"(~{operand})"
        return f"({node.op}{operand})"

    def visit_BooleanOp(self, node):
        op_str = " and " if node.op == "AND" else " or "
        parts = [self._expr(v) for v in node.values]
        return "(" + op_str.join(parts) + ")"

    def visit_CompareOp(self, node):
        parts = [self._expr(node.left)]
        for op, right in node.comparators:
            parts.append(op)
            parts.append(self._expr(right))
        return "(" + " ".join(parts) + ")"

    def visit_CallExpr(self, node):
        func = self._expr(node.func)
        args = [self._expr(a) for a in node.args]
        kwargs = [f"{name}={self._expr(val)}" for name, val in node.keywords]
        all_args = ", ".join(args + kwargs)
        return f"{func}({all_args})"

    def visit_AttributeAccess(self, node):
        obj = self._expr(node.obj)
        return f"{obj}.{node.attr}"

    def visit_IndexAccess(self, node):
        obj = self._expr(node.obj)
        index = self._expr(node.index)
        return f"{obj}[{index}]"

    def visit_LambdaExpr(self, node):
        param_strs = []
        for p in node.params:
            if isinstance(p, str):
                param_strs.append(p)
            else:
                param_strs.append(self._expr(p))
        params = ", ".join(param_strs)
        body = self._expr(node.body)
        return f"(lambda {params}: {body})"

    def visit_YieldExpr(self, node):
        if node.value:
            val = self._expr(node.value)
            return f"(yield {val})"
        return "(yield)"

    def visit_ConditionalExpr(self, node):
        true_expr = self._expr(node.true_expr)
        cond = self._expr(node.condition)
        false_expr = self._expr(node.false_expr)
        return f"({true_expr} if {cond} else {false_expr})"

    def visit_SliceExpr(self, node):
        start = self._expr(node.start) if node.start else ""
        stop = self._expr(node.stop) if node.stop else ""
        if node.step is not None:
            step = self._expr(node.step)
            return f"{start}:{stop}:{step}"
        return f"{start}:{stop}"

    def visit_Parameter(self, node):
        prefix = ""
        if node.is_kwarg:
            prefix = "**"
        elif node.is_vararg:
            prefix = "*"
        if node.default:
            default_expr = self._expr(node.default)
            return f"{prefix}{node.name}={default_expr}"
        return f"{prefix}{node.name}"

    def visit_StarredExpr(self, node):
        val = self._expr(node.value)
        prefix = "**" if node.is_double else "*"
        return f"{prefix}{val}"

    def visit_TupleLiteral(self, node):
        elems = ", ".join(self._expr(e) for e in node.elements)
        return elems

    def visit_ListComprehension(self, node):
        elem = self._expr(node.element)
        target = self._expr(node.target)
        iterable = self._expr(node.iterable)
        result = f"[{elem} for {target} in {iterable}"
        for cond in node.conditions:
            result += f" if {self._expr(cond)}"
        result += "]"
        return result

    def visit_DictComprehension(self, node):
        key = self._expr(node.key)
        val = self._expr(node.value)
        target = self._expr(node.target)
        iterable = self._expr(node.iterable)
        result = "{" + f"{key}: {val} for {target} in {iterable}"
        for cond in node.conditions:
            result += f" if {self._expr(cond)}"
        result += "}"
        return result

    def visit_GeneratorExpr(self, node):
        elem = self._expr(node.element)
        target = self._expr(node.target)
        iterable = self._expr(node.iterable)
        result = f"({elem} for {target} in {iterable}"
        for cond in node.conditions:
            result += f" if {self._expr(cond)}"
        result += ")"
        return result

    def visit_FStringLiteral(self, node):
        result = 'f"'
        for part in node.parts:
            if isinstance(part, str):
                # Escape any double quotes and braces in text
                escaped = part.replace("\\", "\\\\").replace('"', '\\"')
                escaped = escaped.replace("{", "{{").replace("}", "}}")
                result += escaped
            else:
                result += "{" + self._expr(part) + "}"
        result += '"'
        return result

    def generic_visit(self, node):
        raise CodeGenerationError(
            f"Unsupported expression node: {type(node).__name__}",
            node.line, node.column
        )
