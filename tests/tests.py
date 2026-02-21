#
# SPDX-FileCopyrightText: 2022 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Main file to run all the test suites
"""

import unittest

from tests.mp_numeral_test import MPNumeralTestSuite
from tests.roman_numerals_test import RomanNumeralTestSuite
from tests.unicode_numerals_test import UnicodeNumeralTestSuite
from tests.unicode_string_test import UnicodeStringTestSuite
from tests.keyword_registry_test import (
    KeywordRegistryTestSuite,
    KeywordRegistryErrorTestSuite,
    KeywordValidatorTestSuite,
)
from tests.complex_numeral_test import ComplexNumeralTestSuite
from tests.fraction_numeral_test import FractionNumeralTestSuite
from tests.numeral_converter_test import NumeralConverterTestSuite
from tests.mp_datetime_test import (
    MPDateParsingAndFormattingTestSuite,
    MPDateOperationsTestSuite,
    MPTimeTestSuite,
    MPDatetimeTestSuite,
)
from tests.lexer_test import LexerTokenizationTestSuite, LexerBehaviorTestSuite
from tests.ast_nodes_test import ASTNodeConstructionTestSuite
from tests.parser_test import (
    ParserExpressionTestSuite,
    ParserStatementTestSuite,
    ParserCompoundTestSuite,
    ParserMultilingualTestSuite,
    ParserErrorTestSuite,
)
from tests.semantic_analyzer_test import (
    SemanticScopeTestSuite,
    SemanticConstTestSuite,
    SemanticControlFlowTestSuite,
    SemanticDefinitionTestSuite,
    SemanticMultilingualErrorTestSuite,
    SymbolTableTestSuite,
)
from tests.ast_printer_test import ASTPrinterTestSuite
from tests.error_messages_test import ErrorMessageRegistryTestSuite
from tests.python_generator_test import (
    PythonGeneratorExpressionTestSuite,
    PythonGeneratorStatementTestSuite,
    PythonGeneratorCompoundTestSuite,
    PythonGeneratorMultilingualTestSuite,
)
from tests.executor_test import (
    ExecutorBasicTestSuite,
    ExecutorMultilingualTestSuite,
    ExecutorTranspileTestSuite,
    ExecutorErrorTestSuite,
)
from tests.runtime_builtins_test import RuntimeBuiltinsTestSuite
from tests.repl_test import REPLTestSuite, REPLFrenchTestSuite
from tests.critical_features_test import (
    TripleQuotedStringTestSuite,
    SliceSyntaxTestSuite,
    ParameterSystemTestSuite,
    TupleUnpackingTestSuite,
    ComprehensionTestSuite,
    DecoratorTestSuite,
    FStringTestSuite,
    MultilingualCriticalFeaturesTestSuite,
)
from tests.language_completeness_cli_test import (
    AugmentedAssignmentTestSuite,
    MembershipIdentityTestSuite,
    TernaryExpressionTestSuite,
    AssertStatementTestSuite,
    ChainedAssignmentTestSuite,
    CLITestSuite,
    REPLImprovementsTestSuite,
    MultilingualCompletenessCLITestSuite,
)
from tests.advanced_language_features_test import (
    WhileElseTestSuite,
    ForElseTestSuite,
    YieldFromTestSuite,
    RaiseFromTestSuite,
    FromImportStarTestSuite,
    SetComprehensionTestSuite,
    ParameterSeparatorTestSuite,
    FStringFormatTestSuite,
    MatchGuardTestSuite,
    MatchOrPatternTestSuite,
    MatchAsPatternTestSuite,
    GlobalNonlocalSemanticTestSuite,
    AdditionalBuiltinsTestSuite,
    ExceptionTypesTestSuite,
    SpecialValuesTestSuite,
    SurfaceNormalizationTestSuite,
    DataQualityTestSuite,
    AdvancedFeaturesIntegrationTestSuite,
    MultilingualAdvancedFeaturesTestSuite,
    ExtendedBuiltinsTestSuite,
    ExtendedAliasResolutionTestSuite,
    ExtendedAliasExecutionTestSuite,
    StarredUnpackingTestSuite,
)

if __name__ == "__main__":
    mp_numeral_tests = MPNumeralTestSuite()
    roman_numeral_tests = RomanNumeralTestSuite()
    unicode_numeral_tests = UnicodeNumeralTestSuite()
    unicode_string_tests = UnicodeStringTestSuite()
    keyword_registry_tests = KeywordRegistryTestSuite()
    keyword_registry_error_tests = KeywordRegistryErrorTestSuite()
    keyword_validator_tests = KeywordValidatorTestSuite()
    complex_numeral_tests = ComplexNumeralTestSuite()
    fraction_numeral_tests = FractionNumeralTestSuite()
    numeral_converter_tests = NumeralConverterTestSuite()
    mp_date_parsing_and_formatting_tests = MPDateParsingAndFormattingTestSuite()
    mp_date_operation_tests = MPDateOperationsTestSuite()
    mp_time_tests = MPTimeTestSuite()
    mp_datetime_tests = MPDatetimeTestSuite()
    lexer_tokenization_tests = LexerTokenizationTestSuite()
    lexer_behavior_tests = LexerBehaviorTestSuite()
    ast_node_tests = ASTNodeConstructionTestSuite()
    parser_expression_tests = ParserExpressionTestSuite()
    parser_statement_tests = ParserStatementTestSuite()
    parser_compound_tests = ParserCompoundTestSuite()
    parser_multilingual_tests = ParserMultilingualTestSuite()
    parser_error_tests = ParserErrorTestSuite()
    semantic_scope_tests = SemanticScopeTestSuite()
    semantic_const_tests = SemanticConstTestSuite()
    semantic_control_flow_tests = SemanticControlFlowTestSuite()
    semantic_definition_tests = SemanticDefinitionTestSuite()
    semantic_multilingual_error_tests = SemanticMultilingualErrorTestSuite()
    symbol_table_tests = SymbolTableTestSuite()
    ast_printer_tests = ASTPrinterTestSuite()
    error_messages_tests = ErrorMessageRegistryTestSuite()
    python_gen_expr_tests = PythonGeneratorExpressionTestSuite()
    python_gen_stmt_tests = PythonGeneratorStatementTestSuite()
    python_gen_compound_tests = PythonGeneratorCompoundTestSuite()
    python_gen_multilingual_tests = PythonGeneratorMultilingualTestSuite()
    executor_basic_tests = ExecutorBasicTestSuite()
    executor_multilingual_tests = ExecutorMultilingualTestSuite()
    executor_transpile_tests = ExecutorTranspileTestSuite()
    executor_error_tests = ExecutorErrorTestSuite()
    runtime_builtins_tests = RuntimeBuiltinsTestSuite()
    repl_tests = REPLTestSuite()
    repl_french_tests = REPLFrenchTestSuite()
    triple_quote_tests = TripleQuotedStringTestSuite()
    slice_tests = SliceSyntaxTestSuite()
    param_tests = ParameterSystemTestSuite()
    tuple_tests = TupleUnpackingTestSuite()
    comp_tests = ComprehensionTestSuite()
    decorator_tests = DecoratorTestSuite()
    fstring_tests = FStringTestSuite()
    multilingual_critical_tests = MultilingualCriticalFeaturesTestSuite()
    augmented_assign_tests = AugmentedAssignmentTestSuite()
    membership_identity_tests = MembershipIdentityTestSuite()
    ternary_tests = TernaryExpressionTestSuite()
    assert_tests = AssertStatementTestSuite()
    chained_assign_tests = ChainedAssignmentTestSuite()
    cli_tests = CLITestSuite()
    repl_improvements_tests = REPLImprovementsTestSuite()
    multilingual_completeness_cli_tests = MultilingualCompletenessCLITestSuite()
    while_else_tests = WhileElseTestSuite()
    for_else_tests = ForElseTestSuite()
    yield_from_tests = YieldFromTestSuite()
    raise_from_tests = RaiseFromTestSuite()
    from_import_star_tests = FromImportStarTestSuite()
    set_comprehension_tests = SetComprehensionTestSuite()
    parameter_separator_tests = ParameterSeparatorTestSuite()
    fstring_format_tests = FStringFormatTestSuite()
    match_guard_tests = MatchGuardTestSuite()
    match_or_pattern_tests = MatchOrPatternTestSuite()
    match_as_pattern_tests = MatchAsPatternTestSuite()
    global_nonlocal_tests = GlobalNonlocalSemanticTestSuite()
    additional_builtins_tests = AdditionalBuiltinsTestSuite()
    exception_types_tests = ExceptionTypesTestSuite()
    special_values_tests = SpecialValuesTestSuite()
    surface_normalization_tests = SurfaceNormalizationTestSuite()
    data_quality_tests = DataQualityTestSuite()
    advanced_features_integration_tests = AdvancedFeaturesIntegrationTestSuite()
    multilingual_advanced_features_tests = MultilingualAdvancedFeaturesTestSuite()
    extended_builtins_tests = ExtendedBuiltinsTestSuite()
    extended_alias_resolution_tests = ExtendedAliasResolutionTestSuite()
    extended_alias_execution_tests = ExtendedAliasExecutionTestSuite()
    starred_unpacking_tests = StarredUnpackingTestSuite()
    tests = unittest.TestSuite(
        [
            mp_numeral_tests,
            roman_numeral_tests,
            unicode_numeral_tests,
            unicode_string_tests,
            keyword_registry_tests,
            keyword_registry_error_tests,
            keyword_validator_tests,
            complex_numeral_tests,
            fraction_numeral_tests,
            numeral_converter_tests,
            mp_date_parsing_and_formatting_tests,
            mp_date_operation_tests,
            mp_time_tests,
            mp_datetime_tests,
            lexer_tokenization_tests,
            lexer_behavior_tests,
            ast_node_tests,
            parser_expression_tests,
            parser_statement_tests,
            parser_compound_tests,
            parser_multilingual_tests,
            parser_error_tests,
            semantic_scope_tests,
            semantic_const_tests,
            semantic_control_flow_tests,
            semantic_definition_tests,
            semantic_multilingual_error_tests,
            symbol_table_tests,
            ast_printer_tests,
            error_messages_tests,
            python_gen_expr_tests,
            python_gen_stmt_tests,
            python_gen_compound_tests,
            python_gen_multilingual_tests,
            executor_basic_tests,
            executor_multilingual_tests,
            executor_transpile_tests,
            executor_error_tests,
            runtime_builtins_tests,
            repl_tests,
            repl_french_tests,
            triple_quote_tests,
            slice_tests,
            param_tests,
            tuple_tests,
            comp_tests,
            decorator_tests,
            fstring_tests,
            multilingual_critical_tests,
            augmented_assign_tests,
            membership_identity_tests,
            ternary_tests,
            assert_tests,
            chained_assign_tests,
            cli_tests,
            repl_improvements_tests,
            multilingual_completeness_cli_tests,
            while_else_tests,
            for_else_tests,
            yield_from_tests,
            raise_from_tests,
            from_import_star_tests,
            set_comprehension_tests,
            parameter_separator_tests,
            fstring_format_tests,
            match_guard_tests,
            match_or_pattern_tests,
            match_as_pattern_tests,
            global_nonlocal_tests,
            additional_builtins_tests,
            exception_types_tests,
            special_values_tests,
            surface_normalization_tests,
            data_quality_tests,
            advanced_features_integration_tests,
            multilingual_advanced_features_tests,
            extended_builtins_tests,
            extended_alias_resolution_tests,
            extended_alias_execution_tests,
            starred_unpacking_tests,
        ]
    )
    unittest.main()
