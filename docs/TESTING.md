# Test Architecture

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

The default suite is deterministic, offline, and split by the boundary exercised. Public transport
checks and real-team operations remain separately authorized procedures and are not ordinary tests.

## Layer boundaries

- **Unit tests** in `tests/unit/` isolate rules, models, scent, observations, and policies. They do
  not start processes, use public endpoints, or depend on retained operational evidence.
- **Integration tests** in `tests/integration/` exercise local contracts across configuration,
  artifacts, SDK, governance, FastMCP transport, retry, and audit/replay components.
- **System tests** in `tests/system/` exercise a complete local multi-process peer flow. They are
  still offline and use only loopback transport.
- `tests/offline_ops/` is the separately owned release-engineering workstream namespace. It may
  not import or change game behavior and remains outside this core-suite reorganization.

Pytest assigns the `unit`, `integration`, `system`, or `offline_ops` marker from the first directory
below `tests/`. Run one layer with `uv run pytest -m <marker>`.

## Shared fixtures

`tests/conftest.py` owns shared repository-root, match-profile, and free-local-port fixtures.
Non-fixture builders and immutable expected values live under `tests/support/`; test modules must
not recreate path-depth assumptions or leave helper modules at the test root.

## Source-to-test map

| Production or contract area | Primary test location | Expected boundary |
|---|---|---|
| `models.py`, `rules.py`, `scent.py`, `turns.py` | `tests/unit/test_game/` | Pure deterministic state and rule behavior |
| `policies/**` and policy evaluation helpers | `tests/unit/test_policies/` | Observation-only actions and seeded decisions |
| `evaluation.py` | `tests/integration/test_evaluation/` | Reproducible batches and aggregation |
| `configuration.py`, `gatekeeper.py` | `tests/integration/test_configuration/` | Files, strict schemas, queues, and safe failures |
| `league/**` outer-series contracts | `tests/unit/test_league/` | Appendix-B bytes, six slots, identity/provenance, score and refusal paths |
| Artifact and consensus builders | `tests/integration/test_artifacts/` | Exact bytes, hashes, schemas, scoring, and scope |
| Runtime, crypto, transport, retry, audit/replay | `tests/integration/test_interop/` | Local component and FastMCP contracts |
| SDK, frozen manifest, project governance | `tests/integration/test_governance/` | Cross-package and repository invariants |
| Complete two-peer local process | `tests/system/` | End-to-end offline process completion |

Every production change must add or update normal and error-path coverage in the mapped layer.
Shared deterministic fixtures belong in `conftest.py`; external services are mocked or replaced by
local fakes. Test and support Python files remain within the 150 counted-line limit.

## Commands

```bash
uv run pytest --collect-only -q --no-cov
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m system
uv run pytest
uv run ruff check src tests
```

The configured full run enforces branch coverage of at least 85%. Missing, skipped, or unavailable
required validators are not release evidence. Retention and critical-path requirements are defined
in `docs/QUALITY_PLAN.md`.
