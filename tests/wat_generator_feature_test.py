#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Additional WAT generator regression tests split from wat_generator_test."""
# pylint: disable=duplicate-code
# pylint: disable=mixed-line-endings

import unittest

from multilingualprogramming.parser.ast_nodes import (
    NumeralLiteral,
    StringLiteral,
    BooleanLiteral,
    NoneLiteral,
    Identifier,
    BinaryOp,
    CallExpr,
    AttributeAccess,
    VariableDeclaration,
    Assignment,
    ExpressionStatement,
    PassStatement,
    ReturnStatement,
    WithStatement,
    Parameter,
    MatchStatement,
    CaseClause,
    ListLiteral,
    TupleLiteral,
    DictComprehension,
    SetLiteral,
    SetComprehension,
    ComprehensionClause,
    IndexAccess,
    AwaitExpr,
    ListComprehension,
    GeneratorExpr,
    FunctionDef,
    ForLoop,
    Program,
)
from multilingualprogramming.codegen.wat_generator import WATCodeGenerator


def _prog(*stmts):
    """Wrap statements into a Program node."""
    return Program(list(stmts))


def _gen(*stmts):
    """Generate WAT for the given top-level statements."""
    return WATCodeGenerator().generate(_prog(*stmts))


def _param(name: str) -> Parameter:
    """Create a Parameter with an Identifier name."""
    return Parameter(Identifier(name))

class WATMatchCaseTestSuite(unittest.TestCase):
    """WAT lowering for match/case statements."""

    def test_match_numeric_case_generates_block(self):
        """match with numeric literal cases produces block + f64.eq + if."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(NumeralLiteral("1"), [PassStatement()], is_default=False),
                CaseClause(NumeralLiteral("2"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("block $", wat)
        self.assertIn("f64.eq", wat)
        self.assertIn("if", wat)
        self.assertIn("br $", wat)

    def test_match_default_case_emits_body(self):
        """A default case emits its body without a condition check."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(None, [PassStatement()], is_default=True),
            ],
        )
        wat = _gen(stmt)
        self.assertIn(";; case _: (default)", wat)
        self.assertIn("br $", wat)

    def test_match_boolean_case(self):
        """Boolean literal case emits f64.const 1.0 / 0.0 + f64.eq."""
        stmt = MatchStatement(
            subject=Identifier("flag"),
            cases=[
                CaseClause(BooleanLiteral(True), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 1.0", wat)
        self.assertIn("f64.eq", wat)

    def test_match_string_case_lowers_to_f64_eq(self):
        """String pattern is lowered via interned offset comparison (f64.eq)."""
        stmt = MatchStatement(
            subject=Identifier("s"),
            cases=[
                CaseClause(
                    StringLiteral("hello"), [PassStatement()], is_default=False
                ),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("f64.eq", wat)
        self.assertIn("f64.const", wat)
        self.assertNotIn("string patterns not comparable", wat)
        self.assertNotIn("unsupported call: string_pattern_match", wat)

    def test_match_string_case_same_string_matches(self):
        """Two identical string literals intern to the same offset, so the match fires."""
        # Declare s = "world", then match s: case "world": x = 1; case "other": x = 2
        prog = _gen(
            VariableDeclaration(Identifier("s"), StringLiteral("world")),
            MatchStatement(
                subject=Identifier("s"),
                cases=[
                    CaseClause(StringLiteral("world"), [
                        VariableDeclaration(Identifier("x"), NumeralLiteral("1")),
                    ], is_default=False),
                    CaseClause(StringLiteral("other"), [
                        VariableDeclaration(Identifier("x"), NumeralLiteral("2")),
                    ], is_default=False),
                ],
            ),
        )
        # Both patterns lower to f64.eq comparisons against interned offsets.
        self.assertIn("f64.eq", prog)
        self.assertNotIn("unsupported call:", prog)


class WATAugmentedAssignTestSuite(unittest.TestCase):
    """WAT lowering for augmented assignment operators."""

    def _gen_aug(self, op: str) -> str:
        """Generate WAT for ``x = 0; x op= 3``."""
        return _gen(
            VariableDeclaration(Identifier("x"), NumeralLiteral("0")),
            Assignment(Identifier("x"), NumeralLiteral("3"), op=op),
        )

    def test_add_assign(self):
        self.assertIn("f64.add", self._gen_aug("+="))

    def test_sub_assign(self):
        self.assertIn("f64.sub", self._gen_aug("-="))

    def test_mul_assign(self):
        self.assertIn("f64.mul", self._gen_aug("*="))

    def test_div_assign(self):
        self.assertIn("f64.div", self._gen_aug("/="))

    def test_floor_div_assign(self):
        wat = self._gen_aug("//=")
        self.assertIn("f64.div", wat)
        self.assertIn("f64.floor", wat)

    def test_mod_assign(self):
        wat = self._gen_aug("%=")
        self.assertIn("f64.div", wat)
        self.assertIn("f64.floor", wat)
        self.assertIn("f64.neg", wat)
        self.assertIn("f64.add", wat)

    def test_power_assign(self):
        wat = self._gen_aug("**=")
        self.assertIn("call $pow_f64", wat)
        self.assertNotIn("not natively supported", wat)

    def test_bitwise_and_assign(self):
        wat = self._gen_aug("&=")
        self.assertIn("i32.trunc_f64_s", wat)
        self.assertIn("i32.and", wat)
        self.assertIn("f64.convert_i32_s", wat)

    def test_bitwise_or_assign(self):
        wat = self._gen_aug("|=")
        self.assertIn("i32.or", wat)

    def test_bitwise_xor_assign(self):
        wat = self._gen_aug("^=")
        self.assertIn("i32.xor", wat)

    def test_shl_assign(self):
        wat = self._gen_aug("<<=")
        self.assertIn("i32.shl", wat)

    def test_shr_assign(self):
        wat = self._gen_aug(">>=")
        self.assertIn("i32.shr_s", wat)


class WATStringLenTestSuite(unittest.TestCase):
    """WAT len() lowering for string literals and string variables."""

    def test_len_of_string_literal(self):
        """len("hello") → f64.const 5.0 (byte length)."""
        stmt = ExpressionStatement(
            CallExpr(Identifier("len"), [StringLiteral("hello")])
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 5.0", wat)

    def test_len_of_string_variable(self):
        """let s = "hi"; len(s) → local.get of the strlen local."""
        stmts = [
            VariableDeclaration(Identifier("s"), StringLiteral("hi")),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("s")])),
        ]
        wat = _gen(*stmts)
        # strlen local must be declared and used
        self.assertIn("s_strlen", wat)
        self.assertIn("f64.const 2.0", wat)  # "hi" = 2 bytes

    def test_len_string_reassign(self):
        """Re-assigning a string variable updates the strlen local."""
        stmts = [
            VariableDeclaration(Identifier("t"), StringLiteral("abc")),
            Assignment(Identifier("t"), StringLiteral("wxyz"), op="="),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("t")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.const 4.0", wat)  # "wxyz" = 4 bytes

    def test_len_localized_fr(self):
        """longueur() is recognized as len() in WAT."""
        stmt = ExpressionStatement(
            CallExpr(Identifier("longueur"), [StringLiteral("bonjour")])
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 7.0", wat)


class WATListSupportTestSuite(unittest.TestCase):
    """WAT lowering for list literals, indexing, and len()."""

    def test_list_alloc_emits_heap_global(self):
        """A list literal triggers emission of $__heap_ptr."""
        stmt = VariableDeclaration(Identifier("a"), ListLiteral([NumeralLiteral("1")]))
        wat = _gen(stmt)
        self.assertIn("$__heap_ptr", wat)

    def test_list_alloc_stores_length_header(self):
        """[1, 2, 3] stores f64.const 3.0 as the length header."""
        stmt = VariableDeclaration(
            Identifier("a"),
            ListLiteral([NumeralLiteral("1"), NumeralLiteral("2"), NumeralLiteral("3")]),
        )
        wat = _gen(stmt)
        self.assertIn("f64.const 3.0", wat)
        self.assertIn("f64.store", wat)

    def test_list_len(self):
        """len(a) for a list variable emits f64.load at offset 0."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20")]),
            ),
            ExpressionStatement(CallExpr(Identifier("len"), [Identifier("a")])),
        ]
        wat = _gen(*stmts)
        self.assertIn("f64.load", wat)
        self.assertIn(";; list length from header", wat)

    def test_list_index_access(self):
        """a[1] for a list variable emits the correct offset arithmetic."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20")]),
            ),
            ExpressionStatement(
                IndexAccess(Identifier("a"), NumeralLiteral("1"))
            ),
        ]
        wat = _gen(*stmts)
        # Offset arithmetic: i32.const 8 * index (element 1 → offset 8 from data start)
        self.assertIn("i32.const 8", wat)
        self.assertIn("i32.mul", wat)
        self.assertIn("f64.load", wat)

    def test_tuple_alloc(self):
        """Tuple literal (1, 2) is allocated like a list."""
        stmt = VariableDeclaration(
            Identifier("t"),
            TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
        )
        wat = _gen(stmt)
        self.assertIn("$__heap_ptr", wat)
        self.assertIn("f64.const 2.0", wat)


class WATAsyncAwaitTestSuite(unittest.TestCase):
    """WAT lowering for async/await — best-effort synchronous evaluation."""

    def test_await_expr_evaluates_operand(self):
        """await f() in WAT is lowered by simply evaluating f() (no async stub)."""
        func = FunctionDef(
            Identifier("work"),
            params=[],
            body=[ReturnStatement(NumeralLiteral("42"))],
        )
        stmt = ExpressionStatement(
            AwaitExpr(CallExpr(Identifier("work"), []))
        )
        wat = _gen(func, stmt)
        # The call to $work must appear; no "unsupported expr: AwaitExpr" stub.
        self.assertIn("call $work", wat)
        self.assertNotIn("unsupported expr: AwaitExpr", wat)

    def test_await_asyncio_sleep_is_noop(self):
        stmt = ExpressionStatement(
            AwaitExpr(
                CallExpr(AttributeAccess(Identifier("asyncio"), "sleep"), [NumeralLiteral("0")])
            )
        )
        wat = _gen(stmt)
        self.assertIn("asyncio.sleep no-op in WAT", wat)
        self.assertNotIn("unsupported call: asyncio.sleep(...)", wat)

    def test_asyncio_run_evaluates_inner_call(self):
        func = FunctionDef(
            Identifier("work"),
            params=[_param("x")],
            body=[ReturnStatement(Identifier("x"))],
        )
        stmt = VariableDeclaration(
            "result",
            CallExpr(
                AttributeAccess(Identifier("asyncio"), "run"),
                [CallExpr(Identifier("work"), [NumeralLiteral("5")])],
            ),
        )
        wat = _gen(func, stmt)
        self.assertIn("call $work", wat)
        self.assertNotIn("unsupported call: asyncio.run(...)", wat)

    def test_async_def_lowers_as_regular_function(self):
        """async def f() is emitted as a normal WAT function."""
        func = FunctionDef(
            Identifier("f"),
            params=[],
            body=[ReturnStatement(NumeralLiteral("1"))],
            is_async=True,
        )
        wat = _gen(func)
        self.assertIn('(func $f', wat)
        self.assertIn('(export "f")', wat)


class WATWithOpenTestSuite(unittest.TestCase):
    """Best-effort WAT lowering for simple with-open file operations."""

    def test_with_open_write_is_tracked_as_virtual_file(self):
        wat = _gen(
            WithStatement(
                items=[(
                    CallExpr(
                        Identifier("open"),
                        [StringLiteral("tmp.txt"), StringLiteral("w")],
                    ),
                    "handle_w",
                )],
                body=[
                    ExpressionStatement(
                        CallExpr(
                            AttributeAccess(Identifier("handle_w"), "write"),
                            [StringLiteral("ok")],
                        )
                    )
                ],
            )
        )
        self.assertIn("virtual file write 'tmp.txt'", wat)
        self.assertNotIn("unsupported call: handle_w.write(...)", wat)

    def test_with_open_read_materializes_string_value(self):
        wat = _gen(
            WithStatement(
                items=[(
                    CallExpr(
                        Identifier("open"),
                        [StringLiteral("tmp.txt"), StringLiteral("w")],
                    ),
                    "handle_w",
                )],
                body=[
                    ExpressionStatement(
                        CallExpr(
                            AttributeAccess(Identifier("handle_w"), "write"),
                            [StringLiteral("ok")],
                        )
                    )
                ],
            ),
            VariableDeclaration("file_text", StringLiteral("")),
            WithStatement(
                items=[(
                    CallExpr(
                        Identifier("open"),
                        [StringLiteral("tmp.txt"), StringLiteral("r")],
                    ),
                    "handle_r",
                )],
                body=[
                    Assignment(
                        Identifier("file_text"),
                        CallExpr(AttributeAccess(Identifier("handle_r"), "read"), []),
                    )
                ],
            ),
            ExpressionStatement(CallExpr(Identifier("print"), [Identifier("file_text")])),
        )
        self.assertIn("virtual file write 'tmp.txt'", wat)
        self.assertIn("file_text_strlen", wat)
        self.assertNotIn("unsupported call: handle_r.read(...)", wat)


class WATForListTestSuite(unittest.TestCase):
    """WAT lowering for for-loops over list/tuple variables."""

    def test_for_loop_over_list_var_emits_index_loop(self):
        """for x in a (list var) → index-based loop using list header."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("10"), NumeralLiteral("20"), NumeralLiteral("30")]),
            ),
            ForLoop(
                target=Identifier("x"),
                iterable=Identifier("a"),
                body=[ExpressionStatement(Identifier("x"))],
            ),
        ]
        wat = _gen(*stmts)
        # Should emit list-iteration pattern: load length, index loop, f64.load element.
        self.assertIn("i32.const 8", wat)   # element stride
        self.assertIn("i32.mul", wat)
        self.assertIn("f64.load", wat)
        self.assertIn("f64.ge", wat)        # exit condition (idx >= len)
        self.assertNotIn("not supported in WAT", wat)

    def test_for_loop_over_non_tracked_var_emits_comment(self):
        """for x in unknown_var → unsupported comment (not a tracked list)."""
        stmt = ForLoop(
            target=Identifier("x"),
            iterable=Identifier("unknown"),
            body=[PassStatement()],
        )
        wat = _gen(stmt)
        self.assertIn("not supported in WAT", wat)

    def test_async_for_over_list_var_works(self):
        """async for x in a (list var) is lowered identically to sync for."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
            ),
            ForLoop(
                target=Identifier("x"),
                iterable=Identifier("a"),
                body=[PassStatement()],
                is_async=True,
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("i32.mul", wat)
        self.assertNotIn("not supported in WAT", wat)


class WATListComprehensionTestSuite(unittest.TestCase):
    """WAT lowering for comprehensions over list variables."""

    def test_listcomp_over_list_var(self):
        """[x for x in a] over a list variable lowers to an index-based loop."""
        stmts = [
            VariableDeclaration(
                Identifier("a"),
                ListLiteral([NumeralLiteral("1"), NumeralLiteral("2"), NumeralLiteral("3")]),
            ),
            ExpressionStatement(
                ListComprehension(
                    element=Identifier("x"),
                    target=Identifier("x"),
                    iterable=Identifier("a"),
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_list_blk_", wat)
        self.assertIn("f64.load", wat)
        self.assertIn("i32.mul", wat)
        self.assertNotIn("collections not representable as f64", wat)

    def test_listcomp_over_range_materializes_list_storage(self):
        stmts = [
            ExpressionStatement(
                ListComprehension(
                    element=Identifier("x"),
                    target=Identifier("x"),
                    iterable=CallExpr(Identifier("range"), [NumeralLiteral("3")]),
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_list_blk_", wat)
        self.assertIn("global.set $__heap_ptr", wat)
        self.assertNotIn("collections not representable as f64", wat)

    def test_list_builtin_over_generator_expr_over_range_materializes_list(self):
        stmts = [
            VariableDeclaration(
                "values",
                CallExpr(
                    Identifier("list"),
                    [GeneratorExpr(
                        element=Identifier("x"),
                        target=Identifier("x"),
                        iterable=CallExpr(Identifier("range"), [NumeralLiteral("3")]),
                    )],
                ),
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_list_blk_", wat)
        self.assertIn("global.set $__heap_ptr", wat)
        self.assertNotIn("unsupported call: list(...)", wat)

    def test_setcomp_over_range_materializes_sequence_storage(self):
        stmts = [
            ExpressionStatement(
                SetLiteral([NumeralLiteral("0")])
            ),
            ExpressionStatement(
                SetComprehension(
                    element=Identifier("x"),
                    target=Identifier("x"),
                    iterable=CallExpr(Identifier("range"), [NumeralLiteral("4")]),
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_list_blk_", wat)
        self.assertNotIn("collections not representable as f64", wat)

    def test_filtered_listcomp_over_range_materializes_storage(self):
        stmts = [
            ExpressionStatement(
                ListComprehension(
                    element=Identifier("x"),
                    target=Identifier("x"),
                    iterable=CallExpr(Identifier("range"), [NumeralLiteral("6")]),
                    conditions=[
                        BinaryOp(
                            BinaryOp(Identifier("x"), "%", NumeralLiteral("2")),
                            "==",
                            NumeralLiteral("0"),
                        )
                    ],
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_filter_blk_", wat)
        self.assertIn("local.set $__comp_write_", wat)
        self.assertNotIn("collections not representable as f64", wat)

    def test_nested_listcomp_over_ranges_materializes_storage(self):
        stmts = [
            ExpressionStatement(
                ListComprehension(
                    element=BinaryOp(Identifier("i"), "+", Identifier("j")),
                    target=Identifier("i"),
                    iterable=CallExpr(Identifier("range"), [NumeralLiteral("2")]),
                    clauses=[
                        ComprehensionClause(
                            Identifier("i"),
                            CallExpr(Identifier("range"), [NumeralLiteral("2")]),
                        ),
                        ComprehensionClause(
                            Identifier("j"),
                            CallExpr(Identifier("range"), [NumeralLiteral("2")]),
                        ),
                    ],
                )
            ),
        ]
        wat = _gen(*stmts)
        self.assertIn("comp_outer_blk_", wat)
        self.assertIn("comp_inner_blk_", wat)
        self.assertNotIn("collections not representable as f64", wat)

    def test_dictcomp_over_range_materializes_dict_storage(self):
        stmts = [
            VariableDeclaration(
                "values",
                DictComprehension(
                    key=CallExpr(Identifier("str"), [Identifier("k")]),
                    value=BinaryOp(Identifier("k"), "*", Identifier("k")),
                    target=Identifier("k"),
                    iterable=CallExpr(Identifier("range"), [NumeralLiteral("3")]),
                ),
            ),
            ExpressionStatement(IndexAccess(Identifier("values"), StringLiteral("2"))),
        ]
        wat = _gen(*stmts)
        self.assertIn("dict_comp_blk_", wat)
        self.assertNotIn("unsupported expr DictComprehension", wat)
        self.assertNotIn("unsupported index access", wat)


class WATMatchCaseExtendedTestSuite(unittest.TestCase):
    """WAT lowering for additional match/case pattern types."""

    def test_match_none_pattern(self):
        """case None: lowers to f64.eq with f64.const 0."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(NoneLiteral(), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("case None:", wat)
        self.assertIn("f64.const 0", wat)
        self.assertIn("f64.eq", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_match_identifier_capture(self):
        """case y: (capture variable) binds subject value to y and always matches."""
        stmt = MatchStatement(
            subject=Identifier("x"),
            cases=[
                CaseClause(Identifier("y"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("capture variable", wat)
        self.assertIn("local.set", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_match_mixed_patterns(self):
        """Numeric, string, None, and capture cases all lower without stubs."""
        stmt = MatchStatement(
            subject=Identifier("v"),
            cases=[
                CaseClause(NumeralLiteral("1"), [PassStatement()], is_default=False),
                CaseClause(StringLiteral("ok"), [PassStatement()], is_default=False),
                CaseClause(NoneLiteral(), [PassStatement()], is_default=False),
                CaseClause(Identifier("other"), [PassStatement()], is_default=False),
            ],
        )
        wat = _gen(stmt)
        self.assertNotIn("complex pattern not lowerable", wat)
        self.assertNotIn("unsupported call: string_pattern_match", wat)


class WATTupleMatchPatternTestSuite(unittest.TestCase):
    """WAT match/case lowering for tuple/list literal patterns."""

    def test_tuple_pattern_emits_length_and_element_checks(self):
        """case (1, 2): checks length == 2 AND elem[0] == 1.0 AND elem[1] == 2.0."""
        stmts = [
            VariableDeclaration(
                Identifier("t"),
                TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
            ),
            MatchStatement(
                subject=Identifier("t"),
                cases=[
                    CaseClause(
                        TupleLiteral([NumeralLiteral("1"), NumeralLiteral("2")]),
                        [PassStatement()],
                        is_default=False,
                    ),
                ],
            ),
        ]
        wat = _gen(*stmts)
        # Length check: f64.const 2.0 from the pattern tuple
        self.assertIn("f64.const 2.0", wat)
        # Element-wise: each element comparison uses f64.eq + i32.and
        self.assertGreaterEqual(wat.count("f64.eq"), 3)  # len + 2 elements
        self.assertIn("i32.and", wat)
        self.assertNotIn("complex pattern not lowerable", wat)

    def test_tuple_pattern_requires_list_subject(self):
        """Tuple pattern against a non-list subject falls back to stub."""
        stmt = MatchStatement(
            subject=Identifier("x"),   # x is not a list local
            cases=[
                CaseClause(
                    TupleLiteral([NumeralLiteral("1")]),
                    [PassStatement()],
                    is_default=False,
                ),
            ],
        )
        wat = _gen(stmt)
        self.assertIn("complex pattern not lowerable", wat)


class WATDOMBridgeTestSuite(unittest.TestCase):
    """Verify DOM host imports and WAT wrappers are emitted correctly."""

    def setUp(self):
        self.gen = WATCodeGenerator()

    def _gen(self, *stmts):
        return self.gen.generate(Program(list(stmts)))

    def test_dom_get_emits_env_import(self):
        wat = self._gen(
            VariableDeclaration(
                "el",
                CallExpr(Identifier("dom_get"), [StringLiteral("myDiv")]),
            )
        )
        self.assertIn('(import "env" "ml_dom_get"', wat)
        self.assertIn("call $dom_get", wat)

    def test_dom_text_emits_set_text_import(self):
        wat = self._gen(
            VariableDeclaration("el", CallExpr(Identifier("dom_get"), [StringLiteral("x")])),
            ExpressionStatement(
                CallExpr(Identifier("dom_text"), [Identifier("el"), StringLiteral("Hello")])
            ),
        )
        self.assertIn('(import "env" "ml_dom_set_text"', wat)
        self.assertIn("call $dom_text", wat)

    def test_dom_html_emits_set_html_import(self):
        wat = self._gen(
            VariableDeclaration("el", CallExpr(Identifier("dom_get"), [StringLiteral("x")])),
            ExpressionStatement(
                CallExpr(Identifier("dom_html"), [Identifier("el"), StringLiteral("<b>hi</b>")])
            ),
        )
        self.assertIn('(import "env" "ml_dom_set_html"', wat)

    def test_dom_create_and_append(self):
        wat = self._gen(
            VariableDeclaration(
                "parent",
                CallExpr(Identifier("dom_get"), [StringLiteral("root")]),
            ),
            VariableDeclaration(
                "child",
                CallExpr(Identifier("dom_create"), [StringLiteral("div")]),
            ),
            ExpressionStatement(
                CallExpr(Identifier("dom_append"), [Identifier("parent"), Identifier("child")])
            ),
        )
        self.assertIn('(import "env" "ml_dom_create"', wat)
        self.assertIn('(import "env" "ml_dom_append"', wat)

    def test_dom_style_and_attr(self):
        wat = self._gen(
            VariableDeclaration("el", CallExpr(Identifier("dom_get"), [StringLiteral("box")])),
            ExpressionStatement(
                CallExpr(
                    Identifier("dom_style"),
                    [Identifier("el"), StringLiteral("color"), StringLiteral("red")],
                )
            ),
            ExpressionStatement(
                CallExpr(
                    Identifier("dom_attr"),
                    [Identifier("el"), StringLiteral("class"), StringLiteral("active")],
                )
            ),
        )
        self.assertIn('(import "env" "ml_dom_style"', wat)
        self.assertIn('(import "env" "ml_dom_set_attr"', wat)

    def test_dom_wrappers_emitted_in_module(self):
        wat = self._gen(
            VariableDeclaration("el", CallExpr(Identifier("dom_get"), [StringLiteral("x")])),
        )
        self.assertIn("(func $dom_get", wat)

    def test_no_dom_imports_when_unused(self):
        wat = self._gen(
            ExpressionStatement(CallExpr(Identifier("print"), [NumeralLiteral("1")])),
        )
        self.assertNotIn('(import "env"', wat)




if __name__ == "__main__":
    unittest.main()
