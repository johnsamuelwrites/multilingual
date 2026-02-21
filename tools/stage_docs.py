"""Stage root markdown files into docs/ for MkDocs builds."""

from pathlib import Path


def _copy_text(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def _rewrite(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    """Generate docs/index.md and docs/_generated content for MkDocs builds."""
    root = Path(__file__).resolve().parent.parent
    docs_dir = root / "docs"
    generated_dir = docs_dir / "_generated"

    _copy_text(root / "README.md", docs_dir / "index.md")
    _copy_text(root / "RELEASE.md", generated_dir / "RELEASE.md")
    _copy_text(root / "CONTRIBUTING.md", generated_dir / "CONTRIBUTING.md")
    _copy_text(root / "USAGE.md", generated_dir / "USAGE.md")
    _copy_text(root / "examples" / "README.md", generated_dir / "examples" / "README.md")

    index_path = docs_dir / "index.md"
    index_text = index_path.read_text(encoding="utf-8")
    index_text = _rewrite(
        index_text,
        [
            ("](docs/README.md)", "](reference.md)"),
            ("](docs/", "]("),
            ("](README.md)", "](index.md)"),
            ("](USAGE.md)", "](_generated/USAGE.md)"),
            ("](examples/README.md)", "](_generated/examples/README.md)"),
            ("](CONTRIBUTING.md)", "](_generated/CONTRIBUTING.md)"),
        ],
    )
    index_path.write_text(index_text, encoding="utf-8")

    usage_path = generated_dir / "USAGE.md"
    usage_text = usage_path.read_text(encoding="utf-8")
    usage_text = usage_text.replace("](docs/", "](../")
    usage_text = usage_text.replace("](README.md)", "](../index.md)")
    usage_text = usage_text.replace("](../README.md)", "](../index.md)")
    usage_path.write_text(usage_text, encoding="utf-8")


if __name__ == "__main__":
    main()
