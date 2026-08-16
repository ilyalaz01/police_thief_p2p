# Live Project Task Source of Truth

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Allowed statuses: `DONE`, `IN_PROGRESS`, `PLANNED`, `BLOCKED`. Overall guideline compliance is
PARTIAL. Only inspectable repository evidence supports DONE. Priority P0 is highest.

## GOV-001 — Phase 4D0 governance baseline

- Milestone: D0; Priority: P0; Status: DONE; Owner role: Shared Review
- Dependencies: validated commit `96d3878`; Evidence: four Phase 4D0 commits, governance test,
  `docs/audits/phase4d0_guidelines_recovery.json`, and commands recorded in the audit.
- Definition of Done: all required documents/tests exist, link and JSON audits pass, four logical
  commits exist, frozen behavior is unchanged, and Phase 4D0 alone is GREEN.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: stop on any source/existing-test/frozen-hash modification.

## DOC-001 — Complete README user manual

- Milestone: D1; Priority: P1; Status: PLANNED; Owner role: Shared Review
- Dependencies: GOV-001, CFG-001, UX-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: document install, all modes/options/workflows/examples/configuration,
  troubleshooting, contribution, license and credits without overstating readiness.
- Validation commands: `uv run pytest tests/test_project_governance.py --no-cov`.
- Hard stop/escalation: do not invent configuration or operational readiness.

## SDK-001 — Decide and implement complete SDK facade

- Milestone: D1; Priority: P1; Status: PLANNED; Owner role: Core Architecture
- Dependencies: accepted ADR-003; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: every business operation has an approved stable facade, consumers delegate,
  characterization tests pass, and frozen imports/behavior remain compatible.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: escalate any required game, wire, artifact, strategy, or hash change.

## API-001 — Decide gatekeeper scope and controls

- Milestone: D1; Priority: P0; Status: PLANNED; Owner role: Core Architecture
- Dependencies: accepted ADR-004, CFG-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: applicable external calls are inventoried; approved admission/rate policy,
  bounded queues, backpressure, drain and sanitized monitoring are tested without changing frozen
  retries, deadlines, duplicates, ordering, or stale/equivocation behavior.
- Validation commands: `uv run pytest -q -k "phase4a or phase4b" --no-cov`.
- Hard stop/escalation: stop at any wire/deadline semantic drift or unresolved applicability.

## REF-001 — Split files over 150 lines

- Milestone: D1; Priority: P1; Status: IN_PROGRESS; Owner role: Core Architecture
- Dependencies: accepted test-only slice of ADR-005 and characterization evidence; Evidence:
  Phase 4D1A commits and `docs/audits/PHASE4D1A_TEST_SPLIT.md` removed both test violations;
  Phase 4D1B commits and `docs/audits/PHASE4D1B_BELIEF_SPLIT.md` removed the belief violation.
- Definition of Done: all project-authored Python files are ≤150 nonblank/non-comment lines,
  without compression, semantic drift, coverage loss, or frozen-hash change.
- Validation commands: line-count audit from ADR-005; `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: the test-only and belief-helper slices are complete; three production
  proposals remain unselected and require separate review before any source movement.

## DOCS-002 — Complete docstrings and building-block contracts

- Milestone: D2; Priority: P2; Status: PLANNED; Owner role: Core Architecture
- Dependencies: REF-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: every module/class/function documents purpose and public blocks document
  input, output, setup, validation and edge behavior; an automated inventory is green.
- Validation commands: `uv run ruff check src tests`; documented docstring audit command.
- Hard stop/escalation: doc changes must not redefine higher-authority behavior.

## TST-001 — Reorganize and document test layers

- Milestone: D1; Priority: P1; Status: PLANNED; Owner role: Shared Review
- Dependencies: accepted ADR-005; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: unit/integration/system tests have documented boundaries, source mapping,
  shared fixtures, success/error cases, and preserved collection/coverage.
- Validation commands: `uv run pytest --collect-only`; `uv run pytest`.
- Hard stop/escalation: preserve test intent and existing tests during migration.

## QLT-001 — Enforce coverage, path evidence, Ruff and failure reports

- Milestone: D1; Priority: P1; Status: PLANNED; Owner role: Shared Review
- Dependencies: TST-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: ≥85% branch coverage remains enforced, critical-path cases are mapped,
  Ruff is zero, and sanitized pass/failure reports have a retention policy.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: skipped/missing validators are failures for release evidence.

## CFG-001 — Versioned configuration and secret boundary

- Milestone: D1; Priority: P1; Status: PLANNED; Owner role: Core Architecture
- Dependencies: accepted ADR-006; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: approved versioned config loader validates compatibility before side effects;
  `.env-example`, ignore rules and secret scan exist; code/package/config versions are coherent.
- Validation commands: `uv run pytest`; approved secret/config validation commands.
- Hard stop/escalation: never migrate fixed rules or alter frozen profile/config bytes.

## PKG-001 — Audit package/API/path/dependency organization

- Milestone: D2; Priority: P2; Status: PLANNED; Owner role: Core Architecture
- Dependencies: SDK-001, CFG-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: exports, `__init__`, relative paths, attribution and dependency pins are
  audited; `pyproject.toml` stays authoritative and workflow remains uv-only.
- Validation commands: `uv sync`; `uv run pytest`; repository command scan.
- Hard stop/escalation: no dependency changes without separate approval.

## RES-001 — Publish safe reproducible research and sensitivity analysis

- Milestone: D3; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: QLT-001, privacy review; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: public-safe inputs/seeds/commands/results support controlled sensitivity,
  theory/citations and claim-to-data provenance without private/professor content.
- Validation commands: approved `uv run python experiments/...` commands; artifact/link audit.
- Hard stop/escalation: quarantine any private path, body, instruction, or personal data.

## VIS-001 — Create reproducible notebook and visualizations

- Milestone: D3; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: RES-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: a network-free notebook/equivalent regenerates accessible labelled figures
  from published results, with equations, captions and no hidden state/private data.
- Validation commands: documented `uv run` notebook execution and deterministic output check.
- Hard stop/escalation: no new ML/search claim or unverifiable chart.

## UX-001 — Specify and validate CLI/UI usability

- Milestone: D2; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: SDK-001, CFG-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: supported CLI workflows/options/errors/recovery/accessibility are tested and
  documented; GUI applicability is explicitly decided with rationale.
- Validation commands: `uv run python -m police_thief_lab.peer_cli --help`; CLI tests.
- Hard stop/escalation: operational commands cannot imply authorization or expose secrets.

## COST-001 — Produce applicable cost/capacity analysis

- Milestone: D3; Priority: P3; Status: PLANNED; Owner role: Release Engineering
- Dependencies: RE-001, measured usage; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: local compute/storage/network and any actual API/token costs are measured,
  assumptions dated, scaling forecasted, and non-applicable categories explained.
- Validation commands: reproducible measurement command and arithmetic review.
- Hard stop/escalation: do not invent prices, usage, or token histories.

## ISO-001 — Assess ISO/IEC 25010 quality characteristics

- Milestone: D3; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: QLT-001, UX-001, SEC-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: all eight characteristics have scoped metrics, evidence, gaps and owners.
- Validation commands: matrix/link audit and reviewer sign-off.
- Hard stop/escalation: no certification claim; this is an internal assessment.

## EXT-001 — Formalize extension points and compatibility policy

- Milestone: D2; Priority: P2; Status: PLANNED; Owner role: Core Architecture
- Dependencies: SDK-001, PKG-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: existing policy/scent/evaluation/profile extension interfaces, lifecycle,
  compatibility and tests are documented; plugin/middleware applicability is decided.
- Validation commands: interface contract tests and `uv run pytest`.
- Hard stop/escalation: extensions cannot bypass observation or negotiated boundaries.

## CON-001 — Analyze concurrency, lifecycle and capacity

- Milestone: D2; Priority: P1; Status: PLANNED; Owner role: Core Architecture
- Dependencies: API-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: thread/queue ownership, shutdown, race, capacity, resource cleanup and
  exception paths are tested and documented with bounded behavior.
- Validation commands: deterministic concurrency/load tests plus transport suite.
- Hard stop/escalation: preserve ordering/deadlines and avoid network-dependent unit tests.

## SEC-001 — Establish automated security/privacy checks

- Milestone: D2; Priority: P0; Status: PLANNED; Owner role: Release Engineering
- Dependencies: CFG-001, RE-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: secret/private-path/live-endpoint/nonce scans are reproducible, tested with
  synthetic placeholders, fail closed, and retain no sensitive bodies.
- Validation commands: approved `scan-secrets` plus `uv run pytest tests/offline_ops`.
- Hard stop/escalation: never print or commit a detected value.

## RE-001 — Implement offline release-engineering workstream

- Milestone: D2; Priority: P1; Status: PLANNED; Owner role: Release Engineering
- Dependencies: QLT-001, SEC-001 design approval; Evidence for DONE: not applicable.
- Definition of Done: every criterion in `RELEASE_ENGINEERING_WORKSTREAM.md` passes locally and
  via the same thin CI entry, with deterministic sanitized reports and stable exit codes.
- Validation commands: workstream commands plus full project/conformance/frozen gates.
- Hard stop/escalation: remain inside its module boundary; missing validators fail closed.

## GIT-001 — Adopt reviewed branch/PR/release governance

- Milestone: D1; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: GOV-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: branch, commit, PR review, release/tag, attribution and exception evidence
  are documented and demonstrated on a future change without rewriting honest history.
- Validation commands: `git log --oneline --decorate`; PR/release evidence review.
- Hard stop/escalation: never backdate, reassign, force-push, or tag without authorization.

## HUM-001 — Complete bilateral compatibility approvals

- Milestone: D4; Priority: P0; Status: BLOCKED; Owner role: Human/External Coordination
- Dependencies: successful approved uncounted plan and another team's explicit responses;
  Evidence for DONE: not applicable while BLOCKED.
- Definition of Done: every worksheet field/domain and Rule 47/scope decision has explicit
  bilateral evidence, with separate authorization for any activity.
- Validation commands: offline worksheet validation only; no gameplay command is authorized.
- Hard stop/escalation: missing/different response blocks; do not contact, tunnel, or play.
