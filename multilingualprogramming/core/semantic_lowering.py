#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Lower a parser AST into Core 1.0 semantic IR.

This pass is the bridge between the multilingual parser (which produces a
surface-level AST common to all human-language frontends) and the Core 1.0
semantic IR (which defines what programs mean, independently of surface or
backend).

Coverage
--------
Every AST node class produced by the parser should map to a specific IR node
here.  Nodes that are not yet mapped fall back to IRExpression with a warning
recorded in the returned IRProgram.  As the parser gains new Core 1.0 syntax
(fn, observe, ~=, prompt, …) the corresponding branches below should be filled
in rather than relying on the fallback.

AI-native transitional detection
---------------------------------
Until the parser is extended with native AI keyword support, this pass detects
calls like ``prompt(model, template)`` and ``embed(model, value)`` by name and
lifts them into the appropriate IR nodes.  This is intentionally temporary.
"""

from __future__ import annotations

import warnings

from multilingualprogramming.core.effects import Effect, EffectSet
from multilingualprogramming.core.ir_nodes import (
    # -- actively used by the current lowering pass --
    IREnumDecl,
    IRTypeDecl,
    IRAgentDecl,
    IRCapturePattern,
    IRGuardedPattern,
    IRLiteralPattern,
    IROrPattern,
    IRAssertStatement,
    IRAssignment,
    IRAttributeAccess,
    IRAwaitExpr,
    IRBinaryOp,
    IRBinding,
    IRBooleanOp,
    IRBreakStatement,
    IRCallExpr,
    IRClassDecl,
    IRClassifyExpr,
    IRCompareOp,
    IRComprehensionClause,
    IRConditionalExpr,
    IRContinueStatement,
    IRDelStatement,
    IRDictComp,
    IRDictLiteral,
    IRElifClause,
    IREmbedExpr,
    IRExceptHandler,
    IRExpression,
    IRExprStatement,
    IRExtractExpr,
    IRFStringLiteral,
    IRForLoop,
    IRFromImportStatement,
    IRFunction,
    IRGenerateExpr,
    IRGeneratorExpr,
    IRGlobalStatement,
    IRIdentifier,
    IRIfStatement,
    IRImportStatement,
    IRIndexAccess,
    IRLambdaExpr,
    IRListComp,
    IRListLiteral,
    IRLiteral,
    IRMatchCase,
    IRMatchStatement,
    IRModelRef,
    IRNamedExpr,
    IRNonlocalStatement,
    IRObserveBinding,
    IRParameter,
    IRPassStatement,
    IRPipeExpr,
    IRProgram,
    IRPromptExpr,
    IRRaiseStatement,
    IRReturnStatement,
    IRSemanticMatchOp,
    IRSetComp,
    IRSetLiteral,
    IRSliceExpr,
    IRStarredExpr,
    IRStreamExpr,
    IRThinkExpr,
    IRToolDecl,
    IRTryStatement,
    IRTupleLiteral,
    IRUnaryOp,
    IRWithStatement,
    IRWildcardPattern,
    IRWhileLoop,
    IRYieldExpr,
    IRYieldStatement,
)
from multilingualprogramming.core.types import (
    BOOL_TYPE,
    BYTES_TYPE,
    FLOAT_TYPE,
    INT_TYPE,
    MODEL_TYPE,
    NONE_TYPE,
    STREAM_STR,
    STRING_TYPE,
    VECTOR_FLOAT,
    CoreType,
    GenericType,
    NamedType,
    RecordField,
    RecordType,
    UnionType,
    UnionVariant,
)
from multilingualprogramming.parser import ast_nodes as ast


# ---------------------------------------------------------------------------
# Names of call expressions that are transitionally lifted to AI IR nodes
# until the parser gains native keyword support.
# ---------------------------------------------------------------------------
_AI_CALL_NAMES = frozenset({
    "prompt", "generate", "think", "stream", "embed", "extract", "classify",
})

_AGENT_DECORATOR = "agent"
_TOOL_DECORATOR = "tool"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def lower_to_semantic_ir(program_ast: ast.Program, source_language: str) -> IRProgram:
    """Lower a parser Program AST into a Core 1.0 IRProgram."""
    if not isinstance(program_ast, ast.Program):
        raise TypeError("lower_to_semantic_ir expects a Program AST root")

    ctx = _LoweringContext(source_language=source_language or "en")
    body = [ctx.lower(node) for node in program_ast.body]
    return IRProgram(
        body=body,
        source_language=ctx.source_language,
        effects=ctx.accumulated_effects(),
        line=program_ast.line,
        column=program_ast.column,
    )


# ---------------------------------------------------------------------------
# Internal lowering context
# ---------------------------------------------------------------------------

class _LoweringContext:
    """Carries state across a single lowering pass."""

    def __init__(self, source_language: str) -> None:
        self.source_language = source_language
        self._effects: set[str] = set()
        self._warnings: list[str] = []

    # -- Effect tracking ------------------------------------------------

    def require_effect(self, name: str) -> None:
        """Record that lowering needs a named capability."""
        self._effects.add(name)

    def accumulated_effects(self) -> EffectSet:
        """Return all effects required by the lowered program."""
        return EffectSet(effects=tuple(Effect(n) for n in sorted(self._effects)))

    def effects_from_names(self, names: list[str]) -> EffectSet:
        """Build an EffectSet from explicit effect names."""
        return EffectSet(effects=tuple(Effect(n) for n in names))

    # -- Main dispatch --------------------------------------------------

    def lower(self, node) -> object:
        """Dispatch an AST node to its lowering method."""
        if node is None:
            return None
        method = getattr(self, f"_lower_{type(node).__name__}", self._lower_unknown)
        return method(node)

    def lower_list(self, nodes: list) -> list:
        """Lower a list of nodes while preserving order."""
        return [self.lower(n) for n in (nodes or [])]

    # -- Fallback -------------------------------------------------------

    def _lower_unknown(self, node) -> IRExpression:
        name = type(node).__name__
        self._warnings.append(
            f"No IR lowering for AST node {name!r} — using "
            "IRExpression placeholder"
        )
        warnings.warn(
            f"semantic_lowering: no handler for {name!r}, emitting IRExpression placeholder",
            stacklevel=4,
        )
        return IRExpression(
            line=getattr(node, "line", 0),
            column=getattr(node, "column", 0),
        )

    # ==================================================================
    # Literals
    # ==================================================================

    def _lower_NumeralLiteral(self, node: ast.NumeralLiteral) -> IRLiteral:
        raw = str(node.value)
        if "." in raw or "e" in raw.lower():
            return IRLiteral(value=node.value, kind="float",
                             inferred_type=FLOAT_TYPE,
                             line=node.line, column=node.column)
        return IRLiteral(value=node.value, kind="int",
                         inferred_type=INT_TYPE,
                         line=node.line, column=node.column)

    def _lower_StringLiteral(self, node: ast.StringLiteral) -> IRLiteral:
        return IRLiteral(value=node.value, kind="string",
                         inferred_type=STRING_TYPE,
                         line=node.line, column=node.column)

    def _lower_BytesLiteral(self, node: ast.BytesLiteral) -> IRLiteral:
        return IRLiteral(value=node.value, kind="bytes",
                         inferred_type=BYTES_TYPE,
                         line=node.line, column=node.column)

    def _lower_DateLiteral(self, node: ast.DateLiteral) -> IRLiteral:
        return IRLiteral(value=node.value, kind="date",
                         inferred_type=NamedType("date"),
                         line=node.line, column=node.column)

    def _lower_BooleanLiteral(self, node: ast.BooleanLiteral) -> IRLiteral:
        return IRLiteral(value=node.value, kind="bool",
                         inferred_type=BOOL_TYPE,
                         line=node.line, column=node.column)

    def _lower_NoneLiteral(self, node: ast.NoneLiteral) -> IRLiteral:
        return IRLiteral(value=None, kind="none",
                         inferred_type=NONE_TYPE,
                         line=node.line, column=node.column)

    def _lower_FStringLiteral(self, node: ast.FStringLiteral) -> IRFStringLiteral:
        parts = []
        for part in node.parts:
            parts.append(self.lower(part) if isinstance(part, ast.ASTNode) else part)
        return IRFStringLiteral(parts=parts, inferred_type=STRING_TYPE,
                                line=node.line, column=node.column)

    # -- Collections ----------------------------------------------------

    def _lower_ListLiteral(self, node: ast.ListLiteral) -> IRListLiteral:
        return IRListLiteral(elements=self.lower_list(node.elements),
                             line=node.line, column=node.column)

    def _lower_TupleLiteral(self, node: ast.TupleLiteral) -> IRTupleLiteral:
        return IRTupleLiteral(elements=self.lower_list(node.elements),
                              line=node.line, column=node.column)

    def _lower_SetLiteral(self, node: ast.SetLiteral) -> IRSetLiteral:
        return IRSetLiteral(elements=self.lower_list(node.elements),
                            line=node.line, column=node.column)

    def _lower_DictLiteral(self, node: ast.DictLiteral) -> IRDictLiteral:
        entries = []
        for entry in node.entries:
            if isinstance(entry, ast.DictUnpackEntry):
                entries.append(self.lower(entry.value))
            elif isinstance(entry, tuple) and len(entry) == 2:
                entries.append((self.lower(entry[0]), self.lower(entry[1])))
        return IRDictLiteral(entries=entries, line=node.line, column=node.column)

    # ==================================================================
    # Expressions
    # ==================================================================

    def _lower_Identifier(self, node: ast.Identifier) -> IRIdentifier:
        return IRIdentifier(name=node.name, line=node.line, column=node.column)

    def _lower_ModelRefLiteral(self, node: ast.ModelRefLiteral) -> IRModelRef:
        return IRModelRef(
            model_name=node.model_name,
            inferred_type=MODEL_TYPE,
            line=node.line,
            column=node.column,
        )

    def _lower_BinaryOp(self, node: ast.BinaryOp) -> IRBinaryOp | IRPipeExpr | IRSemanticMatchOp:
        if node.op == "|>":
            return IRPipeExpr(
                left=self.lower(node.left),
                right=self.lower(node.right),
                line=node.line, column=node.column,
            )
        if node.op == "~=":
            return IRSemanticMatchOp(
                left=self.lower(node.left),
                right=self.lower(node.right),
                line=node.line, column=node.column,
            )
        return IRBinaryOp(
            left=self.lower(node.left),
            op=node.op,
            right=self.lower(node.right),
            line=node.line, column=node.column,
        )

    def _lower_UnaryOp(self, node: ast.UnaryOp) -> IRUnaryOp:
        return IRUnaryOp(op=node.op, operand=self.lower(node.operand),
                         line=node.line, column=node.column)

    def _lower_BooleanOp(self, node: ast.BooleanOp) -> IRBooleanOp:
        return IRBooleanOp(op=node.op, values=self.lower_list(node.values),
                           inferred_type=BOOL_TYPE,
                           line=node.line, column=node.column)

    def _lower_CompareOp(self, node: ast.CompareOp) -> IRCompareOp:
        comparators = []
        for item in node.comparators:
            if isinstance(item, tuple) and len(item) == 2:
                comparators.append((item[0], self.lower(item[1])))
            else:
                comparators.append(item)
        return IRCompareOp(left=self.lower(node.left), comparators=comparators,
                           inferred_type=BOOL_TYPE,
                           line=node.line, column=node.column)

    def _lower_CallExpr(self, node: ast.CallExpr) -> object:
        # Detect transitional AI call patterns before generic lowering.
        func_name = _call_name(node.func)
        if func_name in _AI_CALL_NAMES:
            return self._lower_ai_call(func_name, node)
        return IRCallExpr(
            func=self.lower(node.func),
            args=self.lower_list(node.args),
            keywords=self._lower_keywords(node.keywords),
            line=node.line, column=node.column,
        )

    def _lower_keywords(self, keywords: list) -> list[tuple[str, object]]:
        result = []
        for kw in (keywords or []):
            if isinstance(kw, tuple) and len(kw) == 2:
                result.append((kw[0], self.lower(kw[1])))
            elif hasattr(kw, "arg") and hasattr(kw, "value"):
                result.append((kw.arg, self.lower(kw.value)))
        return result

    def _lower_ai_call(self, name: str, node: ast.CallExpr) -> object:
        """Transitionally lift known AI call patterns to AI IR nodes."""
        self.require_effect("ai")
        args = node.args or []
        model = None
        payload = None
        if args and isinstance(args[0], ast.ModelRefLiteral):
            model = self.lower(args[0])
            payload = self.lower(args[1]) if len(args) > 1 else None
        elif len(args) > 1:
            model = self.lower(args[0])
            payload = self.lower(args[1])
        elif args:
            payload = self.lower(args[0])

        target_type = _lower_annotation(getattr(node, "core_target_type", None))
        ln, col = node.line, node.column
        if name == "prompt":
            return IRPromptExpr(model=model, template=payload,
                                inferred_type=STRING_TYPE, line=ln, column=col)
        if name == "generate":
            return IRGenerateExpr(model=model, template=payload,
                                  target_type=target_type,
                                  line=ln, column=col)
        if name == "think":
            return IRThinkExpr(model=model, template=payload,
                               line=ln, column=col)
        if name == "stream":
            return IRStreamExpr(model=model, template=payload,
                                inferred_type=STREAM_STR, line=ln, column=col)
        if name == "embed":
            return IREmbedExpr(model=model, value=payload,
                               inferred_type=VECTOR_FLOAT, line=ln, column=col)
        if name == "extract":
            return IRExtractExpr(model=model, source=payload,
                                 target_type=target_type,
                                 line=ln, column=col)
        if name == "classify":
            categories = self.lower_list(args[2:])
            if payload is not None and len(args) == 1:
                categories = []
            return IRClassifyExpr(model=model, subject=payload,
                                  categories=categories,
                                  target_type=target_type,
                                  line=ln, column=col)
        return IRExpression(line=ln, column=col)

    def _lower_AttributeAccess(self, node: ast.AttributeAccess) -> IRAttributeAccess:
        return IRAttributeAccess(obj=self.lower(node.obj), attr=node.attr,
                                 line=node.line, column=node.column)

    def _lower_IndexAccess(self, node: ast.IndexAccess) -> IRIndexAccess:
        return IRIndexAccess(obj=self.lower(node.obj), index=self.lower(node.index),
                             line=node.line, column=node.column)

    def _lower_SliceExpr(self, node: ast.SliceExpr) -> IRSliceExpr:
        return IRSliceExpr(start=self.lower(node.start),
                           stop=self.lower(node.stop),
                           step=self.lower(node.step),
                           line=node.line, column=node.column)

    def _lower_StarredExpr(self, node: ast.StarredExpr) -> IRStarredExpr:
        return IRStarredExpr(value=self.lower(node.value),
                             is_double=node.is_double,
                             line=node.line, column=node.column)

    def _lower_LambdaExpr(self, node: ast.LambdaExpr) -> IRLambdaExpr:
        return IRLambdaExpr(
            parameters=self._lower_params(node.params),
            body=self.lower(node.body),
            line=node.line, column=node.column,
        )

    def _lower_AwaitExpr(self, node: ast.AwaitExpr) -> IRAwaitExpr:
        return IRAwaitExpr(value=self.lower(node.value),
                           line=node.line, column=node.column)

    def _lower_YieldExpr(self, node: ast.YieldExpr) -> IRYieldExpr:
        return IRYieldExpr(value=self.lower(node.value),
                           is_from=node.is_from,
                           line=node.line, column=node.column)

    def _lower_NamedExpr(self, node: ast.NamedExpr) -> IRNamedExpr:
        target = node.target.name if isinstance(node.target, ast.Identifier) else str(node.target)
        return IRNamedExpr(target=target, value=self.lower(node.value),
                           line=node.line, column=node.column)

    def _lower_ConditionalExpr(self, node: ast.ConditionalExpr) -> IRConditionalExpr:
        return IRConditionalExpr(
            condition=self.lower(node.condition),
            true_expr=self.lower(node.true_expr),
            false_expr=self.lower(node.false_expr),
            line=node.line, column=node.column,
        )

    # ==================================================================
    # Comprehensions
    # ==================================================================

    def _lower_ComprehensionClause(self, node: ast.ComprehensionClause) -> IRComprehensionClause:
        return IRComprehensionClause(
            target=self.lower(node.target),
            iterable=self.lower(node.iterable),
            conditions=self.lower_list(node.conditions),
            line=node.line, column=node.column,
        )

    def _lower_clauses(self, node) -> list[IRComprehensionClause]:
        if hasattr(node, "clauses"):
            return [self._lower_ComprehensionClause(c) for c in node.clauses]
        return [IRComprehensionClause(
            target=self.lower(node.target),
            iterable=self.lower(node.iterable),
            conditions=self.lower_list(getattr(node, "conditions", [])),
        )]

    def _lower_ListComprehension(self, node: ast.ListComprehension) -> IRListComp:
        return IRListComp(element=self.lower(node.element),
                          clauses=self._lower_clauses(node),
                          line=node.line, column=node.column)

    def _lower_DictComprehension(self, node: ast.DictComprehension) -> IRDictComp:
        return IRDictComp(key=self.lower(node.key), value=self.lower(node.value),
                          clauses=self._lower_clauses(node),
                          line=node.line, column=node.column)

    def _lower_SetComprehension(self, node: ast.SetComprehension) -> IRSetComp:
        return IRSetComp(element=self.lower(node.element),
                         clauses=self._lower_clauses(node),
                         line=node.line, column=node.column)

    def _lower_GeneratorExpr(self, node: ast.GeneratorExpr) -> IRGeneratorExpr:
        return IRGeneratorExpr(element=self.lower(node.element),
                               clauses=self._lower_clauses(node),
                               line=node.line, column=node.column)

    # ==================================================================
    # Declarations
    # ==================================================================

    def _lower_VariableDeclaration(
        self,
        node: ast.VariableDeclaration,
    ) -> IRBinding | IRObserveBinding:
        annotation = _lower_annotation(node.annotation) if hasattr(node, "annotation") else None
        value = self.lower(node.value)
        kind = getattr(node, "declaration_kind", "let")
        if kind == "observe":
            return IRObserveBinding(name=node.name, value=value, annotation=annotation,
                                    line=node.line, column=node.column)
        return IRBinding(name=node.name, value=value,
                         is_mutable=(kind == "var"),
                         annotation=annotation,
                         line=node.line, column=node.column)

    def _lower_EnumDecl(self, node: ast.EnumDecl) -> IREnumDecl:
        variants = []
        for v in node.variants:
            if v.fields:
                fields = tuple(
                    RecordField(
                        name=fname,
                        field_type=_lower_annotation(ann) or NamedType("unknown"),
                    )
                    for fname, ann in v.fields
                )
                payload = RecordType(name=v.name, fields=fields)
            else:
                payload = None
            variants.append(UnionVariant(name=v.name, payload=payload))
        union_type = UnionType(name=node.name, variants=tuple(variants))
        return IREnumDecl(name=node.name, declared_type=union_type,
                          line=node.line, column=node.column)

    def _lower_RecordDecl(self, node: ast.RecordDecl) -> IRTypeDecl:
        fields = tuple(
            RecordField(
                name=f.name,
                field_type=_lower_annotation(f.annotation) or NamedType("unknown"),
            )
            for f in node.fields
        )
        record_type = RecordType(name=node.name, fields=fields)
        return IRTypeDecl(name=node.name, declared_type=record_type,
                          line=node.line, column=node.column)

    def _lower_ObserveDeclaration(self, node: ast.ObserveDeclaration) -> IRObserveBinding:
        return IRObserveBinding(
            name=node.name,
            value=self.lower(node.value),
            annotation=_lower_annotation(node.annotation),
            line=node.line, column=node.column,
        )

    def _lower_FunctionDef(self, node: ast.FunctionDef) -> IRFunction | IRAgentDecl | IRToolDecl:
        decorators = self.lower_list(node.decorators)
        # Detect @agent and @tool decorators before generic lowering.
        agent_model = _detect_agent_decorator(node.decorators)
        tool_desc = _detect_tool_decorator(node.decorators)
        params = self._lower_params(node.params)
        body = self.lower_list(node.body)
        ret = _lower_annotation(node.return_annotation)
        effects = _parse_effects_annotation(node)

        if agent_model is not None:
            self.require_effect("ai")
            return IRAgentDecl(
                name=node.name,
                model=IRModelRef(model_name=agent_model,
                                 inferred_type=MODEL_TYPE,
                                 line=node.line, column=node.column),
                parameters=params,
                body=body,
                return_type=ret,
                effects=effects,
                is_async=node.is_async,
                line=node.line, column=node.column,
            )

        if tool_desc is not None:
            return IRToolDecl(
                name=node.name,
                description=tool_desc,
                parameters=params,
                body=body,
                return_type=ret,
                effects=effects,
                line=node.line, column=node.column,
            )

        return IRFunction(
            name=node.name,
            parameters=params,
            body=body,
            return_type=ret,
            effects=effects,
            is_async=node.is_async,
            syntax_keyword=getattr(node, "syntax_keyword", "fn"),
            decorators=decorators,
            line=node.line, column=node.column,
        )

    def _lower_params(self, params: list) -> list[IRParameter]:
        result = []
        for p in (params or []):
            if isinstance(p, ast.Parameter):
                result.append(IRParameter(
                    name=p.name,
                    annotation=_lower_annotation(p.annotation),
                    default=self.lower(p.default),
                    is_vararg=p.is_vararg,
                    is_kwarg=p.is_kwarg,
                    line=p.line, column=p.column,
                ))
            else:
                # Plain string parameter name (legacy form)
                result.append(IRParameter(name=str(p)))
        return result

    def _lower_ClassDef(self, node: ast.ClassDef) -> IRClassDecl:
        return IRClassDecl(
            name=node.name,
            bases=self.lower_list(node.bases),
            body=self.lower_list(node.body),
            decorators=self.lower_list(node.decorators),
            line=node.line, column=node.column,
        )

    # ==================================================================
    # Statements
    # ==================================================================

    def _lower_Assignment(self, node: ast.Assignment) -> IRAssignment:
        return IRAssignment(
            target=self.lower(node.target),
            value=self.lower(node.value),
            op=node.op,
            line=node.line, column=node.column,
        )

    def _lower_AnnAssignment(self, node: ast.AnnAssignment) -> IRBinding:
        return IRBinding(
            name=_target_name(node.target),
            value=self.lower(node.value),
            is_mutable=True,
            annotation=_lower_annotation(node.annotation),
            line=node.line, column=node.column,
        )

    def _lower_ChainedAssignment(self, node: ast.ChainedAssignment) -> IRAssignment:
        # a = b = value  →  flatten into last target = value for now
        last = self.lower(node.targets[-1]) if node.targets else None
        return IRAssignment(target=last, value=self.lower(node.value),
                            line=node.line, column=node.column)

    def _lower_ExpressionStatement(self, node: ast.ExpressionStatement) -> IRExprStatement:
        return IRExprStatement(expression=self.lower(node.expression),
                               line=node.line, column=node.column)

    def _lower_PassStatement(self, node: ast.PassStatement) -> IRPassStatement:
        return IRPassStatement(line=node.line, column=node.column)

    def _lower_ReturnStatement(self, node: ast.ReturnStatement) -> IRReturnStatement:
        return IRReturnStatement(value=self.lower(node.value),
                                 line=node.line, column=node.column)

    def _lower_BreakStatement(self, node: ast.BreakStatement) -> IRBreakStatement:
        return IRBreakStatement(line=node.line, column=node.column)

    def _lower_ContinueStatement(self, node: ast.ContinueStatement) -> IRContinueStatement:
        return IRContinueStatement(line=node.line, column=node.column)

    def _lower_RaiseStatement(self, node: ast.RaiseStatement) -> IRRaiseStatement:
        return IRRaiseStatement(value=self.lower(node.value),
                                cause=self.lower(node.cause),
                                line=node.line, column=node.column)

    def _lower_DelStatement(self, node: ast.DelStatement) -> IRDelStatement:
        return IRDelStatement(target=self.lower(node.target),
                              line=node.line, column=node.column)

    def _lower_AssertStatement(self, node: ast.AssertStatement) -> IRAssertStatement:
        return IRAssertStatement(test=self.lower(node.test),
                                 msg=self.lower(node.msg),
                                 line=node.line, column=node.column)

    def _lower_GlobalStatement(self, node: ast.GlobalStatement) -> IRGlobalStatement:
        return IRGlobalStatement(names=list(node.names),
                                 line=node.line, column=node.column)

    def _lower_LocalStatement(self, node: ast.LocalStatement) -> IRNonlocalStatement:
        return IRNonlocalStatement(names=list(node.names),
                                   line=node.line, column=node.column)

    def _lower_YieldStatement(self, node: ast.YieldStatement) -> IRYieldStatement:
        return IRYieldStatement(value=self.lower(node.value),
                                is_from=node.is_from,
                                line=node.line, column=node.column)

    def _lower_ImportStatement(self, node: ast.ImportStatement) -> IRImportStatement:
        return IRImportStatement(module=node.module, alias=node.alias,
                                 line=node.line, column=node.column)

    def _lower_FromImportStatement(self, node: ast.FromImportStatement) -> IRFromImportStatement:
        names: list[tuple[str, str | None]] = []
        for item in node.names:
            if isinstance(item, tuple):
                names.append((item[0], item[1] if len(item) > 1 else None))
            else:
                names.append((str(item), None))
        return IRFromImportStatement(
            module=node.module or "",
            names=names,
            level=getattr(node, "level", 0),
            line=node.line, column=node.column,
        )

    def _lower_WithStatement(self, node: ast.WithStatement) -> IRWithStatement:
        items = [(self.lower(expr), name) for expr, name in node.items]
        return IRWithStatement(
            items=items,
            body=self.lower_list(node.body),
            is_async=node.is_async,
            line=node.line, column=node.column,
        )

    # ==================================================================
    # Control flow
    # ==================================================================

    def _lower_IfStatement(self, node: ast.IfStatement) -> IRIfStatement:
        elif_clauses = []
        for cond, body in (node.elif_clauses or []):
            elif_clauses.append(IRElifClause(
                condition=self.lower(cond),
                body=self.lower_list(body),
            ))
        return IRIfStatement(
            condition=self.lower(node.condition),
            body=self.lower_list(node.body),
            elif_clauses=elif_clauses,
            else_body=self.lower_list(node.else_body),
            line=node.line, column=node.column,
        )

    def _lower_WhileLoop(self, node: ast.WhileLoop) -> IRWhileLoop:
        return IRWhileLoop(
            condition=self.lower(node.condition),
            body=self.lower_list(node.body),
            else_body=self.lower_list(node.else_body),
            line=node.line, column=node.column,
        )

    def _lower_ForLoop(self, node: ast.ForLoop) -> IRForLoop:
        return IRForLoop(
            target=self.lower(node.target),
            iterable=self.lower(node.iterable),
            body=self.lower_list(node.body),
            else_body=self.lower_list(node.else_body),
            is_async=node.is_async,
            line=node.line, column=node.column,
        )

    def _lower_TryStatement(self, node: ast.TryStatement) -> IRTryStatement:
        handlers = [self._lower_ExceptHandler(h) for h in (node.handlers or [])]
        return IRTryStatement(
            body=self.lower_list(node.body),
            handlers=handlers,
            else_body=self.lower_list(node.else_body),
            finally_body=self.lower_list(node.finally_body),
            line=node.line, column=node.column,
        )

    def _lower_ExceptHandler(self, node: ast.ExceptHandler) -> IRExceptHandler:
        return IRExceptHandler(
            exc_type=self.lower(node.exc_type),
            name=node.name,
            body=self.lower_list(node.body),
            line=node.line, column=node.column,
        )

    def _lower_MatchStatement(self, node: ast.MatchStatement) -> IRMatchStatement:
        cases = [self._lower_CaseClause(c) for c in (node.cases or [])]
        return IRMatchStatement(
            subject=self.lower(node.subject),
            cases=cases,
            line=node.line, column=node.column,
        )

    def _lower_CaseClause(self, node: ast.CaseClause) -> IRMatchCase:
        return IRMatchCase(
            pattern=self._lower_pattern(node.pattern, node.guard),
            body=self.lower_list(node.body),
            is_default=node.is_default,
            line=node.line, column=node.column,
        )

    def _lower_pattern(self, pattern, guard=None) -> object:
        """Lower a parser pattern node to an IR pattern node."""
        if pattern is None:
            return None
        node = _lower_pattern_node(self, pattern)
        if guard is not None:
            node = IRGuardedPattern(
                pattern=node,
                guard=self.lower(guard),
                line=getattr(pattern, "line", 0),
                column=getattr(pattern, "column", 0),
            )
        return node


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _lower_annotation(annotation) -> CoreType | None:
    """Convert a narrow set of annotation AST nodes into CoreType values."""
    if annotation is None:
        return None
    if isinstance(annotation, ast.Identifier):
        mapping = {
            "int": INT_TYPE, "float": FLOAT_TYPE, "str": STRING_TYPE,
            "string": STRING_TYPE, "bool": BOOL_TYPE, "bytes": BYTES_TYPE,
            "none": NONE_TYPE, "None": NONE_TYPE,
        }
        return mapping.get(annotation.name, NamedType(annotation.name))
    if isinstance(annotation, ast.IndexAccess):
        # Generic form: list[int], option[str], result[T, E], stream[T]
        outer = _lower_annotation(annotation.obj)
        if isinstance(annotation.index, ast.TupleLiteral):
            params = tuple(_lower_annotation(e) for e in annotation.index.elements)
        else:
            params = (_lower_annotation(annotation.index),)
        name = outer.name if outer else "unknown"
        return GenericType(name, parameters=params)
    return NamedType(type(annotation).__name__)


def _target_name(target) -> str:
    if isinstance(target, ast.Identifier):
        return target.name
    return str(target)


def _call_name(func) -> str | None:
    if isinstance(func, ast.Identifier):
        return func.name
    return None


def _extract_model_from_call(dec: "ast.CallExpr") -> str | None:
    """Return the model name from an @agent call's keywords or first arg."""
    for kw in (dec.keywords or []):
        key, val = (
            kw
            if isinstance(kw, tuple)
            else (getattr(kw, "arg", ""), getattr(kw, "value", None))
        )
        if key == "model":
            if isinstance(val, ast.ModelRefLiteral):
                return val.model_name
            if isinstance(val, ast.Identifier):
                return val.name
    if dec.args:
        if isinstance(dec.args[0], ast.ModelRefLiteral):
            return dec.args[0].model_name
        if isinstance(dec.args[0], ast.Identifier):
            return dec.args[0].name
    return None


def _detect_agent_decorator(decorators: list) -> str | None:
    """Return the model name string if an @agent decorator is present."""
    for dec in (decorators or []):
        if isinstance(dec, ast.CallExpr):
            if _call_name(dec.func) == _AGENT_DECORATOR:
                return _extract_model_from_call(dec)
        elif isinstance(dec, ast.Identifier) and dec.name == _AGENT_DECORATOR:
            return ""
    return None


def _detect_tool_decorator(decorators: list) -> str | None:
    """Return the description string if a @tool decorator is present."""
    for dec in (decorators or []):
        if isinstance(dec, ast.CallExpr):
            if _call_name(dec.func) == _TOOL_DECORATOR:
                for kw in (dec.keywords or []):
                    key, val = (
                        kw
                        if isinstance(kw, tuple)
                        else (getattr(kw, "arg", ""), getattr(kw, "value", None))
                    )
                    if key == "description" and isinstance(val, ast.StringLiteral):
                        return val.value
                if dec.args and isinstance(dec.args[0], ast.StringLiteral):
                    return dec.args[0].value
                return ""
        elif isinstance(dec, ast.Identifier) and dec.name == _TOOL_DECORATOR:
            return ""
    return None


def _parse_effects_annotation(node: ast.FunctionDef) -> EffectSet:
    """Extract capability names from a trailing 'uses x, y' annotation.

    The parser does not yet emit a dedicated effects node, so effects are
    currently stored as a `uses` attribute (list of strings) when the frontend
    adds support.  This helper is forward-compatible with that convention.
    """
    uses = getattr(node, "uses", None)
    if not uses:
        return EffectSet()
    names = [uses] if isinstance(uses, str) else list(uses)
    return EffectSet(effects=tuple(Effect(n) for n in names))


def _lower_pattern_node(ctx: _LoweringContext, pattern) -> object:
    """Lower a parser pattern node to an IR pattern node."""
    if pattern is None:
        return IRWildcardPattern()
    # Wildcard: _
    if isinstance(pattern, ast.Identifier) and pattern.name == "_":
        return IRWildcardPattern(line=pattern.line, column=pattern.column)
    # Capture: any plain name
    if isinstance(pattern, ast.Identifier):
        return IRCapturePattern(name=pattern.name,
                                line=pattern.line, column=pattern.column)
    # Literal
    if isinstance(pattern, (ast.NumeralLiteral, ast.StringLiteral,
                            ast.BooleanLiteral, ast.NoneLiteral)):
        return IRLiteralPattern(value=ctx.lower(pattern),
                                line=pattern.line, column=pattern.column)
    # OR pattern: BinaryOp with op="|"
    if isinstance(pattern, ast.BinaryOp) and pattern.op == "|":
        alts = _flatten_or_pattern(ctx, pattern)
        return IROrPattern(alternatives=alts,
                           line=pattern.line, column=pattern.column)
    # Default: emit capture with a warning
    return IRCapturePattern(name=str(type(pattern).__name__),
                            line=getattr(pattern, "line", 0),
                            column=getattr(pattern, "column", 0))


def _flatten_or_pattern(ctx: _LoweringContext, node: ast.BinaryOp) -> list:
    """Flatten nested | patterns into a flat list of alternatives."""
    result = []
    for side in (node.left, node.right):
        if isinstance(side, ast.BinaryOp) and side.op == "|":
            result.extend(_flatten_or_pattern(ctx, side))
        else:
            result.append(_lower_pattern_node(ctx, side))
    return result
