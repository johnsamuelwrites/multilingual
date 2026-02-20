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

import io
import sys

from multilingualprogramming.lexer.lexer import Lexer
from multilingualprogramming.parser.parser import Parser
from multilingualprogramming.parser.semantic_analyzer import SemanticAnalyzer
from multilingualprogramming.codegen.python_generator import PythonCodeGenerator
from multilingualprogramming.codegen.runtime_builtins import RuntimeBuiltins
from multilingualprogramming.core.lowering import lower_to_core_ir
from multilingualprogramming.exceptions import (
    RuntimeExecutionError,
    CodeGenerationError,
)


class ExecutionResult:
    """Result of executing a multilingual program."""

    def __init__(self, output="", return_value=None, python_source="",
                 errors=None, success=True):
        self.output = output
        self.return_value = return_value
        self.python_source = python_source
        self.errors = errors or []
        self.success = success

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
            # Step 1-3: Frontend to typed core representation
            core_program = self.to_core_ir(source)
            detected_language = core_program.source_language

            # Step 4: Semantic analysis (optional)
            if self.check_semantics:
                analyzer = SemanticAnalyzer(
                    source_language=detected_language
                )
                # Pre-seed symbol table with runtime builtins so that
                # names like print, range, len, etc. are not flagged
                # as undefined.
                builtins_ns = RuntimeBuiltins(detected_language).namespace()
                for name in builtins_ns:
                    analyzer.symbol_table.define(
                        name, "variable", line=0, column=0
                    )
                semantic_errors = analyzer.analyze(core_program.ast)
                if semantic_errors:
                    return ExecutionResult(
                        errors=[str(e) for e in semantic_errors],
                        success=False,
                    )

            # Step 5: Lowered core to Python
            generator = PythonCodeGenerator()
            python_source = generator.generate(core_program)

            # Step 6: Execute
            return self._exec_python(
                python_source, detected_language,
                capture_output, globals_dict
            )

        except (CodeGenerationError, RuntimeExecutionError) as exc:
            return ExecutionResult(
                errors=[str(exc)],
                success=False,
            )
        except Exception as exc:
            return ExecutionResult(
                errors=[f"{type(exc).__name__}: {exc}"],
                success=False,
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
        core_program = self.to_core_ir(source)
        generator = PythonCodeGenerator()
        return generator.generate(core_program)

    def to_core_ir(self, source):
        """Compile source into the typed core representation."""
        lexer = Lexer(source, language=self.language)
        tokens = lexer.tokenize()
        detected_language = lexer.language or self.language or "en"

        parser = Parser(tokens, source_language=detected_language)
        program = parser.parse()
        return lower_to_core_ir(
            program, detected_language, frontend_name="lexer_parser"
        )

    def _exec_python(self, python_source, language,
                     capture_output, globals_dict):
        """Compile and execute generated Python code."""
        # Build execution namespace with builtins
        builtins_ns = RuntimeBuiltins(language).namespace()
        exec_globals = dict(builtins_ns)

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
                )

        return ExecutionResult(
            output=output,
            python_source=python_source,
            success=True,
        )
