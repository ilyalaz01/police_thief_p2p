# Police-Thief P2P

A deterministic university implementation of the Police-Thief game with independent FastMCP
peers, partial observability, commit-reveal audit, replay verification, and schema 1.1 match
artifacts.

## Current status

The repository proves the deterministic game core, role-legal observations, the frozen
`ScentTacticalPolice` champion, policy evaluation, a four-tool reference-compatible FastMCP
transport, bounded retry/deadline/duplicate behavior, audit/replay, schema 1.1 artifact builders,
a public SDK facade, versioned configuration, a centralized bounded Gatekeeper, and offline
release/security tooling. The public quality gate passes with branch coverage above 90%, Hcommit
5/5, frozen hashes 7/7, and conformance vectors 125/125.

Historical local and public self-tests are evidence only. This repository is not yet a final
two-repository submission and is not authorization for a real-team warm-up or counted match.
The authority hierarchy is defined in [the rules baseline](RULES_AND_INTEROP_BASELINE.md), and
negotiated differences are recorded in [interop decisions](docs/INTEROP_DECISIONS.md).

## Requirements

- Python 3.11 or later;
- Git with submodule support;
- `uv` as the only project package manager and task runner;
- Windows, Linux, or WSL with filesystem access to the checkout.

The ordinary test suite is offline. Public transport, Gmail, professor-owned differential source,
and opponent infrastructure are not installation requirements.

## Installation

```bash
git clone --recurse-submodules https://github.com/ilyalaz01/police_thief_p2p.git
cd police_thief_p2p
uv sync
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
uv sync
```

Verify the installation without starting a peer:

```bash
uv run pytest
uv run ruff check src tests tools/offline_ops
uv run python external/copthief-league-protocol/verify_vectors.py
```

The professor-owned reference implementation is not redistributed. Its differential test is
classified as an environmental skip in a clean public checkout; this is not a substitute for an
authorized local differential run.

## Offline quick start

Run one deterministic simulator game through the supported SDK. This is a local simulator
experiment: it is not an interoperability test, public transport test, warm-up, or league game.

```python
from police_thief_lab import PoliceThiefSDK

sdk = PoliceThiefSDK()
result = sdk.evaluation.run_game(
    sdk.domain.GameConfig(),
    seed=7,
    police_factory=sdk.policies.ScentTacticalPolice,
    thief_factory=sdk.policies.RandomLegalThief,
)
print(result.terminal_reason, result.police_score, result.thief_score)
```

For repeatable research batches, use the SDK evaluation service or the reviewed scripts in
`experiments/`. Do not change the frozen champion during integration.

## Architecture

```text
CLI / experiments
        |
PoliceThiefSDK: domain, policies, evaluation, artifacts, transport, configuration
        |
deterministic simulator and role-legal observations
        |
interop runtime: profile, negotiation, turns, audit, replay
        |
FastMCP transport, Gatekeeper, and official artifacts
```

Each peer is a separate process with private local truth. Strategies receive observations rather
than the opponent's hidden coordinate. The [architecture plan](docs/PLAN.md) contains C4, process,
turn, audit, deployment, and artifact flows. The [SDK manual](docs/SDK.md) lists stable operations.

## Peer CLI reference

Inspect the complete interface without starting a peer:

```bash
uv run python -m police_thief_lab.peer_cli --help
```

The command starts one peer process and requires a separately prepared counterpart. Its options
are input/delegation controls; no flag grants permission to contact an opponent or report a game.

| Option | Meaning |
|---|---|
| `--role {police,thief}` | Required local role |
| `--profile PATH` | Required negotiated MatchProfile JSON |
| `--host HOST` | Local listener host; default `127.0.0.1` |
| `--port PORT` | Required local listener port |
| `--opponent-url URL` | Required opponent FastMCP `/mcp` endpoint |
| `--advertised-url URL` | MCP URL advertised as this peer's identity |
| `--public` | Require public HTTPS endpoint validation |
| `--group-id ID` | Local group identity metadata |
| `--group-name NAME` | Local display-name metadata |
| `--git-commit VALUE` | Exact opaque local commit identity |
| `--real-team` | Enable stricter commit preflight; not authorization |
| `--operational-config PATH` | Strict versioned startup-classification JSON |
| `--artifacts DIR` | Required output directory for schema 1.1 artifacts |
| `--output PATH` | Required peer-result JSON path |
| `--seed INTEGER` | Deterministic local seed; default `1` |

The local two-process system test is the safest executable peer example:

```bash
uv run pytest -q tests/system/test_phase4a_process.py --no-cov
```

## Operational modes and authorization

Keep these operation classes distinct:

| Operation | Network | Counts | Authorization |
|---|---|---:|---|
| Local simulator experiment | None | No | Ordinary offline development |
| Local interoperability/system test | Loopback only | No | Ordinary offline validation |
| Historical public self-test | Public HTTPS to our own peers | No | Evidence only; not automatically reusable |
| Real-team uncounted warm-up | Public opponent endpoints | No | Explicit human decision plus completed bilateral worksheet |
| Counted league game | Public opponent endpoints and reporting | Yes | Separate explicit authorization after a successful warm-up |

`--public`, `--real-team`, an operational JSON mode, or a valid Git commit does not authorize an
external operation. Follow the [real-team runbook](docs/REAL_TEAM_WARMUP_RUNBOOK.md); unresolved
Rule 47, scent, barrier, artifact, profile, or consensus responses block play.

## Configuration

Configuration has deliberately separate authority domains:

- `config/operational.self-test.v1.json` classifies startup as `offline`, `self_test`, or
  `real_team`; `counted` is unsupported;
- `config/rate_limits.v1.json` controls bounded FastMCP admission, worker concurrency, queue depth,
  and sanitized monitoring;
- `interop/fixtures/*.json` contains named match/profile fixtures governed by interoperability
  authority, not operational configuration;
- `.env-example` documents optional path selectors only. It contains no secret values.

Select operational configuration with `--operational-config` or
`POLICE_THIEF_CONFIG_PATH`. Select the rate policy with `POLICE_THIEF_RATE_LIMITS_PATH`.
Unknown fields, incompatible versions, invalid values, and mode mismatches fail before peer side
effects. See [configuration](docs/CONFIGURATION.md) for exact schemas and boundaries.

## Outputs and artifacts

A completed peer run writes its requested result JSON plus official schema 1.1 artifacts under
the requested artifact directory:

- `declaration_<game_id>.json`;
- `config_<game_id>_g<NN>.json`;
- `log_<game_id>_g<NN>.json`;
- `result_<game_id>.json`.

Pretty disk JSON, canonical object hashing, and final consensus serialization are distinct. Never
compare or rewrite one scope as another. Output directories must be operator-selected and must not
contain credentials, live tunnel configuration, private correspondence, or retained operational
nonces. The [release manual](docs/RELEASE_ENGINEERING.md) explains offline validation, secret
scanning, and deterministic packaging.

## Verification and quality gate

Run the fail-closed composed gate:

```bash
uv run python -m tools.offline_ops.cli quality-gate
```

It composes pytest/coverage, Ruff, Hcommit vectors, frozen-manifest verification, the pinned
conformance kit, and retained-evidence secret scanning. Match-artifact validation is optional only
when no match path is requested; an unavailable required validator is a failure.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| `uv` is not found | Install `uv`, reopen the shell, and run `uv sync`; do not substitute `pip` |
| Submodule verifier path is missing | Run `git submodule update --init --recursive` |
| Professor differential test skips | Expected in a public clone; do not copy private source into the repository |
| Operational schema/version error | Compare the file with `config/operational.self-test.v1.json`; unknown fields fail closed |
| Operation-mode mismatch | Use `self_test` without `--real-team`, or an approved `real_team` config with it |
| Public endpoint rejected | Public mode requires a valid HTTPS `/mcp` URL; do not weaken validation |
| HTTP 421 behind a tunnel | Preserve the documented origin host-header configuration in the warm-up runbook |
| Real-team commit refused | Each operator must supply that team's exact non-placeholder commit |
| Profile/config/consensus mismatch | Stop and reconcile explicitly; never guess or silently normalize |
| Quality gate exits nonzero | Read the sanitized failing check, fix that scope, and rerun the same command |

## Contributing

Use a focused branch, RED-GREEN-REFACTOR evidence, meaningful commits, and a Pull Request with
scope, tests, risks, and blockers. Run the full offline gates before merge. Every contributor uses
their own Git identity; do not rewrite authorship or fabricate earlier planning/history.

Changes to rules, scoring, `ScentTacticalPolice`, profile/config bytes, Hcommit, scent, wire,
retry/deadline/duplicate behavior, audit/replay, artifacts, or consensus require explicit authority
review. See [CONTRIBUTING](CONTRIBUTING.md) and the [live TODO](docs/TODO.md).

## Submission-readiness limits

This shared development repository is not the final course submission. Higher-authority work still
requires two separate role repositories (Police and Thief), a Live GUI belief-map view, a Replay
view with `Verified OK`, documented screenshots, annotated `v1.0-submission` tags, and human-gated
league/Moodle steps. Counted games and Gmail reporting remain blocked without explicit approval.
The exact evidence and owners are tracked in
[official submission readiness](docs/OFFICIAL_SUBMISSION_READINESS.md).

## Documentation and governance

Retrospective baseline created after the validated prototype.
These documents did not exist before the prototype and do not claim otherwise.

The baseline is honest: historical pre-code PRD/TDD/prompt evidence cannot be recreated. Future
changes follow the documented workflow and produce inspectable evidence.

- [Product requirements](docs/PRD.md)
- [As-built architecture plan](docs/PLAN.md)
- [Live task source of truth](docs/TODO.md)
- [Guidelines compliance matrix](docs/GUIDELINES_COMPLIANCE_MATRIX.md)
- [Official submission readiness](docs/OFFICIAL_SUBMISSION_READINESS.md)
- [Quality plan](docs/QUALITY_PLAN.md)
- [Test architecture](docs/TESTING.md)
- [Critical-path map](docs/QUALITY_CRITICAL_PATHS.md)
- [Concurrency and capacity](docs/CONCURRENCY_AND_CAPACITY.md)
- [Operational configuration](docs/CONFIGURATION.md)
- [SDK entry point](docs/SDK.md)
- [Architecture decisions](docs/adr/README.md)
- [Prompt engineering log](docs/PROMPT_ENGINEERING_LOG.md)
- [Release engineering](docs/RELEASE_ENGINEERING.md)

## License and credits

Project-authored code is licensed under the [MIT License](LICENSE). The independently versioned
[copthief-league-protocol](https://github.com/Imreec/copthief-league-protocol) conformance kit is an
MIT-licensed Git submodule. FastMCP and all Python dependencies retain their upstream licenses.
The official assignment/book and professor reference implementation remain professor-owned and
are not redistributed by this repository.
