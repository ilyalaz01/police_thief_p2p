# Police-Thief P2P — Police

This is the Police role repository for the university Police-Thief P2P project. It contains the
same verified shared engine, protocol runtime, SDK, audit/replay, GUI, tests, and release tooling
as the Thief repository; the role identity and runtime policy below are the deliberate differences.

## Role identity

- Runtime role: `police`
- Runtime policy: `ScentTacticalPolice`
- Policy status: `FROZEN_ACCEPTED`

`ScentTacticalPolice` is the accepted frozen competitive Police policy. Integration and release
work must not change it or the accepted physics, observations, Hcommit, scent, MCP, artifact,
profile, consensus, retry, deadline, duplicate, audit, replay, or scoring semantics.

## Install and validate offline

Requirements are Python 3.11+, Git with submodule support, and `uv`.

```bash
git submodule update --init --recursive
uv sync
uv run python -m police_thief_lab.peer_cli --help
uv run pytest -q tests/system/test_phase4a_process.py --no-cov
uv run python -m tools.offline_ops.cli quality-gate
```

The system test is a loopback interoperability test. It is not authorization for public
transport, another-team contact, a warm-up, or a counted league operation.

## Local simulator use

The supported SDK can run deterministic, network-free simulator experiments. The repository-wide
[user manual](docs/PRD.md) and root package API describe the shared components. Local simulator
results do not prove public transport or opponent compatibility and do not count for the league.

## Live GUI and verified Replay

Inspect the loopback-only Live GUI command without connecting to another team:

```bash
uv run python -m police_thief_lab.viewer_cli live \
  --snapshot artifacts/police-live.json --host 127.0.0.1 --port 8765
```

After an authorized game has ended and matching artifacts are available, create an offline Replay:

```bash
uv run python -m police_thief_lab.viewer_cli replay \
  --log artifacts/log_<game-id>_g01.json \
  --config artifacts/config_<game-id>_g01.json \
  --output artifacts/replay_<game-id>_g01.html
```

The Live view is role-local and cannot carry objective opponent coordinates. Replay verifies the
revealed log before showing `Verified OK`. See [the viewer guide](docs/REPLAY_VIEWER.md).

## Official repository layout

Rule 49 requires separate Police and Thief repositories with reciprocal README links. The future
counterpart repository URL is currently: `PENDING_HUMAN_APPROVAL`.

The placeholder is not a valid cross-link and must remain blocking until the exact Thief URL and
both final repository contents are approved.

Rule 50 requires this README plus the following retained project materials:

- [versioned configuration](config/);
- [product requirements](docs/PRD.md);
- [architecture plan](docs/PLAN.md);
- [live TODO](docs/TODO.md).

## Governance and operational limits

The [authority baseline](RULES_AND_INTEROP_BASELINE.md) controls game and interoperability facts.
The [official readiness ledger](docs/OFFICIAL_SUBMISSION_READINESS.md) separates proven local
evidence from pending human, bilateral, network, league, and submission steps. A valid CLI flag,
commit, artifact, or offline test is not authorization for an external operation.

Use focused branches, truthful authorship, coherent commits, Pull Requests, and the full offline
quality gate. Never invent a bilateral agreement or rewrite accepted frozen behavior.

## License and credits

Project-authored code is MIT-licensed; see [LICENSE](LICENSE). The separately versioned
`copthief-league-protocol` conformance kit retains its own MIT license. Official assignment and
professor-owned materials are not redistributed.
