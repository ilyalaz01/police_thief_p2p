# ISO/IEC 25010 Internal Quality Assessment

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

**Internal engineering assessment; not an ISO certification.**

This document assesses Police-Thief P2P against all eight ISO/IEC 25010:2011 product-quality
characteristics. Evidence is cited by repository-relative path. No external certification body
was engaged. Gaps are recorded honestly and are not claimed as closed.

Source authority for all game, interoperability, and audit claims remains
[`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md).

Current reconciliation: **GUI-001: DONE** on shared `main` through Phase 4D7C. This assessment
incorporates that accepted Live/Replay evidence without implying final-submission readiness.

---

## 1. Functional suitability

Covers functional completeness, functional correctness, and functional appropriateness.

| Field | Detail |
|---|---|
| **Current evidence** | Deterministic rules engine (Rules 46/47, barriers, scoring, survival); role-legal observations; alternating Thief-first turns; four-tool FastMCP exchange; commit-reveal; audit/replay; schema 1.1 artifact builders; 312/312 passing tests; conformance 125/125; Phase 4D7C role-safe Live GUI |
| **Measurable indicator** | Test suite pass rate; conformance vector pass rate; frozen manifest 7/7 |
| **Honest status** | SUBSTANTIAL — core offline function is proven |
| **Remaining gap** | Counted league games are blocked (`HUM-001`); two-repository submission assembly is incomplete (`SUB-001`); safe reproducible research publication is not yet produced (`RES-001`) |
| **Proposed owner/action** | `HUM-001`: obtain bilateral approvals; `SUB-001`: assemble final role repositories; `RES-001`: publish safe reproducible research evidence |

---

## 2. Performance efficiency

Covers time behaviour, resource utilisation, and capacity.

| Field | Detail |
|---|---|
| **Current evidence** | Policy decisions are synchronous and deterministic; Gatekeeper bounded outbound workers; `concurrent_max + queue_max` capacity formula documented in `docs/CONCURRENCY_AND_CAPACITY.md`; retry deadlines are monotonic and frozen |
| **Measurable indicator** | Turn decision latency (ms); game throughput (games/second); peak RAM; CPU time per game |
| **Honest status** | PARTIAL — capacity model is defined; measurements are unmeasured |
| **Remaining gap** | No measured CPU time, RAM peak, or latency under load; multi-game concurrency untested at scale; public transport latency is historical evidence only |
| **Proposed owner/action** | Instrument `evaluation.runner.run_game()` with `time.perf_counter()` and `tracemalloc`; run a bounded offline load test against `config/rate_limits.v1.json` |

---

## 3. Compatibility

Covers co-existence and interoperability.

| Field | Detail |
|---|---|
| **Current evidence** | 125/125 conformance vectors; Hcommit 5/5 golden cases; professor localhost MCP 4/4; MCP wire `VERIFIED_REFERENCE_INTEROP`; duplicate/equivocation behavior verified; scent and artifact schemas documented in `docs/INTEROP_DECISIONS.md` |
| **Measurable indicator** | Conformance vector pass rate; Hcommit vector pass rate; interop fixture coverage |
| **Honest status** | SUBSTANTIAL for reference-v3 profile; PARTIAL for real-team compatibility |
| **Remaining gap** | No other-team counted game performed; turn resolution status `UNRESOLVED` for simultaneous models; artifact schema scope requires per-match agreement (`NEGOTIATED_PER_MATCH`); `HUM-001` BLOCKED |
| **Proposed owner/action** | `HUM-001`: complete bilateral worksheet; pre-match profile negotiation per `docs/REAL_TEAM_WARMUP_RUNBOOK.md` |

---

## 4. Usability

Covers appropriateness recognisability, learnability, operability, user error protection,
user interface aesthetics, and accessibility.

| Field | Detail |
|---|---|
| **Current evidence** | Complete CLI manual in `README.md` (Phase 4D6); guarded `--help`; operation-classification table; Phase 4D7C runtime-fed role-local belief heatmap with exact turn banners; fail-closed Replay; accessible native controls; reviewed Live and `Verified OK` screenshots |
| **Measurable indicator** | CLI/help and presentation test pass rate; governance/link checks; retained visual evidence |
| **Honest status** | SUBSTANTIAL for the shared offline application |
| **Remaining gap** | No formal user study or accessibility audit; the viewer and evidence are not yet assembled into both final role repositories (`SUB-001`) |
| **Proposed owner/action** | `SUB-001`: validate both role-repository user workflows; retain any formal usability/accessibility findings without inventing scores |

---

## 5. Reliability

Covers maturity, availability, fault tolerance, and recoverability.

| Field | Detail |
|---|---|
| **Current evidence** | 312 deterministic offline tests; 92.51% branch coverage; 7/7 frozen hashes guard behavioral regressions; malformed frames fail closed; equivocation rejected; profile mismatch stops before play; queue backpressure and bounded capacity tested; Gatekeeper admission/close atomic |
| **Measurable indicator** | Test pass rate; branch coverage %; frozen manifest; Hcommit pass rate |
| **Honest status** | SUBSTANTIAL for offline scope |
| **Remaining gap** | FastMCP server in-process restart not supported (deliberately process-scoped); no measured MTBF under sustained real-team load; counted-game reliability unvalidated |
| **Proposed owner/action** | Document server-lifecycle limitation explicitly; measure stability under load test once `CON-001` capacity measurements are collected |

---

## 6. Security

Covers confidentiality, integrity, non-repudiation, accountability, and authenticity.

| Field | Detail |
|---|---|
| **Current evidence** | Role-legal observations only (no hidden-state leak to strategies); commit-reveal (SHA-256 `VERIFIED_REFERENCE_INTEROP`); secret scanner (`tools/offline_ops/secrets/`) with zero findings; `.env-example` with no secret values; URL validation and redaction; no credentials in artifacts or docs; `scan-secrets` in composed quality gate |
| **Measurable indicator** | Secret-scan findings count; observation-isolation test pass rate; Hcommit golden-vector pass rate |
| **Honest status** | SUBSTANTIAL for offline/local scope |
| **Remaining gap** | No production security audit performed; tunnel authentication not yet exercised in current phase; Gmail least-privilege setup not yet configured; external-team credential exchange not yet executed |
| **Proposed owner/action** | `SEC-001` (DONE for scanner); `HUM-001`: complete bilateral auth before any external operation |

---

## 7. Maintainability

Covers modularity, reusability, analysability, modifiability, and testability.

| Field | Detail |
|---|---|
| **Current evidence** | All project-authored Python files ≤150 nonblank/non-comment lines (`REF-001` DONE); Ruff zero errors; SDK facade (`SDK-001` DONE); versioned configuration boundary (`CFG-001` DONE); layered tests with documented boundaries (`TST-001` DONE); `DecisionBackend`, `ScentModel`, and policy factory extension points; ADRs for six architectural decisions |
| **Measurable indicator** | Ruff error count; 150-line compliance count; test collection count; SDK facade inventory test |
| **Honest status** | SUBSTANTIAL |
| **Remaining gap** | Complete public-symbol docstring inventory absent (`DOCS-002` PLANNED); project-wide duplication analysis absent; extension-point lifecycle and compatibility policy incomplete (`EXT-001` PLANNED) |
| **Proposed owner/action** | `DOCS-002`: automated docstring inventory; `EXT-001`: document extension contracts |

---

## 8. Portability

Covers adaptability, installability, and replaceability.

| Field | Detail |
|---|---|
| **Current evidence** | Python 3.11+ declared in `pyproject.toml`; `uv`-only workflow; path-safe local execution on Windows, Linux, and WSL; no OS-specific system calls in core game logic; `uv sync` tested in CI (GitHub Actions); cross-Python 3.12/3.13 test serializer fixed in Phase 4D5 |
| **Measurable indicator** | CI pass rate on target Python versions; `uv sync` success; test suite pass rate |
| **Honest status** | SUBSTANTIAL for Windows/Linux/WSL with Python 3.11–3.13 |
| **Remaining gap** | No macOS CI run recorded in current evidence; no Docker or container packaging; two-repository submission layout not yet assembled (`SUB-001`) |
| **Proposed owner/action** | Add macOS CI runner when `GIT-001` branch/release governance is in place; `SUB-001`: assemble role repositories |

---

## Summary table

| # | Characteristic | Honest status | Key gap | TODO |
|---|---|---|---|---|
| 1 | Functional suitability | SUBSTANTIAL | Counted games; submission repos; research publication | HUM-001, SUB-001, RES-001 |
| 2 | Performance efficiency | PARTIAL | CPU/RAM/latency unmeasured | CON-001 measurement plan |
| 3 | Compatibility | SUBSTANTIAL (offline) | Real-team bilateral; artifact scope | HUM-001 |
| 4 | Usability | SUBSTANTIAL (shared offline app) | Formal user/accessibility study; final role-repository workflows | SUB-001 |
| 5 | Reliability | SUBSTANTIAL (offline) | Server restart; load reliability | CON-001 |
| 6 | Security | SUBSTANTIAL (offline) | Production audit; tunnel auth | HUM-001 |
| 7 | Maintainability | SUBSTANTIAL | Docstring inventory; extension policy | DOCS-002, EXT-001 |
| 8 | Portability | SUBSTANTIAL | macOS CI; submission layout | GIT-001, SUB-001 |

**This assessment is internal and evidence-based. It is not a certification, not a claim of
production readiness, not a claim of counted-game readiness, and not a claim of
external-team compatibility. All gaps are tracked in [`docs/TODO.md`](TODO.md).**
