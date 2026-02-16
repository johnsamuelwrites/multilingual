#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Recursive-descent parser for the multilingual programming language."""

from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.parser.ast_nodes import (
    Program, NumeralLiteral, StringLiteral, DateLiteral,
    BooleanLiteral, NoneLiteral, ListLiteral, DictLiteral,
    Identifier, BinaryOp, UnaryOp, BooleanOp, CompareOp,
    CallExpr, AttributeAccess, IndexAccess,
    LambdaExpr, YieldExpr,
    VariableDeclaration, Assignment, ExpressionStatement,
    PassStatement, ReturnStatement, BreakStatement, ContinueStatement,
    RaiseStatement, GlobalStatement, LocalStatement, YieldStatement,
    IfStatement, WhileLoop, ForLoop, FunctionDef, ClassDef,
    TryStatement, ExceptHandler, MatchStatement, CaseClause,
    WithStatement, ImportStatement, FromImportStatement,
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
    "GLOBAL", "LOCAL", "IMPORT", "FROM",
}

# Concepts treated as identifiers when appearing in expressions
_CALLABLE_CONCEPTS = {"PRINT", "INPUT"}
_TYPE_CONCEPTS = {
    "TYPE_INT", "TYPE_FLOAT", "TYPE_STR",
    "TYPE_BOOL", "TYPE_LIST", "TYPE_DICT",
}

# Augmented assignment operators
_AUGMENTED_OPS = {"+=", "-=", "*=", "/="}

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

    def _error(self, message_key, err_token, **kwargs):
        """Raise a ParseError with a multilingual message."""
        kwargs.setdefault("line", err_token.line)
        kwargs.setdefault("column", err_token.column)
        msg = self._error_registry.format(
            message_key, self.source_language, **kwargs
        )
        raise ParseError(msg, err_token.line, err_token.column)

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

        if tok.type == TokenType.KEYWORD and tok.concept:
            concept = tok.concept
            if concept in _COMPOUND_CONCEPTS:
                return self._parse_compound_statement(concept)
            if concept in _SIMPLE_CONCEPTS:
                return self._parse_simple_statement(concept)

        return self._parse_assignment_or_expression()

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

        # Check for assignment operators
        tok = self._current()
        if tok.type == TokenType.OPERATOR and tok.value == "=":
            self._advance()
            value = self._parse_expression()
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
        """Parse: FOR target IN iterable : block."""
        tok = self._advance()  # consume FOR
        target_tok = self._expect_identifier()
        target = Identifier(
            target_tok.value,
            line=target_tok.line, column=target_tok.column
        )
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

    def _parse_function_def(self):
        """Parse: FUNC_DEF name ( params ) : block."""
        tok = self._advance()  # consume FUNC_DEF
        name_tok = self._expect_identifier()
        self._expect_delimiter("(")

        params = []
        if not self._match_delimiter(")"):
            param = self._expect_identifier()
            params.append(param.value)
            while self._match_delimiter(","):
                self._advance()
                param = self._expect_identifier()
                params.append(param.value)

        self._expect_delimiter(")")
        body = self._parse_block()
        return FunctionDef(
            name_tok.value, params, body,
            line=tok.line, column=tok.column
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
        """Parse: WITH expression [AS name] : block."""
        tok = self._advance()  # consume WITH
        context_expr = self._parse_expression()

        name = None
        if self._match_concept("AS"):
            self._advance()
            name_tok = self._expect_identifier()
            name = name_tok.value

        body = self._parse_block()
        return WithStatement(
            context_expr, name, body,
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
        return self._parse_or_expression()

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
        """Parse: bitwise_or (comp_op bitwise_or)*  (chained)."""
        left = self._parse_bitwise_or()
        comparators = []
        while self._current().type == TokenType.OPERATOR \
                and self._current().value in _COMPARISON_OPS:
            op = self._advance().value
            right = self._parse_bitwise_or()
            comparators.append((op, right))
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
        """Parse: (- | + | ~) unary | power."""
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
                index = self._parse_expression()
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

    def _parse_call(self, func):
        """Parse function call arguments: (expr, expr, name=expr, ...)."""
        tok = self._advance()  # consume (
        args = []
        keywords = []

        if not self._match_delimiter(")"):
            self._parse_argument(args, keywords)
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter(")"):
                    break
                self._parse_argument(args, keywords)

        self._expect_delimiter(")")
        return CallExpr(func, args, keywords,
                        line=tok.line, column=tok.column)

    def _parse_argument(self, args, keywords):
        """Parse a single argument (positional or keyword)."""
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

        # Parenthesized expression
        if self._match_delimiter("("):
            self._advance()
            expr = self._parse_expression()
            self._expect_delimiter(")")
            return expr

        # List literal
        if self._match_delimiter("["):
            return self._parse_list_literal()

        # Dict literal
        if self._match_delimiter("{"):
            return self._parse_dict_literal()

        self._error("EXPECTED_EXPRESSION", tok, token=tok.value)

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
        """Parse: [ expr, expr, ... ]."""
        tok = self._advance()  # consume [
        elements = []
        if not self._match_delimiter("]"):
            elements.append(self._parse_expression())
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter("]"):
                    break
                elements.append(self._parse_expression())
        self._expect_delimiter("]")
        return ListLiteral(elements, line=tok.line, column=tok.column)

    def _parse_dict_literal(self):
        """Parse: { key: value, key: value, ... }."""
        tok = self._advance()  # consume {
        pairs = []
        if not self._match_delimiter("}"):
            key = self._parse_expression()
            self._expect_delimiter(":")
            value = self._parse_expression()
            pairs.append((key, value))
            while self._match_delimiter(","):
                self._advance()
                if self._match_delimiter("}"):
                    break
                key = self._parse_expression()
                self._expect_delimiter(":")
                value = self._parse_expression()
                pairs.append((key, value))
        self._expect_delimiter("}")
        return DictLiteral(pairs, line=tok.line, column=tok.column)
