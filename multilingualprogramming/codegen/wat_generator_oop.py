#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""OOP and class-lowering helpers for the WAT code generator."""

from multilingualprogramming.parser.ast_nodes import (
    Assignment,
    AttributeAccess,
    CallExpr,
    ClassDef,
    ForLoop,
    FunctionDef,
    Identifier,
    IfStatement,
    WhileLoop,
)

from multilingualprogramming.codegen.wat_generator_support import (
    _STREAM_RENDER_MODES,
    _extract_render_mode,
    _has_decorator,
    _name,
    _real_params,
)


class WATGeneratorOOPMixin:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Mixin implementing class lowering, dispatch, and object allocation."""

    @staticmethod
    def _mangle_class_method_name(class_name: str, method_name: str) -> str:
        return f"{class_name}__{method_name}"

    def _register_class_members(self, cls: ClassDef) -> None:
        """Register methods, constructors, and direct field layout for one class."""
        class_name = _name(cls.name)
        self._class_bases[class_name] = [
            _name(base) for base in (cls.bases or [])
            if isinstance(base, Identifier)
        ]
        for member in (cls.body or []):
            if not isinstance(member, FunctionDef):
                continue
            method_name = _name(member.name)
            lowered = self._mangle_class_method_name(class_name, method_name)
            self._defined_func_names.add(lowered)
            self._func_real_params[lowered] = _real_params(member)
            self._func_render_modes[lowered] = _extract_render_mode(member)
            self._class_attr_call_names[f"{class_name}.{method_name}"] = lowered
            if _has_decorator(member, ("staticmethod", "classmethod")):
                self._static_method_names.add(lowered)
            if _has_decorator(member, "property"):
                self._property_getters[f"{class_name}.{method_name}"] = lowered
            if method_name == "__init__":
                self._class_ctor_names[class_name] = lowered
        self._class_direct_fields[class_name] = self._collect_class_fields(cls)

    def _apply_inherited_field_layouts(self) -> None:
        """Compute inherited field layouts and object sizes for all classes."""
        for class_name in self._class_direct_fields:
            effective = self._effective_field_layout(class_name)
            self._class_field_layouts[class_name] = effective
            self._class_obj_sizes[class_name] = len(effective) * 8

    def _inherit_class_methods_and_ctors(self) -> None:
        """Propagate inherited methods and constructors through the MRO."""
        for class_name in self._class_bases:
            for ancestor in self._mro(class_name)[1:]:
                self._inherit_methods_from_ancestor(class_name, ancestor)
                if (class_name not in self._class_ctor_names
                        and ancestor in self._class_ctor_names):
                    self._class_ctor_names[class_name] = self._class_ctor_names[ancestor]

    def _inherit_methods_from_ancestor(self, class_name: str, ancestor: str) -> None:
        """Copy ancestor method lookup entries that the subclass does not override."""
        for key, value in list(self._class_attr_call_names.items()):
            if not key.startswith(f"{ancestor}."):
                continue
            method_name = key[len(ancestor) + 1:]
            own_key = f"{class_name}.{method_name}"
            if own_key not in self._class_attr_call_names:
                self._class_attr_call_names[own_key] = value

    def _assign_stateful_class_ids(self, classes: list[ClassDef]) -> None:
        """Assign integer runtime IDs to stateful classes."""
        for cls in classes:
            class_name = _name(cls.name)
            if self._is_stateful_class(class_name) and class_name not in self._class_ids:
                self._class_ids[class_name] = len(self._class_ids)

    def _collect_polymorphic_methods(self) -> dict[str, list[str]]:
        """Return methods directly defined on more than one stateful class."""
        method_classes: dict[str, list[str]] = {}
        for key in self._class_attr_call_names:
            cls_name, method_name = key.split(".", 1)
            if not self._is_dispatch_candidate(cls_name, method_name):
                continue
            own_lowered = self._mangle_class_method_name(cls_name, method_name)
            if own_lowered in self._defined_func_names:
                method_classes.setdefault(method_name, []).append(cls_name)
        return method_classes

    def _is_dispatch_candidate(self, class_name: str, method_name: str) -> bool:
        """Return True if a method can participate in dynamic dispatch."""
        return (
            self._is_stateful_class(class_name)
            and method_name != "__init__"
            and class_name in self._class_ids
        )

    def _register_dispatch_functions(self) -> None:
        """Create dispatch function names for polymorphic methods."""
        for method_name, class_names in self._collect_polymorphic_methods().items():
            if len(class_names) > 1:
                dispatch_wat = self._wat_symbol(f"__dispatch_{method_name}")
                self._dispatch_func_names[method_name] = dispatch_wat

    def _collect_class_lowering(self, classes: list[ClassDef]) -> None:
        """Pre-collect lowered names, layouts, constructors, and dispatch info."""
        for cls in classes:
            self._register_class_members(cls)
        self._apply_inherited_field_layouts()
        self._inherit_class_methods_and_ctors()
        self._assign_stateful_class_ids(classes)
        self._register_dispatch_functions()

    def _collect_class_fields(self, class_def: ClassDef) -> dict[str, int]:
        """Scan all method bodies for ``self.attr = ...`` to build a field layout."""
        fields: dict[str, int] = {}

        def _scan(statements):
            for stmt in (statements or []):
                if isinstance(stmt, Assignment):
                    target = stmt.target
                    if (isinstance(target, AttributeAccess)
                            and isinstance(target.obj, Identifier)
                            and target.obj.name == "self"
                            and target.attr not in fields):
                        fields[target.attr] = len(fields) * 8
                elif isinstance(stmt, IfStatement):
                    _scan(stmt.body)
                    for _, elif_body in (stmt.elif_clauses or []):
                        _scan(elif_body)
                    _scan(stmt.else_body)
                elif isinstance(stmt, (WhileLoop, ForLoop, FunctionDef)):
                    _scan(stmt.body)

        for member in (class_def.body or []):
            if isinstance(member, FunctionDef):
                _scan(member.body)
        return fields

    def _mro(self, class_name: str) -> list[str]:
        """Return the C3 linearization for ``class_name``."""
        return self._c3_mro(class_name, frozenset())

    def _c3_mro(self, class_name: str, visiting: frozenset) -> list[str]:
        """Recursive C3 linearization step."""
        if class_name in visiting:
            return [class_name]
        visiting = visiting | {class_name}
        bases = self._class_bases.get(class_name, [])
        if not bases:
            return [class_name]
        sequences = [list(self._c3_mro(base, visiting)) for base in bases] + [list(bases)]
        return [class_name] + self._c3_merge(sequences)

    @staticmethod
    def _c3_merge(sequences: list[list[str]]) -> list[str]:
        """C3 merge step: pick heads not present in any tail."""
        result: list[str] = []
        while True:
            sequences = [sequence for sequence in sequences if sequence]
            if not sequences:
                return result
            for sequence in sequences:
                candidate = sequence[0]
                if not any(candidate in other[1:] for other in sequences):
                    result.append(candidate)
                    for other in sequences:
                        if other and other[0] == candidate:
                            del other[0]
                    break
            else:
                candidate = sequences[0][0]
                result.append(candidate)
                for sequence in sequences:
                    if sequence and sequence[0] == candidate:
                        del sequence[0]

    def _effective_field_layout(
            self, class_name: str, _visiting: set[str] | None = None) -> dict[str, int]:
        """Compute inherited field layout for ``class_name``."""
        if _visiting is None:
            _visiting = set()
        if class_name in _visiting:
            return {}
        _visiting.add(class_name)
        layout: dict[str, int] = {}
        for base in self._class_bases.get(class_name, []):
            for field in self._effective_field_layout(base, _visiting):
                if field not in layout:
                    layout[field] = len(layout) * 8
        own = self._class_direct_fields.get(class_name) or {}
        for field in sorted(own, key=lambda name: own[name]):
            if field not in layout:
                layout[field] = len(layout) * 8
        return layout

    def _resolve_super_call(self, call_expr) -> str | None:
        """Resolve ``super().method(...)`` to the lowered ancestor method name."""
        func = call_expr.func
        if not isinstance(func, AttributeAccess):
            return None
        obj = func.obj
        if not (isinstance(obj, CallExpr)
                and isinstance(obj.func, Identifier)
                and obj.func.name == "super"):
            return None
        if not self._current_class:
            return None
        method_name = _name(func.attr)
        for ancestor in self._mro(self._current_class)[1:]:
            key = f"{ancestor}.{method_name}"
            if key in self._class_attr_call_names:
                return self._class_attr_call_names[key]
        return None

    def _resolve_field(self, class_name: str, field_name: str) -> int | None:
        """Return byte offset of ``field_name`` in ``class_name``."""
        return (self._class_field_layouts.get(class_name) or {}).get(field_name)

    def _is_stateful_class(self, class_name: str) -> bool:
        """Return True if the class has at least one ``self.attr`` field."""
        return bool(self._class_obj_sizes.get(class_name, 0))

    def _restore_func_state(self, saved) -> None:
        """Restore function-local generation state after emitting a nested function."""
        (self._instrs, self._locals, self._loop_stack,
         self._var_class_types, self._current_class,
         self._string_len_locals, self._list_locals,
         self._dict_key_maps,
         self._lambda_locals) = saved

    def _infer_class_name(self, expr) -> str | None:
        """Infer a tracked class name from a simple expression."""
        if isinstance(expr, CallExpr):
            called_name = _name(expr.func)
            if called_name in self._class_ctor_names:
                return called_name
            if "." in called_name:
                owner_name, _method_name = called_name.split(".", 1)
                lowered = self._class_attr_call_names.get(called_name)
                if owner_name in self._class_ctor_names and lowered in self._static_method_names:
                    return owner_name
        if isinstance(expr, Identifier):
            return self._var_class_types.get(expr.name)
        return None

    def _class_method_target_from_call(self, call_expr: CallExpr) -> str | None:
        """Resolve ``obj.method(...)`` to a lowered class method when possible."""
        func = call_expr.func
        if not isinstance(func, AttributeAccess):
            return None
        obj = func.obj
        if not isinstance(obj, Identifier):
            return None
        class_name = self._var_class_types.get(obj.name)
        if not class_name:
            return None
        return self._class_attr_call_names.get(f"{class_name}.{func.attr}")

    def _emit_function(self, func_def: FunctionDef, emitted_name: str | None = None) -> None:
        """Generate WAT for a user-defined function."""
        saved = self._save_func_state()

        func_name = emitted_name or _name(func_def.name)
        param_names = _real_params(func_def)
        self._locals = set(param_names)

        self._gen_stmts(func_def.body, "    ")
        body_instrs = list(self._instrs)
        local_names = sorted(self._locals - set(param_names))

        wat_func_name = self._wat_symbol(func_name)
        lines = [f'  (func ${wat_func_name} (export "{func_name}")']
        for param_name in param_names:
            lines.append(f"    (param ${self._wat_symbol(param_name)} f64)")
        lines.append("    (result f64)")
        for local_name in local_names:
            lines.append(f"    (local ${self._wat_symbol(local_name)} f64)")
        lines.extend(body_instrs)
        lines.append("    f64.const 0  ;; implicit return")
        lines.append("  )")

        self._funcs.append("\n".join(lines))
        if self._func_render_modes.get(func_name) in _STREAM_RENDER_MODES:
            self._funcs.append(self._build_stream_buffer_helpers(func_name))
        self._restore_func_state(saved)

    def _emit_class(self, class_def: ClassDef) -> None:
        """Lower class methods to standalone WAT functions."""
        class_name = _name(class_def.name)
        self._current_class = class_name
        for member in (class_def.body or []):
            if isinstance(member, FunctionDef):
                method_name = _name(member.name)
                lowered_name = self._mangle_class_method_name(class_name, method_name)
                self._emit_function(member, emitted_name=lowered_name)
        self._current_class = None

    def _emit_dispatch_functions(self) -> None:
        """Emit WAT dispatch functions for polymorphic methods."""
        for method_name, dispatch_wat in self._dispatch_func_names.items():
            impls: list[tuple[int, str]] = []
            for class_name, class_id in sorted(self._class_ids.items(), key=lambda item: item[1]):
                own_lowered = self._mangle_class_method_name(class_name, method_name)
                if own_lowered in self._defined_func_names:
                    impls.append((class_id, own_lowered))
            if len(impls) < 2:
                continue

            lines = [
                f"  (func ${dispatch_wat} (param $self f64) (result f64)",
                "    (local $__tag i32)",
                "    ;; load type tag at self_ptr - 8",
                "    local.get $self",
                "    i32.trunc_f64_u",
                "    i32.const 8",
                "    i32.sub",
                "    i32.load",
                "    local.set $__tag",
            ]
            first_class_id, first_fn = impls[0]
            lines += [
                "    local.get $__tag",
                f"    i32.const {first_class_id}  ;; {first_fn}",
                "    i32.eq",
                "    if (result f64)",
                "      local.get $self",
                f"      call ${self._wat_symbol(first_fn)}",
            ]
            for class_id, fn_name in impls[1:-1]:
                lines += [
                    "    else",
                    "      local.get $__tag",
                    f"      i32.const {class_id}  ;; {fn_name}",
                    "      i32.eq",
                    "      if (result f64)",
                    "        local.get $self",
                    f"        call ${self._wat_symbol(fn_name)}",
                ]
            _, last_fn = impls[-1]
            lines += [
                "    else",
                "      local.get $self",
                f"      call ${self._wat_symbol(last_fn)}",
            ]
            for _ in impls[1:]:
                lines.append("    end")
            lines.append("  )")
            self._funcs.append("\n".join(lines))

    def _emit_stateful_ctor(
            self, class_name: str, ctor: str, call_expr, indent: str, keep_ref: bool) -> None:
        """Emit WAT for allocating a stateful object instance and calling ``__init__``."""
        obj_size = self._class_obj_sizes[class_name]
        alloc_size = obj_size + 8
        class_id = self._class_ids.get(class_name, 0)
        self._emit(f"{indent};; alloc {class_name} (type_tag=8 + fields={obj_size} bytes)")
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}i32.const {class_id}   ;; class_id for {class_name}")
        self._emit(f"{indent}i32.store")
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}i32.const {alloc_size}")
        self._emit(f"{indent}i32.add")
        self._emit(f"{indent}global.set $__heap_ptr")
        self._emit(f"{indent}global.get $__heap_ptr")
        self._emit(f"{indent}i32.const {obj_size}")
        self._emit(f"{indent}i32.sub")
        self._emit(f"{indent}f64.convert_i32_u  ;; self ptr as f64 (past type-tag)")
        self._gen_call_args(call_expr, indent, ctor, skip_params=1)
        self._emit(f"{indent}call ${self._wat_symbol(ctor)}")
        self._emit(f"{indent}drop  ;; discard __init__ return value")
        if keep_ref:
            self._emit(f"{indent}global.get $__heap_ptr")
            self._emit(f"{indent}i32.const {obj_size}")
            self._emit(f"{indent}i32.sub")
            self._emit(f"{indent}f64.convert_i32_u  ;; object ref as f64")

    def _emit_main(self, stmts: list) -> None:
        """Generate the exported ``__main`` entry-point function."""
        saved = self._save_func_state()

        self._gen_stmts(stmts, "    ")
        body_instrs = list(self._instrs)
        local_names = sorted(self._locals)

        lines = ['  (func $__main (export "__main")']
        for local_name in local_names:
            lines.append(f"    (local ${self._wat_symbol(local_name)} f64)")
        lines.extend(body_instrs)
        lines.append("  )")

        self._funcs.append("\n".join(lines))
        self._restore_func_state(saved)
