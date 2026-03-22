#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Lower semantic IR programs to the legacy AST used by current backends."""
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

from __future__ import annotations

from multilingualprogramming.core import ir_nodes as ir
from multilingualprogramming.core.types import CoreType, GenericType
from multilingualprogramming.parser import ast_nodes as ast


def lower_ir_to_runtime_ast(program: ir.IRProgram) -> ast.Program:
    """Convert an IRProgram into the executable legacy AST form."""
    if not isinstance(program, ir.IRProgram):
        raise TypeError("lower_ir_to_runtime_ast expects an IRProgram")
    return ast.Program(
        [_LoweringContext().lower_stmt(node) for node in program.body],
        line=program.line,
        column=program.column,
    )


class _LoweringContext:
    """Translate semantic IR nodes to the legacy backend AST."""

    def lower_stmt(self, node):
        if isinstance(node, ir.IRBinding):
            return ast.VariableDeclaration(
                node.name,
                self.lower_expr(node.value),
                declaration_kind="var" if node.is_mutable else "let",
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRObserveBinding):
            return ast.ObserveDeclaration(
                node.name,
                self.lower_expr(node.value),
                annotation=self._lower_type(node.annotation),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRFunction):
            return ast.FunctionDef(
                node.name,
                [self._lower_param(param) for param in node.parameters],
                [self.lower_stmt(stmt) for stmt in node.body],
                decorators=[self.lower_expr(dec) for dec in node.decorators],
                return_annotation=self._lower_type(node.return_type),
                is_async=node.is_async,
                syntax_keyword=node.syntax_keyword,
                uses=list(node.effects.names()),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRAgentDecl):
            return ast.FunctionDef(
                node.name,
                [self._lower_param(param) for param in node.parameters],
                [self.lower_stmt(stmt) for stmt in node.body],
                decorators=[ast.CallExpr(
                    ast.Identifier("agent"),
                    [],
                    keywords=[("model", self.lower_expr(node.model))],
                    line=node.line,
                    column=node.column,
                )],
                return_annotation=self._lower_type(node.return_type),
                is_async=node.is_async,
                syntax_keyword="fn",
                uses=list(node.effects.names()),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRToolDecl):
            return ast.FunctionDef(
                node.name,
                [self._lower_param(param) for param in node.parameters],
                [self.lower_stmt(stmt) for stmt in node.body],
                decorators=[ast.CallExpr(
                    ast.Identifier("tool"),
                    [],
                    keywords=[("description", ast.StringLiteral(node.description))],
                    line=node.line,
                    column=node.column,
                )],
                return_annotation=self._lower_type(node.return_type),
                syntax_keyword="fn",
                uses=list(node.effects.names()),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRClassDecl):
            return ast.ClassDef(
                node.name,
                [self.lower_expr(base) for base in node.bases],
                [self.lower_stmt(stmt) for stmt in node.body],
                decorators=[self.lower_expr(dec) for dec in node.decorators],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRTypeDecl):
            return ast.RecordDecl(
                node.name,
                [
                    ast.RecordField(
                        field.name,
                        self._lower_type(field.field_type),
                        line=node.line,
                        column=node.column,
                    )
                    for field in getattr(node.declared_type, "fields", ())
                ],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IREnumDecl):
            variants = []
            for variant in getattr(node.declared_type, "variants", ()):
                fields = []
                if variant.payload is not None:
                    fields = [
                        (field.name, self._lower_type(field.field_type))
                        for field in variant.payload.fields
                    ]
                variants.append(ast.EnumVariant(variant.name, fields, line=node.line, column=node.column))
            return ast.EnumDecl(node.name, variants, line=node.line, column=node.column)
        if isinstance(node, ir.IRAssignment):
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
        if isinstance(node, ir.IRExprStatement):
            return ast.ExpressionStatement(self.lower_expr(node.expression), line=node.line, column=node.column)
        if isinstance(node, ir.IRReturnStatement):
            return ast.ReturnStatement(self.lower_expr(node.value), line=node.line, column=node.column)
        if isinstance(node, ir.IRBreakStatement):
            return ast.BreakStatement(line=node.line, column=node.column)
        if isinstance(node, ir.IRContinueStatement):
            return ast.ContinueStatement(line=node.line, column=node.column)
        if isinstance(node, ir.IRPassStatement):
            return ast.PassStatement(line=node.line, column=node.column)
        if isinstance(node, ir.IRRaiseStatement):
            return ast.RaiseStatement(
                self.lower_expr(node.value),
                cause=self.lower_expr(node.cause),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRDelStatement):
            return ast.DelStatement(
                self.lower_expr(node.target),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRGlobalStatement):
            return ast.GlobalStatement(list(node.names), line=node.line, column=node.column)
        if isinstance(node, ir.IRNonlocalStatement):
            return ast.LocalStatement(list(node.names), line=node.line, column=node.column)
        if isinstance(node, ir.IRYieldStatement):
            return ast.YieldStatement(
                self.lower_expr(node.value),
                is_from=node.is_from,
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRAssertStatement):
            return ast.AssertStatement(
                self.lower_expr(node.test),
                msg=self.lower_expr(node.msg),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRImportStatement):
            return ast.ImportStatement(node.module, alias=node.alias, line=node.line, column=node.column)
        if isinstance(node, ir.IRFromImportStatement):
            return ast.FromImportStatement(
                node.module,
                node.names,
                level=node.level,
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRWithStatement):
            return ast.WithStatement(
                [(self.lower_expr(expr), name) for expr, name in node.items],
                body=[self.lower_stmt(stmt) for stmt in node.body],
                is_async=node.is_async,
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRIfStatement):
            return ast.IfStatement(
                self.lower_expr(node.condition),
                [self.lower_stmt(stmt) for stmt in node.body],
                elif_clauses=[
                    (self.lower_expr(clause.condition), [self.lower_stmt(stmt) for stmt in clause.body])
                    for clause in node.elif_clauses
                ],
                else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRWhileLoop):
            return ast.WhileLoop(
                self.lower_expr(node.condition),
                [self.lower_stmt(stmt) for stmt in node.body],
                else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRForLoop):
            return ast.ForLoop(
                self.lower_expr(node.target),
                self.lower_expr(node.iterable),
                [self.lower_stmt(stmt) for stmt in node.body],
                is_async=node.is_async,
                else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRTryStatement):
            return ast.TryStatement(
                [self.lower_stmt(stmt) for stmt in node.body],
                handlers=[
                    ast.ExceptHandler(
                        self.lower_expr(handler.exc_type),
                        name=handler.name,
                        body=[self.lower_stmt(stmt) for stmt in handler.body],
                        line=handler.line,
                        column=handler.column,
                    )
                    for handler in node.handlers
                ],
                else_body=[self.lower_stmt(stmt) for stmt in node.else_body],
                finally_body=[self.lower_stmt(stmt) for stmt in node.finally_body],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRMatchStatement):
            return ast.MatchStatement(
                self.lower_expr(node.subject),
                [
                    ast.CaseClause(
                        pattern=self._lower_pattern(case.pattern),
                        body=[self.lower_stmt(stmt) for stmt in case.body],
                        is_default=case.is_default,
                        line=case.line,
                        column=case.column,
                    )
                    for case in node.cases
                ],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IROnChange):
            return ast.OnChangeStatement(
                self.lower_expr(node.signal),
                [self.lower_stmt(stmt) for stmt in node.body],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRCanvasBlock):
            return ast.CanvasBlock(
                name=node.name,
                body=[self.lower_stmt(stmt) for stmt in node.children],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRRenderExpr):
            return ast.RenderStatement(
                self.lower_expr(node.target),
                self.lower_expr(node.value),
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRViewBinding):
            return ast.ViewBindingStatement(
                self.lower_expr(node.signal),
                self.lower_expr(node.target),
                line=node.line,
                column=node.column,
            )
        raise TypeError(f"Unsupported IR statement node: {type(node).__name__}")

    def lower_expr(self, node):
        if node is None:
            return None
        if isinstance(node, ir.IRLiteral):
            if node.kind == "string":
                return ast.StringLiteral(str(node.value), line=node.line, column=node.column)
            if node.kind == "bytes":
                return ast.BytesLiteral(node.value, line=node.line, column=node.column)
            if node.kind == "bool":
                return ast.BooleanLiteral(bool(node.value), line=node.line, column=node.column)
            if node.kind == "none":
                return ast.NoneLiteral(line=node.line, column=node.column)
            return ast.NumeralLiteral(str(node.value), line=node.line, column=node.column)
        if isinstance(node, ir.IRIdentifier):
            return ast.Identifier(node.name, line=node.line, column=node.column)
        if isinstance(node, ir.IRModelRef):
            return ast.ModelRefLiteral(node.model_name, line=node.line, column=node.column)
        if isinstance(node, ir.IRFStringLiteral):
            parts = []
            for part in node.parts:
                if isinstance(part, ir.IRNode):
                    lowered = self.lower_expr(part)
                    for attr in (
                        "fstring_format_spec",
                        "fstring_conversion",
                        "_fstring_format_spec",
                        "_fstring_conversion",
                    ):
                        if hasattr(part, attr):
                            setattr(lowered, attr, getattr(part, attr))
                    parts.append(lowered)
                else:
                    parts.append(part)
            return ast.FStringLiteral(parts, line=node.line, column=node.column)
        if isinstance(node, ir.IRListLiteral):
            return ast.ListLiteral([self.lower_expr(elem) for elem in node.elements], line=node.line, column=node.column)
        if isinstance(node, ir.IRTupleLiteral):
            return ast.TupleLiteral([self.lower_expr(elem) for elem in node.elements], line=node.line, column=node.column)
        if isinstance(node, ir.IRSetLiteral):
            return ast.SetLiteral([self.lower_expr(elem) for elem in node.elements], line=node.line, column=node.column)
        if isinstance(node, ir.IRDictLiteral):
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
        if isinstance(node, ir.IRBinaryOp):
            return ast.BinaryOp(self.lower_expr(node.left), node.op, self.lower_expr(node.right), line=node.line, column=node.column)
        if isinstance(node, ir.IRUnaryOp):
            return ast.UnaryOp(node.op, self.lower_expr(node.operand), line=node.line, column=node.column)
        if isinstance(node, ir.IRBooleanOp):
            return ast.BooleanOp(node.op, [self.lower_expr(value) for value in node.values], line=node.line, column=node.column)
        if isinstance(node, ir.IRCompareOp):
            return ast.CompareOp(
                self.lower_expr(node.left),
                [(op, self.lower_expr(right)) for op, right in node.comparators],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRAttributeAccess):
            return ast.AttributeAccess(self.lower_expr(node.obj), node.attr, line=node.line, column=node.column)
        if isinstance(node, ir.IRIndexAccess):
            return ast.IndexAccess(self.lower_expr(node.obj), self.lower_expr(node.index), line=node.line, column=node.column)
        if isinstance(node, ir.IRSliceExpr):
            return ast.SliceExpr(self.lower_expr(node.start), self.lower_expr(node.stop), self.lower_expr(node.step), line=node.line, column=node.column)
        if isinstance(node, ir.IRStarredExpr):
            return ast.StarredExpr(self.lower_expr(node.value), is_double=node.is_double, line=node.line, column=node.column)
        if isinstance(node, ir.IRLambdaExpr):
            return ast.LambdaExpr([self._lower_param(param) for param in node.parameters], self.lower_expr(node.body), line=node.line, column=node.column)
        if isinstance(node, ir.IRAwaitExpr):
            return ast.AwaitExpr(self.lower_expr(node.value), line=node.line, column=node.column)
        if isinstance(node, ir.IRYieldExpr):
            return ast.YieldExpr(self.lower_expr(node.value), is_from=node.is_from, line=node.line, column=node.column)
        if isinstance(node, ir.IRNamedExpr):
            return ast.NamedExpr(ast.Identifier(node.target, line=node.line, column=node.column), self.lower_expr(node.value), line=node.line, column=node.column)
        if isinstance(node, ir.IRConditionalExpr):
            return ast.ConditionalExpr(self.lower_expr(node.condition), self.lower_expr(node.true_expr), self.lower_expr(node.false_expr), line=node.line, column=node.column)
        if isinstance(node, ir.IRCallExpr):
            return ast.CallExpr(
                self.lower_expr(node.func),
                [self.lower_expr(arg) for arg in node.args],
                keywords=[(name, self.lower_expr(value)) for name, value in node.keywords],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRPipeExpr):
            return ast.CallExpr(self.lower_expr(node.right), [self.lower_expr(node.left)], line=node.line, column=node.column)
        if isinstance(node, ir.IRResultPropagation):
            return ast.CallExpr(
                ast.Identifier("__ml_result_propagate", line=node.line, column=node.column),
                [self.lower_expr(node.operand)],
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRPromptExpr):
            return self._runtime_call("prompt", node.model, node.template, line=node.line, column=node.column)
        if isinstance(node, ir.IRGenerateExpr):
            return self._runtime_call("generate", node.model, node.template, target_type=node.target_type, line=node.line, column=node.column)
        if isinstance(node, ir.IRThinkExpr):
            return self._runtime_call("think", node.model, node.template, line=node.line, column=node.column)
        if isinstance(node, ir.IRStreamExpr):
            return self._runtime_call("stream", node.model, node.template, line=node.line, column=node.column)
        if isinstance(node, ir.IREmbedExpr):
            return self._runtime_call("embed", node.model, node.value, line=node.line, column=node.column)
        if isinstance(node, ir.IRExtractExpr):
            return self._runtime_call("extract", node.model, node.source, target_type=node.target_type, line=node.line, column=node.column)
        if isinstance(node, ir.IRClassifyExpr):
            args = [self.lower_expr(node.subject)] + [self.lower_expr(item) for item in node.categories]
            keywords = []
            if node.target_type is not None:
                keywords.append(("target_type", self._lower_type(node.target_type)))
            return ast.CallExpr(
                ast.Identifier("classify", line=node.line, column=node.column),
                ([self.lower_expr(node.model)] if node.model is not None else [ast.ModelRefLiteral("")]) + args,
                keywords=keywords,
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRPlanExpr):
            return self._runtime_call("plan", node.model, node.goal, line=node.line, column=node.column)
        if isinstance(node, ir.IRTranscribeExpr):
            return self._runtime_call("transcribe", node.model, node.source, line=node.line, column=node.column)
        if isinstance(node, ir.IRRetrieveExpr):
            args = [self.lower_expr(node.index), self.lower_expr(node.query)]
            keywords = []
            if node.model is not None:
                keywords.append(("model", self.lower_expr(node.model)))
            return ast.CallExpr(ast.Identifier("retrieve"), args, keywords=keywords, line=node.line, column=node.column)
        if isinstance(node, ir.IRSemanticMatchOp):
            keywords = [("threshold", ast.NumeralLiteral(str(node.threshold), line=node.line, column=node.column))]
            if node.model is not None:
                keywords.append(("model", self.lower_expr(node.model)))
            return ast.CallExpr(
                ast.Identifier("semantic_match", line=node.line, column=node.column),
                [self.lower_expr(node.left), self.lower_expr(node.right)],
                keywords=keywords,
                line=node.line,
                column=node.column,
            )
        if isinstance(node, ir.IRListComp):
            clauses = [self._lower_clause(clause) for clause in node.clauses]
            first = clauses[0]
            return ast.ListComprehension(self.lower_expr(node.element), first.target, first.iterable, first.conditions, clauses=clauses, line=node.line, column=node.column)
        if isinstance(node, ir.IRDictComp):
            clauses = [self._lower_clause(clause) for clause in node.clauses]
            first = clauses[0]
            return ast.DictComprehension(self.lower_expr(node.key), self.lower_expr(node.value), first.target, first.iterable, first.conditions, clauses=clauses, line=node.line, column=node.column)
        if isinstance(node, ir.IRSetComp):
            clauses = [self._lower_clause(clause) for clause in node.clauses]
            first = clauses[0]
            return ast.SetComprehension(self.lower_expr(node.element), first.target, first.iterable, first.conditions, clauses=clauses, line=node.line, column=node.column)
        if isinstance(node, ir.IRGeneratorExpr):
            clauses = [self._lower_clause(clause) for clause in node.clauses]
            first = clauses[0]
            return ast.GeneratorExpr(self.lower_expr(node.element), first.target, first.iterable, first.conditions, clauses=clauses, line=node.line, column=node.column)
        raise TypeError(f"Unsupported IR expression node: {type(node).__name__}")

    def _runtime_call(self, name: str, model, payload, *, target_type=None, line=0, column=0):
        args = []
        if model is not None:
            args.append(self.lower_expr(model))
        else:
            args.append(ast.ModelRefLiteral("", line=line, column=column))
        args.append(self.lower_expr(payload))
        keywords = []
        if target_type is not None:
            keywords.append(("target_type", self._lower_type(target_type)))
        return ast.CallExpr(ast.Identifier(name, line=line, column=column), args, keywords=keywords, line=line, column=column)

    def _lower_clause(self, clause: ir.IRComprehensionClause) -> ast.ComprehensionClause:
        return ast.ComprehensionClause(
            self.lower_expr(clause.target),
            self.lower_expr(clause.iterable),
            [self.lower_expr(condition) for condition in clause.conditions],
            line=clause.line,
            column=clause.column,
        )

    def _lower_param(self, param: ir.IRParameter) -> ast.Parameter:
        return ast.Parameter(
            param.name,
            default=self.lower_expr(param.default),
            is_vararg=param.is_vararg,
            is_kwarg=param.is_kwarg,
            annotation=self._lower_type(param.annotation),
            line=param.line,
            column=param.column,
        )

    def _lower_pattern(self, pattern):
        if pattern is None:
            return None
        if isinstance(pattern, ir.IRLiteralPattern):
            return self.lower_expr(pattern.value)
        if isinstance(pattern, ir.IRCapturePattern):
            return ast.Identifier(pattern.name, line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IRWildcardPattern):
            return ast.Identifier("_", line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IROrPattern):
            result = self._lower_pattern(pattern.alternatives[0])
            for alt in pattern.alternatives[1:]:
                result = ast.BinaryOp(result, "|", self._lower_pattern(alt), line=pattern.line, column=pattern.column)
            return result
        if isinstance(pattern, ir.IRAsPattern):
            return ast.BinaryOp(
                self._lower_pattern(pattern.pattern),
                " as ",
                ast.Identifier(pattern.name, line=pattern.line, column=pattern.column),
                line=pattern.line,
                column=pattern.column,
            )
        if isinstance(pattern, ir.IRSequencePattern):
            return ast.TupleLiteral([self._lower_pattern(element) for element in pattern.elements], line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IRRecordPattern):
            entries = []
            for name, value in pattern.fields.items():
                entries.append((ast.StringLiteral(name, line=pattern.line, column=pattern.column), self._lower_pattern(value)))
            return ast.DictLiteral(entries, line=pattern.line, column=pattern.column)
        if isinstance(pattern, ir.IRGuardedPattern):
            return self._lower_pattern(pattern.pattern)
        return self.lower_expr(pattern)

    def _lower_type(self, type_value: CoreType | None):
        if type_value is None:
            return None
        if isinstance(type_value, GenericType):
            params = [self._lower_type(param) for param in type_value.parameters]
            index = params[0] if len(params) == 1 else ast.TupleLiteral(params)
            return ast.IndexAccess(ast.Identifier(self._python_type_name(type_value.name)), index)
        return ast.Identifier(self._python_type_name(type_value.name))

    @staticmethod
    def _python_type_name(type_name: str) -> str:
        """Map core type names to Python runtime annotation identifiers."""
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
