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
solves the local technical core; governance and several professional-project controls remain.

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
commit-reveal, audit/replay, artifact builders, role-safe presentation models, the offline Replay
Viewer, tests, research evidence, and governance.

Outside the accepted implementation baseline: rule changes, new strategy/AI/ML/search, runtime-fed
Live GUI operation, production deployment, Gmail, tunnels, league reporting, opponent contact, and
any uncounted or counted match. The official GUI requirement remains in progress under `GUI-001`:
the offline Replay shell and role-local view boundary exist, while runtime integration and reviewed
screenshots remain open. Research, visualization, submission assembly, and human-gated operations
remain tracked in [TODO](TODO.md).

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
approval for external activity. Risks include professor/kit scope differences, incomplete daemon
lifecycle analysis, flat tests, and private research evidence that cannot simply be published.

## Evidence boundary and timeline

Proven by current code/tests/reports: deterministic core and observation isolation; policy
evaluation; local two-peer FastMCP; duplicate/equivocation behavior; Hcommit/replay/audit;
schema 1.1 builders; strict versioned operational/rate configuration; bounded FastMCP Gatekeeper
and inboxes; >90% historical branch coverage; a single SDK consumer facade with typed CLI
delegation; 125/125 vectors; frozen champion/hashes. Public transport validation is historical
evidence, not current authorization or readiness. Phase 4D7B additionally proves a nonce-free
artifact-backed Replay HTML app and a live-view model with no opponent-coordinate field.

Planned or incomplete: runtime-fed Live GUI operation and screenshots, reproducible public research
package, notebook/visuals, cost/ISO analysis, two-role-repository submission assembly, and bilateral
readiness. The offline Replay view, structured tests, CLI UX, and CI/offline release tooling are
implemented.

Milestones: D0 governance baseline; D1 technical compliance; D2 release/offline operations and CLI
manual; D3 GUI/replay plus research/quality publication; D4 two-repository submission assembly and
human-gated bilateral compatibility. Exact ordering remains governed by [TODO](TODO.md).
