#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""WAT-local semantic IR adapter.

This keeps the WAT backend's IR intake owned by the backend instead of routing
through the generic runtime AST bridge.  It converts the subset of semantic IR
that the current WAT backend can already lower into the legacy AST forms the
existing WAT internals expect.
"""

from __future__ import annotations

from multilingualprogramming.core import ir_nodes as ir
from multilingualprogramming.core.types import CoreType, GenericType
from multilingualprogramming.parser import ast_nodes as ast


def lower_ir_to_wat_ast(program: ir.IRProgram) -> ast.Program:
    """Convert an IRProgram into the AST subset the WAT backend supports."""
    if not isinstance(program, ir.IRProgram):
        raise TypeError("lower_ir_to_wat_ast expects an IRProgram")
    ctx = _WATIRAdapter()
    return ast.Program(
        [ctx.lower_stmt(node) for node in program.body],
        line=program.line,
        column=program.column,
    )


class _WATIRAdapter:
    """Backend-owned semantic IR -> AST adapter for WAT code generation."""

    def lower_stmt(self, node):
        """Lower a semantic IR statement node into a legacy AST node."""
        return self._dispatch(node)

    def lower_expr(self, node):
        """Lower a semantic IR expression node into a legacy AST node."""
        return self._dispatch(node)

    def _dispatch(self, node):
        """Dispatch *node* to its matching lowering handler."""
        method = getattr(self, f"_lower_{type(node).__name__}", None)
        if method is None or not callable(method):
            raise NotImplementedError(
                f"WAT IR adapter does not support {type(node).__name__}"
            )
        return method(node)  # pylint: disable=not-callable

    def _lower_IRBinding(self, node):
        return ast.VariableDeclaration(
            node.name,
            self.lower_expr(node.value),
            is_const=not node.is_mutable,
            declaration_kind="var" if node.is_mutable else "let",
            line=node.line,
            column=node.column,
        )

    def _lower_IRObserveBinding(self, node):
        return ast.ObserveDeclaration(
            node.name,
            self.lower_expr(node.value),
            annotation=self._lower_type(node.annotation),
            line=node.line,
            column=node.column,
        )

    def _lower_IRAssignment(self, node):
        chain_targets = getattr(node, "chain_targets", None)
        if chain_targets:
            return ast.ChainedAssignment(
                [self.lower_expr(target) for target in chain_targets],
                self.lower_expr(node.value),
                line=node.line,
                column=node.column,
            )
        return ast.Assignment(
            self.lower_expr(node.target),
            self.lower_expr(node.value),
            op=node.op,
            line=node.line,
            column=node.column,
        )

    def _lower_IRExprStatement(self, node):
        return ast.ExpressionStatement(
            self.lower_expr(node.expression),
            line=node.line,
            column=node.column,
        )

    def _lower_IRReturnStatement(self, node):
        return ast.ReturnStatement(
            self.lower_expr(node.value) if node.value is not None else None,
            line=node.line,
            column=node.column,
        )

    def _lower_IRBreakStatement(self, node):
        return ast.BreakStatement(line=node.line, column=node.column)

    def _lower_IRContinueStatement(self, node):
        return ast.ContinueStatement(line=node.line, column=node.column)

    def _lower_IRPassStatement(self, node):
        return ast.PassStatement(line=node.line, column=node.column)

    def _lower_IRRaiseStatement(self, node):
        return ast.RaiseStatement(
            self.lower_expr(node.value) if node.value is not None else None,
            cause=self.lower_expr(node.cause) if node.cause is not None else None,
            line=node.line,
            column=node.column,
        )

    def _lower_IRDelStatement(self, node):
        return ast.DelStatement(
            self.lower_expr(node.target),
            line=node.line,
            column=node.column,
        )

    def _lower_IRAssertStatement(self, node):
        return ast.AssertStatement(
            self.lower_expr(node.test),
            msg=self.lower_expr(node.msg) if node.msg is not None else None,
            line=node.line,
            column=node.column,
        )

    def _lower_IRGlobalStatement(self, node):
        return ast.GlobalStatement(node.names, line=node.line, column=node.column)

    def _lower_IRNonlocalStatement(self, node):
        return ast.LocalStatement(node.names, line=node.line, column=node.column)

    def _lower_IRYieldStatement(self, node):
        return ast.YieldStatement(
            self.lower_expr(node.value) if node.value is not None else None,
            is_from=node.is_from,
            line=node.line,
            column=node.column,
        )

    def _lower_IRImportStatement(self, node):
        return ast.ImportStatement(
            node.module,
            alias=node.alias,
            line=node.line,
            column=node.column,
        )

    def _lower_IRFromImportStatement(self, node):
        return ast.FromImportStatement(
            node.module,
            node.names,
            level=node.level,
            line=node.line,
            column=node.column,
        )

    def _lower_IRWithStatement(self, node):
        return ast.WithStatement(
            [(self.lower_expr(expr), name) for expr, name in node.items],
            body=[self.lower_stmt(stmt) for stmt in node.body],
            is_async=node.is_async,
            line=node.line,
            column=node.column,
        )

    def _lower_IRIfStatement(self, node):
        return ast.IfStatement(
            self.lower_expr(node.condition),
            [self.lower_stmt(stmt) for stmt in node.body],
            elif_clauses=[
                (self.lower_expr(clause.condition),
                 [self.lower_stmt(stmt) for stmt in clause.body])
                for clause in node.elif_clauses
            ],
            else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRWhileLoop(self, node):
        return ast.WhileLoop(
            self.lower_expr(node.condition),
            [self.lower_stmt(stmt) for stmt in node.body],
            else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRForLoop(self, node):
        return ast.ForLoop(
            self.lower_expr(node.target),
            self.lower_expr(node.iterable),
            [self.lower_stmt(stmt) for stmt in node.body],
            is_async=node.is_async,
            else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRExceptHandler(self, node):
        return ast.ExceptHandler(
            exc_type=(
                self.lower_expr(node.exc_type)
                if node.exc_type is not None else None
            ),
            name=node.name,
            body=[self.lower_stmt(stmt) for stmt in node.body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRTryStatement(self, node):
        return ast.TryStatement(
            [self.lower_stmt(stmt) for stmt in node.body],
            handlers=[self._lower_IRExceptHandler(h) for h in node.handlers],
            else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
            finally_body=[self.lower_stmt(stmt) for stmt in node.finally_body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRMatchStatement(self, node):
        return ast.MatchStatement(
            self.lower_expr(node.subject),
            [self._lower_IRMatchCase(case) for case in node.cases],
            line=node.line,
            column=node.column,
        )

    def _lower_IRMatchCase(self, node):
        return ast.CaseClause(
            pattern=self._lower_pattern(node.pattern),
            body=[self.lower_stmt(stmt) for stmt in node.body],
            is_default=node.is_default,
            line=node.line,
            column=node.column,
        )

    def _lower_IRFunction(self, node):
        return ast.FunctionDef(
            node.name,
            [self._lower_param(param) for param in node.parameters],
            [self.lower_stmt(stmt) for stmt in node.body],
            decorators=[self.lower_expr(dec) for dec in node.decorators],
            return_annotation=self._lower_type(node.return_type),
            is_async=node.is_async,
            syntax_keyword=node.syntax_keyword,
            uses=sorted(effect.name for effect in node.effects.values()),
            line=node.line,
            column=node.column,
        )

    def _lower_IRAgentDecl(self, node):
        return ast.FunctionDef(
            node.name,
            [self._lower_param(param) for param in node.parameters],
            [self.lower_stmt(stmt) for stmt in node.body],
            decorators=[
                ast.CallExpr(
                    ast.Identifier("agent", line=node.line, column=node.column),
                    [],
                    keywords=[("model", self.lower_expr(node.model))],
                    line=node.line,
                    column=node.column,
                )
            ],
            return_annotation=self._lower_type(node.return_type),
            is_async=node.is_async,
            uses=sorted(effect.name for effect in node.effects.values()),
            line=node.line,
            column=node.column,
        )

    def _lower_IRToolDecl(self, node):
        return ast.FunctionDef(
            node.name,
            [self._lower_param(param) for param in node.parameters],
            [self.lower_stmt(stmt) for stmt in node.body],
            decorators=[
                ast.CallExpr(
                    ast.Identifier("tool", line=node.line, column=node.column),
                    [],
                    keywords=[("description", ast.StringLiteral(node.description))],
                    line=node.line,
                    column=node.column,
                )
            ],
            return_annotation=self._lower_type(node.return_type),
            uses=sorted(effect.name for effect in node.effects.values()),
            line=node.line,
            column=node.column,
        )

    def _lower_IRClassDecl(self, node):
        return ast.ClassDef(
            node.name,
            [self.lower_expr(base) for base in node.bases],
            [self.lower_stmt(stmt) for stmt in node.body],
            decorators=[self.lower_expr(dec) for dec in node.decorators],
            line=node.line,
            column=node.column,
        )

    def _lower_IREnumDecl(self, node):
        return ast.EnumDecl(node.name, [], line=node.line, column=node.column)

    def _lower_IRTypeDecl(self, node):
        return ast.RecordDecl(node.name, [], line=node.line, column=node.column)

    def _lower_IROnChange(self, node):
        return ast.OnChangeStatement(
            self.lower_expr(node.signal),
            body=[self.lower_stmt(stmt) for stmt in node.body],
            line=node.line,
            column=node.column,
        )

    def _lower_IRCanvasBlock(self, node):
        return ast.CanvasBlock(
            node.name,
            body=[self.lower_stmt(stmt) for stmt in node.children],
            line=node.line,
            column=node.column,
        )

    def _lower_IRRenderExpr(self, node):
        return ast.RenderStatement(
            self.lower_expr(node.target),
            self.lower_expr(node.value),
            line=node.line,
            column=node.column,
        )

    def _lower_IRViewBinding(self, node):
        return ast.ViewBindingStatement(
            self.lower_expr(node.signal),
            self.lower_expr(node.target),
            line=node.line,
            column=node.column,
        )

    def _lower_IRLiteral(self, node):
        if node.kind in {"int", "float", "decimal"}:
            return ast.NumeralLiteral(str(node.value), line=node.line, column=node.column)
        if node.kind == "string":
            return ast.StringLiteral(node.value, line=node.line, column=node.column)
        if node.kind == "bytes":
            return ast.BytesLiteral(node.value, line=node.line, column=node.column)
        if node.kind == "bool":
            return ast.BooleanLiteral(node.value, line=node.line, column=node.column)
        if node.kind == "none":
            return ast.NoneLiteral(line=node.line, column=node.column)
        if node.kind == "date":
            return ast.DateLiteral(node.value, line=node.line, column=node.column)
        raise NotImplementedError(f"Unsupported IR literal kind: {node.kind}")

    def _lower_IRFStringLiteral(self, node):
        parts = [
            self.lower_expr(part) if not isinstance(part, str) else part
            for part in node.parts
        ]
        return ast.FStringLiteral(parts, line=node.line, column=node.column)

    def _lower_IRListLiteral(self, node):
        return ast.ListLiteral(
            [self.lower_expr(elem) for elem in node.elements],
            line=node.line,
            column=node.column,
        )

    def _lower_IRDictLiteral(self, node):
        entries = []
        for entry in node.entries:
            if isinstance(entry, tuple):
                entries.append((self.lower_expr(entry[0]), self.lower_expr(entry[1])))
            elif isinstance(entry, ir.IRStarredExpr) and entry.is_double:
                entries.append(
                    ast.DictUnpackEntry(
                        self.lower_expr(entry.value),
                        line=entry.line,
                        column=entry.column,
                    )
                )
            else:
                entries.append(self.lower_expr(entry))
        return ast.DictLiteral(entries, line=node.line, column=node.column)

    def _lower_IRSetLiteral(self, node):
        return ast.SetLiteral(
            [self.lower_expr(elem) for elem in node.elements],
            line=node.line,
            column=node.column,
        )

    def _lower_IRTupleLiteral(self, node):
        return ast.TupleLiteral(
            [self.lower_expr(elem) for elem in node.elements],
            line=node.line,
            column=node.column,
        )

    def _lower_IRIdentifier(self, node):
        return ast.Identifier(node.name, line=node.line, column=node.column)

    def _lower_IRModelRef(self, node):
        return ast.ModelRefLiteral(node.model_name, line=node.line, column=node.column)

    def _lower_IRBinaryOp(self, node):
        return ast.BinaryOp(
            self.lower_expr(node.left),
            node.op,
            self.lower_expr(node.right),
            line=node.line,
            column=node.column,
        )

    def _lower_IRUnaryOp(self, node):
        return ast.UnaryOp(
            node.op,
            self.lower_expr(node.operand),
            line=node.line,
            column=node.column,
        )

    def _lower_IRBooleanOp(self, node):
        return ast.BooleanOp(
            node.op,
            [self.lower_expr(value) for value in node.values],
            line=node.line,
            column=node.column,
        )

    def _lower_IRCompareOp(self, node):
        return ast.CompareOp(
            self.lower_expr(node.left),
            [(op, self.lower_expr(right)) for op, right in node.comparators],
            line=node.line,
            column=node.column,
        )

    def _lower_IRCallExpr(self, node):
        return ast.CallExpr(
            self.lower_expr(node.func),
            [self.lower_expr(arg) for arg in node.args],
            keywords=[
                (name, self.lower_expr(value))
                for name, value in node.keywords
            ],
            line=node.line,
            column=node.column,
        )

    def _lower_IRAttributeAccess(self, node):
        return ast.AttributeAccess(
            self.lower_expr(node.obj),
            node.attr,
            line=node.line,
            column=node.column,
        )

    def _lower_IRIndexAccess(self, node):
        return ast.IndexAccess(
            self.lower_expr(node.obj),
            self.lower_expr(node.index),
            line=node.line,
            column=node.column,
        )

    def _lower_IRSliceExpr(self, node):
        return ast.SliceExpr(
            self.lower_expr(node.start) if node.start is not None else None,
            self.lower_expr(node.stop) if node.stop is not None else None,
            self.lower_expr(node.step) if node.step is not None else None,
            line=node.line,
            column=node.column,
        )

    def _lower_IRStarredExpr(self, node):
        return ast.StarredExpr(
            self.lower_expr(node.value),
            is_double=node.is_double,
            line=node.line,
            column=node.column,
        )

    def _lower_IRLambdaExpr(self, node):
        return ast.LambdaExpr(
            [self._lower_param(param) for param in node.parameters],
            self.lower_expr(node.body),
            line=node.line,
            column=node.column,
        )

    def _lower_IRPipeExpr(self, node):
        if isinstance(node.right, ir.IRCallExpr):
            return ast.CallExpr(
                self.lower_expr(node.right.func),
                [self.lower_expr(node.left)]
                + [self.lower_expr(arg) for arg in node.right.args],
                keywords=[
                    (name, self.lower_expr(value))
                    for name, value in node.right.keywords
                ],
                line=node.line,
                column=node.column,
            )
        return ast.CallExpr(
            self.lower_expr(node.right),
            [self.lower_expr(node.left)],
            line=node.line,
            column=node.column,
        )

    def _lower_IRResultPropagation(self, node):
        return ast.CallExpr(
            ast.Identifier("__ml_result_propagate", line=node.line, column=node.column),
            [self.lower_expr(node.operand)],
            line=node.line,
            column=node.column,
        )

    def _lower_IRAwaitExpr(self, node):
        return ast.AwaitExpr(self.lower_expr(node.value), line=node.line, column=node.column)

    def _lower_IRYieldExpr(self, node):
        return ast.YieldExpr(
            self.lower_expr(node.value) if node.value is not None else None,
            is_from=node.is_from,
            line=node.line,
            column=node.column,
        )

    def _lower_IRNamedExpr(self, node):
        return ast.NamedExpr(
            ast.Identifier(node.target, line=node.line, column=node.column),
            self.lower_expr(node.value),
            line=node.line,
            column=node.column,
        )

    def _lower_IRConditionalExpr(self, node):
        return ast.ConditionalExpr(
            self.lower_expr(node.condition),
            self.lower_expr(node.true_expr),
            self.lower_expr(node.false_expr),
            line=node.line,
            column=node.column,
        )

    def _lower_IRListComp(self, node):
        return ast.ListComprehension(
            self.lower_expr(node.element),
            self.lower_expr(node.clauses[0].target),
            self.lower_expr(node.clauses[0].iterable),
            clauses=[self._lower_clause(c) for c in node.clauses],
            line=node.line,
            column=node.column,
        )

    def _lower_IRDictComp(self, node):
        return ast.DictComprehension(
            self.lower_expr(node.key),
            self.lower_expr(node.value),
            self.lower_expr(node.clauses[0].target),
            self.lower_expr(node.clauses[0].iterable),
            clauses=[self._lower_clause(c) for c in node.clauses],
            line=node.line,
            column=node.column,
        )

    def _lower_IRSetComp(self, node):
        return ast.SetComprehension(
            self.lower_expr(node.element),
            self.lower_expr(node.clauses[0].target),
            self.lower_expr(node.clauses[0].iterable),
            clauses=[self._lower_clause(c) for c in node.clauses],
            line=node.line,
            column=node.column,
        )

    def _lower_IRGeneratorExpr(self, node):
        return ast.GeneratorExpr(
            self.lower_expr(node.element),
            self.lower_expr(node.clauses[0].target),
            self.lower_expr(node.clauses[0].iterable),
            clauses=[self._lower_clause(c) for c in node.clauses],
            line=node.line,
            column=node.column,
        )

    def _lower_IRPromptExpr(self, node):
        return self._lower_native_call("prompt", [node.model, node.template], node)

    def _lower_IRGenerateExpr(self, node):
        keywords = []
        if node.target_type is not None:
            keywords.append(("target_type", self._lower_type(node.target_type)))
        return self._lower_native_call("generate", [node.model, node.template], node, keywords)

    def _lower_IRThinkExpr(self, node):
        return self._lower_native_call("think", [node.model, node.template], node)

    def _lower_IRStreamExpr(self, node):
        return self._lower_native_call("stream", [node.model, node.template], node)

    def _lower_IREmbedExpr(self, node):
        return self._lower_native_call("embed", [node.model, node.value], node)

    def _lower_IRExtractExpr(self, node):
        keywords = []
        if node.target_type is not None:
            keywords.append(("target_type", self._lower_type(node.target_type)))
        return self._lower_native_call("extract", [node.model, node.source], node, keywords)

    def _lower_IRClassifyExpr(self, node):
        keywords = []
        if node.categories:
            keywords.append(
                ("categories", ast.ListLiteral([self.lower_expr(cat) for cat in node.categories]))
            )
        if node.target_type is not None:
            keywords.append(("target_type", self._lower_type(node.target_type)))
        return self._lower_native_call("classify", [node.model, node.subject], node, keywords)

    def _lower_IRPlanExpr(self, node):
        return self._lower_native_call("plan", [node.model, node.goal], node)

    def _lower_IRTranscribeExpr(self, node):
        return self._lower_native_call("transcribe", [node.model, node.source], node)

    def _lower_IRRetrieveExpr(self, node):
        keywords = []
        if node.model is not None:
            keywords.append(("model", self.lower_expr(node.model)))
        return self._lower_native_call("retrieve", [node.index, node.query], node, keywords)

    def _lower_IRSemanticMatchOp(self, node):
        keywords = [("threshold", ast.NumeralLiteral(str(node.threshold)))]
        if node.model is not None:
            keywords.append(("model", self.lower_expr(node.model)))
        return ast.CallExpr(
            ast.Identifier("semantic_match", line=node.line, column=node.column),
            [self.lower_expr(node.left), self.lower_expr(node.right)],
            keywords=keywords,
            line=node.line,
            column=node.column,
        )

    def _lower_native_call(self, name, args, node, keywords=None):
        return ast.CallExpr(
            ast.Identifier(name, line=node.line, column=node.column),
            [self.lower_expr(arg) for arg in args],
            keywords=keywords or [],
            line=node.line,
            column=node.column,
        )

    def _lower_clause(self, clause):
        return ast.ComprehensionClause(
            self.lower_expr(clause.target),
            self.lower_expr(clause.iterable),
            [self.lower_expr(cond) for cond in clause.conditions],
            line=clause.line,
            column=clause.column,
        )

    def _lower_param(self, node):
        return ast.Parameter(
            node.name,
            default=self.lower_expr(node.default) if node.default is not None else None,
            is_vararg=node.is_vararg,
            is_kwarg=node.is_kwarg,
            annotation=self._lower_type(node.annotation),
            line=node.line,
            column=node.column,
        )

    def _lower_type(self, type_value: CoreType | None):
        if type_value is None:
            return None
        if isinstance(type_value, GenericType):
            params = [self._lower_type(param) for param in type_value.parameters]
            index = params[0] if len(params) == 1 else ast.TupleLiteral(params)
            return ast.IndexAccess(ast.Identifier(_python_type_name(type_value.name)), index)
        return ast.Identifier(_python_type_name(type_value.name))

    def _lower_pattern(self, pattern):
        if pattern is None:
            return ast.Identifier("_")
        if isinstance(pattern, ir.IRLiteralPattern):
            return self.lower_expr(pattern.value)
        if isinstance(pattern, ir.IRCapturePattern):
            return ast.Identifier(pattern.name, line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IRWildcardPattern):
            return ast.Identifier("_", line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IROrPattern):
            result = self._lower_pattern(pattern.alternatives[0])
            for alt in pattern.alternatives[1:]:
                result = ast.BinaryOp(
                    result,
                    "|",
                    self._lower_pattern(alt),
                    line=pattern.line,
                    column=pattern.column,
                )
            return result
        if isinstance(pattern, ir.IRSequencePattern):
            return ast.TupleLiteral(
                [self._lower_pattern(elem) for elem in pattern.elements],
                line=pattern.line,
                column=pattern.column,
            )
        if isinstance(pattern, ir.IRRecordPattern):
            return ast.DictLiteral(
                [
                    (ast.StringLiteral(name), self._lower_pattern(value))
                    for name, value in pattern.fields.items()
                ],
                line=pattern.line,
                column=pattern.column,
            )
        if isinstance(pattern, ir.IRGuardedPattern):
            return self._lower_pattern(pattern.pattern)
        if isinstance(pattern, ir.IRAsPattern):
            return ast.BinaryOp(
                self._lower_pattern(pattern.pattern),
                " as ",
                ast.Identifier(pattern.name, line=pattern.line, column=pattern.column),
                line=pattern.line,
                column=pattern.column,
            )
        if isinstance(pattern, ir.IRSemanticPattern):
            return self.lower_expr(pattern.template)
        return self.lower_expr(pattern)


def _python_type_name(type_name: str) -> str:
    return {
        "integer": "int",
        "int": "int",
        "float": "float",
        "string": "str",
        "str": "str",
        "bool": "bool",
        "bytes": "bytes",
        "list": "list",
        "dict": "dict",
        "tuple": "tuple",
        "set": "set",
        "none": "None",
        "any": "object",
    }.get(type_name, type_name)
