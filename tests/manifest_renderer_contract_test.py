#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Renderer contract validation against ABI manifest metadata."""

import unittest

from multilingualprogramming.codegen.wat_generator import WATCodeGenerator
from multilingualprogramming.parser.ast_nodes import (
    Program,
    FunctionDef,
    Identifier,
    Parameter,
    ReturnStatement,
    NumeralLiteral,
    CallExpr,
    StringLiteral,
)


def _param(name: str) -> Parameter:
    return Parameter(Identifier(name))


class ManifestRendererContractTestSuite(unittest.TestCase):
    """Ensure manifest metadata and generated renderer contract agree."""

    def test_stream_exports_have_writer_and_count_in_wat(self):
        fn = FunctionDef(
            Identifier("draw"),
            [_param("x")],
            [ReturnStatement(NumeralLiteral("0"))],
            decorators=[CallExpr(Identifier("render_mode"), [StringLiteral("point_stream")])],
        )
        program = Program([fn])
        gen = WATCodeGenerator()
        manifest = gen.generate_abi_manifest(program)
        wat = gen.generate(program)

        stream = manifest["exports"][0]["stream_output"]
        self.assertIn(f'(export "{stream["writer_export"]}")', wat)
        self.assertIn(f'(export "{stream["count_export"]}")', wat)

    def test_host_shim_covers_required_imports(self):
        gen = WATCodeGenerator()
        manifest = gen.generate_abi_manifest(Program([]))
        shim = gen.generate_js_host_shim(manifest)
        for item in manifest["required_host_imports"]:
            self.assertIn(item["name"], shim)


if __name__ == "__main__":
    unittest.main()
