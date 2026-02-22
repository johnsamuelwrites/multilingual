#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Proof-of-Concept tests for WASM Code Generation.

WASM Codegen Backend
Validates that the WASM generator produces valid Rust/WASM code.
"""

import unittest
from multilingualprogramming.codegen.wasm_generator import (
    WasmCodeGenerator,
    WasmTarget,
    WasmBuildConfig,
    generate_wasm_for_function,
)
from multilingualprogramming.parser.ast_nodes import (
    Program,
    FunctionDef,
    Identifier,
    NumeralLiteral,
    ReturnStatement,
    Parameter,
)
from multilingualprogramming.wasm.loader import is_wasm_available
from multilingualprogramming.runtime.backend_selector import (
    BackendSelector,
    Backend,
    get_current_backend,
)


class WasmCodegenProofOfConceptTestSuite(unittest.TestCase):
    """Test WASM code generation proof-of-concept."""

    def test_wasm_generator_initialization(self):
        """Verify WASM generator initializes correctly."""
        generator = WasmCodeGenerator()
        self.assertIsNotNone(generator)
        self.assertTrue(generator.target.optimize)

    def test_wasm_generator_with_custom_target(self):
        """Verify WASM generator accepts custom target."""
        target = WasmTarget(optimize=False, debug_info=True)
        generator = WasmCodeGenerator(target)
        self.assertFalse(generator.target.optimize)
        self.assertTrue(generator.target.debug_info)

    def test_minimal_program_generation(self):
        """Verify generating WASM for minimal program."""
        # Create minimal AST: just a return statement
        ret = ReturnStatement(NumeralLiteral(42, 1, 0), 1, 0)
        program = Program([ret], 1, 0)

        generator = WasmCodeGenerator()
        rust_code = generator.generate(program)

        # Verify output is Rust code
        self.assertIsInstance(rust_code, str)
        self.assertIn("WebAssembly Module", rust_code)
        self.assertIn("extern \"C\"", rust_code)

    def test_function_definition_generation(self):
        """Verify generating WASM for function definition."""
        # Create simple function: fn add_one() -> 42
        param = Parameter(Identifier("x", 1, 0), None, 1, 0)
        func = FunctionDef(
            name=Identifier("add_one", 1, 0),
            params=[param],
            body=[ReturnStatement(NumeralLiteral(42, 1, 0), 1, 0)],
            decorators=[],
            line=1,
            column=0,
        )

        generator = WasmCodeGenerator()
        rust_code = generator.generate(Program([func], 1, 0))

        # Verify function appears in output
        self.assertIn("add_one", rust_code)
        self.assertIn("#[no_mangle]", rust_code)
        self.assertIn("pub extern \"C\"", rust_code)

    def test_exported_functions_tracking(self):
        """Verify generator tracks exported functions."""
        func = FunctionDef(
            name=Identifier("multiply", 1, 0),
            params=[
                Parameter(Identifier("a", 1, 0), None, 1, 0),
                Parameter(Identifier("b", 1, 0), None, 1, 0),
            ],
            body=[ReturnStatement(NumeralLiteral(1, 1, 0), 1, 0)],
            decorators=[],
            line=1,
            column=0,
        )

        generator = WasmCodeGenerator()
        generator.generate(Program([func], 1, 0))

        exported = generator.get_exported_functions()
        self.assertIn("multiply", exported)

    def test_wasm_build_config_creation(self):
        """Verify WASM build configuration."""
        config = WasmBuildConfig(output_path="test.wasm")
        self.assertEqual(config.output_path, "test.wasm")
        self.assertEqual(config.build_profile, "release")

    def test_generate_wasm_for_function_convenience(self):
        """Verify convenience function for single function WASM generation."""
        func = FunctionDef(
            name=Identifier("test_fn", 1, 0),
            params=[],
            body=[ReturnStatement(NumeralLiteral(0, 1, 0), 1, 0)],
            decorators=[],
            line=1,
            column=0,
        )

        rust_code = generate_wasm_for_function(func, optimize=True)

        self.assertIsInstance(rust_code, str)
        self.assertIn("test_fn", rust_code)
        self.assertIn("extern \"C\"", rust_code)

    def test_wasm_module_availability_detection(self):
        """Verify WASM availability detection."""
        available = is_wasm_available()
        # This will be False in test environment without wasmtime
        # but the check should work
        self.assertIsInstance(available, bool)

    def test_backend_selector_initialization(self):
        """Verify backend selector initializes correctly."""
        selector = BackendSelector(prefer_backend=Backend.AUTO)
        self.assertIsNotNone(selector)

    def test_backend_selector_auto_mode(self):
        """Verify backend selector auto-detects backend."""
        BackendSelector(prefer_backend=Backend.AUTO)
        # Should default to Python if WASM not available
        # or WASM if available and supported
        current = get_current_backend()
        self.assertIn(current, ["Python", "WASM"])

    def test_backend_selector_python_fallback(self):
        """Verify backend selector can force Python."""
        selector = BackendSelector(prefer_backend=Backend.PYTHON)
        # Should not use WASM
        self.assertFalse(selector.is_wasm_available())

    def test_rust_code_structure(self):
        """Verify generated Rust code has required structure."""
        generator = WasmCodeGenerator()
        program = Program([], 1, 0)
        rust_code = generator.generate(program)

        # Check for key Rust/WASM boilerplate
        self.assertIn("#![no_std]", rust_code)
        self.assertIn("const WASM_MEMORY_PAGES", rust_code)
        self.assertIn("#[panic_handler]", rust_code)
        self.assertIn("__multilingual_wasm_version", rust_code)

    def test_wasm_memory_constants(self):
        """Verify WASM memory configuration."""
        generator = WasmCodeGenerator()
        rust_code = generator.generate(Program([], 1, 0))

        # WASM memory should be 1024 pages = 64MB
        self.assertIn("1024", rust_code)
        self.assertIn("65536", rust_code)

    def test_multiple_functions_generation(self):
        """Verify generating multiple functions."""
        func1 = FunctionDef(
            name=Identifier("func_a", 1, 0),
            params=[],
            body=[ReturnStatement(NumeralLiteral(1, 1, 0), 1, 0)],
            decorators=[],
            line=1,
            column=0,
        )

        func2 = FunctionDef(
            name=Identifier("func_b", 1, 0),
            params=[],
            body=[ReturnStatement(NumeralLiteral(2, 1, 0), 1, 0)],
            decorators=[],
            line=2,
            column=0,
        )

        generator = WasmCodeGenerator()
        rust_code = generator.generate(Program([func1, func2], 1, 0))

        # Both functions should appear
        self.assertIn("func_a", rust_code)
        self.assertIn("func_b", rust_code)

        # Both should be exported
        exported = generator.get_exported_functions()
        self.assertEqual(len(exported), 2)
        self.assertIn("func_a", exported)
        self.assertIn("func_b", exported)

    def test_wasm_functions_tracking(self):
        """Verify WASM function tracking."""
        func = FunctionDef(
            name=Identifier("tracked_fn", 1, 0),
            params=[],
            body=[ReturnStatement(NumeralLiteral(0, 1, 0), 1, 0)],
            decorators=[],
            line=1,
            column=0,
        )

        generator = WasmCodeGenerator()
        generator.generate(Program([func], 1, 0))

        wasm_funcs = generator.get_wasm_functions()
        self.assertIn("tracked_fn", wasm_funcs)
        self.assertIsInstance(wasm_funcs["tracked_fn"], FunctionDef)


class WasmCodegenIntegrationProofOfConceptTestSuite(unittest.TestCase):
    """Integration tests for WASM infrastructure."""

    def test_codegen_to_config_pipeline(self):
        """Verify pipeline from codegen to build config."""
        generator = WasmCodeGenerator()
        program = Program([], 1, 0)
        rust_code = generator.generate(program)

        config = WasmBuildConfig("output.wasm")
        # Note: actual build() requires cranelift, skipped in POC
        self.assertIsNone(config.build(rust_code))

        # But we can get the Rust code back
        self.assertEqual(config.get_rust_code(), rust_code)

    def test_backend_selector_with_fallback(self):
        """Verify backend selector with fallback."""

        def python_impl(_fn_name, *_args, **_kwargs):
            return 42

        selector = BackendSelector(prefer_backend=Backend.PYTHON)
        selector.set_python_fallback(python_impl)

        # Should use Python fallback
        result = selector.call_function("test", 1, 2, 3)
        self.assertEqual(result, 42)

    def test_wasm_availability_consistency(self):
        """Verify WASM availability check is consistent."""
        available1 = is_wasm_available()
        available2 = is_wasm_available()
        self.assertEqual(available1, available2)


if __name__ == "__main__":
    unittest.main()
