#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""
Runtime built-in functions for the multilingual programming language.

Provides a namespace dict of built-in functions that are injected into
the execution environment so that multilingual identifiers (e.g., the
Hindi word for "print") resolve to Python built-ins.
"""

import json
from pathlib import Path

from multilingualprogramming.keyword.keyword_registry import KeywordRegistry


class RuntimeBuiltins:
    """
    Builds a dict of built-in names that should be available at runtime.

    For a given source language, the keyword used for PRINT, INPUT, and
    type keywords are mapped to the corresponding Python built-ins.

    Usage:
        builtins = RuntimeBuiltins("fr").namespace()
        # {'afficher': <built-in function print>,
        #  'saisir':   <built-in function input>, ...}

    The returned dict is intended to be merged into the exec() globals
    so that transpiled code can call built-in functions by their
    multilingual names.
    """

    # Mapping from USM concept ID to the Python built-in object
    _CONCEPT_TO_BUILTIN = {
        "PRINT": print,
        "INPUT": input,
        "TYPE_INT": int,
        "TYPE_FLOAT": float,
        "TYPE_STR": str,
        "TYPE_BOOL": bool,
        "TYPE_LIST": list,
        "TYPE_DICT": dict,
    }

    # Additional Python built-ins available in every language
    _UNIVERSAL_BUILTINS = {
        "len": len,
        "range": range,
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "map": map,
        "filter": filter,
        "isinstance": isinstance,
        "type": type,
        "hasattr": hasattr,
        "getattr": getattr,
        "setattr": setattr,
        "repr": repr,
        "round": round,
        "open": open,
        "iter": iter,
        "next": next,
        "any": any,
        "all": all,
        "chr": chr,
        "ord": ord,
        "hex": hex,
        "oct": oct,
        "bin": bin,
        "id": id,
        "hash": hash,
        "callable": callable,
        "dir": dir,
        "vars": vars,
        "super": super,
        "property": property,
        "staticmethod": staticmethod,
        "classmethod": classmethod,
        "print": print,
        "input": input,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "frozenset": frozenset,
        "bytes": bytes,
        "bytearray": bytearray,
        "memoryview": memoryview,
        "object": object,
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "KeyError": KeyError,
        "IndexError": IndexError,
        "AttributeError": AttributeError,
        "RuntimeError": RuntimeError,
        "StopIteration": StopIteration,
        "ZeroDivisionError": ZeroDivisionError,
        "FileNotFoundError": FileNotFoundError,
        "IOError": IOError,
        "OSError": OSError,
        "ImportError": ImportError,
        "NotImplementedError": NotImplementedError,
        "True": True,
        "False": False,
        "None": None,
    }

    _BUILTIN_ALIAS_CATALOG = None

    def __init__(self, source_language="en"):
        self._language = source_language
        self._registry = KeywordRegistry()

    @classmethod
    def _load_builtin_alias_catalog(cls):
        """Load localized built-in aliases from resources."""
        if cls._BUILTIN_ALIAS_CATALOG is not None:
            return cls._BUILTIN_ALIAS_CATALOG

        path = (
            Path(__file__).resolve().parent.parent
            / "resources" / "usm" / "builtins_aliases.json"
        )
        with open(path, "r", encoding="utf-8-sig") as handle:
            cls._BUILTIN_ALIAS_CATALOG = json.load(handle)
        return cls._BUILTIN_ALIAS_CATALOG

    @classmethod
    def _localized_builtin_aliases(cls, language):
        """Return alias->builtin map for a given language."""
        catalog = cls._load_builtin_alias_catalog()
        aliases = {}
        for canonical, by_language in catalog.get("aliases", {}).items():
            builtin_obj = cls._UNIVERSAL_BUILTINS.get(canonical)
            if builtin_obj is None or not isinstance(by_language, dict):
                continue
            for alias in by_language.get(language, []):
                aliases[alias] = builtin_obj
        return aliases

    def namespace(self):
        """
        Return a dict mapping multilingual names to Python built-ins.

        Includes:
        1. Language-specific keyword mappings (PRINT -> afficher, etc.)
        2. Universal Python built-ins (len, range, abs, etc.)
        """
        ns = dict(self._UNIVERSAL_BUILTINS)

        # Add language-specific mappings
        for concept, builtin_obj in self._CONCEPT_TO_BUILTIN.items():
            try:
                keyword = self._registry.get_keyword(concept, self._language)
                ns[keyword] = builtin_obj
            except Exception:
                pass  # Skip if concept not found for this language
        for alias, builtin_obj in self._localized_builtin_aliases(
            self._language
        ).items():
            # Keep canonical names stable if an alias collides.
            if alias not in ns:
                ns[alias] = builtin_obj

        return ns

    @classmethod
    def all_languages_namespace(cls):
        """
        Return a namespace containing built-in mappings for ALL supported
        languages simultaneously. Useful for multi-language environments.
        """
        ns = dict(cls._UNIVERSAL_BUILTINS)
        registry = KeywordRegistry()

        for lang in registry.get_supported_languages():
            for concept, builtin_obj in cls._CONCEPT_TO_BUILTIN.items():
                try:
                    keyword = registry.get_keyword(concept, lang)
                    ns[keyword] = builtin_obj
                except Exception:
                    pass
            for alias, builtin_obj in cls._localized_builtin_aliases(
                lang
            ).items():
                # Keep canonical names stable if an alias collides.
                if alias not in ns:
                    ns[alias] = builtin_obj

        return ns
