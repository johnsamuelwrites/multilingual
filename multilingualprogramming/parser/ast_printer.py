#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""AST pretty-printer for debugging and visualization."""

# pylint: disable=duplicate-code

class ASTPrinter:
    """Pretty-prints an AST as indented text."""

    def __init__(self, indent_str="  "):
        self.indent_str = indent_str
        self._depth = 0
        self._lines = []

    def print(self, node):
        """Generate a pretty-printed string of the AST."""
        self._depth = 0
        self._lines = []
        node.accept(self)
        return "\n".join(self._lines)

    def _emit(self, text):
        """Add a line at the current indentation level."""
        self._lines.append(self.indent_str * self._depth + text)

    def _indent(self):
        self._depth += 1

    def _dedent(self):
        self._depth -= 1

    def _visit_body(self, body):
        """Visit a list of statements."""
        self._indent()
        for stmt in body:
            stmt.accept(self)
        self._dedent()

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def visit_Program(self, node):
        self._emit("Program")
        self._visit_body(node.body)

    def visit_NumeralLiteral(self, node):
        self._emit(f"NumeralLiteral {node.value!r}")

    def visit_StringLiteral(self, node):
        self._emit(f"StringLiteral {node.value!r}")

    def visit_DateLiteral(self, node):
        self._emit(f"DateLiteral {node.value!r}")

    def visit_BooleanLiteral(self, node):
        self._emit(f"BooleanLiteral {node.value}")

    def visit_NoneLiteral(self, _node):
        self._emit("NoneLiteral")

    def visit_ListLiteral(self, node):
        self._emit("ListLiteral")
        self._indent()
        for elem in node.elements:
            elem.accept(self)
        self._dedent()

    def visit_DictLiteral(self, node):
        self._emit("DictLiteral")
        self._indent()
        for entry in node.entries:
            if isinstance(entry, tuple):
                key, value = entry
                self._emit("pair:")
                self._indent()
                key.accept(self)
                value.accept(self)
                self._dedent()
            else:
                self._emit("unpack:")
                self._indent()
                entry.accept(self)
                self._dedent()
        self._dedent()

    def visit_SetLiteral(self, node):
        self._emit("SetLiteral")
        self._indent()
        for elem in node.elements:
            elem.accept(self)
        self._dedent()

    def visit_DictUnpackEntry(self, node):
        self._emit("DictUnpackEntry")
        self._indent()
        node.value.accept(self)
        self._dedent()

    def visit_Identifier(self, node):
        self._emit(f"Identifier {node.name!r}")

    def visit_BinaryOp(self, node):
        self._emit(f"BinaryOp {node.op!r}")
        self._indent()
        node.left.accept(self)
        node.right.accept(self)
        self._dedent()

    def visit_UnaryOp(self, node):
        self._emit(f"UnaryOp {node.op!r}")
        self._indent()
        node.operand.accept(self)
        self._dedent()

    def visit_BooleanOp(self, node):
        self._emit(f"BooleanOp {node.op!r}")
        self._indent()
        for val in node.values:
            val.accept(self)
        self._dedent()

    def visit_CompareOp(self, node):
        self._emit("CompareOp")
        self._indent()
        node.left.accept(self)
        for op, right in node.comparators:
            self._emit(f"op: {op!r}")
            right.accept(self)
        self._dedent()

    def visit_CallExpr(self, node):
        self._emit("CallExpr")
        self._indent()
        self._emit("func:")
        self._indent()
        node.func.accept(self)
        self._dedent()
        if node.args:
            self._emit("args:")
            self._indent()
            for arg in node.args:
                arg.accept(self)
            self._dedent()
        if node.keywords:
            self._emit("keywords:")
            self._indent()
            for name, val in node.keywords:
                self._emit(f"{name}=")
                self._indent()
                val.accept(self)
                self._dedent()
            self._dedent()
        self._dedent()

    def visit_AttributeAccess(self, node):
        self._emit(f"AttributeAccess .{node.attr!r}")
        self._indent()
        node.obj.accept(self)
        self._dedent()

    def visit_IndexAccess(self, node):
        self._emit("IndexAccess")
        self._indent()
        node.obj.accept(self)
        self._emit("index:")
        self._indent()
        node.index.accept(self)
        self._dedent()
        self._dedent()

    def visit_LambdaExpr(self, node):
        self._emit(f"LambdaExpr params={node.params!r}")
        self._indent()
        node.body.accept(self)
        self._dedent()

    def visit_YieldExpr(self, node):
        self._emit("YieldExpr")
        if node.value:
            self._indent()
            node.value.accept(self)
            self._dedent()

    def visit_AwaitExpr(self, node):
        self._emit("AwaitExpr")
        self._indent()
        node.value.accept(self)
        self._dedent()

    def visit_NamedExpr(self, node):
        self._emit("NamedExpr")
        self._indent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("value:")
        self._indent()
        node.value.accept(self)
        self._dedent()
        self._dedent()

    def visit_ConditionalExpr(self, node):
        self._emit("ConditionalExpr")
        self._indent()
        self._emit("condition:")
        self._indent()
        node.condition.accept(self)
        self._dedent()
        self._emit("true:")
        self._indent()
        node.true_expr.accept(self)
        self._dedent()
        self._emit("false:")
        self._indent()
        node.false_expr.accept(self)
        self._dedent()
        self._dedent()

    def visit_VariableDeclaration(self, node):
        kind = "const" if node.is_const else "let"
        self._emit(f"VariableDeclaration ({kind}) {node.name!r}")
        self._indent()
        node.value.accept(self)
        self._dedent()

    def visit_Assignment(self, node):
        self._emit(f"Assignment op={node.op!r}")
        self._indent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("value:")
        self._indent()
        node.value.accept(self)
        self._dedent()
        self._dedent()

    def visit_AnnAssignment(self, node):
        self._emit("AnnAssignment")
        self._indent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("annotation:")
        self._indent()
        node.annotation.accept(self)
        self._dedent()
        if node.value:
            self._emit("value:")
            self._indent()
            node.value.accept(self)
            self._dedent()
        self._dedent()

    def visit_ExpressionStatement(self, node):
        self._emit("ExpressionStatement")
        self._indent()
        node.expression.accept(self)
        self._dedent()

    def visit_PassStatement(self, _node):
        self._emit("PassStatement")

    def visit_ReturnStatement(self, node):
        self._emit("ReturnStatement")
        if node.value:
            self._indent()
            node.value.accept(self)
            self._dedent()

    def visit_BreakStatement(self, _node):
        self._emit("BreakStatement")

    def visit_ContinueStatement(self, _node):
        self._emit("ContinueStatement")

    def visit_RaiseStatement(self, node):
        self._emit("RaiseStatement")
        if node.value:
            self._indent()
            node.value.accept(self)
            self._dedent()

    def visit_AssertStatement(self, node):
        self._emit("AssertStatement")
        self._indent()
        self._emit("test:")
        self._indent()
        node.test.accept(self)
        self._dedent()
        if node.msg:
            self._emit("msg:")
            self._indent()
            node.msg.accept(self)
            self._dedent()
        self._dedent()

    def visit_ChainedAssignment(self, node):
        self._emit("ChainedAssignment")
        self._indent()
        self._emit("targets:")
        self._indent()
        for target in node.targets:
            target.accept(self)
        self._dedent()
        self._emit("value:")
        self._indent()
        node.value.accept(self)
        self._dedent()
        self._dedent()

    def visit_GlobalStatement(self, node):
        self._emit(f"GlobalStatement {node.names!r}")

    def visit_LocalStatement(self, node):
        self._emit(f"LocalStatement {node.names!r}")

    def visit_YieldStatement(self, node):
        self._emit("YieldStatement")
        if node.value:
            self._indent()
            node.value.accept(self)
            self._dedent()

    def visit_IfStatement(self, node):
        self._emit("IfStatement")
        self._indent()
        self._emit("condition:")
        self._indent()
        node.condition.accept(self)
        self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        for elif_cond, elif_body in node.elif_clauses:
            self._emit("elif:")
            self._indent()
            elif_cond.accept(self)
            self._dedent()
            self._emit("elif_body:")
            self._visit_body(elif_body)
        if node.else_body:
            self._emit("else:")
            self._visit_body(node.else_body)
        self._dedent()

    def visit_WhileLoop(self, node):
        self._emit("WhileLoop")
        self._indent()
        self._emit("condition:")
        self._indent()
        node.condition.accept(self)
        self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        self._dedent()

    def visit_ForLoop(self, node):
        self._emit("ForLoop")
        self._indent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("iterable:")
        self._indent()
        node.iterable.accept(self)
        self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        self._dedent()

    def visit_FunctionDef(self, node):
        for dec in getattr(node, 'decorators', []):
            self._emit("Decorator")
            self._indent()
            dec.accept(self)
            self._dedent()
        self._emit(
            f"FunctionDef name={node.name!r} async={getattr(node, 'is_async', False)}"
        )
        self._indent()
        self._emit(f"params: {node.params!r}")
        if getattr(node, "return_annotation", None):
            self._emit("returns:")
            self._indent()
            node.return_annotation.accept(self)
            self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        self._dedent()

    def visit_ClassDef(self, node):
        for dec in getattr(node, 'decorators', []):
            self._emit("Decorator")
            self._indent()
            dec.accept(self)
            self._dedent()
        self._emit(f"ClassDef name={node.name!r}")
        self._indent()
        if node.bases:
            self._emit("bases:")
            self._indent()
            for base in node.bases:
                base.accept(self)
            self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        self._dedent()

    def visit_TryStatement(self, node):
        self._emit("TryStatement")
        self._indent()
        self._emit("body:")
        self._visit_body(node.body)
        for handler in node.handlers:
            handler.accept(self)
        if node.finally_body:
            self._emit("finally:")
            self._visit_body(node.finally_body)
        self._dedent()

    def visit_ExceptHandler(self, node):
        parts = ["ExceptHandler"]
        if node.exc_type:
            parts.append(f"type={node.exc_type.name!r}")
        if node.name:
            parts.append(f"as={node.name!r}")
        self._emit(" ".join(parts))
        self._indent()
        for stmt in node.body:
            stmt.accept(self)
        self._dedent()

    def visit_MatchStatement(self, node):
        self._emit("MatchStatement")
        self._indent()
        self._emit("subject:")
        self._indent()
        node.subject.accept(self)
        self._dedent()
        for case in node.cases:
            case.accept(self)
        self._dedent()

    def visit_CaseClause(self, node):
        if node.is_default:
            self._emit("DefaultClause")
        else:
            self._emit("CaseClause")
            self._indent()
            self._emit("pattern:")
            self._indent()
            node.pattern.accept(self)
            self._dedent()
            self._dedent()
        self._indent()
        for stmt in node.body:
            stmt.accept(self)
        self._dedent()

    def visit_WithStatement(self, node):
        self._emit("WithStatement")
        self._indent()
        self._emit("items:")
        self._indent()
        for context_expr, name in node.items:
            self._emit(f"item as={name!r}")
            self._indent()
            context_expr.accept(self)
            self._dedent()
        self._dedent()
        self._emit("body:")
        self._visit_body(node.body)
        self._dedent()

    def visit_ImportStatement(self, node):
        parts = [f"ImportStatement module={node.module!r}"]
        if node.alias:
            parts.append(f"as={node.alias!r}")
        self._emit(" ".join(parts))

    def visit_FromImportStatement(self, node):
        self._emit(f"FromImportStatement module={node.module!r}")
        self._indent()
        for name, alias in node.names:
            if alias:
                self._emit(f"{name} as {alias}")
            else:
                self._emit(name)
        self._dedent()

    def visit_SliceExpr(self, node):
        self._emit("SliceExpr")
        self._indent()
        if node.start:
            self._emit("start:")
            self._indent()
            node.start.accept(self)
            self._dedent()
        if node.stop:
            self._emit("stop:")
            self._indent()
            node.stop.accept(self)
            self._dedent()
        if node.step:
            self._emit("step:")
            self._indent()
            node.step.accept(self)
            self._dedent()
        self._dedent()

    def visit_Parameter(self, node):
        parts = [f"Parameter {node.name!r}"]
        if node.is_vararg:
            parts.append("*")
        if node.is_kwarg:
            parts.append("**")
        self._emit(" ".join(parts))
        if node.annotation or node.default:
            self._indent()
            if node.annotation:
                self._emit("annotation:")
                self._indent()
                node.annotation.accept(self)
                self._dedent()
            self._emit("default:")
            if node.default:
                self._indent()
                node.default.accept(self)
                self._dedent()
            else:
                self._emit("None")
            self._dedent()

    def visit_StarredExpr(self, node):
        prefix = "**" if node.is_double else "*"
        self._emit(f"StarredExpr {prefix}")
        self._indent()
        node.value.accept(self)
        self._dedent()

    def visit_TupleLiteral(self, node):
        self._emit("TupleLiteral")
        self._indent()
        for elem in node.elements:
            elem.accept(self)
        self._dedent()

    def visit_ListComprehension(self, node):
        self._emit("ListComprehension")
        self._indent()
        self._emit("element:")
        self._indent()
        node.element.accept(self)
        self._dedent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("iterable:")
        self._indent()
        node.iterable.accept(self)
        self._dedent()
        if node.conditions:
            self._emit("conditions:")
            self._indent()
            for cond in node.conditions:
                cond.accept(self)
            self._dedent()
        self._dedent()

    def visit_DictComprehension(self, node):
        self._emit("DictComprehension")
        self._indent()
        self._emit("key:")
        self._indent()
        node.key.accept(self)
        self._dedent()
        self._emit("value:")
        self._indent()
        node.value.accept(self)
        self._dedent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("iterable:")
        self._indent()
        node.iterable.accept(self)
        self._dedent()
        if node.conditions:
            self._emit("conditions:")
            self._indent()
            for cond in node.conditions:
                cond.accept(self)
            self._dedent()
        self._dedent()

    def visit_GeneratorExpr(self, node):
        self._emit("GeneratorExpr")
        self._indent()
        self._emit("element:")
        self._indent()
        node.element.accept(self)
        self._dedent()
        self._emit("target:")
        self._indent()
        node.target.accept(self)
        self._dedent()
        self._emit("iterable:")
        self._indent()
        node.iterable.accept(self)
        self._dedent()
        if node.conditions:
            self._emit("conditions:")
            self._indent()
            for cond in node.conditions:
                cond.accept(self)
            self._dedent()
        self._dedent()

    def visit_FStringLiteral(self, node):
        self._emit("FStringLiteral")
        self._indent()
        for part in node.parts:
            if isinstance(part, str):
                self._emit(f"text: {part!r}")
            else:
                self._emit("expr:")
                self._indent()
                part.accept(self)
                self._dedent()
        self._dedent()

    def generic_visit(self, node):
        """Fallback rendering for nodes without a specialized visitor."""
        self._emit(f"{type(node).__name__}")
