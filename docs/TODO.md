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

- Milestone: D2; Priority: P2; Status: DONE; Owner role: Core Architecture
- Dependencies: REF-001; Evidence: Phase 4D8 RED/GREEN inventory,
  `docs/BUILDING_BLOCK_CONTRACTS.md`, and `docs/audits/PHASE4D8_PACKAGE_CONTRACTS.md`.
- Definition of Done: every module/class/function documents purpose and public blocks document
  input, output, setup, validation and edge behavior; an automated inventory is green.
- Validation commands: `uv run pytest -q
  tests/integration/test_governance/test_package_building_blocks.py --no-cov`;
  `uv run ruff check src tests tools`.
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

- Milestone: D2; Priority: P2; Status: DONE; Owner role: Core Architecture
- Dependencies: SDK-001, CFG-001; Evidence: `docs/PACKAGE_AUDIT.md`, team author metadata,
  explicit export/package/import regressions, and Phase 4D8 audit evidence.
- Definition of Done: exports, `__init__`, relative paths, attribution and dependency pins are
  audited; `pyproject.toml` stays authoritative and workflow remains uv-only.
- Validation commands: `uv sync`; `uv run pytest`; repository command scan.
- Hard stop/escalation: no dependency changes without separate approval.

## RES-001 — Publish safe reproducible research and sensitivity analysis

- Milestone: D3; Priority: P2; Status: DONE; Owner role: Shared Review
- Dependencies: QLT-001, privacy review; Evidence: the preregistered
  `data/research/sensitivity_design.v1.json`, public-safe raw/summary results, hash manifest,
  network-free generator, Phase 4D9 audit, and five research publication contract tests.
- Definition of Done: public-safe inputs/seeds/commands/results support controlled sensitivity,
  theory/citations and claim-to-data provenance without private/professor content.
- Validation commands: `uv run python -m tools.research.cli`; `uv run pytest -q
  tests/integration/test_research/test_sensitivity_publication.py --no-cov`; artifact/link audit.
- Hard stop/escalation: quarantine any private path, body, instruction, or personal data.

## VIS-001 — Create reproducible notebook and visualizations

- Milestone: D3; Priority: P2; Status: DONE; Owner role: Shared Review
- Dependencies: RES-001; Evidence: `notebooks/POLICY_SENSITIVITY_ANALYSIS.md`, two accessible
  1200×700 SVG figures with labelled axes/legends/Wilson intervals, deterministic hash evidence,
  and the Phase 4D9 RED/GREEN figure/notebook contract.
- Definition of Done: a network-free notebook/equivalent regenerates accessible labelled figures
  from published results, with equations, captions and no hidden state/private data.
- Validation commands: `uv run python -m tools.research.cli`; deterministic output and SVG
  accessibility checks in the Phase 4D9 test.
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

- Milestone: D3; Priority: P1; Status: DONE; Owner role: Core Architecture
- Dependencies: UX-001, SDK-001, QLT-001; Evidence: Phase 4D7B Replay acceptance plus Phase 4D7C
  runtime-fed role-safe Live GUI, strict feed/server boundary, offline two-peer integration test,
  browser review, retained Live/Replay screenshots, and
  `docs/audits/PHASE4D7C_LIVE_GUI.md`.
- Definition of Done: a role-legal Live GUI displays belief/scent and current status without hidden
  truth; an artifact-backed Replay view displays deterministic verification including
  `Verified OK`; public-safe screenshots, accessibility notes, and offline tests are retained.
- Validation commands: focused GUI/replay tests; `uv run pytest`; `uv run ruff check src tests`.
- Hard stop/escalation: the live view cannot expose objective opponent coordinates, and the Replay
  view cannot treat an unverified or malformed log as verified.

## COST-001 — Produce applicable cost/capacity analysis

- Milestone: D3; Priority: P3; Status: DONE; Owner role: Release Engineering
- Dependencies: RE-001, measured usage; Evidence: partner-authored deterministic repository
  measurement tool, corrected `docs/COST_AND_CAPACITY_ANALYSIS.md`, Phase 4D7A audit, and the
  preregistered Phase 4D10 local simulator timing/memory/result-size evidence.
- Definition of Done: local compute/storage/network and any actual API/token costs are measured,
  assumptions dated, scaling forecasted, and non-applicable categories explained.
- Validation commands: reproducible repository measurement; `uv run python -m
  tools.quality_assessment.runtime_cli`; retained-sample arithmetic test; full quality gate.
- Hard stop/escalation: do not invent prices, usage, or token histories.

## ISO-001 — Assess ISO/IEC 25010 quality characteristics

- Milestone: D3; Priority: P2; Status: DONE; Owner role: Shared Review
- Dependencies: QLT-001, UX-001, SEC-001; Evidence: corrected
  `docs/ISO_IEC_25010_ASSESSMENT.md` covers all eight characteristics and Phase 4D7A records
  evidence, gaps, metrics, owners, and the explicit non-certification boundary.
- Definition of Done: all eight characteristics have scoped metrics, evidence, gaps and owners.
- Validation commands: matrix/link audit and reviewer sign-off.
- Hard stop/escalation: no certification claim; this is an internal assessment.

## EXT-001 — Formalize extension points and compatibility policy

- Milestone: D2; Priority: P2; Status: DONE; Owner role: Core Architecture
- Dependencies: SDK-001, PKG-001; Evidence: `docs/EXTENSION_POINTS.md`, existing protocol/factory
  tests, and Phase 4D8 package/extension governance tests.
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

- Milestone: D1; Priority: P2; Status: DONE; Owner role: Shared Review
- Dependencies: GOV-001; Evidence: `docs/GIT_RELEASE_GOVERNANCE.md`, the annotated
  `team-baseline-v1` tag, 18 accepted first-parent PR merges through PR #19, preserved partner
  authorship, full-history CI checkout, and the Phase 4D11 audit/regression contract.
- Definition of Done: branch, commit, PR review, release/tag, attribution and exception evidence
  are documented and demonstrated on a future change without rewriting honest history.
- Validation commands: `git log --first-parent --merges --oneline main`; `git cat-file -t
  team-baseline-v1`; Phase 4D11 governance test; PR/release evidence review.
- Hard stop/escalation: never backdate, reassign, force-push, or tag without authorization.

## LGE-001 — Complete the official counted-series and shared-config boundary

- Milestone: D4; Priority: P0; Status: IN_PROGRESS; Owner role: Core Architecture / Release Engineering
- Dependencies: accepted single-sub-game runtime, Appendix-B/F authority review, HUM-001 for any
  opponent-specific value; Evidence today: professor/reference cross-play and schema-1.1 artifacts
  prove one sub-game, while `docs/INTEROP_DECISIONS.md` records
  `UNRESOLVED_FOR_COUNTED_SERIES` for the distinct full shared-config scope. Phase 4D13A and its
  `docs/audits/PHASE4D13A_OFFICIAL_SERIES_ENTRY.md` evidence add the
  fail-closed offline config/schedule/identity/provenance/aggregation entry contract without
  changing the single-game runtime or claiming bilateral approval. Phase 4D13B and
  `docs/audits/PHASE4D13B_LOCALHOST_SERIES.md` run six games as twelve loopback processes,
  verify all audits/replays, and produce two checker-accepted series bundles plus distinct
  byte-identical full Appendix-B files. Synthetic fixture values do not satisfy `HUM-001`.
- Definition of Done: an outer offline coordinator runs the fixed six-sub-game series without
  changing frozen game/wire behavior; role assignment, per-game commit, truthful game count,
  eight-character group identity, members/repos/hardware declaration metadata, token totals,
  scoring, audit, and aggregate result are deterministic; the
  full Appendix-B shared configuration is byte-locked as its own named scope and every
  professor/schema-1.1 serialization remains exact.
- Validation commands: focused series/config success and refusal tests; unmodified-professor
  differential; full quality gate; six-sub-game localhost audit/replay with no external network.
- Remaining acceptance: replace synthetic identity/provenance/profile approvals only with actual
  operator values and explicit bilateral evidence; the offline technical adapter itself is GREEN.
- Hard stop/escalation: do not invent missing identity/hardware/repository values, conflate the
  three config/hash domains, change the frozen champion or semantics, contact a peer, or report a
  counted result.

## MAIL-001 — Implement and authorize official Gmail result reporting

- Milestone: D4; Priority: P0; Status: IN_PROGRESS; Owner role: Release Engineering / Human Operator
- Dependencies: explicit user authorization to begin Gmail work, LGE-001 result bytes, HUM-001,
  and least-privilege OAuth setup; Evidence so far: the operator authorized the work on
  2026-08-21 and `src/police_thief_lab/reporting/` implements the versioned reporting boundary,
  deterministic message construction and the send-only sender with mocked transports, covered by
  `tests/integration/test_reporting/` and documented in `docs/OFFICIAL_RESULT_REPORTING.md`.
  Still missing: no OAuth client, no credential, no real transport and no send has occurred, and
  the three graded league fields named in kit SPEC 6.2 are absent from our result artifact.
- Definition of Done: both roles can independently send the exact mutually agreed result JSON as
  an attachment through a send-only Gmail API boundary; quota, token-bucket, retry/backoff,
  queue/DOS protection, Table-19 configuration, secret handling, and deterministic mocked failure
  paths are tested; any live send occurs only for a separately authorized counted operation.
- Validation commands: network-free mocked sender/Gatekeeper tests and secret scan first; later,
  only after explicit approval, a bounded least-privilege operational preflight and audited send.
- Hard stop/escalation: do not add credentials, start OAuth, open Gmail, send a draft/message, or
  treat a mock as operational evidence without the user's explicit choice.

## SUB-001 — Assemble the official two-repository submission

- Milestone: D4; Priority: P1; Status: IN_PROGRESS; Owner role: Release Engineering
- Dependencies: DOC-001, GUI-001, GIT-001, completed final content; Evidence so far: the guarded
  candidate policy in `data/submission/role_content_policy.v1.json`,
  `docs/ROLE_REPOSITORY_CONTENT_POLICY.md`, Phase 4D12A, the tested Police/Thief README overlays,
  `docs/ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md` from Phase 4D12B, Phase 4D14A deterministic
  integration of the partner exporter, and the accepted Phase 4D14B repository gate. Phase 4D14C
  creates and independently validates the actual history-preserving Police commit `c52f907...`
  and Thief commit `fd87d62...` from accepted source `e3fda929...`. Both exact repository gates,
  338-pass role suites at 91.10%, Ruff, Hcommit 5/5, frozen 7/7, conformance 125/125 and secret
  scans are GREEN. The corrected accepted-source set is 329 selected regular files plus
  `.gitmodules` and one pinned gitlink. Phase 4D14D accepts exact reciprocal URLs; Phase 4D14E
  integrates accepted source `cff96c44...`, repeats both exact/local gates, and non-forcibly
  publishes public Police `42c5367...` and Thief `f279dc2...`. Both reciprocal links and public CI
  reruns are GREEN. Only separately authorized annotated `v1.0-submission` tags remain for SUB-001.
- Definition of Done: separate Police and Thief repositories contain the required role code,
  config, PRD/PLAN/TODO and academic README; both cross-link each other, pass their own gates, and
  receive reviewed annotated `v1.0-submission` tags at the exact approved commits.
- Validation commands: role-export manifest checks, both repository quality gates, link/secret
  review, and `git show v1.0-submission` in each final repository.
- Hard stop/escalation: preserve the verified public commits; do not create final tags without
  separate approval; never copy ignored sources,
  professor-owned code, credentials, correspondence, or retained private evidence.

## HUM-001 — Complete bilateral compatibility approvals

- Milestone: D4; Priority: P0; Status: IN_PROGRESS; Owner role: Human/External Coordination
- Dependencies: successful approved uncounted plan and another team's explicit responses;
  Evidence so far: group `vm__fabi` answered every worksheet item in writing with ACCEPT and
  reproduced both published hashes byte-exactly; three uncounted public games in both roles are
  recorded in `docs/audits/PHASE4F_REAL_TEAM_UNCOUNTED_WARMUP.md`. Still missing for DONE: the
  opponent's own consensus hashes for comparison and a counter-signed operator worksheet.
- Definition of Done: every worksheet field/domain and Rule 47/scope decision has explicit
  bilateral evidence, with separate authorization for any activity.
- Validation commands: offline worksheet validation only; no gameplay command is authorized.
- Hard stop/escalation: missing/different response blocks; do not contact, tunnel, or play.
