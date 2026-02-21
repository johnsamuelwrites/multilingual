# Releasing

This project publishes to PyPI via GitHub Actions trusted publishing.

## Preconditions

1. PyPI trusted publisher configured for this repository/workflow.
2. GitHub environment `pypi` exists and is allowed to run release jobs.
3. Branch protection requires CI checks listed in `CONTRIBUTING.md`.

## Release Checklist

1. Update `multilingualprogramming/version.py` with the new version.
2. Add release notes to `CHANGELOG.md` under a new version heading.
3. Run local checks:
```bash
python -m pytest -q
python -m pylint (git ls-files '*.py')
```
4. Push changes to `main`.
5. Create and push a version tag:
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```
6. Verify workflow `Release to PyPI` succeeds.
7. Confirm package availability on PyPI.

## Post-release

1. Create a GitHub release for tag `vX.Y.Z`.
2. Move changelog placeholders under `Unreleased` as needed.
