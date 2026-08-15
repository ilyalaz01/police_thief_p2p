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

## Operational safety

The repository contains no live credentials, tunnel configuration, private audit bodies, or
counted-match authorization. Real-team play requires the explicit gates in
`docs/REAL_TEAM_WARMUP_RUNBOOK.md`.
