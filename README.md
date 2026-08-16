# Police-Thief P2P

A deterministic university implementation of the Police-Thief game with independent FastMCP
peers, partial observability, commit-reveal audit, replay verification, and schema 1.1 match
artifacts.

## Current status

- deterministic game rules and simulator;
- frozen Police champion: `ScentTacticalPolice`;
- belief/search evaluation framework and Thief baselines;
- four-tool reference-compatible FastMCP transport;
- bounded retries, deadlines, duplicate handling, audit, and replay;
- official schema 1.1 artifact builders;
- one documented `PoliceThiefSDK` entry point for domain, policy, evaluation, artifact, transport,
  and configuration operations;
- local and public self-play validation;
- more than 90% branch coverage and 125/125 conformance vectors.

The rule and interoperability authority hierarchy is defined in
`RULES_AND_INTEROP_BASELINE.md`. Negotiated decisions are recorded in
`docs/INTEROP_DECISIONS.md`.

## Architecture

```text
policy / evaluation
        |
deterministic simulator and role-legal observations
        |
interop runtime: profile, negotiation, turns, audit, replay
        |
FastMCP transport and official artifacts
```

Release Engineering and Offline Operations is an independent subsystem specified in
`docs/RELEASE_ENGINEERING_WORKSTREAM.md`.

## Installation

Requirements: Python 3.11 or later, Git, and `uv`.

```bash
git clone --recurse-submodules https://github.com/ilyalaz01/police_thief_p2p.git
cd police_thief_p2p
uv sync
```

## Verification

```bash
uv run pytest
uv run ruff check src tests
uv run python external/copthief-league-protocol/verify_vectors.py
```

The professor-owned reference implementation is not redistributed. Exact professor differential
tests run only in an authorized local workspace and report an explicit skip when that dependency
is absent.

## SDK entry point

```python
from police_thief_lab import PoliceThiefSDK

sdk = PoliceThiefSDK()
config = sdk.domain.GameConfig()
result = sdk.evaluation.run_game(
    config,
    seed=7,
    police_factory=sdk.policies.ScentTacticalPolice,
    thief_factory=sdk.policies.RandomLegalThief,
)
```

The [SDK manual](docs/SDK.md) lists the six services and the typed CLI delegation boundary.

## Operational safety

The repository contains no live credentials, tunnel configuration, private audit bodies, or
counted-match authorization. Real-team play requires the explicit gates in
`docs/REAL_TEAM_WARMUP_RUNBOOK.md`.

Optional startup classification uses the strict versioned JSON boundary documented in
[Operational configuration](docs/CONFIGURATION.md). The tracked self-test example contains no
credentials and cannot authorize public, real-team, or counted activity.

Development workflow and review requirements are documented in `CONTRIBUTING.md`.

## Documentation and governance

Retrospective baseline created after the validated prototype.
These documents did not exist before the prototype and do not claim otherwise.

Phase 4D0 established the retrospective documentation/governance baseline. Later accepted changes
closed the 150-line, versioned-configuration, and SDK-entry-point gaps, but this does not mean full
Software Project Guidelines compliance, real-team readiness, or counted-match readiness; overall
compliance remains **PARTIAL**.

- [Product requirements](docs/PRD.md)
- [As-built architecture plan](docs/PLAN.md)
- [Live task source of truth](docs/TODO.md)
- [Guidelines compliance matrix](docs/GUIDELINES_COMPLIANCE_MATRIX.md)
- [Quality plan](docs/QUALITY_PLAN.md)
- [Operational configuration](docs/CONFIGURATION.md)
- [SDK entry point](docs/SDK.md)
- [Architecture decision records](docs/adr/README.md)
- [Prompt engineering log](docs/PROMPT_ENGINEERING_LOG.md)
- [Release engineering workstream specification](docs/RELEASE_ENGINEERING_WORKSTREAM.md)

## License

Project-authored code is licensed under the MIT License. The conformance kit is an independently
versioned MIT-licensed Git submodule.
