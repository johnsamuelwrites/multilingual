#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Orchestration/state helpers for the WAT generator."""

from multilingualprogramming.core.ir import CoreIRProgram
from multilingualprogramming.core.ir_nodes import IRProgram
from multilingualprogramming.core.runtime_lowering import lower_ir_to_runtime_ast
from multilingualprogramming.parser.ast_nodes import CallExpr, ClassDef, FunctionDef

from multilingualprogramming.codegen.wat_generator_support import (
    _extract_render_mode,
    _name,
    _real_params,
)


class WATGeneratorOrchestratorMixin:
    """State-reset and high-level generation helpers for WATCodeGenerator."""

    def generate(self, program, *, wasm_target: str = "browser") -> str:
        """Generate a complete WAT module string from an AST node."""
        self._wasm_target = wasm_target
        self._reset_generation_state()

        if isinstance(program, CoreIRProgram):
            program = program.ast
        elif isinstance(program, IRProgram):
            program = lower_ir_to_runtime_ast(program)

        funcs, classes, top = self._split_program_sections(program)
        self._collect_function_metadata(funcs)
        self._collect_class_lowering(classes)
        self._collect_import_aliases(top)
        self._emit_program_sections(funcs, classes, top)

        return self._build_module()

    def _reset_generation_state(self) -> None:
        """Reset all mutable per-module generation state."""
        _reset_generator_state(self)

    @staticmethod
    def _split_program_sections(program) -> tuple[list, list, list]:
        """Split a program body into functions, classes, and top-level statements."""
        funcs = [stmt for stmt in program.body if isinstance(stmt, FunctionDef)]
        classes = [stmt for stmt in program.body if isinstance(stmt, ClassDef)]
        top = [
            stmt for stmt in program.body
            if not isinstance(stmt, (FunctionDef, ClassDef))
        ]
        return funcs, classes, top

    def _collect_function_metadata(self, funcs: list[FunctionDef]) -> None:
        """Collect callable metadata used by later WAT lowering."""
        self._defined_func_names = {_name(func.name) for func in funcs}
        for func in funcs:
            fname = _name(func.name)
            self._func_real_params[fname] = _real_params(func)
            self._func_render_modes[fname] = _extract_render_mode(func)
            if self._returns_string_like(func):
                self._string_return_funcs.add(fname)

    def _emit_program_sections(self, funcs: list, classes: list, top: list) -> None:
        """Emit functions, classes, dispatch helpers, and optional main body."""
        for func in funcs:
            self._emit_function(func)
        for cls in classes:
            self._emit_class(cls)
        self._emit_dispatch_functions()
        if top:
            self._emit_main(top)

    def _gen_call_args(
        self, call_expr: CallExpr, indent: str, fname: str, skip_params: int = 0
    ):
        """Push argument values for a call to a known WAT function."""
        real_params = self._func_real_params.get(fname)
        if real_params:
            kwargs = dict(call_expr.keywords or [])
            effective_params = real_params[skip_params:]
            for i, pname in enumerate(effective_params):
                if i < len(call_expr.args):
                    self._gen_expr(call_expr.args[i], indent)
                elif pname in kwargs:
                    self._gen_expr(kwargs[pname], indent)
                else:
                    self._emit(f"{indent}f64.const 0  ;; missing arg: {pname}")
        else:
            for arg in call_expr.args:
                self._gen_expr(arg, indent)

    def _save_func_state(self):
        """Snapshot and reset nested function state while preserving class context."""
        saved = self._capture_func_state()
        self._reset_func_state()
        return saved


def _reset_generator_state(generator) -> None:
    """Reset all mutable per-module generation state for *generator*."""
    state = {
        "_instrs": [],
        "_locals": set(),
        "_label_count": 0,
        "_loop_stack": [],
        "_data": bytearray(),
        "_strings": {},
        "_funcs": [],
        "_defined_func_names": set(),
        "_func_real_params": {},
        "_func_render_modes": {},
        "_class_ctor_names": {},
        "_class_attr_call_names": {},
        "_var_class_types": {},
        "_wat_symbols": {},
        "_used_wat_symbols": set(),
        "_class_direct_fields": {},
        "_class_field_layouts": {},
        "_class_obj_sizes": {},
        "_current_class": None,
        "_class_bases": {},
        "_string_len_locals": {},
        "_list_locals": set(),
        "_tuple_locals": set(),
        "_static_sequence_elements": {},
        "_zip_pair_locals": set(),
        "_dict_key_maps": {},
        "_imported_call_aliases": {},
        "_module_aliases": {},
        "_open_aliases": {},
        "_virtual_file_contents": {},
        "_need_heap_ptr": False,
        "_uses_dom": False,
        "_lambda_table": [],
        "_lambda_locals": {},
        "_str_concat_helper_emitted": False,
        "_str_slice_helper_emitted": False,
        "_sequence_func_names": set(),
        "_string_return_funcs": set(),
        "_string_format_helpers_emitted": False,
        "_closure_factory_funcs": {},
        "_closure_locals": {},
        "_try_stack": [],
        "_property_setters": {},
        "_property_deleters": {},
        "_class_special_methods": {},
        "_str_slice_step_helper_emitted": False,
        "_static_method_names": set(),
        "_property_getters": {},
        "_class_ids": {},
        "_dispatch_func_names": {},
    }
    for name, value in state.items():
        setattr(generator, name, value)
