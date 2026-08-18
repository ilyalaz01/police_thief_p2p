# Product Requirements Document

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: retrospective requirements baseline; overall guideline compliance is **PARTIAL**.

## Product and context

Police-Thief P2P is a deterministic university prototype for independently running Police and
Thief peers. It provides role-legal partial observations, game simulation, policy evaluation,
reference-compatible FastMCP exchange, commit-reveal audit/replay, and schema 1.1 artifacts. It
exists to make rule correctness, interoperability, and experimental claims inspectable. It is
not a production service or a claim of real-team or counted-match readiness.

Stakeholders are the course owner (rules and assessment), project maintainers, peer-team
operators, reviewers, and researchers. Target users are developers validating game mechanisms,
researchers comparing deterministic policies, and—only after explicit human gates—operators of
an uncounted compatibility exercise.

## Problem, goals, and measures

The problem is to implement a partially observable two-process game without leaking hidden truth
or silently diverging on rules, bytes, deadlines, or audit results. The validated prototype
solves the local game core, the offline six-sub-game runtime/artifact rehearsal, and the generic
professional-project controls. Official final delivery still requires role repositories, real
operator values and bilateral locks, authorized Gmail reporting, and human/external operations.

Measurable goals and KPIs:

- preserve 7/7 frozen hashes and 5/5 Hcommit vectors on every accepted change;
- keep the network-free suite green with branch coverage at least 85% and Ruff at zero errors;
- keep the pinned conformance verifier at 125/125;
- reject mismatched profiles before play and make replay/audit deterministic;
- maintain traceability from every documented compliance gap to one stable TODO ID;
- allow no real-team readiness claim while required bilateral fields remain unresolved.

## Requirements

Functional requirements:

- FR-1: model legal movement, barriers, capture, survival, scoring, and alternating Thief-first
  turns according to the higher-authority baseline.
- FR-2: expose only role-legal observations to policies and support deterministic replay.
- FR-3: evaluate interchangeable Police and Thief decision backends reproducibly.
- FR-4: negotiate exact terms/profile domains, exchange four FastMCP tools, and enforce the
  frozen retry/deadline/duplicate contract.
- FR-5: seal complete action records, verify reveal/audit chains, and generate the official four
  artifact families without conflating serialization scopes.
- FR-6: provide offline, reproducible quality and conformance evidence.

Non-functional requirements:

- NFR-1 correctness: deterministic tests, ≥85% configured branch coverage, frozen-hash guards.
- NFR-2 security: no hidden-state leakage, credentials, live endpoints, operational nonces, or
  private/professor source publication.
- NFR-3 interoperability: preserve byte/hash semantics and fail closed on unresolved agreements.
- NFR-4 maintainability: documented interfaces, ADRs, TDD, Ruff, and a live task ledger.
- NFR-5 performance: decisions and transport complete inside negotiated budgets; evaluations are
  reproducible and report timing rather than promising unmeasured throughput.
- NFR-6 portability: Python 3.11+, `uv`-only workflow, path-safe local execution.

## Stories, scenarios, and acceptance

- As a policy researcher, I run seeded cross-play and obtain the same outcomes and legal
  observations on repetition.
- As a peer operator, I start two isolated peers, detect a profile mismatch before play, and can
  audit every accepted turn afterward.
- As a reviewer, I trace a claimed capability to tests/reports and a remaining gap to `TODO.md`.
- As a release reviewer, I run one documented set of offline checks without contacting a peer.

Acceptance is: all functional behavior has inspectable tests; validation metrics meet the KPIs;
artifacts parse and validate; documentation distinguishes evidence from intent; and human or
bilateral prerequisites fail closed. A real-team or counted game is explicitly not acceptance.

## Scope and boundaries

In scope: deterministic core, observations, policies/evaluation, current local transport,
commit-reveal, audit/replay, artifact builders, the runtime-fed role-safe Live GUI, the offline
verified Replay Viewer, tests, research evidence, and governance.

Outside the accepted implementation baseline: rule changes, new strategy/AI/ML/search, production
deployment, Gmail, tunnels, league reporting, opponent contact, and any uncounted or counted match.
The shared-code GUI requirement is complete under `GUI-001`; final role-repository placement is
still owned by `SUB-001`. Research, visualization, and applicable local cost measurement are
complete. The localhost technical slice of the official counted-series/shared-config layer is
complete; real inputs and bilateral approval remain under `LGE-001`/`HUM-001`. Gmail sender
authorization (`MAIL-001`), submission assembly, and human-gated operations remain tracked in
[TODO](TODO.md).

The competitive/interoperability boundary is frozen: game rules, scoring, policies/profiles,
hashes, serialization, crypto, audit/replay, transport/runtime behavior, artifacts, strategy,
`ScentTacticalPolice`, and the seven-file frozen manifest cannot change in this phase.

## Authority, assumptions, dependencies, and risk

Authority, highest first: (1) Official PDF v3 Appendix E/F, (2) pinned professor reference,
(3) conformance kit, (4) explicit WhatsApp agreements, (5) Software Project Guidelines,
(6) research reports. The generic guidelines never override game rules, frozen semantics, or
negotiated interoperability decisions. See [the baseline](../RULES_AND_INTEROP_BASELINE.md).

Assumptions: Python/`uv` are available; pinned public kit remains present; fixtures represent only
their named profiles. Dependencies: FastMCP 3.4.3 and development tools in `pyproject.toml`.
Constraints include two-process isolation, no network in ordinary tests, and explicit human
approval for external activity. Risks include professor/kit scope differences, process-scoped
daemon lifecycle, and extrapolating bounded local research beyond its preregistered grid.

## Evidence boundary and timeline

Proven by current code/tests/reports: deterministic core and observation isolation; policy
evaluation; local two-peer FastMCP; duplicate/equivocation behavior; Hcommit/replay/audit;
schema 1.1 builders; strict versioned operational/rate configuration; bounded FastMCP Gatekeeper
and inboxes; >90% historical branch coverage; a single SDK consumer facade with typed CLI
delegation; 125/125 vectors; frozen champion/hashes. Public transport validation is historical
evidence, not current authorization or readiness. Phase 4D7B proves a nonce-free artifact-backed
Replay HTML app and a live-view model with no opponent-coordinate field. Phase 4D7C proves
runtime-fed atomic role-local snapshots, loopback serving, exact turn banners, a scent/belief
heatmap, and reviewed synthetic screenshots. Phase 4D9 proves a preregistered 2,400-game local
OAT study, public-safe row/summary provenance, byte-identical regeneration, Wilson intervals,
two accessible figures, and a cited notebook equivalent without changing the champion.
Phase 4D10 adds preregistered one-machine local simulator wall/CPU timing, Python-allocation peak,
result-size, and sequential-capacity evidence without inferring a vendor or electricity price.
Phase 4D13B runs the unchanged peer boundary as twelve child processes across six loopback games,
verifies both audits/replays per game, and assembles two mutually agreeing 14-artifact sets plus
byte-identical full Appendix-B files. Its synthetic identities and approvals are local-test data.

Implemented locally: deterministic guarded Police/Thief snapshot assembly with exact role README
overlays and candidate-tree secret scans, plus a real-Git role repository verifier for history,
bytes, submodule pin, privacy and tag absence. Planned or incomplete: two actual history-preserving
role branches and their independent gate runs; exact URLs/remotes/tags; real series identity/config inputs
and bilateral approval; Gmail API sender/authorization; and external-team readiness.
Research/visualization, applicable cost/capacity measurement, package/building-block/extension
documentation, and the internal ISO assessment are accepted alongside the Live GUI, Replay view,
structured tests, CLI UX, and release tooling.

Milestones: D0 governance baseline; D1 technical compliance; D2 release/offline operations and CLI
manual; D3 GUI/replay plus research/quality publication; D4 official series/reporting closure,
two-repository submission assembly, and human-gated bilateral compatibility. Exact ordering
remains governed by [TODO](TODO.md).
