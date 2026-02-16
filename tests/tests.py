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
        ]
    )
    unittest.main()
