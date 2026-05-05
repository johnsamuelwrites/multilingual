#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Helpers for multilingual source-file extensions."""

from pathlib import Path


PREFERRED_SOURCE_EXTENSION = ".multi"
LEGACY_SOURCE_EXTENSION = ".ml"
SOURCE_EXTENSIONS = (
    PREFERRED_SOURCE_EXTENSION,
    LEGACY_SOURCE_EXTENSION,
)


def has_source_extension(path: str | Path) -> bool:
    """Return whether *path* ends with a supported source extension."""
    return Path(path).suffix.lower() in SOURCE_EXTENSIONS


def find_package_init(directory: str | Path) -> Path | None:
    """Return the first supported package initializer in *directory*."""
    base = Path(directory)
    for ext in SOURCE_EXTENSIONS:
        candidate = base / f"__init__{ext}"
        if candidate.is_file():
            return candidate
    return None


def find_module_source(base_dir: str | Path, module_name: str) -> Path | None:
    """Return the first supported source file for *module_name* in *base_dir*."""
    base = Path(base_dir)
    for ext in SOURCE_EXTENSIONS:
        candidate = base / f"{module_name}{ext}"
        if candidate.is_file():
            return candidate
    return None


def iter_source_files(directory: str | Path, pattern_prefix: str) -> list[Path]:
    """Return unique supported source files matching *pattern_prefix*."""
    base = Path(directory)
    seen: set[Path] = set()
    matches: list[Path] = []
    for ext in SOURCE_EXTENSIONS:
        for path in sorted(base.glob(f"{pattern_prefix}{ext}")):
            if path not in seen:
                seen.add(path)
                matches.append(path)
    return matches
