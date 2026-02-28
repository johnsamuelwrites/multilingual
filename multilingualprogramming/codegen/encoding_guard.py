#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Encoding guardrails for generated compiler/runtime artifacts."""

from pathlib import Path

_MOJIBAKE_MARKERS = (
    "\ufffd",   # replacement character
    "Ã",
    "Â",
    "â€”",
    "â€“",
    "â€œ",
    "â€",
    "â€˜",
    "â€™",
    "â€¦",
    "â†’",
    "â‰¥",
)


def detect_text_encoding_issues(text: str) -> list[str]:
    """Return a list of encoding/mojibake issues detected in *text*."""
    issues = []
    if text.startswith("\ufeff"):
        issues.append("utf8_bom_present")
    for marker in _MOJIBAKE_MARKERS:
        if marker in text:
            issues.append(f"suspicious_marker:{marker}")
    return issues


def assert_clean_text_encoding(label: str, text: str) -> None:
    """Raise ValueError when text contains BOM or mojibake markers."""
    issues = detect_text_encoding_issues(text)
    if issues:
        joined = ", ".join(issues)
        raise ValueError(f"{label} contains encoding issues: {joined}")


def assert_clean_utf8_file(path: str | Path) -> None:
    """Validate file can be decoded as UTF-8 and has no known mojibake markers."""
    fpath = Path(path)
    content = fpath.read_text(encoding="utf-8")
    assert_clean_text_encoding(str(fpath), content)
