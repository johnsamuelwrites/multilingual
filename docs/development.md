# Development and Debugging Guide

This guide is for contributors who prefer Python-native workflows (`python -m ...`)
for development, testing, and debugging.

## Setup

Use a virtual environment and editable install so code changes are picked up
without reinstalling on every edit.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

If your shell does not support extras syntax, run:

```bash
python -m pip install -e .
python -m pip install pytest pytest-cov pylint
```

## CLI During Development

Installed CLI commands (end-user style):

```bash
multilingual repl
multilingual run hello.ml
multilg run hello.ml
```

Python module style (recommended while developing/debugging):

```bash
python -m multilingualprogramming repl
python -m multilingualprogramming run hello.ml --lang fr
python -m multilingualprogramming compile hello.ml
python -m multilingualprogramming smoke --all
```

Use module style when you want certainty about which Python interpreter and
environment are executing the code.

## Targeted Tests

Run all tests:

```bash
python -m pytest -q
```

Run one test file:

```bash
python -m pytest -q tests/parser_test.py
```

Run a focused subset:

```bash
python -m pytest -q tests/parser_test.py -k "async or comprehension"
```

Show print output during debugging:

```bash
python -m pytest -q -s tests/repl_test.py
```

## Lint and Basic Quality Checks

```bash
python -m pylint $(git ls-files '*.py')
```

On Windows PowerShell, if command substitution is unavailable in your shell:

```powershell
python -m pylint (git ls-files '*.py')
```

## Build Docs Locally

Stage root markdown files into `docs/` and run a strict MkDocs build:

```bash
python tools/stage_docs.py
python -m mkdocs build --strict
```

## Debugging Tips

Debug CLI path with Python module execution:

```bash
python -m multilingualprogramming repl --show-python
```

Debug parser/codegen behavior quickly:

```bash
python -m multilingualprogramming compile examples/surface_for_es.ml --lang es
```

Use temporary breakpoints in code:

```python
breakpoint()
```

Then run the exact module path you are testing:

```bash
python -m multilingualprogramming run examples/arithmetics_en.ml --lang en
```

## Packaging Sanity Check

After entry-point changes in `pyproject.toml`, reinstall editable package:

```bash
python -m pip install -e .
```

Then verify commands:

```bash
multilingual --version
multilg --version
python -m multilingualprogramming --version
```
