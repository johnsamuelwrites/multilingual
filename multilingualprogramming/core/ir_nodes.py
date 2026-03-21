#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Semantic IR node vocabulary for Multilingual Core 1.0.

Every construct that has a defined meaning in Core 1.0 has a corresponding node
here.  This is the semantic vocabulary of the language — the point where
surface variation across human languages ends and shared meaning begins.

Node families
-------------
  Program root    — IRProgram
  Declarations    — IRBinding, IRFunction, IREnumDecl, IRTypeDecl,
                    IRClassDecl, IRAgentDecl, IRToolDecl
  Parameters      — IRParameter
  Literals        — IRLiteral, IRFStringLiteral,
                    IRListLiteral, IRDictLiteral, IRSetLiteral, IRTupleLiteral
  Expressions     — IRIdentifier, IRBinaryOp, IRUnaryOp, IRBooleanOp,
                    IRCompareOp, IRCallExpr, IRAttributeAccess, IRIndexAccess,
                    IRLambdaExpr, IRPipeExpr, IRResultPropagation,
                    IRAwaitExpr, IRYieldExpr, IRNamedExpr, IRConditionalExpr,
                    IRSliceExpr, IRStarredExpr
  Comprehensions  — IRComprehensionClause, IRListComp, IRDictComp,
                    IRSetComp, IRGeneratorExpr
  AI-native       — IRModelRef, IRPromptExpr, IRGenerateExpr, IRThinkExpr,
                    IRStreamExpr, IREmbedExpr, IRExtractExpr, IRClassifyExpr,
                    IRSemanticMatchOp
  Statements      — IRAssignment, IRAugAssignment, IRExprStatement,
                    IRReturnStatement, IRBreakStatement, IRContinueStatement,
                    IRPassStatement, IRRaiseStatement, IRDelStatement,
                    IRAssertStatement, IRGlobalStatement, IRNonlocalStatement,
                    IRYieldStatement, IRImportStatement, IRFromImportStatement,
                    IRWithStatement
  Control flow    — IRIfStatement, IRElifClause, IRWhileLoop, IRForLoop,
                    IRTryStatement, IRExceptHandler,
                    IRMatchStatement, IRMatchCase
  Patterns        — IRLiteralPattern, IRCapturePattern, IRWildcardPattern,
                    IROrPattern, IRRecordPattern, IRGuardedPattern,
                    IRAsPattern, IRSemanticPattern
  Reactive        — IRObserveBinding, IROnChange,
                    IRCanvasBlock, IRRenderExpr, IRViewBinding
"""

from __future__ import annotations

from dataclasses import dataclass, field

from multilingualprogramming.core.effects import EffectSet
from multilingualprogramming.core.types import CoreType


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class IRNode:
    """Base semantic IR node.  All nodes carry source position."""

    line: int = 0
    column: int = 0


# ---------------------------------------------------------------------------
# Program root
# ---------------------------------------------------------------------------

@dataclass
class IRProgram(IRNode):
    """Root of a semantic IR program."""

    body: list[IRNode] = field(default_factory=list)
    source_language: str = "en"
    effects: EffectSet = field(default_factory=EffectSet)


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

@dataclass  # pylint: disable=too-many-instance-attributes
class IRParameter(IRNode):
    """Function or agent parameter with full type and calling-convention info."""

    name: str = ""
    annotation: CoreType | None = None
    default: IRNode | None = None
    is_vararg: bool = False       # *args
    is_kwarg: bool = False        # **kwargs
    is_keyword_only: bool = False
    is_positional_only: bool = False

    def __eq__(self, other):
        """Keep legacy comparisons to bare parameter names working."""
        if isinstance(other, str):
            return self.name == other
        return super().__eq__(other)


# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------

@dataclass
class IRBinding(IRNode):
    """Immutable (let) or mutable (var) named binding."""

    name: str = ""
    value: IRNode | None = None
    is_mutable: bool = False
    annotation: CoreType | None = None


@dataclass
class IRObserveBinding(IRNode):
    """Reactive mutable binding: observe var name: T = value.

    Signals downstream views or handlers whenever the value changes.
    """

    name: str = ""
    value: IRNode | None = None
    annotation: CoreType | None = None

# pylint: disable=too-many-instance-attributes
@dataclass
class IRFunction(IRNode):
    """Named function declaration."""

    name: str = ""
    parameters: list[IRParameter] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    return_type: CoreType | None = None
    effects: EffectSet = field(default_factory=EffectSet)
    is_async: bool = False
    syntax_keyword: str = "fn"   # "fn" (Core 1.0) or "def" (legacy)
    decorators: list[IRNode] = field(default_factory=list)


@dataclass
class IRTypeDecl(IRNode):
    """Named type alias or record declaration: type Name = ..."""

    name: str = ""
    declared_type: CoreType | None = None


@dataclass
class IREnumDecl(IRNode):
    """Tagged union declaration: enum Name = | Variant ..."""

    name: str = ""
    declared_type: CoreType | None = None  # UnionType


@dataclass
class IRClassDecl(IRNode):
    """Class declaration (OOP form, from legacy or class keyword)."""

    name: str = ""
    bases: list[IRNode] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    decorators: list[IRNode] = field(default_factory=list)


@dataclass
class IRAgentDecl(IRNode):
    """Agent declaration: @agent(model: @name) fn name(params) -> T uses ai."""

    name: str = ""
    model: IRNode | None = None  # IRModelRef
    parameters: list[IRParameter] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    return_type: CoreType | None = None
    effects: EffectSet = field(default_factory=EffectSet)
    is_async: bool = False


@dataclass
class IRToolDecl(IRNode):
    """Tool declaration: @tool(description: "...") fn name(params) -> T."""

    name: str = ""
    description: str = ""
    parameters: list[IRParameter] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    return_type: CoreType | None = None
    effects: EffectSet = field(default_factory=EffectSet)


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------

@dataclass
class IRLiteral(IRNode):
    """Scalar literal value.

    kind: "int" | "float" | "decimal" | "string" | "bytes" | "bool" |
          "none" | "date"
    """

    value: object = None
    kind: str = "unknown"
    inferred_type: CoreType | None = None


@dataclass
class IRFStringLiteral(IRNode):
    """F-string with interpolated expressions: f"text {expr} text"."""

    parts: list[str | IRNode] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRListLiteral(IRNode):
    """List literal: [a, b, c]."""

    elements: list[IRNode] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRDictLiteral(IRNode):
    """Dict literal: {k: v, **d}.

    entries: list of (key_node, value_node) pairs or unpack IRNode.
    """

    entries: list = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRSetLiteral(IRNode):
    """Set literal: {a, b, c}."""

    elements: list[IRNode] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRTupleLiteral(IRNode):
    """Tuple literal or unpacking target: a, b, c."""

    elements: list[IRNode] = field(default_factory=list)
    inferred_type: CoreType | None = None


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

@dataclass
class IRIdentifier(IRNode):
    """Named reference to a binding, function, or type."""

    name: str = ""
    inferred_type: CoreType | None = None


@dataclass
class IRBinaryOp(IRNode):
    """Binary operation: left op right.

    op: "+", "-", "*", "/", "//", "%", "**", "|", "&", "^", "<<", ">>"
    """

    left: IRNode | None = None
    op: str = ""
    right: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRUnaryOp(IRNode):
    """Unary operation: op operand.

    op: "-", "+", "~", "not"
    """

    op: str = ""
    operand: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRBooleanOp(IRNode):
    """Short-circuit logical operation: a and b and c / a or b or c."""

    op: str = ""   # "and" | "or"
    values: list[IRNode] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRCompareOp(IRNode):
    """Chained comparison: a < b <= c.

    comparators: list of (op_str, right_node) pairs.
    """

    left: IRNode | None = None
    comparators: list = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRCallExpr(IRNode):
    """Function or method call: func(args, key=val)."""

    func: IRNode | None = None
    args: list[IRNode] = field(default_factory=list)
    keywords: list[tuple[str, IRNode]] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRAttributeAccess(IRNode):
    """Attribute access: obj.attr."""

    obj: IRNode | None = None
    attr: str = ""
    inferred_type: CoreType | None = None


@dataclass
class IRIndexAccess(IRNode):
    """Index or subscript: obj[index]."""

    obj: IRNode | None = None
    index: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRSliceExpr(IRNode):
    """Slice: start:stop:step (any part may be None)."""

    start: IRNode | None = None
    stop: IRNode | None = None
    step: IRNode | None = None


@dataclass
class IRStarredExpr(IRNode):
    """Starred expression in calls or assignments: *expr or **expr."""

    value: IRNode | None = None
    is_double: bool = False   # True for **expr


@dataclass
class IRLambdaExpr(IRNode):
    """Anonymous function: fn(params): body."""

    parameters: list[IRParameter] = field(default_factory=list)
    body: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRPipeExpr(IRNode):
    """Pipe composition: left |> right.

    Semantics: right(left) — threads the left value as the first argument of
    the right-hand expression.
    """

    left: IRNode | None = None
    right: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRResultPropagation(IRNode):
    """Result propagation operator: expr?.

    Propagates the Err branch of a result<T, E> to the enclosing function's
    return value.  Only valid inside a function returning result<T, E>.
    """

    operand: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRAwaitExpr(IRNode):
    """Await expression: await expr."""

    value: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRYieldExpr(IRNode):
    """Yield expression: yield [from] value."""

    value: IRNode | None = None
    is_from: bool = False
    inferred_type: CoreType | None = None


@dataclass
class IRNamedExpr(IRNode):
    """Walrus operator: target := value."""

    target: str = ""
    value: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRConditionalExpr(IRNode):
    """Ternary conditional: true_expr if condition else false_expr."""

    condition: IRNode | None = None
    true_expr: IRNode | None = None
    false_expr: IRNode | None = None
    inferred_type: CoreType | None = None


# ---------------------------------------------------------------------------
# Comprehensions
# ---------------------------------------------------------------------------

@dataclass
class IRComprehensionClause(IRNode):
    """Single for-clause in a comprehension: for target in iterable [if ...]."""

    target: IRNode | None = None
    iterable: IRNode | None = None
    conditions: list[IRNode] = field(default_factory=list)
    is_async: bool = False


@dataclass
class IRListComp(IRNode):
    """List comprehension: [expr for ...]."""

    element: IRNode | None = None
    clauses: list[IRComprehensionClause] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRDictComp(IRNode):
    """Dict comprehension: {k: v for ...}."""

    key: IRNode | None = None
    value: IRNode | None = None
    clauses: list[IRComprehensionClause] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRSetComp(IRNode):
    """Set comprehension: {expr for ...}."""

    element: IRNode | None = None
    clauses: list[IRComprehensionClause] = field(default_factory=list)
    inferred_type: CoreType | None = None


@dataclass
class IRGeneratorExpr(IRNode):
    """Generator expression: (expr for ...)."""

    element: IRNode | None = None
    clauses: list[IRComprehensionClause] = field(default_factory=list)
    inferred_type: CoreType | None = None


# ---------------------------------------------------------------------------
# AI-native expressions
#
# These nodes have no equivalent in the existing AST.  They will be produced
# by the lowering pass once the parser gains the corresponding keywords.
# Until then they can be produced from detected call patterns in the lowering
# pass as a transitional mechanism.
# ---------------------------------------------------------------------------

@dataclass
class IRModelRef(IRNode):
    """Model reference literal: @claude-sonnet, @gpt-4o, etc."""

    model_name: str = ""
    inferred_type: CoreType | None = None  # always ModelType


@dataclass
class IRPromptExpr(IRNode):
    """Prompt expression: prompt @model: template -> string."""

    model: IRNode | None = None   # IRModelRef
    template: IRNode | None = None
    inferred_type: CoreType | None = None  # always StringType


@dataclass
class IRGenerateExpr(IRNode):
    """Structured generation: generate @model: template -> T.

    The declared return type constrains the model output to a schema.
    """

    model: IRNode | None = None
    template: IRNode | None = None
    target_type: CoreType | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRThinkExpr(IRNode):
    """Chain-of-thought reasoning: think @model: template.

    Returns a structured result with .conclusion (string) and .trace (string).
    """

    model: IRNode | None = None
    template: IRNode | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRStreamExpr(IRNode):
    """Streaming generation: stream @model: template -> stream<string>."""

    model: IRNode | None = None
    template: IRNode | None = None
    inferred_type: CoreType | None = None  # always StreamType(StringType)


@dataclass
class IREmbedExpr(IRNode):
    """Embedding expression: embed @model: value -> vector<float>."""

    model: IRNode | None = None
    value: IRNode | None = None
    inferred_type: CoreType | None = None  # always VectorType(FloatType)


@dataclass
class IRExtractExpr(IRNode):
    """Typed extraction: extract @model: source -> T."""

    model: IRNode | None = None
    source: IRNode | None = None
    target_type: CoreType | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRClassifyExpr(IRNode):
    """Classification: classify @model: subject into categories -> T."""

    model: IRNode | None = None
    subject: IRNode | None = None
    categories: list[IRNode] = field(default_factory=list)
    target_type: CoreType | None = None
    inferred_type: CoreType | None = None


@dataclass
class IRSemanticMatchOp(IRNode):
    """Semantic approximate match: left ~= right.

    Compares using embedding similarity rather than exact equality.
    threshold controls the minimum cosine similarity (default 0.80).
    model overrides the embedding model for this expression only.
    """

    left: IRNode | None = None
    right: IRNode | None = None
    threshold: float = 0.80
    model: IRNode | None = None  # optional IRModelRef override
    inferred_type: CoreType | None = None  # always BoolType


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass
class IRAssignment(IRNode):
    """Simple or augmented assignment: target op= value."""

    target: IRNode | None = None
    value: IRNode | None = None
    op: str = "="   # "=" | "+=" | "-=" | "*=" | "/=" | etc.


@dataclass
class IRExprStatement(IRNode):
    """A bare expression used as a statement."""

    expression: IRNode | None = None


@dataclass
class IRReturnStatement(IRNode):
    """Return from a function."""

    value: IRNode | None = None


@dataclass
class IRBreakStatement(IRNode):
    """Break out of a loop."""


@dataclass
class IRContinueStatement(IRNode):
    """Continue to the next loop iteration."""


@dataclass
class IRPassStatement(IRNode):
    """No-op placeholder statement."""


@dataclass
class IRRaiseStatement(IRNode):
    """Raise an exception: raise expr [from cause]."""

    value: IRNode | None = None
    cause: IRNode | None = None


@dataclass
class IRDelStatement(IRNode):
    """Delete a binding or subscript: del target."""

    target: IRNode | None = None


@dataclass
class IRAssertStatement(IRNode):
    """Assert a condition: assert test [, msg]."""

    test: IRNode | None = None
    msg: IRNode | None = None


@dataclass
class IRGlobalStatement(IRNode):
    """Declare names as module-global."""

    names: list[str] = field(default_factory=list)


@dataclass
class IRNonlocalStatement(IRNode):
    """Declare names as nonlocal (from enclosing scope)."""

    names: list[str] = field(default_factory=list)


@dataclass
class IRYieldStatement(IRNode):
    """Yield as a statement: yield [from] value."""

    value: IRNode | None = None
    is_from: bool = False


@dataclass
class IRImportStatement(IRNode):
    """Simple import: import module [as alias]."""

    module: str = ""
    alias: str | None = None


@dataclass
class IRFromImportStatement(IRNode):
    """From-import: from module import name [as alias], ...

    names: list of (original_name, alias_or_None) pairs.
    level: number of leading dots for relative imports.
    """

    module: str = ""
    names: list[tuple[str, str | None]] = field(default_factory=list)
    level: int = 0


@dataclass
class IRWithStatement(IRNode):
    """Context manager: with expr [as name], ...: body."""

    items: list[tuple[IRNode, str | None]] = field(default_factory=list)
    body: list[IRNode] = field(default_factory=list)
    is_async: bool = False


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------

@dataclass
class IRElifClause(IRNode):
    """Single elif branch."""

    condition: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)


@dataclass
class IRIfStatement(IRNode):
    """Conditional: if condition: body [elif ...] [else ...]."""

    condition: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)
    elif_clauses: list[IRElifClause] = field(default_factory=list)
    else_body: list[IRNode] = field(default_factory=list)


@dataclass
class IRWhileLoop(IRNode):
    """While loop with optional else branch."""

    condition: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)
    else_body: list[IRNode] = field(default_factory=list)
    is_async: bool = False


@dataclass
class IRForLoop(IRNode):
    """For loop with optional else branch."""

    target: IRNode | None = None
    iterable: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)
    else_body: list[IRNode] = field(default_factory=list)
    is_async: bool = False


@dataclass
class IRExceptHandler(IRNode):
    """Single except clause: except Type [as name]: body."""

    exc_type: IRNode | None = None
    name: str | None = None
    body: list[IRNode] = field(default_factory=list)


@dataclass
class IRTryStatement(IRNode):
    """Try/except/else/finally block."""

    body: list[IRNode] = field(default_factory=list)
    handlers: list[IRExceptHandler] = field(default_factory=list)
    else_body: list[IRNode] = field(default_factory=list)
    finally_body: list[IRNode] = field(default_factory=list)


@dataclass
class IRMatchCase(IRNode):
    """Single case branch in a match statement."""

    pattern: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)
    is_default: bool = False


@dataclass
class IRMatchStatement(IRNode):
    """Match statement.

    is_semantic: True when the subject is compared with ~= (semantic match).
    """

    subject: IRNode | None = None
    cases: list[IRMatchCase] = field(default_factory=list)
    is_semantic: bool = False


# ---------------------------------------------------------------------------
# Patterns  (used inside IRMatchCase.pattern)
# ---------------------------------------------------------------------------

@dataclass
class IRLiteralPattern(IRNode):
    """Match a literal value."""

    value: IRNode | None = None   # IRLiteral


@dataclass
class IRCapturePattern(IRNode):
    """Capture a matched value into a name."""

    name: str = ""


@dataclass
class IRWildcardPattern(IRNode):
    """Wildcard: _ — matches anything and discards it."""


@dataclass
class IROrPattern(IRNode):
    """Alternative patterns: p1 | p2 | p3."""

    alternatives: list[IRNode] = field(default_factory=list)


@dataclass
class IRRecordPattern(IRNode):
    """Record/class destructuring pattern: TypeName { field: pattern }."""

    type_name: str = ""
    fields: dict[str, IRNode] = field(default_factory=dict)


@dataclass
class IRGuardedPattern(IRNode):
    """Pattern with guard expression: pattern if guard."""

    pattern: IRNode | None = None
    guard: IRNode | None = None


@dataclass
class IRAsPattern(IRNode):
    """Binding pattern: pattern as name."""

    pattern: IRNode | None = None
    name: str = ""


@dataclass
class IRSemanticPattern(IRNode):
    """Semantic match pattern for use with ~= match.

    Matches when the subject is approximately equal to the template string
    according to embedding similarity.
    """

    template: IRNode | None = None  # usually IRLiteral(kind="string")
    threshold: float = 0.80


# ---------------------------------------------------------------------------
# Reactive
# ---------------------------------------------------------------------------

@dataclass
class IROnChange(IRNode):
    """Event handler: on signal.change: body.

    signal: the reactive binding being observed (usually IRIdentifier).
    """

    signal: IRNode | None = None
    body: list[IRNode] = field(default_factory=list)


@dataclass
class IRCanvasBlock(IRNode):
    """Declarative view composition block: canvas { ... }."""

    children: list[IRNode] = field(default_factory=list)
    name: str = ""  # optional named canvas

@dataclass
class IRRenderExpr(IRNode):
    """Render expression: render target with value."""

    target: IRNode | None = None   # the view target (identifier or canvas)
    value: IRNode | None = None    # the value to render

@dataclass
class IRViewBinding(IRNode):
    """Bind a stream or signal to a view: bind signal -> view."""

    signal: IRNode | None = None   # the source signal/stream
    target: IRNode | None = None   # the view target


# ---------------------------------------------------------------------------
# Backward-compatible placeholder (kept for gradual migration)
# ---------------------------------------------------------------------------

@dataclass
class IRExpression(IRNode):
    """Unresolved expression placeholder.

    Used when the lowering pass encounters an AST node it does not yet have
    a specific IR representation for.  These nodes should be replaced as the
    lowering pass becomes more complete.
    """

    inferred_type: CoreType | None = None
