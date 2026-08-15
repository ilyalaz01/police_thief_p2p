# Contributing

## Workflow

1. Create a focused branch from the current validated baseline.
2. Keep each commit limited to one coherent change.
3. Add or update deterministic tests with implementation changes.
4. Run the relevant local checks before every commit.
5. Open a Pull Request and document scope, evidence, risks, and remaining blockers.
6. Merge only after review and green required checks.

Recommended branch prefixes are `feature/`, `fix/`, `docs/`, `test/`, and `chore/`.

Commit messages use an imperative summary and explain the project outcome, for example:

```text
feat: add offline artifact validation command
test: cover path traversal and timeout failures
docs: document release recovery procedure
```

Every contributor must commit with their own Git identity. Authored commits must not be squashed
or reassigned without agreement during review.

## Required checks

```bash
uv run pytest
uv run ruff check src tests
uv run python external/copthief-league-protocol/verify_vectors.py
```

Tests must be deterministic and network-free unless a separately authorized interoperability or
public-transport procedure explicitly requires network access.

## Protected semantics

Changes to game rules, scoring, profile bytes, consensus scope, serialization, cryptography,
audit/replay behavior, frozen policies, or external dependencies require an explicit architecture
and interoperability review. Differences must never be resolved silently.

No commit may contain credentials, live endpoints, private audit bodies, operational nonces,
personal correspondence, generated environments, or professor-owned implementation code.

## Review checklist

- Scope matches the issue or workstream specification.
- Tests cover success and failure paths.
- Coverage remains at or above the configured threshold.
- Ruff and conformance checks pass.
- Documentation matches observable behavior.
- No unrelated files or generated outputs are included.
- Remaining limitations and human blockers are stated explicitly.
