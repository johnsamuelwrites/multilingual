#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Program executor: full pipeline from multilingual source to execution.

    source (any language) -> Lexer -> Parser -> SemanticAnalyzer
        -> PythonCodeGenerator -> compile + exec
"""
# pylint: disable=mixed-line-endings

import io
import sys

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import SemanticAnalyzer, Scope, Symbol
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.core.lowering import lower_to_core_ir
from multilingualprogramming.core.semantic_lowering import lower_to_semantic_ir
from multilingualprogramming.core.validators import validate_all
from multilingualprogramming.imports import enable_multilingual_imports
from multilingualprogramming.exceptions import (
    RuntimeExecutionError,
    CodeGenerationError,
)


class ExecutionResult:  # pylint: disable=too-many-instance-attributes
    """Result of executing a multilingual program."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, output="", return_value=None, python_source="",
        errors=None, success=True, backend_name="python",
        backend_reason="python-codegen-exec",
        backend_details=None
    ):
        self.output = output
        self.return_value = return_value
        self.python_source = python_source
        self.errors = errors or []
        self.success = success
        self.backend_name = backend_name
        self.backend_reason = backend_reason
        self.backend_details = dict(backend_details or {})

    @property
    def backend_summary(self):
        """Return a short human-readable backend summary."""
        return f"{self.backend_name} ({self.backend_reason})"

    def backend_report(self):
        """Return structured backend metadata for CLI/reporting use."""
        report = {
            "name": self.backend_name,
            "reason": self.backend_reason,
        }
        if self.backend_details:
            report["details"] = dict(self.backend_details)
        return report

    def __repr__(self):
        status = "OK" if self.success else "FAILED"
        return (f"ExecutionResult({status}, "
                f"output={self.output!r}, "
                f"errors={self.errors!r})")


class ProgramExecutor:
    """
    Executes multilingual source code through the full pipeline.

    Usage:
        executor = ProgramExecutor(language="fr")
        result = executor.execute(french_source)
        print(result.output)    # captured stdout
        print(result.success)   # True/False
    """

    def __init__(self, language=None, check_semantics=True):
        """
        Initialize the executor.

        Args:
            language: Source language code (e.g., "en", "fr", "hi").
                     If None, auto-detect from keywords.
            check_semantics: Whether to run semantic analysis before
                           code generation. Default True.
        """
        self.language = language
        self.check_semantics = check_semantics
        self._last_program_ast = None

    def execute(self, source, capture_output=True, globals_dict=None):
        """
        Execute multilingual source code.

        Args:
            source: Multilingual source code string.
            capture_output: If True, capture stdout to result.output.
                          If False, print to actual stdout.
            globals_dict: Optional dict to merge into execution globals.

        Returns:
            ExecutionResult with output, generated Python source, and errors.
        """
        try:
            # Step 1-3: Frontend to semantic IR
            ir_program = self.to_semantic_ir(source)
            detected_language = ir_program.source_language

            # Step 4: Semantic analysis (optional)
            if self.check_semantics:
                analyzer = SemanticAnalyzer(
                    source_language=detected_language
                )
                # Pre-seed a builtins scope *below* the global scope so that
                # names like print, range, len, etc. are found by lookup()
                # but NOT by lookup_local().  This lets user code redeclare a
                # builtin with `let x = ...` (VariableDeclaration) without
                # triggering a spurious DUPLICATE_DEFINITION error.
                builtins_ns = RuntimeBuiltins(detected_language).namespace()
                builtins_scope = Scope("builtins", "global")
                for name in builtins_ns:
                    builtins_scope.define(Symbol(name, "variable"))
                # Attach the builtins scope as the parent of the global scope.
                analyzer.symbol_table.global_scope.parent = builtins_scope
                semantic_errors = analyzer.analyze(self._last_program_ast)
                if semantic_errors:
                    return ExecutionResult(
                        errors=[str(e) for e in semantic_errors],
                        success=False,
                        backend_details={"stage": "semantic-analysis"},
                    )
            ir_diagnostics = validate_all(ir_program)
            if ir_diagnostics:
                return ExecutionResult(
                    errors=ir_diagnostics,
                    success=False,
                    backend_details={"stage": "semantic-ir-validation"},
                )

            # Step 5: Semantic IR to Python
            generator = PythonCodeGenerator()
            python_source = generator.generate(ir_program)

            # Step 6: Execute
            return self._exec_python(
                python_source, detected_language,
                capture_output, globals_dict
            )

        except (CodeGenerationError, RuntimeExecutionError) as exc:
            return ExecutionResult(
                errors=[str(exc)],
                success=False,
                backend_details={"stage": "execution"},
            )
        except Exception as exc:
            return ExecutionResult(
                errors=[f"{type(exc).__name__}: {exc}"],
                success=False,
                backend_details={"stage": "execution"},
            )

    def transpile(self, source):
        """
        Transpile multilingual source to Python without executing.

        Args:
            source: Multilingual source code string.

        Returns:
            Python source code string.

        Raises:
            Various exceptions on lex/parse/codegen errors.
        """
        core_program = self.to_semantic_ir(source)
        generator = PythonCodeGenerator()
        return generator.generate(core_program)

    def to_core_ir(self, source):
        """Compile source into the legacy typed core wrapper."""
        program, detected_language = self._parse_source(source)
        return lower_to_core_ir(
            program, detected_language, frontend_name="lexer_parser"
        )

    def to_semantic_ir(self, source):
        """Compile source into the semantic IR compiler boundary."""
        program, detected_language = self._parse_source(source)
        return lower_to_semantic_ir(program, detected_language)

    def _parse_source(self, source):
        """Tokenize and parse *source*, caching the AST for later stages."""
        lexer = Lexer(source, language=self.language)
        tokens = lexer.tokenize()
        detected_language = lexer.language or self.language or "en"

        parser = Parser(tokens, source_language=detected_language)
        program = parser.parse()
        self._last_program_ast = program
        return program, detected_language

    def _exec_python(self, python_source, language,
                     capture_output, globals_dict):
        """Compile and execute generated Python code."""
        enable_multilingual_imports()

        # Build execution namespace with builtins
        builtins_ns = RuntimeBuiltins(language).namespace()
        exec_globals = dict(builtins_ns)

        # Python's import system requires __name__ and __package__ to be
        # present in the globals dict before any relative import is attempted.
        # Set safe defaults; callers can override via globals_dict.
        exec_globals.setdefault("__name__", "__main__")
        exec_globals.setdefault("__package__", None)
        exec_globals.setdefault("__spec__", None)

        if globals_dict:
            exec_globals.update(globals_dict)

        # Compile for better error reporting
        try:
            code = compile(python_source, "<multilingual>", "exec")
        except SyntaxError as exc:
            return ExecutionResult(
                python_source=python_source,
                errors=[f"Generated Python has syntax error: {exc}"],
                success=False,
                backend_reason="generated-python-invalid",
                backend_details={"stage": "compile"},
            )

        # Execute with optional output capture
        output = ""
        if capture_output:
            captured = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = captured
                exec(code, exec_globals)  # pylint: disable=exec-used
                output = captured.getvalue()
            except Exception as exc:
                output = captured.getvalue()
                return ExecutionResult(
                    output=output,
                    python_source=python_source,
                    errors=[f"{type(exc).__name__}: {exc}"],
                    success=False,
                    backend_details={"stage": "exec"},
                )
            finally:
                sys.stdout = old_stdout
        else:
            try:
                exec(code, exec_globals)  # pylint: disable=exec-used
            except Exception as exc:
                return ExecutionResult(
                    python_source=python_source,
                    errors=[f"{type(exc).__name__}: {exc}"],
                    success=False,
                    backend_details={"stage": "exec"},
                )

        return ExecutionResult(
            output=output,
            python_source=python_source,
            success=True,
        )
