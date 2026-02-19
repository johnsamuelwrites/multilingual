#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Test suite for the multilingual lexer
"""

import unittest
from multilingualprogramming.keyword.keyword_registry import KeywordRegistry
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.lexer.token_types import TokenType
from multilingualprogramming.exceptions import UnexpectedTokenError


class LexerTestBase(unittest.TestCase):
    """
    Shared helpers for lexer test suites
    """

    def setUp(self):
        """Reset keyword registry singleton."""
        KeywordRegistry.reset()

    def _token_types(self, tokens):
        """Extract token types from a token list (excluding EOF)."""
        return [t.type for t in tokens if t.type != TokenType.EOF]

    def _token_values(self, tokens):
        """Extract token values from a token list (excluding EOF)."""
        return [t.value for t in tokens if t.type != TokenType.EOF]


class LexerTokenizationTestSuite(LexerTestBase):
    """
    Test cases for lexer tokenization primitives
    """

    def test_simple_english(self):
        """Test tokenizing simple English code."""
        source = "if x > 5:\n    print(x)"
        lexer = Lexer(source, language="en")
        tokens = lexer.tokenize()

        types = self._token_types(tokens)
        self.assertIn(TokenType.KEYWORD, types)
        self.assertIn(TokenType.IDENTIFIER, types)
        self.assertIn(TokenType.OPERATOR, types)
        self.assertIn(TokenType.NUMERAL, types)

    def test_english_keyword_detection(self):
        """Test that English keywords are recognized with concepts."""
        source = "if x > 5:\n    print(x)"
        lexer = Lexer(source, language="en")
        tokens = lexer.tokenize()

        # 'if' should be a keyword with concept COND_IF
        if_token = tokens[0]
        self.assertEqual(if_token.type, TokenType.KEYWORD)
        self.assertEqual(if_token.value, "if")
        self.assertEqual(if_token.concept, "COND_IF")

    def test_french_keywords(self):
        """Test tokenizing French-keyword code."""
        source = "si x > 5:\n    afficher(x)"
        lexer = Lexer(source, language="fr")
        tokens = lexer.tokenize()

        si_token = tokens[0]
        self.assertEqual(si_token.type, TokenType.KEYWORD)
        self.assertEqual(si_token.value, "si")
        self.assertEqual(si_token.concept, "COND_IF")

        # Find the 'afficher' token
        afficher_tokens = [t for t in tokens if t.value == "afficher"]
        self.assertEqual(len(afficher_tokens), 1)
        self.assertEqual(afficher_tokens[0].concept, "PRINT")

    def test_portuguese_phrase_keywords(self):
        """Phrase aliases should tokenize as single keyword concepts."""
        source = "senão se x:\n    passe\npara cada i em lista:\n    imprima(i)\n"
        lexer = Lexer(source, language="pt")
        tokens = lexer.tokenize()

        phrase_values = [t.value for t in tokens if t.type == TokenType.KEYWORD]
        self.assertIn("senão se", phrase_values)
        self.assertIn("para cada", phrase_values)

        senao_se = [t for t in tokens if t.value == "senão se"][0]
        para_cada = [t for t in tokens if t.value == "para cada"][0]
        self.assertEqual(senao_se.concept, "COND_ELIF")
        self.assertEqual(para_cada.concept, "LOOP_FOR")

    def test_french_phrase_keywords(self):
        """French phrase aliases should tokenize as single keyword concepts."""
        source = "sinon si x:\n    passer\npour chaque i dans liste:\n    afficher(i)\n"
        lexer = Lexer(source, language="fr")
        tokens = lexer.tokenize()

        phrase_values = [t.value for t in tokens if t.type == TokenType.KEYWORD]
        self.assertIn("sinon si", phrase_values)
        self.assertIn("pour chaque", phrase_values)

        sinon_si = [t for t in tokens if t.value == "sinon si"][0]
        pour_chaque = [t for t in tokens if t.value == "pour chaque"][0]
        self.assertEqual(sinon_si.concept, "COND_ELIF")
        self.assertEqual(pour_chaque.concept, "LOOP_FOR")

    def test_hindi_keywords(self):
        """Test tokenizing Hindi-keyword code."""
        source = "अगर x > ५:\n    छापो(x)"
        lexer = Lexer(source, language="hi")
        tokens = lexer.tokenize()

        agar_token = tokens[0]
        self.assertEqual(agar_token.type, TokenType.KEYWORD)
        self.assertEqual(agar_token.value, "अगर")
        self.assertEqual(agar_token.concept, "COND_IF")

    def test_numeral_tokenization_ascii(self):
        """Test tokenizing ASCII numerals."""
        source = "42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "42")

    def test_numeral_tokenization_devanagari(self):
        """Test tokenizing Devanagari numerals."""
        source = "५४२"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "५४२")

    def test_numeral_tokenization_arabic_indic(self):
        """Test tokenizing Arabic-Indic numerals."""
        source = "١٢٣"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "١٢٣")

    def test_numeral_with_decimal(self):
        """Test tokenizing decimal numerals."""
        source = "3.14"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "3.14")

    def test_numeral_hex_literal(self):
        source = "0xFF"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "0xFF")

    def test_numeral_octal_literal(self):
        source = "0o77"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "0o77")

    def test_numeral_binary_literal(self):
        source = "0b1011"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "0b1011")

    def test_numeral_scientific_notation(self):
        source = "1.5e-3"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.NUMERAL)
        self.assertEqual(tokens[0].value, "1.5e-3")

    def test_string_double_quote(self):
        """Test tokenizing double-quoted strings."""
        source = '"hello world"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello world")

    def test_string_single_quote(self):
        """Test tokenizing single-quoted strings."""
        source = "'hello'"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello")

    def test_string_guillemets(self):
        """Test tokenizing guillemet-quoted strings."""
        source = '\u00abbonjour\u00bb'
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "bonjour")

    def test_string_cjk_corners(self):
        """Test tokenizing CJK corner bracket strings."""
        source = '\u300c\u3053\u3093\u306b\u3061\u306f\u300d'
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "\u3053\u3093\u306b\u3061\u306f")

    def test_operator_ascii(self):
        """Test tokenizing ASCII operators."""
        source = "x + y * z"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0].value, "+")
        self.assertEqual(ops[1].value, "*")

    def test_operator_multi_char(self):
        """Test tokenizing multi-character operators."""
        source = "x == y != z"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(ops[0].value, "==")
        self.assertEqual(ops[1].value, "!=")

    def test_operator_walrus(self):
        source = "x := 1"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].value, ":=")

    def test_operator_unicode_multiply(self):
        """Test Unicode multiplication sign ×."""
        source = "x \u00d7 y"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].value, "*")

    def test_operator_unicode_not_equal(self):
        """Test Unicode not-equal sign ≠."""
        source = "x \u2260 y"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].value, "!=")

    def test_operator_unicode_less_equal(self):
        """Test Unicode less-than-or-equal sign ≤."""
        source = "x \u2264 y"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].value, "<=")

    def test_delimiters(self):
        """Test tokenizing delimiters."""
        source = "f(x, y)"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        delims = [t for t in tokens if t.type == TokenType.DELIMITER]
        values = [t.value for t in delims]
        self.assertIn("(", values)
        self.assertIn(",", values)
        self.assertIn(")", values)

    def test_date_literal(self):
        """Test tokenizing date literals."""
        source = "\u301415-January-2024\u3015"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.DATE_LITERAL)
        self.assertEqual(tokens[0].value, "15-January-2024")

    def test_indentation(self):
        """Test indentation handling."""
        source = "if x:\n    y = 1\n    z = 2"
        lexer = Lexer(source, language="en")
        tokens = lexer.tokenize()

        types = self._token_types(tokens)
        self.assertIn(TokenType.INDENT, types)


class LexerBehaviorTestSuite(LexerTestBase):
    """
    Test cases for lexer behavior, detection, and errors
    """

    def test_dedentation(self):
        """Test dedentation handling."""
        source = "if x:\n    y = 1\nz = 2"
        lexer = Lexer(source, language="en")
        tokens = lexer.tokenize()

        types = self._token_types(tokens)
        self.assertIn(TokenType.INDENT, types)
        self.assertIn(TokenType.DEDENT, types)

    def test_comment(self):
        """Test comment tokenization."""
        source = "x = 5 # this is a comment"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        comments = [t for t in tokens if t.type == TokenType.COMMENT]
        self.assertEqual(len(comments), 1)
        self.assertIn("this is a comment", comments[0].value)

    def test_language_auto_detect_english(self):
        """Test automatic language detection for English."""
        source = "if x > 5:\n    return x"
        lexer = Lexer(source)
        lexer.tokenize()
        self.assertEqual(lexer.language, "en")

    def test_language_auto_detect_french(self):
        """Test automatic language detection for French."""
        source = "si x > 5:\n    retour x"
        lexer = Lexer(source)
        lexer.tokenize()
        self.assertEqual(lexer.language, "fr")

    def test_line_column_tracking(self):
        """Test that line and column numbers are correct."""
        source = "x = 5\ny = 10"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # First token 'x' should be at line 1, column 1
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)

    def test_unicode_identifier(self):
        """Test tokenizing Unicode identifiers."""
        source = "площадь = 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "площадь")

    def test_mixed_script_identifiers(self):
        """Test identifiers in different scripts."""
        source = "변수 = 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "변수")

    def test_eof_token(self):
        """Test that EOF token is always present."""
        source = "x"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_empty_source(self):
        """Test tokenizing empty source."""
        lexer = Lexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)

    def test_unexpected_token_error(self):
        """Test that unexpected characters raise UnexpectedTokenError."""
        source = "x = 5\n`invalid"
        lexer = Lexer(source)
        with self.assertRaises(UnexpectedTokenError):
            lexer.tokenize()

    def test_unterminated_string(self):
        """Test that unterminated strings raise errors."""
        source = '"hello'
        lexer = Lexer(source)
        with self.assertRaises(UnexpectedTokenError):
            lexer.tokenize()

    def test_chinese_keywords(self):
        """Test tokenizing Chinese keywords."""
        source = "如果 x > 5:\n    打印(x)"
        lexer = Lexer(source, language="zh")
        tokens = lexer.tokenize()

        if_token = tokens[0]
        self.assertEqual(if_token.type, TokenType.KEYWORD)
        self.assertEqual(if_token.value, "如果")
        self.assertEqual(if_token.concept, "COND_IF")

    def test_arabic_keywords(self):
        """Test tokenizing Arabic keywords."""
        source = "إذا x > 5:\n    اطبع(x)"
        lexer = Lexer(source, language="ar")
        tokens = lexer.tokenize()

        if_token = tokens[0]
        self.assertEqual(if_token.type, TokenType.KEYWORD)
        self.assertEqual(if_token.value, "إذا")
        self.assertEqual(if_token.concept, "COND_IF")

    def test_japanese_keywords(self):
        """Test tokenizing Japanese keywords."""
        source = "もし x > 5:\n    表示(x)"
        lexer = Lexer(source, language="ja")
        tokens = lexer.tokenize()

        if_token = tokens[0]
        self.assertEqual(if_token.type, TokenType.KEYWORD)
        self.assertEqual(if_token.value, "もし")
        self.assertEqual(if_token.concept, "COND_IF")
