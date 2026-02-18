#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Recursive-descent parser for the multilingual programming language."""

from typing import NoReturn

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.parser.ast_nodes import (
    Program, NumeralLiteral, StringLiteral, DateLiteral,
    BooleanLiteral, NoneLiteral, ListLiteral, DictLiteral, SetLiteral,
    Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess, ConditionalExpr,
    LambdaExpr, YieldExpr, AwaitExpr, NamedExpr,
    VariableDeclaration, Assignment, AnnAssignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, GlobalStatement, LocalStatement, YieldStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, CaseClause,
    WithStatement, ImportStatement, FromImportStatement,
    SliceExpr, Parameter, StarredExpr, TupleLiteral,
    ListComprehension, DictComprehension, GeneratorExpr,
    FStringLiteral, AssertStatement, ChainedAssignment, DictUnpackEntry,
)
from multilingualprogramming.parser.error_messages import ErrorMessageRegistry
from multilingualprogramming.exceptions import ParseError

# Concepts that begin compound statements
_COMPOUND_CONCEPTS = {
    "COND_IF", "LOOP_WHILE", "LOOP_FOR", "FUNC_DEF", "CLASS_DEF",
    "TRY", "MATCH", "WITH",
}

# Concepts that begin simple keyword statements
_SIMPLE_CONCEPTS = {
    "LET", "CONST", "RETURN", "YIELD", "RAISE",
    "LOOP_BREAK", "LOOP_CONTINUE", "PASS",
    "GLOBAL", "LOCAL", "IMPORT", "FROM", "ASSERT",
}

# Concepts treated as identifiers when appearing in expressions
_CALLABLE_CONCEPTS = {"PRINT", "INPUT"}
_TYPE_CONCEPTS = {
    "TYPE_INT", "TYPE_FLOAT", "TYPE_STR",
    "TYPE_BOOL", "TYPE_LIST", "TYPE_DICT",
}

# Augmented assignment operators
_AUGMENTED_OPS = {
    "+=", "-=", "*=", "/=",
    "**=", "//=", "%=", "&=", "|=", "^=", "<<=", ">>=",
}

# Comparison operators
_COMPARISON_OPS = {"==", "!=", "<", ">", "<=", ">="}


class Parser:
    """
    Recursive-descent parser for the multilingual programming language.

    Consumes a list[Token] from the Lexer and produces an AST.
    Dispatches on token.concept for language-agnostic parsing.
    """

    def __init__(self, tokens, source_language=None):
        self.tokens = tokens
        self.pos = 0
        self.source_language = source_language or "en"
        self._error_registry = ErrorMessageRegistry()

    # ------------------------------------------------------------------
    # Token navigation
    # ------------------------------------------------------------------

    def _current(self):
        """Return current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF

    def _advance(self):
        """Consume and return current token."""
        token = self._current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def _match_type(self, token_type):
        """Check if current token matches the given type."""
        return self._current().type == token_type

    def _match_concept(self, concept):
        """Check if current token is a KEYWORD with the given concept."""
        tok = self._current()
        return tok.type == TokenType.KEYWORD and tok.concept == concept

    def _peek_concept(self, concept):
        """Check if next token (pos+1) is a KEYWORD with the given concept."""
        idx = self.pos + 1
        if idx < len(self.tokens):
            tok = self.tokens[idx]
            return tok.type == TokenType.KEYWORD and tok.concept == concept
        return False

    def _match_operator(self, op):
        """Check if current token is an OPERATOR with the given value."""
        tok = self._current()
        return tok.type == TokenType.OPERATOR and tok.value == op

    def _match_delimiter(self, delim):
        """Check if current token is a DELIMITER with the given value."""
        tok = self._current()
        return tok.type == TokenType.DELIMITER and tok.value == delim

    def _expect_type(self, token_type):
        """Consume if type matches; raise ParseError otherwise."""
        tok = self._current()
        if tok.type == token_type:
            return self._advance()
        self._error(
            "MISMATCHED_DELIMITER",
            tok,
            expected=token_type.name,
            actual=tok.type.name,
        )

    def _expect_concept(self, concept):
        """Consume if KEYWORD with given concept; raise otherwise."""
        tok = self._current()
        if tok.type == TokenType.KEYWORD and tok.concept == concept:
            return self._advance()
        self._error(
            "UNEXPECTED_TOKEN",
            tok,
            token=tok.value,
        )

    def _expect_operator(self, op):
        """Consume if OPERATOR with given value; raise otherwise."""
        tok = self._current()
        if tok.type == TokenType.OPERATOR and tok.value == op:
            return self._advance()
        self._error(
            "MISMATCHED_DELIMITER",
            tok,
            expected=op,
            actual=tok.value,
        )

    def _expect_delimiter(self, delim):
        """Consume if DELIMITER with given value; raise otherwise."""
        tok = self._current()
        if tok.type == TokenType.DELIMITER and tok.value == delim:
            return self._advance()
        self._error(
            "MISMATCHED_DELIMITER",
            tok,
            expected=delim,
            actual=tok.value,
        )

    def _expect_identifier(self):
        """Consume an IDENTIFIER token; raise otherwise."""
        tok = self._current()
        if tok.type == TokenType.IDENTIFIER:
            return self._advance()
        self._error("EXPECTED_IDENTIFIER", tok, token=tok.value)

    def _at_end(self):
        """Check if current token is EOF."""
        return self._current().type == TokenType.EOF

    def _skip_newlines(self):
        """Skip NEWLINE and COMMENT tokens."""
        while self._current().type in (TokenType.NEWLINE, TokenType.COMMENT):
            self._advance()

    def _error(self, message_key, err_token, **kwargs) -> NoReturn:
        """Raise a ParseError with a multilingual message."""
        kwargs.setdefault("line", err_token.line)
        kwargs.setdefault("column", err_token.column)
        msg = self._error_registry.format(
            message_key, self.source_language, **kwargs
        )
        raise ParseError(msg, err_token.line, err_token.column)

    def parse_expression_fragment(self):
        """Parse and return a single expression from the current token stream."""
        return self._parse_expression()

    # ------------------------------------------------------------------
    # Top-level entry point
    # ------------------------------------------------------------------

    def parse(self):
        """Parse the token stream into a Program AST."""
        self._skip_newlines()
        body = []
        while not self._at_end():
            stmt = self._parse_statement()
            body.append(stmt)
            self._skip_newlines()
        line = self.tokens[0].line if self.tokens else 0
        col = self.tokens[0].column if self.tokens else 0
        return Program(body, line, col)

    # ------------------------------------------------------------------
    # Statement parsing
    # ------------------------------------------------------------------

    def _parse_statement(self):
        """Parse a single statement."""
        self._skip_newlines()
        tok = self._current()

        # Decorators: @expr before def/class
        if self._match_delimiter("@"):
            return self._parse_decorated()

        if tok.type == TokenType.KEYWORD and tok.concept == "ASYNC":
            return self._parse_async_statement()

        if tok.type == TokenType.KEYWORD and tok.concept:
            concept = tok.concept
            if concept in _COMPOUND_CONCEPTS:
                return self._parse_compound_statement(concept)
            if concept in _SIMPLE_CONCEPTS:
                return self._parse_simple_statement(concept)

        return self._parse_assignment_or_expression()

    def _parse_async_statement(self):
        """Parse async-prefixed compound statements."""
        tok = self._advance()  # consume ASYNC
        if self._match_concept("FUNC_DEF"):
            return self._parse_function_def(is_async=True, async_tok=tok)
        self._error("UNEXPECTED_TOKEN", self._current(),
                    token=self._current().value)

    def _parse_decorated(self):
        """Parse decorated function or class definition."""
        decorators = []
        while self._match_delimiter("@"):
            self._advance()  # consume @
            dec_expr = self._parse_expression()
            decorators.append(dec_expr)
            self._skip_newlines()

        # The next statement must be a function or class def
        tok = self._current()
        if tok.type == TokenType.KEYWORD and tok.concept == "FUNC_DEF":
            node = self._parse_function_def()
            node.decorators = decorators
            return node
        if tok.type == TokenType.KEYWORD and tok.concept == "ASYNC":
            node = self._parse_async_statement()
            if isinstance(node, FunctionDef):
                node.decorators = decorators
                return node
        if tok.type == TokenType.KEYWORD and tok.concept == "CLASS_DEF":
            node = self._parse_class_def()
            node.decorators = decorators
            return node

        self._error("UNEXPECTED_TOKEN", tok, token=tok.value)

    def _parse_compound_statement(self, concept):
        """Parse a compound (block) statement."""
        if concept == "COND_IF":
            return self._parse_if_statement()
        if concept == "LOOP_WHILE":
            return self._parse_while_loop()
        if concept == "LOOP_FOR":
            return self._parse_for_loop()
        if concept == "FUNC_DEF":
            return self._parse_function_def()
        if concept == "CLASS_DEF":
            return self._parse_class_def()
        if concept == "TRY":
            return self._parse_try_statement()
        if concept == "MATCH":
            return self._parse_match_statement()
        if concept == "WITH":
            return self._parse_with_statement()
        self._error("UNEXPECTED_TOKEN", self._current(),
                     token=self._current().value)

    def _parse_simple_statement(self, concept):
        """Parse a simple keyword statement."""
        if concept == "LET":
            return self._parse_let_declaration()
        if concept == "CONST":
            return self._parse_const_declaration()
        if concept == "RETURN":
            return self._parse_return_statement()
        if concept == "YIELD":
            return self._parse_yield_statement()
        if concept == "RAISE":
            return self._parse_raise_statement()
        if concept == "LOOP_BREAK":
            return self._parse_break_statement()
        if concept == "LOOP_CONTINUE":
            return self._parse_continue_statement()
        if concept == "PASS":
            return self._parse_pass_statement()
        if concept == "GLOBAL":
            return self._parse_global_statement()
        if concept == "LOCAL":
            return self._parse_local_statement()
        if concept == "IMPORT":
            return self._parse_import_statement()
        if concept == "FROM":
            return self._parse_from_import_statement()
        if concept == "ASSERT":
            return self._parse_assert_statement()
        self._error("UNEXPECTED_TOKEN", self._current(),
                     token=self._current().value)

    # ------------------------------------------------------------------
    # Block parsing
    # ------------------------------------------------------------------

    def _parse_block(self):
        """Parse an indented block: colon NEWLINE INDENT stmts DEDENT."""
        self._expect_delimiter(":")
        self._skip_newlines()
        self._expect_type(TokenType.INDENT)
        self._skip_newlines()

        body = []
        while not self._at_end() and not self._match_type(TokenType.DEDENT):
            stmt = self._parse_statement()
            body.append(stmt)
            self._skip_newlines()

        if self._match_type(TokenType.DEDENT):
            self._advance()

        return body

    # ------------------------------------------------------------------
    # Variable declarations and assignments
    # ------------------------------------------------------------------

    def _parse_let_declaration(self):
        """Parse: LET name = expression."""
        tok = self._advance()  # consume LET
        name_tok = self._expect_identifier()
        self._expect_operator("=")
        value = self._parse_expression()
        return VariableDeclaration(
            name_tok.value, value, is_const=False,
            line=tok.line, column=tok.column
        )

    def _parse_const_declaration(self):
        """Parse: CONST name = expression."""
        tok = self._advance()  # consume CONST
        name_tok = self._expect_identifier()
        self._expect_operator("=")
        value = self._parse_expression()
        return VariableDeclaration(
            name_tok.value, value, is_const=True,
            line=tok.line, column=tok.column
        )

    def _parse_assignment_or_expression(self):
        """Parse assignment or expression statement."""
        expr = self._parse_expression()

        # Annotated assignment: name: type [= value]
        if isinstance(expr, Identifier) and self._match_delimiter(":"):
            tok = self._advance()  # consume :
            annotation = self._parse_expression()
            value = None
            if self._match_operator("="):
                self._advance()
                value = self._parse_expression()
            return AnnAssignment(
                expr, annotation, value,
                line=tok.line, column=tok.column
            )

        # Check for comma (tuple unpacking: a, b = ...)
        if self._match_delimiter(","):
            elements = [expr]
            while self._match_delimiter(","):
                self._advance()
                # Stop if we hit = after comma (trailing comma)
                if self._current().type == TokenType.OPERATOR \
                        and self._current().value == "=":
                    break
                elements.append(self._parse_expression())
            expr = TupleLiteral(elements,
                                line=expr.line, column=expr.column)

        # Check for assignment operators
        tok = self._current()
        if tok.type == TokenType.OPERATOR and tok.value == "=":
            self._advance()
            value = self._parse_expression()
            # Check for tuple on the right side too
            if self._match_delimiter(","):
                right_elements = [value]
                while self._match_delimiter(","):
                    self._advance()
                    if self._at_end() or self._match_type(TokenType.NEWLINE):
                        break
                    right_elements.append(self._parse_expression())
                value = TupleLiteral(right_elements,
                                     line=value.line, column=value.column)
            # Check for chained assignment (a = b = c = 0)
            if self._current().type == TokenType.OPERATOR \
                    and self._current().value == "=":
                targets = [expr, value]
                while self._current().type == TokenType.OPERATOR \
                        and self._current().value == "=":
                    self._advance()
                    value = self._parse_expression()
                    targets.append(value)
                final_value = targets.pop()
                return ChainedAssignment(
                    targets, final_value,
                    line=expr.line, column=expr.column
                )
            return Assignment(
                expr, value, op="=",
                line=expr.line, column=expr.column
            )

        if tok.type == TokenType.OPERATOR and tok.value in _AUGMENTED_OPS:
            op = self._advance().value
            value = self._parse_expression()
            return Assignment(
                expr, value, op=op,
                line=expr.line, column=expr.column
            )

        return ExpressionStatement(
            expr, line=expr.line, column=expr.column
        )

    # ------------------------------------------------------------------
    # Control flow
    # ------------------------------------------------------------------

    def _parse_if_statement(self):
        """Parse: IF condition : block [ELIF ...] [ELSE ...]."""
        tok = self._advance()  # consume IF
        condition = self._parse_expression()
        body = self._parse_block()
        self._skip_newlines()

        elif_clauses = []
        while self._match_concept("COND_ELIF"):
            self._advance()
            elif_cond = self._parse_expression()
            elif_body = self._parse_block()
            elif_clauses.append((elif_cond, elif_body))
            self._skip_newlines()

        else_body = None
        if self._match_concept("COND_ELSE"):
            self._advance()
            else_body = self._parse_block()

        return IfStatement(
            condition, body, elif_clauses, else_body,
            line=tok.line, column=tok.column
        )

    def _parse_while_loop(self):
        """Parse: WHILE condition : block."""
        tok = self._advance()  # consume WHILE
        condition = self._parse_expression()
        body = self._parse_block()
        return WhileLoop(
            condition, body,
            line=tok.line, column=tok.column
        )

    def _parse_for_loop(self):
        """Parse: FOR target[, target2, ...] IN iterable : block."""
        tok = self._advance()  # consume FOR
        target_tok = self._expect_identifier()
        target = Identifier(
            target_tok.value,
            line=target_tok.line, column=target_tok.column
        )
        # Support tuple unpacking: for a, b in items
        if self._match_delimiter(","):
            elements = [target]
            while self._match_delimiter(","):
                self._advance()
                next_tok = self._expect_identifier()
                elements.append(Identifier(
                    next_tok.value,
                    line=next_tok.line, column=next_tok.column
                ))
            target = TupleLiteral(elements,
                                  line=target.line, column=target.column)
        self._expect_concept("IN")
        iterable = self._parse_expression()
        body = self._parse_block()
        return ForLoop(
            target, iterable, body,
            line=tok.line, column=tok.column
        )

    def _parse_match_statement(self):
        """Parse: MATCH subject : NEWLINE INDENT (CASE/DEFAULT : block)+ DEDENT."""
        tok = self._advance()  # consume MATCH
        subject = self._parse_expression()
        self._expect_delimiter(":")
        self._skip_newlines()
        self._expect_type(TokenType.INDENT)
        self._skip_newlines()

        cases = []
        while not self._at_end() and not self._match_type(TokenType.DEDENT):
            if self._match_concept("CASE"):
                case_tok = self._advance()
                pattern = self._parse_expression()
                case_body = self._parse_block()
                cases.append(CaseClause(
                    pattern, case_body, is_default=False,
                    line=case_tok.line, column=case_tok.column
                ))
            elif self._match_concept("DEFAULT"):
                case_tok = self._advance()
                case_body = self._parse_block()
                cases.append(CaseClause(
                    None, case_body, is_default=True,
                    line=case_tok.line, column=case_tok.column
                ))
            else:
                self._error("UNEXPECTED_TOKEN", self._current(),
                             token=self._current().value)
            self._skip_newlines()

        if self._match_type(TokenType.DEDENT):
            self._advance()

        return MatchStatement(
            subject, cases,
            line=tok.line, column=tok.column
        )

    # ------------------------------------------------------------------
    # Definitions
    # ------------------------------------------------------------------

    def _parse_function_def(self, is_async=False, async_tok=None):
        """Parse: FUNC_DEF name ( params ) : block."""
        tok = self._advance()  # consume FUNC_DEF
        name_tok = self._expect_identifier()
        self._expect_delimiter("(")

        params = []
        if not self._match_delimiter(")"):
            params.append(self._parse_parameter())
            while self._match_delimiter(","):
                self._advance()
                params.append(self._parse_parameter())

        self._expect_delimiter(")")
        return_annotation = None
        if self._match_operator("->"):
            self._advance()
            return_annotation = self._parse_expression()
        body = self._parse_block()
        line = async_tok.line if async_tok else tok.line
        column = async_tok.column if async_tok else tok.column
        return FunctionDef(
            name_tok.value, params, body,
            return_annotation=return_annotation,
            is_async=is_async,
            line=line, column=column
        )

    def _parse_parameter(self):
        """Parse a single function parameter: [*|**] name [: type] [= default]."""
        is_vararg = False
        is_kwarg = False

        if self._match_operator("**"):
            self._advance()
            is_kwarg = True
        elif self._match_operator("*"):
            self._advance()
            is_vararg = True

        name_tok = self._expect_identifier()
        annotation = None
        if self._match_delimiter(":"):
            self._advance()
            annotation = self._parse_expression()
        default = None
        if self._match_operator("="):
            self._advance()
            default = self._parse_expression()

        return Parameter(
            name_tok.value, default, is_vararg, is_kwarg, annotation,
            line=name_tok.line, column=name_tok.column
        )

    def _parse_class_def(self):
        """Parse: CLASS_DEF name [(bases)] : block."""
        tok = self._advance()  # consume CLASS_DEF
        name_tok = self._expect_identifier()

        bases = []
        if self._match_delimiter("("):
            self._advance()
            if not self._match_delimiter(")"):
                bases.append(self._parse_expression())
                while self._match_delimiter(","):
                    self._advance()
                    bases.append(self._parse_expression())
            self._expect_delimiter(")")

        body = self._parse_block()
        return ClassDef(
            name_tok.value, bases, body,
            line=tok.line, column=tok.column
        )

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def _parse_try_statement(self):
        """Parse: TRY : block (EXCEPT ...)* [FINALLY ...]."""
        tok = self._advance()  # consume TRY
        body = self._parse_block()
        self._skip_newlines()

        handlers = []
        while self._match_concept("EXCEPT"):
            handlers.append(self._parse_except_handler())
            self._skip_newlines()

        finally_body = None
        if self._match_concept("FINALLY"):
            self._advance()
            finally_body = self._parse_block()

        return TryStatement(
            body, handlers, finally_body,
            line=tok.line, column=tok.column
        )

    def _parse_except_handler(self):
        """Parse: EXCEPT [Type [AS name]] : block."""
        tok = self._advance()  # consume EXCEPT
        exc_type = None
        name = None

        # Check for exception type
        if not self._match_delimiter(":"):
            exc_type_tok = self._expect_identifier()
            exc_type = Identifier(
                exc_type_tok.value,
                line=exc_type_tok.line, column=exc_type_tok.column
            )
            if self._match_concept("AS"):
                self._advance()
                name_tok = self._expect_identifier()
                name = name_tok.value

        handler_body = self._parse_block()
        return ExceptHandler(
            exc_type, name, handler_body,
            line=tok.line, column=tok.column
        )

    # ------------------------------------------------------------------
    # With statement
    # ------------------------------------------------------------------

    def _parse_with_statement(self):
        """Parse: WITH expression [AS name] (, expression [AS name])* : block."""
        tok = self._advance()  # consume WITH
        items = []
        while True:
            context_expr = self._parse_expression()
            name = None
            if self._match_concept("AS"):
                self._advance()
                name_tok = self._expect_identifier()
                name = name_tok.value
            items.append((context_expr, name))
            if not self._match_delimiter(","):
                break
            self._advance()

        body = self._parse_block()
        return WithStatement(
            items, body,
            line=tok.line, column=tok.column
        )

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def _parse_import_statement(self):
        """Parse: IMPORT module [AS alias]."""
        tok = self._advance()  # consume IMPORT
        module_tok = self._expect_identifier()
        module = module_tok.value

        # Support dotted module names
        while self._match_delimiter("."):
            self._advance()
            next_tok = self._expect_identifier()
            module += "." + next_tok.value

        alias = None
        if self._match_concept("AS"):
            self._advance()
            alias_tok = self._expect_identifier()
            alias = alias_tok.value

        return ImportStatement(
            module, alias,
            line=tok.line, column=tok.column
        )

    def _parse_from_import_statement(self):
        """Parse: FROM module IMPORT name [AS alias], ..."""
        tok = self._advance()  # consume FROM
        module_tok = self._expect_identifier()
        module = module_tok.value

        while self._match_delimiter("."):
            self._advance()
            next_tok = self._expect_identifier()
            module += "." + next_tok.value

        self._expect_concept("IMPORT")

        names = []
        name_tok = self._expect_identifier()
        alias = None
        if self._match_concept("AS"):
            self._advance()
            alias_tok = self._expect_identifier()
            alias = alias_tok.value
        names.append((name_tok.value, alias))

        while self._match_delimiter(","):
            self._advance()
            name_tok = self._expect_identifier()
            alias = None
            if self._match_concept("AS"):
                self._advance()
                alias_tok = self._expect_identifier()
                alias = alias_tok.value
            names.append((name_tok.value, alias))

        return FromImportStatement(
            module, names,
            line=tok.line, column=tok.column
        )

    # ------------------------------------------------------------------
    # Other simple statements
    # ------------------------------------------------------------------

    def _parse_return_statement(self):
        """Parse: RETURN [expression]."""
        tok = self._advance()  # consume RETURN
        value = None
        if not self._at_end() and not self._match_type(TokenType.NEWLINE) \
                and not self._match_type(TokenType.DEDENT) \
                and not self._match_type(TokenType.EOF):
            value = self._parse_expression()
        return ReturnStatement(value, line=tok.line, column=tok.column)

    def _parse_yield_statement(self):
        """Parse: YIELD [expression]."""
        tok = self._advance()  # consume YIELD
        value = None
        if not self._at_end() and not self._match_type(TokenType.NEWLINE) \
                and not self._match_type(TokenType.DEDENT) \
                and not self._match_type(TokenType.EOF):
            value = self._parse_expression()
        return YieldStatement(value, line=tok.line, column=tok.column)

    def _parse_raise_statement(self):
        """Parse: RAISE [expression]."""
        tok = self._advance()  # consume RAISE
        value = None
        if not self._at_end() and not self._match_type(TokenType.NEWLINE) \
                and not self._match_type(TokenType.DEDENT) \
                and not self._match_type(TokenType.EOF):
            value = self._parse_expression()
        return RaiseStatement(value, line=tok.line, column=tok.column)

    def _parse_assert_statement(self):
        """Parse: ASSERT test [, msg]."""
        tok = self._advance()  # consume ASSERT
        test = self._parse_expression()
        msg = None
        if self._match_delimiter(","):
            self._advance()
            msg = self._parse_expression()
        return AssertStatement(test, msg, line=tok.line, column=tok.column)

    def _parse_break_statement(self):
        """Parse: BREAK."""
        tok = self._advance()
        return BreakStatement(line=tok.line, column=tok.column)

    def _parse_continue_statement(self):
        """Parse: CONTINUE."""
        tok = self._advance()
        return ContinueStatement(line=tok.line, column=tok.column)

    def _parse_pass_statement(self):
        """Parse: PASS."""
        tok = self._advance()
        return PassStatement(line=tok.line, column=tok.column)

    def _parse_global_statement(self):
        """Parse: GLOBAL name, name, ..."""
        tok = self._advance()  # consume GLOBAL
        names = [self._expect_identifier().value]
        while self._match_delimiter(","):
            self._advance()
            names.append(self._expect_identifier().value)
        return GlobalStatement(names, line=tok.line, column=tok.column)

    def _parse_local_statement(self):
        """Parse: LOCAL name, name, ..."""
        tok = self._advance()  # consume LOCAL
        names = [self._expect_identifier().value]
        while self._match_delimiter(","):
            self._advance()
            names.append(self._expect_identifier().value)
        return LocalStatement(names, line=tok.line, column=tok.column)

    # ------------------------------------------------------------------
    # Expression parsing (precedence climbing)
    # ------------------------------------------------------------------

    def _parse_expression(self):
        """Parse an expression (top level)."""
        return self._parse_named_expression()

    def _parse_named_expression(self):
        """Parse assignment expression: conditional_expr [:= expression]."""
        left = self._parse_conditional_expression()
        if self._match_operator(":="):
            tok = self._advance()
            if not isinstance(left, Identifier):
                self._error("UNEXPECTED_TOKEN", tok, token=tok.value)
            value = self._parse_expression()
            return NamedExpr(left, value, line=tok.line, column=tok.column)
        return left

    def _parse_conditional_expression(self):
        """Parse: or_expr [IF or_expr ELSE conditional_expr]."""
        true_expr = self._parse_or_expression()
        if self._match_concept("COND_IF"):
            tok = self._advance()
            condition = self._parse_or_expression()
            if not self._match_concept("COND_ELSE"):
                self._error("EXPECTED_EXPRESSION", self._current())
            self._advance()
            false_expr = self._parse_conditional_expression()
            return ConditionalExpr(
                condition, true_expr, false_expr,
                line=tok.line, column=tok.column
            )
        return true_expr

    def _parse_or_expression(self):
        """Parse: and_expr (OR and_expr)*."""
        left = self._parse_and_expression()
        values = [left]
        while self._match_concept("OR"):
            self._advance()
            values.append(self._parse_and_expression())
        if len(values) == 1:
            return left
        return BooleanOp("OR", values, line=left.line, column=left.column)

    def _parse_and_expression(self):
        """Parse: not_expr (AND not_expr)*."""
        left = self._parse_not_expression()
        values = [left]
        while self._match_concept("AND"):
            self._advance()
            values.append(self._parse_not_expression())
        if len(values) == 1:
            return left
        return BooleanOp("AND", values, line=left.line, column=left.column)

    def _parse_not_expression(self):
        """Parse: NOT not_expr | comparison."""
        if self._match_concept("NOT"):
            tok = self._advance()
            operand = self._parse_not_expression()
            return UnaryOp("NOT", operand, line=tok.line, column=tok.column)
        return self._parse_comparison()

    def _parse_comparison(self):
        """Parse: bitwise_or (comp_op bitwise_or)*  (chained).

        Supports standard operators (==, !=, <, >, <=, >=) plus
        keyword operators: in, not in, is, is not.
        """
        left = self._parse_bitwise_or()
        comparators = []
        while True:
            if self._current().type == TokenType.OPERATOR \
                    and self._current().value in _COMPARISON_OPS:
                op = self._advance().value
                right = self._parse_bitwise_or()
                comparators.append((op, right))
            elif self._match_concept("IN"):
                self._advance()
                right = self._parse_bitwise_or()
                comparators.append(("in", right))
            elif self._match_concept("NOT") and self._peek_concept("IN"):
                self._advance()  # consume NOT
                self._advance()  # consume IN
                right = self._parse_bitwise_or()
                comparators.append(("not in", right))
            elif self._match_concept("IS"):
                self._advance()
                if self._match_concept("NOT"):
                    self._advance()
                    right = self._parse_bitwise_or()
                    comparators.append(("is not", right))
                else:
                    right = self._parse_bitwise_or()
                    comparators.append(("is", right))
            else:
                break
        if not comparators:
            return left
        return CompareOp(left, comparators, line=left.line, column=left.column)

    def _parse_bitwise_or(self):
        """Parse: bitwise_xor (| bitwise_xor)*."""
        left = self._parse_bitwise_xor()
        while self._match_operator("|"):
            tok = self._advance()
            right = self._parse_bitwise_xor()
            left = BinaryOp(left, "|", right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_bitwise_xor(self):
        """Parse: bitwise_and (^ bitwise_and)*."""
        left = self._parse_bitwise_and()
        while self._match_operator("^"):
            tok = self._advance()
            right = self._parse_bitwise_and()
            left = BinaryOp(left, "^", right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_bitwise_and(self):
        """Parse: shift_expr (& shift_expr)*."""
        left = self._parse_shift_expression()
        while self._match_operator("&"):
            tok = self._advance()
            right = self._parse_shift_expression()
            left = BinaryOp(left, "&", right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_shift_expression(self):
        """Parse: additive (<< additive | >> additive)*."""
        left = self._parse_additive()
        while self._current().type == TokenType.OPERATOR \
                and self._current().value in ("<<", ">>"):
            tok = self._advance()
            right = self._parse_additive()
            left = BinaryOp(left, tok.value, right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_additive(self):
        """Parse: multiplicative ((+ | -) multiplicative)*."""
        left = self._parse_multiplicative()
        while self._current().type == TokenType.OPERATOR \
                and self._current().value in ("+", "-"):
            tok = self._advance()
            right = self._parse_multiplicative()
            left = BinaryOp(left, tok.value, right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_multiplicative(self):
        """Parse: unary ((* | / | // | %) unary)*."""
        left = self._parse_unary()
        while self._current().type == TokenType.OPERATOR \
                and self._current().value in ("*", "/", "//", "%"):
            tok = self._advance()
            right = self._parse_unary()
            left = BinaryOp(left, tok.value, right,
                            line=tok.line, column=tok.column)
        return left

    def _parse_unary(self):
        """Parse: AWAIT unary | (- | + | ~) unary | power."""
        if self._match_concept("AWAIT"):
            tok = self._advance()
            value = self._parse_unary()
            return AwaitExpr(value, line=tok.line, column=tok.column)
        if self._current().type == TokenType.OPERATOR \
                and self._current().value in ("-", "+", "~"):
            tok = self._advance()
            operand = self._parse_unary()
            return UnaryOp(tok.value, operand,
                           line=tok.line, column=tok.column)
        return self._parse_power()

    def _parse_power(self):
        """Parse: primary (** unary)?  (right-associative)."""
        base = self._parse_primary()
        if self._match_operator("**"):
            tok = self._advance()
            exponent = self._parse_unary()
            return BinaryOp(base, "**", exponent,
                            line=tok.line, column=tok.column)
        return base

    def _parse_primary(self):
        """Parse: atom trailer*  where trailer is (args) or [index] or .attr."""
        node = self._parse_atom()

        while True:
            if self._match_delimiter("("):
                node = self._parse_call(node)
            elif self._match_delimiter("["):
                tok = self._advance()
                index = self._parse_slice_or_index()
                self._expect_delimiter("]")
                node = IndexAccess(node, index,
                                   line=tok.line, column=tok.column)
            elif self._match_delimiter("."):
                tok = self._advance()
                attr_tok = self._expect_identifier()
                node = AttributeAccess(node, attr_tok.value,
                                       line=tok.line, column=tok.column)
            else:
                break

        return node

    def _parse_slice_or_index(self):
        """Parse index or slice expression inside [].

        Returns a SliceExpr if colons are present, otherwise a normal expression.
        Handles: [i], [s:e], [s:e:step], [:e], [s:], [::step], [:], [::]
        """
        tok = self._current()
        start = None
        # Check if we start with a colon (no start expression)
        if not self._match_delimiter(":"):
            start = self._parse_expression()

        # If no colon follows, it's a simple index
        if not self._match_delimiter(":"):
            return start

        # We have a slice — consume first colon
        self._advance()
        stop = None
        step = None

        # Parse stop (if present and not another colon or ])
        if not self._match_delimiter("]") and not self._match_delimiter(":"):
            stop = self._parse_expression()

        # Check for second colon (step)
        if self._match_delimiter(":"):
            self._advance()
            if not self._match_delimiter("]"):
                step = self._parse_expression()

        return SliceExpr(start, stop, step,
                         line=tok.line, column=tok.column)

    def _parse_call(self, func):
        """Parse function call arguments: (expr, expr, name=expr, ...)."""
        tok = self._advance()  # consume (
        args = []
        keywords = []

        if not self._match_delimiter(")"):
            self._parse_argument(args, keywords)
            # Check for generator expression: func(expr FOR ...)
            if len(args) == 1 and not keywords \
                    and self._match_concept("LOOP_FOR"):
                gen = self._parse_comprehension_tail(
                    args[0], tok, "generator"
                )
                # _parse_comprehension_tail consumed the closing )
                return CallExpr(func, [gen], [],
                                line=tok.line, column=tok.column)
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter(")"):
                    break
                self._parse_argument(args, keywords)

        self._expect_delimiter(")")
        return CallExpr(func, args, keywords,
                        line=tok.line, column=tok.column)

    def _parse_argument(self, args, keywords):
        """Parse a single argument (positional, keyword, *args, or **kwargs)."""
        # Check for **kwargs
        if self._match_operator("**"):
            tok = self._advance()
            value = self._parse_expression()
            args.append(StarredExpr(value, is_double=True,
                                    line=tok.line, column=tok.column))
            return

        # Check for *args
        if self._match_operator("*"):
            tok = self._advance()
            value = self._parse_expression()
            args.append(StarredExpr(value, is_double=False,
                                    line=tok.line, column=tok.column))
            return

        # Check for keyword argument: name=value
        if self._match_type(TokenType.IDENTIFIER):
            # Look ahead for '='
            save_pos = self.pos
            name_tok = self._advance()
            if self._match_operator("="):
                self._advance()
                value = self._parse_expression()
                keywords.append((name_tok.value, value))
                return
            # Not a keyword arg, restore and parse as expression
            self.pos = save_pos

        args.append(self._parse_expression())

    def _parse_atom(self):
        """Parse atomic expressions: literals, identifiers, parenthesized."""
        tok = self._current()

        # Numeral literal
        if tok.type == TokenType.NUMERAL:
            self._advance()
            return NumeralLiteral(tok.value,
                                  line=tok.line, column=tok.column)

        # String literal
        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(tok.value,
                                 line=tok.line, column=tok.column)

        # F-string literal
        if tok.type == TokenType.FSTRING:
            self._advance()
            return self._parse_fstring(tok)

        # Date literal
        if tok.type == TokenType.DATE_LITERAL:
            self._advance()
            return DateLiteral(tok.value,
                               line=tok.line, column=tok.column)

        # Identifier
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Identifier(tok.value,
                              line=tok.line, column=tok.column)

        # Keyword-based atoms
        if tok.type == TokenType.KEYWORD:
            concept = tok.concept

            # Boolean literals
            if concept == "TRUE":
                self._advance()
                return BooleanLiteral(True,
                                      line=tok.line, column=tok.column)
            if concept == "FALSE":
                self._advance()
                return BooleanLiteral(False,
                                      line=tok.line, column=tok.column)

            # None literal
            if concept == "NONE":
                self._advance()
                return NoneLiteral(line=tok.line, column=tok.column)

            # PRINT, INPUT as callable identifiers
            if concept in _CALLABLE_CONCEPTS:
                self._advance()
                return Identifier(tok.value,
                                  line=tok.line, column=tok.column)

            # Type keywords as identifiers
            if concept in _TYPE_CONCEPTS:
                self._advance()
                return Identifier(tok.value,
                                  line=tok.line, column=tok.column)

            # Lambda
            if concept == "LAMBDA":
                return self._parse_lambda()

            # Yield expression
            if concept == "YIELD":
                return self._parse_yield_expr()

        # Parenthesized expression or generator expression
        if self._match_delimiter("("):
            open_tok = self._advance()
            if self._match_delimiter(")"):
                # Empty tuple ()
                return TupleLiteral([], line=open_tok.line,
                                    column=open_tok.column)
            expr = self._parse_expression()
            # Check for generator expression: (expr FOR ...)
            if self._match_concept("LOOP_FOR"):
                result = self._parse_comprehension_tail(
                    expr, open_tok, "generator"
                )
                return result
            self._expect_delimiter(")")
            return expr

        # List literal
        if self._match_delimiter("["):
            return self._parse_list_literal()

        # Dict / set literal
        if self._match_delimiter("{"):
            return self._parse_brace_literal()

        self._error("EXPECTED_EXPRESSION", tok, token=tok.value)

    def _parse_fstring(self, tok):
        """Parse an f-string by extracting {expr} segments from the raw text."""
        raw = tok.value
        parts = []
        i = 0
        current_text = ""
        while i < len(raw):
            ch = raw[i]
            if ch == "{":
                if i + 1 < len(raw) and raw[i + 1] == "{":
                    # Escaped {{ → literal {
                    current_text += "{"
                    i += 2
                    continue
                # Start of expression — save current text
                if current_text:
                    parts.append(current_text)
                    current_text = ""
                # Find matching closing }
                depth = 1
                i += 1
                expr_text = ""
                while i < len(raw) and depth > 0:
                    if raw[i] == "{":
                        depth += 1
                    elif raw[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    expr_text += raw[i]
                    i += 1
                i += 1  # skip closing }
                # Parse the expression text
                sub_lexer = Lexer(expr_text, language=self.source_language)
                sub_tokens = sub_lexer.tokenize()
                sub_parser = Parser(sub_tokens, self.source_language)
                expr_node = sub_parser.parse_expression_fragment()
                parts.append(expr_node)
            elif ch == "}" and i + 1 < len(raw) and raw[i + 1] == "}":
                # Escaped }} → literal }
                current_text += "}"
                i += 2
            else:
                current_text += ch
                i += 1
        if current_text:
            parts.append(current_text)
        return FStringLiteral(parts, line=tok.line, column=tok.column)

    def _parse_lambda(self):
        """Parse: LAMBDA params : expression."""
        tok = self._advance()  # consume LAMBDA
        params = []
        if not self._match_delimiter(":"):
            param = self._expect_identifier()
            params.append(param.value)
            while self._match_delimiter(","):
                self._advance()
                param = self._expect_identifier()
                params.append(param.value)

        self._expect_delimiter(":")
        body = self._parse_expression()
        return LambdaExpr(params, body, line=tok.line, column=tok.column)

    def _parse_yield_expr(self):
        """Parse: YIELD [expression]."""
        tok = self._advance()  # consume YIELD
        value = None
        if not self._at_end() and not self._match_type(TokenType.NEWLINE) \
                and not self._match_type(TokenType.DEDENT) \
                and not self._match_delimiter(")") \
                and not self._match_delimiter(","):
            value = self._parse_expression()
        return YieldExpr(value, line=tok.line, column=tok.column)

    def _parse_list_literal(self):
        """Parse: [ expr, expr, ... ] or [expr for target in iter [if cond]]."""
        tok = self._advance()  # consume [
        if self._match_delimiter("]"):
            self._advance()  # consume ]
            return ListLiteral([], line=tok.line, column=tok.column)

        first = self._parse_expression()

        # Check for list comprehension: [expr FOR ...]
        if self._match_concept("LOOP_FOR"):
            return self._parse_comprehension_tail(
                first, tok, "list"
            )

        elements = [first]
        while self._match_delimiter(","):
            self._advance()
            if self._match_delimiter("]"):
                break
            elements.append(self._parse_expression())
        self._expect_delimiter("]")
        return ListLiteral(elements, line=tok.line, column=tok.column)

    def _parse_brace_literal(self):
        """Parse dict or set literal, including dict unpacking."""
        tok = self._advance()  # consume {
        if self._match_delimiter("}"):
            self._advance()  # consume }
            return DictLiteral([], line=tok.line, column=tok.column)

        # Dict unpack at start
        if self._match_operator("**"):
            entries = [self._parse_dict_unpack_entry()]
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter("}"):
                    break
                if self._match_operator("**"):
                    entries.append(self._parse_dict_unpack_entry())
                else:
                    key = self._parse_expression()
                    self._expect_delimiter(":")
                    value = self._parse_expression()
                    entries.append((key, value))
            self._expect_delimiter("}")
            return DictLiteral(entries, line=tok.line, column=tok.column)

        first = self._parse_expression()

        # Dict literal/comprehension
        if self._match_delimiter(":"):
            self._advance()
            value = self._parse_expression()

            # Check for dict comprehension: {k: v FOR ...}
            if self._match_concept("LOOP_FOR"):
                return self._parse_dict_comprehension_tail(
                    first, value, tok
                )

            entries = [(first, value)]
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter("}"):
                    break
                if self._match_operator("**"):
                    entries.append(self._parse_dict_unpack_entry())
                    continue
                key = self._parse_expression()
                self._expect_delimiter(":")
                value = self._parse_expression()
                entries.append((key, value))
            self._expect_delimiter("}")
            return DictLiteral(entries, line=tok.line, column=tok.column)

        # Set literal
        elements = [first]
        while self._match_delimiter(","):
            self._advance()
            if self._match_delimiter("}"):
                break
            elements.append(self._parse_expression())
        self._expect_delimiter("}")
        return SetLiteral(elements, line=tok.line, column=tok.column)

    def _parse_dict_unpack_entry(self):
        """Parse a dict unpack element: **expr."""
        tok = self._advance()  # consume **
        value = self._parse_expression()
        return DictUnpackEntry(value, line=tok.line, column=tok.column)

    def _parse_comp_target(self):
        """Parse a comprehension target: single identifier or tuple (a, b)."""
        first_tok = self._expect_identifier()
        target = Identifier(first_tok.value,
                            line=first_tok.line, column=first_tok.column)
        if self._match_delimiter(","):
            elements = [target]
            while self._match_delimiter(","):
                self._advance()
                next_tok = self._expect_identifier()
                elements.append(Identifier(
                    next_tok.value,
                    line=next_tok.line, column=next_tok.column
                ))
            target = TupleLiteral(elements,
                                  line=first_tok.line, column=first_tok.column)
        return target

    def _parse_comprehension_tail(self, element, tok, kind):
        """Parse: FOR target IN iterable [IF cond]... and close bracket.

        `element` is the already-parsed element expression.
        `kind` is 'list' or 'generator'.
        Uses _parse_or_expression for iterable/conditions to avoid
        consuming the comprehension 'if' as a ternary operator.
        """
        self._advance()  # consume FOR keyword
        target = self._parse_comp_target()
        self._expect_concept("IN")
        iterable = self._parse_or_expression()

        conditions = []
        while self._match_concept("COND_IF"):
            self._advance()
            conditions.append(self._parse_or_expression())

        if kind == "list":
            self._expect_delimiter("]")
            return ListComprehension(
                element, target, iterable, conditions,
                line=tok.line, column=tok.column
            )
        # generator
        self._expect_delimiter(")")
        return GeneratorExpr(
            element, target, iterable, conditions,
            line=tok.line, column=tok.column
        )

    def _parse_dict_comprehension_tail(self, key, value, tok):
        """Parse: FOR target IN iterable [IF cond]... }."""
        self._advance()  # consume FOR keyword
        target = self._parse_comp_target()
        self._expect_concept("IN")
        iterable = self._parse_or_expression()

        conditions = []
        while self._match_concept("COND_IF"):
            self._advance()
            conditions.append(self._parse_or_expression())

        self._expect_delimiter("}")
        return DictComprehension(
            key, value, target, iterable, conditions,
            line=tok.line, column=tok.column
        )
