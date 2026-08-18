# ISO/IEC 25010 Internal Quality Assessment

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

**Internal engineering assessment; not an ISO certification.**

This document assesses Police-Thief P2P against all eight ISO/IEC 25010:2011 product-quality
characteristics. Evidence is cited by repository-relative path. No external certification body
was engaged. Gaps are recorded honestly and are not claimed as closed.

Source authority for all game, interoperability, and audit claims remains
[`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md).

Current reconciliation: **GUI-001: DONE; DOCS-002, PKG-001, EXT-001, RES-001, and VIS-001: DONE**
on the shared baseline through Phase 4D9. This assessment incorporates that evidence without
implying final-submission readiness.

---

## 1. Functional suitability

Covers functional completeness, functional correctness, and functional appropriateness.

| Field | Detail |
|---|---|
| **Current evidence** | Deterministic rules engine (Rules 46/47, barriers, scoring, survival); role-legal observations; alternating Thief-first turns; four-tool FastMCP exchange; commit-reveal; audit/replay; schema 1.1 artifact builders; full passing suite; conformance 125/125; Phase 4D7C role-safe Live GUI; Phase 4D9 reproducible local sensitivity publication |
| **Measurable indicator** | Test suite pass rate; conformance vector pass rate; frozen manifest 7/7 |
| **Honest status** | SUBSTANTIAL — core offline function is proven |
| **Remaining gap** | Official six-sub-game aggregation/full shared config (`LGE-001`), Gmail reporting (`MAIL-001`), counted league games (`HUM-001`), and two-repository assembly (`SUB-001`) remain open |
| **Proposed owner/action** | Complete each named gate without modifying the frozen single-sub-game core or inferring external authorization |

---

## 2. Performance efficiency

Covers time behaviour, resource utilisation, and capacity.

| Field | Detail |
|---|---|
| **Current evidence** | Policy decisions are synchronous and deterministic; Gatekeeper bounded outbound workers; `concurrent_max + queue_max` capacity formula documented in `docs/CONCURRENCY_AND_CAPACITY.md`; retry deadlines are monotonic and frozen; Phase 4D10 retains 200 local wall/CPU samples, 30 separate `tracemalloc` peaks, result sizes and sequential throughput |
| **Measurable indicator** | Turn decision latency (ms); game throughput (games/second); peak RAM; CPU time per game |
| **Honest status** | SUBSTANTIAL for the measured fixed local simulator workload |
| **Remaining gap** | `tracemalloc` is not whole-process RSS; multi-game parallelism and Gatekeeper load remain unmeasured at scale; public transport latency is historical evidence only |
| **Proposed owner/action** | Keep the Phase 4D10 one-machine boundary explicit; profile RSS or network/load only when an approved operational scope requires it |

---

## 3. Compatibility

Covers co-existence and interoperability.

| Field | Detail |
|---|---|
| **Current evidence** | 125/125 conformance vectors; Hcommit 5/5 golden cases; professor localhost MCP 4/4; MCP wire `VERIFIED_REFERENCE_INTEROP`; duplicate/equivocation behavior verified; scent and artifact schemas documented in `docs/INTEROP_DECISIONS.md` |
| **Measurable indicator** | Conformance vector pass rate; Hcommit vector pass rate; interop fixture coverage |
| **Honest status** | SUBSTANTIAL for reference-v3 profile; PARTIAL for real-team compatibility |
| **Remaining gap** | No other-team counted game; simultaneous-model turn resolution and artifact consensus remain negotiated; the full Appendix-B counted-series config is unresolved under `LGE-001`; `HUM-001` is BLOCKED |
| **Proposed owner/action** | `LGE-001`: preserve separate config/hash scopes; `HUM-001`: complete the bilateral worksheet and pre-match profile negotiation |

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
| **Current evidence** | Latest accepted full offline quality gate passes with branch coverage above 90%; 7/7 frozen hashes guard behavioral regressions; malformed frames fail closed; equivocation rejected; profile mismatch stops before play; queue backpressure and bounded capacity are tested; Gatekeeper admission/close is atomic |
| **Measurable indicator** | Test pass rate; branch coverage %; frozen manifest; Hcommit pass rate |
| **Honest status** | SUBSTANTIAL for offline scope |
| **Remaining gap** | FastMCP server in-process restart not supported (deliberately process-scoped); no measured MTBF under sustained real-team load; counted-game reliability unvalidated |
| **Proposed owner/action** | Keep the documented process-owned server limitation explicit; add sustained real-team/load evidence only under a separately approved operational scope |

---

## 6. Security

Covers confidentiality, integrity, non-repudiation, accountability, and authenticity.

| Field | Detail |
|---|---|
| **Current evidence** | Role-legal observations only (no hidden-state leak to strategies); commit-reveal (SHA-256 `VERIFIED_REFERENCE_INTEROP`); secret scanner (`tools/offline_ops/secrets/`) with zero findings; `.env-example` with no secret values; URL validation and redaction; no credentials in artifacts or docs; `scan-secrets` in composed quality gate |
| **Measurable indicator** | Secret-scan findings count; observation-isolation test pass rate; Hcommit golden-vector pass rate |
| **Honest status** | SUBSTANTIAL for offline/local scope |
| **Remaining gap** | No production security audit; tunnel authentication is not current evidence; the Gmail sender/least-privilege setup is not implemented or authorized; no external-team credential exchange occurred |
| **Proposed owner/action** | `MAIL-001`: begin only after explicit approval; `HUM-001`: complete bilateral auth before any external operation |

---

## 7. Maintainability

Covers modularity, reusability, analysability, modifiability, and testability.

| Field | Detail |
|---|---|
| **Current evidence** | All project-authored Python files ≤150 nonblank/non-comment lines (`REF-001` DONE); Ruff zero errors; SDK facade (`SDK-001` DONE); versioned configuration boundary (`CFG-001` DONE); layered tests (`TST-001` DONE); complete editable-production docstring inventory plus frozen external contracts (`DOCS-002` DONE); audited package and typed extension lifecycle/compatibility policy (`PKG-001`, `EXT-001` DONE); six ADRs |
| **Measurable indicator** | Ruff error count; 150-line compliance count; test collection count; SDK facade inventory test |
| **Honest status** | SUBSTANTIAL |
| **Remaining gap** | Final role-specific package/export validation and release tags remain incomplete (`SUB-001`); no exhaustive clone detector is claimed beyond the reviewed structural DRY assessment |
| **Proposed owner/action** | `SUB-001`: validate both final role repositories after content approval |

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
| 1 | Functional suitability | SUBSTANTIAL | Series/config/reporting; counted games; submission repos | LGE-001, MAIL-001, HUM-001, SUB-001 |
| 2 | Performance efficiency | SUBSTANTIAL (fixed local workload) | Whole-process RSS; parallel/network load | HUM-001 |
| 3 | Compatibility | SUBSTANTIAL (offline) | Full series config; real-team bilateral; artifact scope | LGE-001, HUM-001 |
| 4 | Usability | SUBSTANTIAL (shared offline app) | Formal user/accessibility study; final role-repository workflows | SUB-001 |
| 5 | Reliability | SUBSTANTIAL (offline) | Server restart; real-team load reliability | HUM-001 |
| 6 | Security | SUBSTANTIAL (offline) | Gmail boundary; production audit; tunnel auth | MAIL-001, HUM-001 |
| 7 | Maintainability | SUBSTANTIAL | Final role-package/export validation | SUB-001 |
| 8 | Portability | SUBSTANTIAL | macOS CI; submission layout | SUB-001 |

**This assessment is internal and evidence-based. It is not a certification, not a claim of
production readiness, not a claim of counted-game readiness, and not a claim of
external-team compatibility. All gaps are tracked in [`docs/TODO.md`](TODO.md).**
