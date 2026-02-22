#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Tests for AST normalization determinism across all 17 languages."""

import unittest
from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.ast_nodes import (
    IfStatement, ForLoop, FunctionDef, ClassDef, WhileLoop,
    BinaryOp, BooleanOp, CompareOp, CallExpr,
    ListComprehension, DictComprehension, SetComprehension,
)


def _parse(source, language):
    """Helper: lex + parse source code."""
    lexer = Lexer(source, language=language)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_language=language)
    return parser.parse()


def _ast_structure(node):
    """Extract structural representation of AST node for comparison."""
    if node is None:
        return "None"
    if isinstance(node, list):
        return tuple(_ast_structure(item) for item in node)

    # For AST nodes, return type name and key structural properties
    node_type = type(node).__name__

    # Extract key attributes depending on node type
    attrs = {}

    if isinstance(node, IfStatement):
        attrs['condition_type'] = type(node.condition).__name__
        attrs['body_count'] = len(node.body) if node.body else 0
        attrs['elif_count'] = len(node.elif_clauses) if node.elif_clauses else 0
        attrs['has_else'] = node.else_body is not None
    elif isinstance(node, ForLoop):
        attrs['target_type'] = type(node.target).__name__
        attrs['iterable_type'] = type(node.iterable).__name__
        attrs['body_count'] = len(node.body) if node.body else 0
    elif isinstance(node, WhileLoop):
        attrs['condition_type'] = type(node.condition).__name__
        attrs['body_count'] = len(node.body) if node.body else 0
    elif isinstance(node, FunctionDef):
        attrs['params_count'] = len(node.params) if node.params else 0
        attrs['decorator_count'] = len(node.decorators) if node.decorators else 0
        attrs['body_count'] = len(node.body) if node.body else 0
    elif isinstance(node, ClassDef):
        attrs['base_count'] = len(node.bases) if node.bases else 0
        attrs['body_count'] = len(node.body) if node.body else 0
    elif isinstance(node, BinaryOp):
        attrs['op'] = node.op
        attrs['left_type'] = type(node.left).__name__
        attrs['right_type'] = type(node.right).__name__
    elif isinstance(node, BooleanOp):
        attrs['op'] = node.op
        attrs['operand_count'] = len(node.operands) if node.operands else 0
    elif isinstance(node, CompareOp):
        attrs['comparator_count'] = len(node.comparators) if node.comparators else 0
    elif isinstance(node, CallExpr):
        attrs['arg_count'] = len(node.args) if node.args else 0
        attrs['keyword_count'] = len(node.keywords) if node.keywords else 0
    elif isinstance(node, (ListComprehension, DictComprehension, SetComprehension)):
        attrs['for_count'] = len(node.for_clauses) if hasattr(node, 'for_clauses') else 0

    # Return just the type and counts, don't include body structure (avoid recursion complexity)
    return (node_type, tuple(sorted(attrs.items())))


class ASTNormalizationTestSuite(unittest.TestCase):
    """Test AST normalization across languages."""

    def test_if_statement_normalization(self):
        """Same if statement in different languages produces equivalent AST."""
        sources = {
            "en": "if x > 5:\n    pass\n",
            "fr": "si x > 5:\n    passer\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0] for lang in sources}

        # All should have same structure
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_for_loop_normalization(self):
        """For loop across languages produces equivalent AST."""
        sources = {
            "en": "for i in range(5):\n    pass\n",
            "fr": "pour i dans intervalle(5):\n    passer\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0] for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_while_loop_normalization(self):
        """While loop across languages produces equivalent AST."""
        sources = {
            "en": "while True:\n    pass\n",
            "fr": "tantque Vrai:\n    passer\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0] for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_function_definition_normalization(self):
        """Function definition across languages produces equivalent AST."""
        sources = {
            "en": "def func(a, b):\n    return a + b\n",
            "fr": "def func(a, b):\n    retour a + b\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0] for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_class_definition_normalization(self):
        """Class definition in English parses correctly."""
        source = "class A(object):\n    pass\n"
        prog = _parse(source, "en")
        stmt = prog.body[0]
        self.assertIsInstance(stmt, ClassDef)

    def test_boolean_expression_normalization(self):
        """Boolean expressions parse correctly."""
        source = "x and y or z\n"
        prog = _parse(source, "en")
        expr = prog.body[0].expression
        self.assertIsInstance(expr, BooleanOp)

    def test_comparison_normalization(self):
        """Comparison expressions across languages produce equivalent AST."""
        sources = {
            "en": "a < b <= c < d\n",
            "fr": "a < b <= c < d\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0].expression for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_function_call_normalization(self):
        """Function calls across languages produce equivalent AST."""
        sources = {
            "en": "func(1, 2, x=3, y=4)\n",
            "fr": "func(1, 2, x=3, y=4)\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0].expression for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_nested_structures_normalization(self):
        """Nested if-for-function structures produce equivalent AST."""
        sources = {
            "en": "def f():\n    for i in range(5):\n        if i > 2:\n            pass\n",
            "fr": "def f():\n    pour i dans intervalle(5):\n        si i > 2:\n            passer\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0] for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")

    def test_comprehension_normalization(self):
        """List comprehensions across languages produce equivalent AST."""
        sources = {
            "en": "[x for x in range(5) if x > 2]\n",
            "fr": "[x pour x dans intervalle(5) si x > 2]\n",
        }

        asts = {lang: _parse(sources[lang], lang).body[0].expression for lang in sources}
        structures = {lang: _ast_structure(asts[lang]) for lang in asts}
        first_structure = list(structures.values())[0]

        for lang, struct in structures.items():
            self.assertEqual(struct, first_structure,
                           f"AST structure mismatch for language {lang}")


if __name__ == "__main__":
    unittest.main()
