#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Python code generator: transpiles AST or semantic IR to valid Python."""

from multilingualprogramming.core import ir_nodes as ir
from multilingualprogramming.core.ir_nodes import IRProgram
from multilingualprogramming.core.types import GenericType
from multilingualprogramming.exceptions import CodeGenerationError
from multilingualprogramming.numeral.mp_numeral import MPNumeral


def _emit_raw_literal(prefix: str, value: str) -> str:
    """Emit a raw string or raw bytes literal with the given prefix (r or rb).

    Chooses the quote style (single, double, triple) to avoid unescapable
    quote conflicts, since backslash escapes are not allowed in raw literals.
    """
    if '"' not in value:
        return f'{prefix}"{value}"'
    if "'" not in value:
        return f"{prefix}'{value}'"
    # Both quote chars present — use triple double-quotes if possible
    if '"""' not in value:
        return f'{prefix}"""{value}"""'
    return f"{prefix}'''{value}'''"


def _convert_numeral_literal(raw_value):
    """Convert a multilingual numeral into a Python numeric literal."""
    try:
        num = MPNumeral(raw_value)
        decimal = num.to_decimal()
        if isinstance(decimal, float):
            return repr(decimal)
        return str(decimal)
    except Exception:
        try:
            if isinstance(raw_value, str) and raw_value.lower().startswith(
                ("0x", "0o", "0b")
            ):
                return str(int(raw_value, 0))
            return str(int(raw_value))
        except ValueError:
            try:
                return repr(float(raw_value))
            except ValueError:
                return raw_value


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
        if isinstance(node, IRProgram):
            return self._generate_ir_program(node)
        self._depth = 0
        self._lines = []
        node.accept(self)
        return "\n".join(self._lines) + "\n"

    def _generate_ir_program(self, program):
        """Generate Python directly from semantic IR."""
        self._depth = 0
        self._lines = []
        for stmt in program.body:
            self._emit_ir_stmt(stmt)
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

    def _emit_ir_body(self, body):
        """Emit a list of IR statements as an indented block."""
        self._indent()
        if not body:
            self._emit("pass")
        else:
            for stmt in body:
                self._emit_ir_stmt(stmt)
        self._dedent()

    def _expr(self, node):
        """Generate the expression string for a node.

        Uses a sub-generator so expression visitors can return strings
        rather than emitting lines.
        """
        sub = _ExpressionGenerator()
        return node.accept(sub)

    def _expr_ir(self, node):
        """Generate the expression string for an IR expression node."""
        return _IRExpressionGenerator().render(node)

    def _error(self, message, node):
        """Raise a CodeGenerationError with source location."""
        raise CodeGenerationError(message, node.line, node.column)

    def _emit_ir_stmt(self, node):
        """Dispatch semantic IR statement generation."""
        method = getattr(self, f"_emit_{type(node).__name__}", None)
        if method is None:
            self._error(
                f"Unsupported IR node type: {type(node).__name__}",
                node,
            )
        else:
            method(node)

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

    def visit_AnnAssignment(self, node):
        target = self._expr(node.target)
        annotation = self._expr(node.annotation)
        if node.value is None:
            self._emit(f"{target}: {annotation}")
        else:
            val = self._expr(node.value)
            self._emit(f"{target}: {annotation} = {val}")

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
            if getattr(node, "cause", None):
                cause = self._expr(node.cause)
                self._emit(f"raise {val} from {cause}")
            else:
                self._emit(f"raise {val}")
        else:
            self._emit("raise")

    def visit_DelStatement(self, node):
        target = self._expr(node.target)
        self._emit(f"del {target}")

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
        keyword = "yield from" if getattr(node, "is_from", False) else "yield"
        if node.value:
            val = self._expr(node.value)
            self._emit(f"{keyword} {val}")
        else:
            self._emit(keyword)

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
        if node.else_body:
            self._emit("else:")
            self._emit_body(node.else_body)

    def visit_ForLoop(self, node):
        target = self._expr(node.target)
        iterable = self._expr(node.iterable)
        prefix = "async " if getattr(node, "is_async", False) else ""
        self._emit(f"{prefix}for {target} in {iterable}:")
        self._emit_body(node.body)
        if getattr(node, "else_body", None):
            self._emit("else:")
            self._emit_body(node.else_body)

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
        prefix = "async " if getattr(node, "is_async", False) else ""
        ret_ann = ""
        if getattr(node, "return_annotation", None) is not None:
            ret_ann = f" -> {self._expr(node.return_annotation)}"
        self._emit(f"{prefix}def {node.name}({params}){ret_ann}:")
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
        if node.else_body:
            self._emit("else:")
            self._emit_body(node.else_body)
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
        if self._needs_match_if_chain(node):
            self._emit_match_if_chain(node)
            return
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
            guard = ""
            if getattr(node, "guard", None):
                guard = f" if {self._expr(node.guard)}"
            self._emit(f"case {pattern}{guard}:")
        self._emit_body(node.body)

    def visit_WithStatement(self, node):
        parts = []
        for ctx_expr, name in node.items:
            ctx = self._expr(ctx_expr)
            if name:
                parts.append(f"{ctx} as {name}")
            else:
                parts.append(ctx)
        prefix = "async " if getattr(node, "is_async", False) else ""
        self._emit(f"{prefix}with {', '.join(parts)}:")
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
        # Relative imports: level dots prepended to module name
        # e.g. level=1, module=""     → "from . import X"
        #      level=1, module="sous" → "from .sous import X"
        #      level=2, module="util" → "from ..util import X"
        dots = "." * getattr(node, "level", 0)
        self._emit(f"from {dots}{node.module} import {names}")

    def visit_ObserveDeclaration(self, node):
        val = self._expr(node.value)
        self._emit(f"{node.name} = {val}")

    def visit_OnChangeStatement(self, _node):
        self._emit("pass  # reactive on-change handler lowered separately")

    def visit_CanvasBlock(self, _node):
        self._emit("pass  # canvas block lowered separately")

    def visit_RenderStatement(self, _node):
        self._emit("pass  # render statement lowered separately")

    def visit_ViewBindingStatement(self, _node):
        self._emit("pass  # view binding lowered separately")

    def visit_RecordDecl(self, node):
        self._emit(f"class {node.name}(dict):")
        self._emit_body([])

    def visit_EnumDecl(self, node):
        self._emit(f"class {node.name}:")
        self._emit_body([])
        for variant in node.variants:
            self._emit(f"{node.name}.{variant.name} = {variant.name!r}")

    def generic_visit(self, node):
        """Raise when statement node code generation is not implemented."""
        self._error(
            f"Unsupported AST node type: {type(node).__name__}", node
        )

    # ------------------------------------------------------------------
    # IR statement emitters
    # ------------------------------------------------------------------

    def _emit_IRBinding(self, node):
        target = node.name
        annotation = _format_ir_type(node.annotation)
        value = self._expr_ir(node.value)
        if annotation is not None:
            self._emit(f"{target}: {annotation} = {value}")
        else:
            self._emit(f"{target} = {value}")

    def _emit_IRObserveBinding(self, node):
        self._emit_IRBinding(node)

    def _emit_IRAssignment(self, node):
        chain_targets = getattr(node, "chain_targets", None)
        if chain_targets:
            targets = " = ".join(self._expr_ir(target) for target in chain_targets)
            self._emit(f"{targets} = {self._expr_ir(node.value)}")
            return
        self._emit(
            f"{self._expr_ir(node.target)} {node.op} {self._expr_ir(node.value)}"
        )

    def _emit_IRExprStatement(self, node):
        self._emit(self._expr_ir(node.expression))

    def _emit_IRReturnStatement(self, node):
        if node.value is None:
            self._emit("return")
            return
        self._emit(f"return {self._expr_ir(node.value)}")

    def _emit_IRBreakStatement(self, _node):
        self._emit("break")

    def _emit_IRContinueStatement(self, _node):
        self._emit("continue")

    def _emit_IRPassStatement(self, _node):
        self._emit("pass")

    def _emit_IRRaiseStatement(self, node):
        if node.value is None:
            self._emit("raise")
            return
        value = self._expr_ir(node.value)
        if node.cause is not None:
            self._emit(f"raise {value} from {self._expr_ir(node.cause)}")
            return
        self._emit(f"raise {value}")

    def _emit_IRDelStatement(self, node):
        self._emit(f"del {self._expr_ir(node.target)}")

    def _emit_IRAssertStatement(self, node):
        test = self._expr_ir(node.test)
        if node.msg is None:
            self._emit(f"assert {test}")
            return
        self._emit(f"assert {test}, {self._expr_ir(node.msg)}")

    def _emit_IRGlobalStatement(self, node):
        self._emit(f"global {', '.join(node.names)}")

    def _emit_IRNonlocalStatement(self, node):
        self._emit(f"nonlocal {', '.join(node.names)}")

    def _emit_IRYieldStatement(self, node):
        keyword = "yield from" if node.is_from else "yield"
        if node.value is None:
            self._emit(keyword)
            return
        self._emit(f"{keyword} {self._expr_ir(node.value)}")

    def _emit_IRImportStatement(self, node):
        if node.alias:
            self._emit(f"import {node.module} as {node.alias}")
        else:
            self._emit(f"import {node.module}")

    def _emit_IRFromImportStatement(self, node):
        names = []
        for name, alias in node.names:
            names.append(f"{name} as {alias}" if alias else name)
        self._emit(
            f"from {'.' * node.level}{node.module} import {', '.join(names)}"
        )

    def _emit_IRIfStatement(self, node):
        self._emit(f"if {self._expr_ir(node.condition)}:")
        self._emit_ir_body(node.body)
        for clause in node.elif_clauses:
            self._emit(f"elif {self._expr_ir(clause.condition)}:")
            self._emit_ir_body(clause.body)
        if node.else_body:
            self._emit("else:")
            self._emit_ir_body(node.else_body)

    def _emit_IRWhileLoop(self, node):
        prefix = "async " if getattr(node, "is_async", False) else ""
        self._emit(f"{prefix}while {self._expr_ir(node.condition)}:")
        self._emit_ir_body(node.body)
        if node.else_body:
            self._emit("else:")
            self._emit_ir_body(node.else_body)

    def _emit_IRForLoop(self, node):
        prefix = "async " if node.is_async else ""
        self._emit(
            f"{prefix}for {self._expr_ir(node.target)} in "
            f"{self._expr_ir(node.iterable)}:"
        )
        self._emit_ir_body(node.body)
        if node.else_body:
            self._emit("else:")
            self._emit_ir_body(node.else_body)

    def _emit_IRFunction(self, node):
        for dec in node.decorators:
            self._emit(f"@{self._expr_ir(dec)}")
        params = ", ".join(_IRExpressionGenerator().render_parameter(p) for p in node.parameters)
        prefix = "async " if node.is_async else ""
        ret_ann = ""
        if node.return_type is not None:
            ret_ann = f" -> {_format_ir_type(node.return_type)}"
        self._emit(f"{prefix}def {node.name}({params}){ret_ann}:")
        self._emit_ir_body(node.body)

    def _emit_IRAgentDecl(self, node):
        self._emit(f"@agent(model={self._expr_ir(node.model)})")
        fn_node = ir.IRFunction(
            name=node.name,
            parameters=node.parameters,
            body=node.body,
            return_type=node.return_type,
            effects=node.effects,
            is_async=node.is_async,
            line=node.line,
            column=node.column,
        )
        self._emit_IRFunction(fn_node)

    def _emit_IRToolDecl(self, node):
        self._emit(f"@tool(description={node.description!r})")
        fn_node = ir.IRFunction(
            name=node.name,
            parameters=node.parameters,
            body=node.body,
            return_type=node.return_type,
            effects=node.effects,
            line=node.line,
            column=node.column,
        )
        self._emit_IRFunction(fn_node)

    def _emit_IRClassDecl(self, node):
        for dec in node.decorators:
            self._emit(f"@{self._expr_ir(dec)}")
        if node.bases:
            bases = ", ".join(self._expr_ir(base) for base in node.bases)
            self._emit(f"class {node.name}({bases}):")
        else:
            self._emit(f"class {node.name}:")
        self._emit_ir_body(node.body)

    def _emit_IRTryStatement(self, node):
        self._emit("try:")
        self._emit_ir_body(node.body)
        for handler in node.handlers:
            self._emit_IRExceptHandler(handler)
        if node.else_body:
            self._emit("else:")
            self._emit_ir_body(node.else_body)
        if node.finally_body:
            self._emit("finally:")
            self._emit_ir_body(node.finally_body)

    def _emit_IRExceptHandler(self, node):
        if node.exc_type is None:
            self._emit("except:")
        elif node.name:
            self._emit(f"except {self._expr_ir(node.exc_type)} as {node.name}:")
        else:
            self._emit(f"except {self._expr_ir(node.exc_type)}:")
        self._emit_ir_body(node.body)

    def _emit_IRMatchStatement(self, node):
        match_var = f"__ml_match_subject_{id(node)}"
        matched_var = f"__ml_match_done_{id(node)}"
        self._emit(f"{match_var} = {self._expr_ir(node.subject)}")
        self._emit(f"{matched_var} = False")
        for case in node.cases:
            cond, prelude = self._ir_match_case_condition(case, match_var, node.is_semantic)
            self._emit(f"if not {matched_var}:")
            self._indent()
            for line in prelude:
                self._emit(line)
            self._emit(f"if {cond}:")
            self._indent()
            self._emit(f"{matched_var} = True")
            if case.body:
                for stmt in case.body:
                    self._emit_ir_stmt(stmt)
            else:
                self._emit("pass")
            self._dedent()
            self._dedent()
        if not node.cases:
            self._emit("pass")

    def _emit_IRWithStatement(self, node):
        prefix = "async " if node.is_async else ""
        parts = []
        for expr, name in node.items:
            rendered = self._expr_ir(expr)
            parts.append(f"{rendered} as {name}" if name else rendered)
        self._emit(f"{prefix}with {', '.join(parts)}:")
        self._emit_ir_body(node.body)

    def _emit_IREnumDecl(self, node):
        self._emit(f"class {node.name}:")
        self._emit_ir_body([])

    def _emit_IRTypeDecl(self, node):
        self._emit(f"{node.name} = {_format_ir_type(node.declared_type)}")

    def _emit_IROnChange(self, _node):
        self._emit("pass  # reactive on-change handler lowered separately")

    def _emit_IRCanvasBlock(self, _node):
        self._emit("pass  # canvas block lowered separately")

    def _emit_IRRenderExpr(self, _node):
        self._emit("pass  # render statement lowered separately")

    def _emit_IRViewBinding(self, _node):
        self._emit("pass  # view binding lowered separately")

    def _ir_match_case_condition(self, case, match_var, is_semantic):
        """Return (condition, prelude_lines) for a semantic IR match case."""
        pattern = case.pattern
        if case.is_default or isinstance(pattern, ir.IRWildcardPattern):
            return "True", []
        if isinstance(pattern, ir.IRGuardedPattern):
            cond, prelude = self._ir_match_pattern_condition(
                pattern.pattern,
                match_var,
                is_semantic,
            )
            return f"({cond}) and ({self._expr_ir(pattern.guard)})", prelude
        if isinstance(pattern, ir.IRCapturePattern):
            return "True", [f"{pattern.name} = {match_var}"]
        if isinstance(pattern, ir.IRAsPattern):
            cond, prelude = self._ir_match_pattern_condition(
                pattern.pattern,
                match_var,
                is_semantic,
            )
            return cond, prelude + [f"{pattern.name} = {match_var}"]
        return self._ir_match_pattern_condition(pattern, match_var, is_semantic)

    def _ir_match_pattern_condition(self, pattern, match_var, is_semantic):
        """Return (condition, prelude_lines) for an IR pattern."""
        if pattern is None or isinstance(pattern, ir.IRWildcardPattern):
            return "True", []
        if isinstance(pattern, ir.IRGuardedPattern):
            cond, prelude = self._ir_match_pattern_condition(
                pattern.pattern,
                match_var,
                is_semantic,
            )
            return f"({cond}) and ({self._expr_ir(pattern.guard)})", prelude
        if isinstance(pattern, ir.IRLiteralPattern):
            return f"{match_var} == {self._expr_ir(pattern.value)}", []
        if isinstance(pattern, ir.IRCapturePattern):
            return "True", [f"{pattern.name} = {match_var}"]
        if isinstance(pattern, ir.IRAsPattern):
            cond, prelude = self._ir_match_pattern_condition(
                pattern.pattern,
                match_var,
                is_semantic,
            )
            return cond, prelude + [f"{pattern.name} = {match_var}"]
        if isinstance(pattern, ir.IROrPattern):
            conditions = []
            prelude = []
            for alt in pattern.alternatives:
                cond, extra = self._ir_match_pattern_condition(alt, match_var, is_semantic)
                conditions.append(f"({cond})")
                prelude.extend(extra)
            return " or ".join(conditions), prelude
        if isinstance(pattern, ir.IRSequencePattern):
            values = ", ".join(self._ir_pattern_expr(elem) for elem in pattern.elements)
            return f"{match_var} == ({values})", []
        if isinstance(pattern, ir.IRRecordPattern):
            entries = ", ".join(
                f"{name!r}: {self._ir_pattern_expr(value)}"
                for name, value in pattern.fields.items()
            )
            return f"{match_var} == {{{entries}}}", []
        if isinstance(pattern, ir.IRSemanticPattern) or is_semantic:
            template = pattern.template if isinstance(pattern, ir.IRSemanticPattern) else pattern
            threshold = getattr(pattern, "threshold", 0.80)
            return (
                "semantic_match("
                f"{match_var}, {self._expr_ir(template)}, threshold={threshold!r})",
                [],
            )
        return f"{match_var} == {self._expr_ir(pattern)}", []

    def _ir_pattern_expr(self, pattern):
        """Render a pattern as a comparable Python expression."""
        if isinstance(pattern, ir.IRLiteralPattern):
            return self._expr_ir(pattern.value)
        if isinstance(pattern, ir.IRSequencePattern):
            values = ", ".join(self._ir_pattern_expr(elem) for elem in pattern.elements)
            if len(pattern.elements) == 1:
                values += ","
            return f"({values})"
        if isinstance(pattern, ir.IRRecordPattern):
            entries = ", ".join(
                f"{name!r}: {self._ir_pattern_expr(value)}"
                for name, value in pattern.fields.items()
            )
            return f"{{{entries}}}"
        if isinstance(pattern, ir.IRAsPattern):
            return self._ir_pattern_expr(pattern.pattern)
        if isinstance(pattern, ir.IRGuardedPattern):
            return self._ir_pattern_expr(pattern.pattern)
        return self._expr_ir(pattern)

    def _needs_match_if_chain(self, node):
        """Return True when a match statement needs if/elif fallback codegen."""
        for case in node.cases:
            pattern = getattr(case, "pattern", None)
            if self._match_capture_name(pattern) is not None:
                return True
            if self._match_has_as_binding(pattern):
                return True
        return False

    def _emit_match_if_chain(self, node):
        """Emit match/case as an if/elif chain for capture-heavy patterns."""
        subject = self._expr(node.subject)
        match_var = f"__ml_match_subject_{id(node)}"
        self._emit(f"{match_var} = {subject}")
        first = True
        for case in node.cases:
            keyword = "if" if first else "elif"
            cond, prelude = self._match_case_condition(case, match_var)
            self._emit(f"{keyword} {cond}:")
            self._indent()
            for line in prelude:
                self._emit(line)
            if case.body:
                for stmt in case.body:
                    stmt.accept(self)
            else:
                self._emit("pass")
            self._dedent()
            first = False
        if not node.cases:
            self._emit("pass")

    def _match_case_condition(self, case, match_var):
        """Return (condition, prelude_lines) for a fallback match case."""
        pattern = getattr(case, "pattern", None)
        guard = getattr(case, "guard", None)
        prelude = []
        capture_name = self._match_capture_name(pattern)
        if case.is_default or self._is_wildcard_pattern(pattern):
            cond = "True"
        elif capture_name is not None:
            prelude.append(f"{capture_name} = {match_var}")
            cond = self._expr(guard) if guard is not None else "True"
        elif self._match_has_as_binding(pattern):
            bound_name = pattern.right.name
            base_cond, base_prelude = self._match_pattern_condition(
                pattern.left,
                match_var,
            )
            prelude.extend(base_prelude)
            prelude.append(f"{bound_name} = {match_var}")
            cond = base_cond
            if guard is not None:
                cond = f"({cond}) and ({self._expr(guard)})"
        else:
            cond, extra = self._match_pattern_condition(pattern, match_var)
            prelude.extend(extra)
            if guard is not None:
                cond = f"({cond}) and ({self._expr(guard)})"
        return cond, prelude

    def _match_pattern_condition(self, pattern, match_var):
        """Return (condition, prelude_lines) for a non-capture pattern."""
        if pattern is None or self._is_wildcard_pattern(pattern):
            return "True", []
        if self._match_capture_name(pattern) is not None:
            name = self._match_capture_name(pattern)
            return "True", [f"{name} = {match_var}"]
        if type(pattern).__name__ in {
            "NumeralLiteral",
            "StringLiteral",
            "BooleanLiteral",
            "NoneLiteral",
        }:
            return f"{match_var} == {self._expr(pattern)}", []
        if type(pattern).__name__ == "BinaryOp" and pattern.op == "|":
            left, left_prelude = self._match_pattern_condition(pattern.left, match_var)
            right, right_prelude = self._match_pattern_condition(
                pattern.right,
                match_var,
            )
            return f"({left}) or ({right})", left_prelude + right_prelude
        if type(pattern).__name__ == "TupleLiteral":
            elems = [self._expr(elem) for elem in pattern.elements]
            return f"{match_var} == ({', '.join(elems)})", []
        if type(pattern).__name__ == "ListLiteral":
            elems = [self._expr(elem) for elem in pattern.elements]
            return f"{match_var} == [{', '.join(elems)}]", []
        if type(pattern).__name__ == "DictLiteral":
            return f"{match_var} == {self._expr(pattern)}", []
        return f"{match_var} == {self._expr(pattern)}", []

    @staticmethod
    def _is_wildcard_pattern(pattern):
        return (
            pattern is not None
            and type(pattern).__name__ == "Identifier"
            and getattr(pattern, "name", None) == "_"
        )

    @staticmethod
    def _match_capture_name(pattern):
        if pattern is not None and type(pattern).__name__ == "Identifier":
            name = getattr(pattern, "name", "")
            if name != "_":
                return name
        return None

    @staticmethod
    def _match_has_as_binding(pattern):
        return (
            pattern is not None
            and type(pattern).__name__ == "BinaryOp"
            and getattr(pattern, "op", None) == " as "
            and type(getattr(pattern, "right", None)).__name__ == "Identifier"
        )


def _format_ir_type(type_value):
    """Format a CoreType as a Python annotation string."""
    if type_value is None:
        return None
    if isinstance(type_value, GenericType):
        params = ", ".join(
            _format_ir_type(param) or "object" for param in type_value.parameters
        )
        return f"{_python_type_name(type_value.name)}[{params}]"
    return _python_type_name(type_value.name)


def _python_type_name(type_name):
    """Map core type names to Python annotation identifiers."""
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


# ======================================================================
# Expression sub-generator (returns strings instead of emitting lines)
# ======================================================================

class _ExpressionGenerator:
    """Visitor that returns Python expression strings."""

    def _expr(self, node):
        """Recursively generate an expression string."""
        return node.accept(self)

    def _comprehension_clauses(self, node):
        """Return comprehension clauses with backward compatibility."""
        clauses = getattr(node, "clauses", None)
        if clauses:
            return clauses
        return [node]

    def _convert_numeral(self, raw_value):
        """Convert a multilingual numeral string to a Python numeric literal."""
        return _convert_numeral_literal(raw_value)

    # -- Literals --

    def visit_NumeralLiteral(self, node):
        return self._convert_numeral(node.value)

    def visit_StringLiteral(self, node):
        if getattr(node, "raw", False):
            return _emit_raw_literal("r", node.value)
        return repr(node.value)

    def visit_BytesLiteral(self, node):
        if getattr(node, "raw", False):
            return _emit_raw_literal("rb", node.value)
        return f"b{repr(node.value)}"

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
        parts = []
        for entry in node.entries:
            if isinstance(entry, tuple):
                key, value = entry
                parts.append(f"{self._expr(key)}: {self._expr(value)}")
            else:
                parts.append(self._expr(entry))
        return "{" + ", ".join(parts) + "}"

    def visit_SetLiteral(self, node):
        elems = ", ".join(self._expr(e) for e in node.elements)
        return "{" + elems + "}"

    def visit_DictUnpackEntry(self, node):
        return f"**{self._expr(node.value)}"

    # -- Expressions --

    def visit_Identifier(self, node):
        return node.name

    def visit_ModelRefLiteral(self, node):
        return f"ModelRef({node.model_name!r})"

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
        keyword = "yield from" if getattr(node, "is_from", False) else "yield"
        if node.value:
            val = self._expr(node.value)
            return f"({keyword} {val})"
        return f"({keyword})"

    def visit_AwaitExpr(self, node):
        val = self._expr(node.value)
        return f"(await {val})"

    def visit_NamedExpr(self, node):
        target = self._expr(node.target)
        value = self._expr(node.value)
        return f"({target} := {value})"

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
        # Handle separator markers: bare * and /
        if node.name in ("*", "/"):
            return node.name
        prefix = ""
        if node.is_kwarg:
            prefix = "**"
        elif node.is_vararg:
            prefix = "*"
        annotation = ""
        if getattr(node, "annotation", None):
            annotation = f": {self._expr(node.annotation)}"
        if node.default:
            default_expr = self._expr(node.default)
            return f"{prefix}{node.name}{annotation}={default_expr}"
        return f"{prefix}{node.name}{annotation}"

    def visit_StarredExpr(self, node):
        val = self._expr(node.value)
        prefix = "**" if node.is_double else "*"
        return f"{prefix}{val}"

    def visit_TupleLiteral(self, node):
        elems = ", ".join(self._expr(e) for e in node.elements)
        # Single-element tuples need trailing comma: (x,)
        if len(node.elements) == 1:
            elems += ","
        return f"({elems})"

    def visit_ListComprehension(self, node):
        elem = self._expr(node.element)
        result = f"[{elem}"
        for clause in self._comprehension_clauses(node):
            target = self._expr(clause.target)
            iterable = self._expr(clause.iterable)
            result += f" for {target} in {iterable}"
            for cond in clause.conditions:
                result += f" if {self._expr(cond)}"
        result += "]"
        return result

    def visit_DictComprehension(self, node):
        key = self._expr(node.key)
        val = self._expr(node.value)
        result = "{" + f"{key}: {val}"
        for clause in self._comprehension_clauses(node):
            target = self._expr(clause.target)
            iterable = self._expr(clause.iterable)
            result += f" for {target} in {iterable}"
            for cond in clause.conditions:
                result += f" if {self._expr(cond)}"
        result += "}"
        return result

    def visit_GeneratorExpr(self, node):
        elem = self._expr(node.element)
        result = f"({elem}"
        for clause in self._comprehension_clauses(node):
            target = self._expr(clause.target)
            iterable = self._expr(clause.iterable)
            result += f" for {target} in {iterable}"
            for cond in clause.conditions:
                result += f" if {self._expr(cond)}"
        result += ")"
        return result

    def visit_SetComprehension(self, node):
        elem = self._expr(node.element)
        result = "{" + elem
        for clause in self._comprehension_clauses(node):
            target = self._expr(clause.target)
            iterable = self._expr(clause.iterable)
            result += f" for {target} in {iterable}"
            for cond in clause.conditions:
                result += f" if {self._expr(cond)}"
        result += "}"
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
                conversion = getattr(
                    part, "fstring_conversion",
                    getattr(part, "_fstring_conversion", "")
                )
                format_spec = getattr(
                    part, "fstring_format_spec",
                    getattr(part, "_fstring_format_spec", "")
                )
                expr_str = self._expr(part)
                suffix = ""
                if conversion:
                    suffix += f"!{conversion}"
                if format_spec:
                    suffix += f":{format_spec}"
                result += "{" + expr_str + suffix + "}"
        result += '"'
        return result

    def generic_visit(self, node):
        """Raise when expression node code generation is not implemented."""
        raise CodeGenerationError(
            f"Unsupported expression node: {type(node).__name__}",
            node.line, node.column
        )


class _IRExpressionGenerator:
    """Render semantic IR expressions directly as Python source."""

    def render(self, node):
        """Render an IR expression node."""
        method = getattr(self, f"_render_{type(node).__name__}", None)
        if callable(method):
            return method(node)  # pylint: disable=not-callable
        raise CodeGenerationError(
            f"Unsupported IR expression node: {type(node).__name__}",
            node.line,
            node.column,
        )

    def render_parameter(self, node):
        """Render an IR parameter."""
        if node.name in ("*", "/"):
            return node.name
        prefix = ""
        if node.is_kwarg:
            prefix = "**"
        elif node.is_vararg:
            prefix = "*"
        annotation = ""
        if node.annotation is not None:
            annotation = f": {_format_ir_type(node.annotation)}"
        if node.default is not None:
            return f"{prefix}{node.name}{annotation}={self.render(node.default)}"
        return f"{prefix}{node.name}{annotation}"

    def _render_IRLiteral(self, node):
        if node.kind in {"int", "float", "decimal"}:
            return _convert_numeral_literal(node.value)
        if node.kind == "string":
            return repr(node.value)
        if node.kind == "bytes":
            return f"b{repr(node.value)}"
        if node.kind == "bool":
            return "True" if node.value else "False"
        if node.kind == "none":
            return "None"
        if node.kind == "date":
            return repr(node.value)
        return repr(node.value)

    def _render_IRFStringLiteral(self, node):
        result = 'f"'
        for part in node.parts:
            if isinstance(part, str):
                escaped = part.replace("\\", "\\\\").replace('"', '\\"')
                escaped = escaped.replace("{", "{{").replace("}", "}}")
                result += escaped
            else:
                conversion = getattr(
                    part,
                    "fstring_conversion",
                    getattr(part, "_fstring_conversion", ""),
                )
                format_spec = getattr(
                    part,
                    "fstring_format_spec",
                    getattr(part, "_fstring_format_spec", ""),
                )
                suffix = ""
                if conversion:
                    suffix += f"!{conversion}"
                if format_spec:
                    suffix += f":{format_spec}"
                result += "{" + self.render(part) + suffix + "}"
        return result + '"'

    def _render_IRListLiteral(self, node):
        return "[" + ", ".join(self.render(elem) for elem in node.elements) + "]"

    def _render_IRDictLiteral(self, node):
        parts = []
        for entry in node.entries:
            if isinstance(entry, tuple):
                parts.append(f"{self.render(entry[0])}: {self.render(entry[1])}")
            else:
                parts.append(self.render(entry))
        return "{" + ", ".join(parts) + "}"

    def _render_IRSetLiteral(self, node):
        return "{" + ", ".join(self.render(elem) for elem in node.elements) + "}"

    def _render_IRTupleLiteral(self, node):
        elems = ", ".join(self.render(elem) for elem in node.elements)
        if len(node.elements) == 1:
            elems += ","
        return f"({elems})"

    def _render_IRIdentifier(self, node):
        return node.name

    def _render_IRModelRef(self, node):
        return f"ModelRef({node.model_name!r})"

    def _render_IRBinaryOp(self, node):
        return f"({self.render(node.left)} {node.op} {self.render(node.right)})"

    def _render_IRUnaryOp(self, node):
        operand = self.render(node.operand)
        if node.op == "NOT":
            return f"(not {operand})"
        if node.op == "not":
            return f"(not {operand})"
        if node.op == "~":
            return f"(~{operand})"
        return f"({node.op}{operand})"

    def _render_IRBooleanOp(self, node):
        op_name = node.op.lower() if isinstance(node.op, str) else node.op
        op = f" {op_name} "
        return "(" + op.join(self.render(value) for value in node.values) + ")"

    def _render_IRCompareOp(self, node):
        parts = [self.render(node.left)]
        for op, right in node.comparators:
            parts.append(op)
            parts.append(self.render(right))
        return "(" + " ".join(parts) + ")"

    def _render_IRCallExpr(self, node):
        args = [self.render(arg) for arg in node.args]
        kwargs = [f"{name}={self.render(value)}" for name, value in node.keywords]
        return f"{self.render(node.func)}({', '.join(args + kwargs)})"

    def _render_IRAttributeAccess(self, node):
        return f"{self.render(node.obj)}.{node.attr}"

    def _render_IRIndexAccess(self, node):
        return f"{self.render(node.obj)}[{self.render(node.index)}]"

    def _render_IRSliceExpr(self, node):
        start = self.render(node.start) if node.start is not None else ""
        stop = self.render(node.stop) if node.stop is not None else ""
        if node.step is not None:
            return f"{start}:{stop}:{self.render(node.step)}"
        return f"{start}:{stop}"

    def _render_IRStarredExpr(self, node):
        prefix = "**" if node.is_double else "*"
        return f"{prefix}{self.render(node.value)}"

    def _render_IRLambdaExpr(self, node):
        params = ", ".join(self.render_parameter(param) for param in node.parameters)
        return f"(lambda {params}: {self.render(node.body)})"

    def _render_IRPipeExpr(self, node):
        left = self.render(node.left)
        right = node.right
        if isinstance(right, ir.IRCallExpr):
            args = [left] + [self.render(arg) for arg in right.args]
            kwargs = [f"{name}={self.render(value)}" for name, value in right.keywords]
            return f"{self.render(right.func)}({', '.join(args + kwargs)})"
        return f"{self.render(right)}({left})"

    def _render_IRResultPropagation(self, node):
        return f"__ml_result_propagate({self.render(node.operand)})"

    def _render_IRAwaitExpr(self, node):
        return f"(await {self.render(node.value)})"

    def _render_IRYieldExpr(self, node):
        keyword = "yield from" if node.is_from else "yield"
        if node.value is None:
            return f"({keyword})"
        return f"({keyword} {self.render(node.value)})"

    def _render_IRNamedExpr(self, node):
        return f"({node.target} := {self.render(node.value)})"

    def _render_IRConditionalExpr(self, node):
        return (
            f"({self.render(node.true_expr)} if {self.render(node.condition)} "
            f"else {self.render(node.false_expr)})"
        )

    def _render_IRListComp(self, node):
        result = f"[{self.render(node.element)}"
        for clause in node.clauses:
            prefix = " async" if clause.is_async else ""
            result += (
                f"{prefix} for {self.render(clause.target)} "
                f"in {self.render(clause.iterable)}"
            )
            for cond in clause.conditions:
                result += f" if {self.render(cond)}"
        return result + "]"

    def _render_IRDictComp(self, node):
        result = "{" + f"{self.render(node.key)}: {self.render(node.value)}"
        for clause in node.clauses:
            prefix = " async" if clause.is_async else ""
            result += (
                f"{prefix} for {self.render(clause.target)} "
                f"in {self.render(clause.iterable)}"
            )
            for cond in clause.conditions:
                result += f" if {self.render(cond)}"
        return result + "}"

    def _render_IRSetComp(self, node):
        result = "{" + self.render(node.element)
        for clause in node.clauses:
            prefix = " async" if clause.is_async else ""
            result += (
                f"{prefix} for {self.render(clause.target)} "
                f"in {self.render(clause.iterable)}"
            )
            for cond in clause.conditions:
                result += f" if {self.render(cond)}"
        return result + "}"

    def _render_IRGeneratorExpr(self, node):
        result = f"({self.render(node.element)}"
        for clause in node.clauses:
            prefix = " async" if clause.is_async else ""
            result += (
                f"{prefix} for {self.render(clause.target)} "
                f"in {self.render(clause.iterable)}"
            )
            for cond in clause.conditions:
                result += f" if {self.render(cond)}"
        return result + ")"

    def _render_IRPromptExpr(self, node):
        return f"prompt({self.render(node.model)}, {self.render(node.template)})"

    def _render_IRGenerateExpr(self, node):
        args = [self.render(node.model), self.render(node.template)]
        if node.target_type is not None:
            args.append(f"target_type={_format_ir_type(node.target_type)}")
        return f"generate({', '.join(args)})"

    def _render_IRThinkExpr(self, node):
        return f"think({self.render(node.model)}, {self.render(node.template)})"

    def _render_IRStreamExpr(self, node):
        return f"stream({self.render(node.model)}, {self.render(node.template)})"

    def _render_IREmbedExpr(self, node):
        return f"embed({self.render(node.model)}, {self.render(node.value)})"

    def _render_IRExtractExpr(self, node):
        args = [self.render(node.model), self.render(node.source)]
        if node.target_type is not None:
            args.append(f"target_type={_format_ir_type(node.target_type)}")
        return f"extract({', '.join(args)})"

    def _render_IRClassifyExpr(self, node):
        args = [self.render(node.model), self.render(node.subject)]
        if node.categories:
            cats = "[" + ", ".join(self.render(cat) for cat in node.categories) + "]"
            args.append(f"categories={cats}")
        if node.target_type is not None:
            args.append(f"target_type={_format_ir_type(node.target_type)}")
        return f"classify({', '.join(args)})"

    def _render_IRPlanExpr(self, node):
        return f"plan({self.render(node.model)}, {self.render(node.goal)})"

    def _render_IRTranscribeExpr(self, node):
        return f"transcribe({self.render(node.model)}, {self.render(node.source)})"

    def _render_IRRetrieveExpr(self, node):
        args = [self.render(node.index), self.render(node.query)]
        if node.model is not None:
            args.append(f"model={self.render(node.model)}")
        return f"retrieve({', '.join(args)})"

    def _render_IRSemanticMatchOp(self, node):
        args = [
            self.render(node.left),
            self.render(node.right),
            f"threshold={node.threshold!r}",
        ]
        if node.model is not None:
            args.append(f"model={self.render(node.model)}")
        return f"semantic_match({', '.join(args)})"
