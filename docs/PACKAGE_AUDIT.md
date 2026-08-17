# Python Package and Dependency Audit

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: package organization is accepted for the shared repository. This audit changes metadata
and documentation only; it does not authorize final two-repository submission assembly.

## Definition and metadata

- `pyproject.toml` is the dependency/build source of truth: package `police-thief-lab`, version
  `1.0.0`, MIT license, and team-level author metadata.
- `src/police_thief_lab/__init__.py` exposes the same `__version__ = "1.0.0"` and explicit public
  `__all__` surface.
- `uv.lock` is tracked; no `requirements.txt` exists. The documented workflow is **uv-only**.
- Runtime dependency `fastmcp==3.4.3` is exactly constrained. Development ranges are resolved to
  exact artifacts by `uv.lock`; the lockfile remains the reproducible installation evidence.
- **No dependency change** was made in Phase 4D8.

## Package boundaries and exports

All Python package directories contain `__init__.py`. The consumer-facing root and the
`evaluation`, `interop`, `policies`, `presentation`, and `sdk` packages declare explicit `__all__`
lists. `PoliceThiefSDK` remains the single supported consumer facade; legacy imports remain for
validated compatibility rather than creating a second implementation.

An AST regression rejects absolute internal imports such as `from police_thief_lab...` inside the
package. Current internal imports are relative, while tests and consumers correctly import the
installed package name. Filesystem operations accept operator paths or derive repository/package
paths; production code contains no user-specific absolute path.

## Attribution and external code

- Project-authored code is MIT-licensed by the root `LICENSE`.
- `external/copthief-league-protocol` is a separately attributed MIT Git submodule and remains
  outside the project package, lint ownership and source-authority boundary.
- Professor reference material is not packaged or redistributed in the public repository.

## Maintainability review

The 150-counted-line regression covers `src/` and tests; the release-engineering workstream checks
its own files. Runtime concerns are separated into single-purpose mixins, SDK services contain
aliases/delegation rather than copied business logic, and artifact encoding/writing helpers are
shared. The Phase 4D8 docstring inventory covers editable `src/` and `tools/` production symbols.

This is a structural and review-backed DRY assessment, not a mathematical proof that no two token
sequences resemble each other. Any future duplicated behavior found in review reopens `PKG-001`.

## Reproduction

```bash
uv sync --locked
uv run pytest -q tests/integration/test_governance/test_package_building_blocks.py --no-cov
uv run ruff check src tests tools
uv run python -m tools.offline_ops.cli quality-gate
```

The last command composes tests, Ruff, Hcommit vectors, frozen hashes, the conformance kit and a
fail-closed secret scan. It starts no peer, tunnel, Gmail action, opponent contact or gameplay.
