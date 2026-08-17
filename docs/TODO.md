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

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Shared Review
- Dependencies: GOV-001, CFG-001, UX-001; Evidence: Phase 4D6 RED/GREEN commits, guarded manual
  sections/options, and `docs/audits/PHASE4D6_CLI_MANUAL.md`.
- Definition of Done: document install, all modes/options/workflows/examples/configuration,
  troubleshooting, contribution, license and credits without overstating readiness.
- Validation commands:
  `uv run pytest tests/integration/test_governance/test_project_governance.py --no-cov`.
- Hard stop/escalation: do not invent configuration or operational readiness.

## SDK-001 — Decide and implement complete SDK facade

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Core Architecture
- Dependencies: accepted ADR-003; Evidence: Phase 4D2B commits and
  `docs/audits/PHASE4D2B_SDK_FACADE.md`.
- Definition of Done: every business operation has an approved stable facade, consumers delegate,
  characterization tests pass, and frozen imports/behavior remain compatible.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`;
  `uv run pytest -q tests/integration/test_governance/test_sdk_contract.py --no-cov`.
- Hard stop/escalation: a consumer bypass, missing public operation, changed legacy identity,
  game/wire/artifact/strategy/hash drift, or SDK-side authorization claim reopens SDK-001.

## API-001 — Decide gatekeeper scope and controls

- Milestone: D1; Priority: P0; Status: DONE; Owner role: Core Architecture
- Dependencies: accepted ADR-004, CFG-001; Evidence: Phase 4D2C commits and
  `docs/audits/PHASE4D2C_API_GATEKEEPER.md`.
- Definition of Done: applicable external calls are inventoried; approved admission/rate policy,
  bounded queues, backpressure, drain and sanitized monitoring are tested without changing frozen
  retries, deadlines, duplicates, ordering, or stale/equivocation behavior.
- Validation commands: `uv run pytest -q tests/integration/test_configuration/test_gatekeeper.py
  tests/integration/test_configuration/test_gatekeeper_config.py --no-cov`; `uv run pytest`;
  `uv run ruff check src tests`.
- Hard stop/escalation: an external-call bypass, unversioned/hard-coded limit, retained value,
  dropped/reordered queue item, or frozen retry/deadline/wire drift reopens API-001 and stops.

## REF-001 — Split files over 150 lines

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Core Architecture
- Dependencies: accepted test-only slice of ADR-005 and characterization evidence; Evidence: Phase
  4D1A commits and `docs/audits/PHASE4D1A_TEST_SPLIT.md` removed both test violations;
  Phase 4D1B commits and `docs/audits/PHASE4D1B_BELIEF_SPLIT.md` removed the belief violation;
  Phase 4D1C commits and `docs/audits/PHASE4D1C_ARTIFACT_SPLIT.md` removed the artifact violation;
  Phase 4D1D commits and `docs/audits/PHASE4D1D_PRODUCTION_SPLITS.md` removed the Phase 3B and
  runtime violations and added the permanent 150-line regression gate.
- Definition of Done: all project-authored Python files are ≤150 nonblank/non-comment lines,
  without compression, semantic drift, coverage loss, or frozen-hash change.
- Validation commands: line-count audit from ADR-005; `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: any future violation, compressed formatting, public-contract drift,
  strategy/output change, wire/artifact change, or frozen-hash change reopens REF-001 and stops.

## DOCS-002 — Complete docstrings and building-block contracts

- Milestone: D2; Priority: P2; Status: PLANNED; Owner role: Core Architecture
- Dependencies: REF-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: every module/class/function documents purpose and public blocks document
  input, output, setup, validation and edge behavior; an automated inventory is green.
- Validation commands: `uv run ruff check src tests`; documented docstring audit command.
- Hard stop/escalation: doc changes must not redefine higher-authority behavior.

## TST-001 — Reorganize and document test layers

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Shared Review
- Dependencies: accepted ADR-005; Evidence: Phase 4D3 RED/GREEN commits and
  `docs/audits/PHASE4D3_TEST_QUALITY.md`.
- Definition of Done: unit/integration/system tests have documented boundaries, source mapping,
  shared fixtures, success/error cases, and preserved collection/coverage.
- Validation commands: `uv run pytest --collect-only -q --no-cov`; `uv run pytest`.
- Hard stop/escalation: preserve test intent and existing tests during migration.

## QLT-001 — Enforce coverage, path evidence, Ruff and failure reports

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Shared Review
- Dependencies: TST-001; Evidence: `docs/QUALITY_CRITICAL_PATHS.md`, Phase 4D3 RED/GREEN commits,
  and `docs/audits/phase4d3_test_quality.json`.
- Definition of Done: ≥85% branch coverage remains enforced, critical-path cases are mapped,
  Ruff is zero, and sanitized pass/failure reports have a retention policy.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: skipped/missing validators are failures for release evidence.

## CFG-001 — Versioned configuration and secret boundary

- Milestone: D1; Priority: P1; Status: DONE; Owner role: Core Architecture
- Dependencies: accepted ADR-006; Evidence: Phase 4D2A commits and
  `docs/audits/PHASE4D2A_VERSIONED_CONFIGURATION.md`.
- Definition of Done: approved versioned config loader validates compatibility before side effects;
  `.env-example`, ignore rules and secret scan exist; code/package/config versions are coherent.
- Validation commands: `uv run pytest`; `uv run ruff check src tests`;
  `uv run pytest -q tests/integration/test_configuration/test_configuration.py --no-cov`.
- Hard stop/escalation: any fixed-rule/profile/hash change, retained secret value, implicit schema
  migration, or operational side effect during validation reopens CFG-001 and stops.

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

- Milestone: D2; Priority: P2; Status: DONE; Owner role: Shared Review
- Dependencies: SDK-001, CFG-001; Evidence: Phase 4D6 parser/help tests, complete option and
  recovery manual, operation-classification table, and explicit GUI applicability decision.
- Definition of Done: supported CLI workflows/options/errors/recovery/accessibility are tested and
  documented; GUI applicability is explicitly decided with rationale.
- Validation commands: `uv run python -m police_thief_lab.peer_cli --help`; CLI tests.
- Hard stop/escalation: operational commands cannot imply authorization or expose secrets.

## GUI-001 — Implement the mandatory Live GUI and Replay view

- Milestone: D3; Priority: P1; Status: PLANNED; Owner role: Core Architecture
- Dependencies: UX-001, SDK-001, QLT-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: a role-legal Live GUI displays belief/scent and current status without hidden
  truth; an artifact-backed Replay view displays deterministic verification including
  `Verified OK`; public-safe screenshots, accessibility notes, and offline tests are retained.
- Validation commands: focused GUI/replay tests; `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: the live view cannot expose objective opponent coordinates, and the Replay
  view cannot treat an unverified or malformed log as verified.

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

- Milestone: D2; Priority: P1; Status: DONE; Owner role: Core Architecture
- Dependencies: API-001; Evidence: Phase 4D4 RED/GREEN commits,
  `docs/CONCURRENCY_AND_CAPACITY.md`, and
  `docs/audits/PHASE4D4_CONCURRENCY_LIFECYCLE.md`.
- Definition of Done: thread/queue ownership, shutdown, race, capacity, resource cleanup and
  exception paths are tested and documented with bounded behavior.
- Validation commands: `uv run pytest -q
  tests/integration/test_configuration/test_gatekeeper_lifecycle.py --no-cov`; `uv run pytest`;
  `uv run ruff check src tests`.
- Hard stop/escalation: preserve ordering/deadlines and avoid network-dependent unit tests.

## SEC-001 — Establish automated security/privacy checks

- Milestone: D2; Priority: P0; Status: DONE; Owner role: Release Engineering
- Dependencies: CFG-001, RE-001; Evidence: `tools/offline_ops/secrets/` (pattern-based fail-closed
  scanner: private keys, cloud/VCS tokens, JWTs, authorization headers, tunnel URLs/configuration,
  cache/temp files, symlink/path-escape, non-artifact nonce material), composed into
  `quality-gate`'s `scan_secrets` check and exposed directly as `scan-secrets PATH`;
  `tests/offline_ops/test_secrets_scanner.py` and
  `tests/offline_ops/test_scan_secrets_command.py` use synthetic
  placeholder values only and assert a matched value is never retained in any report.
- Definition of Done: secret/private-path/live-endpoint/nonce scans are reproducible, tested with
  synthetic placeholders, fail closed, and retain no sensitive bodies.
- Validation commands: approved `scan-secrets` plus `uv run pytest tests/offline_ops`.
- Hard stop/escalation: never print or commit a detected value.

## RE-001 — Implement offline release-engineering workstream

- Milestone: D2; Priority: P1; Status: DONE; Owner role: Release Engineering
- Dependencies: QLT-001, SEC-001 design approval; Evidence: `tools/offline_ops/**`
  (`quality-gate`, `validate-match`, `package-match`, `scan-secrets`),
  `.github/workflows/quality-gate.yml`, `docs/RELEASE_ENGINEERING.md`. Ported from
  `feature/release-engineering` (`2d3063f`) and reconciled with the current layered test
  architecture on `feature/release-engineering-integration` (clean-port, path-reconciliation, and
  encoding-fix commits). 96 tests in `tests/offline_ops/`, zero Ruff violations, every
  project-authored file at or under 150 counted lines.
- Definition of Done: every criterion in `RELEASE_ENGINEERING_WORKSTREAM.md` passes locally and
  via the same thin CI entry, with deterministic sanitized reports and stable exit codes.
- Validation commands: workstream commands plus full project/conformance/frozen gates.
- Hard stop/escalation: remain inside its module boundary; missing validators fail closed.
- Phase 4D5 correction: the composed quality gate is GREEN. The prior AST failure was a
  Python-3.12/3.13 empty-field representation difference in a test serializer; the stable
  cross-version test fix retained production source and the expected hash.

## GIT-001 — Adopt reviewed branch/PR/release governance

- Milestone: D1; Priority: P2; Status: PLANNED; Owner role: Shared Review
- Dependencies: GOV-001; Evidence for DONE: not applicable while PLANNED.
- Definition of Done: branch, commit, PR review, release/tag, attribution and exception evidence
  are documented and demonstrated on a future change without rewriting honest history.
- Validation commands: `git log --oneline --decorate`; PR/release evidence review.
- Hard stop/escalation: never backdate, reassign, force-push, or tag without authorization.

## SUB-001 — Assemble the official two-repository submission

- Milestone: D4; Priority: P1; Status: PLANNED; Owner role: Release Engineering
- Dependencies: DOC-001, GUI-001, GIT-001, completed final content; Evidence for DONE: not
  applicable while PLANNED.
- Definition of Done: separate Police and Thief repositories contain the required role code,
  config, PRD/PLAN/TODO and academic README; both cross-link each other, pass their own gates, and
  receive reviewed annotated `v1.0-submission` tags at the exact approved commits.
- Validation commands: role-export manifest checks, both repository quality gates, link/secret
  review, and `git show v1.0-submission` in each final repository.
- Hard stop/escalation: do not create/tag final remotes before content approval; never copy ignored
  sources, professor-owned code, credentials, correspondence, or retained private evidence.

## HUM-001 — Complete bilateral compatibility approvals

- Milestone: D4; Priority: P0; Status: BLOCKED; Owner role: Human/External Coordination
- Dependencies: successful approved uncounted plan and another team's explicit responses;
  Evidence for DONE: not applicable while BLOCKED.
- Definition of Done: every worksheet field/domain and Rule 47/scope decision has explicit
  bilateral evidence, with separate authorization for any activity.
- Validation commands: offline worksheet validation only; no gameplay command is authorized.
- Hard stop/escalation: missing/different response blocks; do not contact, tunnel, or play.
