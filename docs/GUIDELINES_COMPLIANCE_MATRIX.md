# Software Project Guidelines Compliance Matrix

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Allowed ratings are `COMPLIANT`, `PARTIAL`, `MISSING`, `NOT_APPLICABLE_WITH_RATIONALE`, and
`BLOCKED_BY_HIGHER_AUTHORITY`. Overall status is **PARTIAL**; generic guidance cannot override the
[authority hierarchy](../RULES_AND_INTEROP_BASELINE.md).

| Guideline item | Status | Current evidence | Exact gap / applicability | TODO | Acceptance evidence required |
|---|---|---|---|---|---|
| 0 Professional model/SDLC | PARTIAL | `CONTRIBUTING.md`; retrospective PRD/PLAN/TODO | Formal planning followed prototype; future lifecycle evidence absent | GIT-001 | Reviewed future change demonstrates ordered governance/TDD |
| 1 README | PARTIAL | Root README install/verification/safety plus governance index | Not a complete manual for options, config, examples and troubleshooting | DOC-001 | User-manual review and link/governance test |
| 1 PRD/PLAN/TODO | COMPLIANT | `docs/PRD.md`, `PLAN.md`, `TODO.md` | Retrospective limitation disclosed | GOV-001 | Phase 4D0 audit and governance tests |
| 1 Dedicated PRDs | COMPLIANT | Six mechanism PRDs | Must remain live as mechanisms change | GOV-001 | Required-file/link test |
| 1 Recommended layout | PARTIAL | Layered `src`, `tests/unit`, `tests/integration`, `tests/system`, `docs`, `interop`, `reports`, `config`; `pyproject.toml`, `uv.lock`, `.env-example` | `results`, `assets`, and `notebooks` remain absent | VIS-001 | Phase 4D3 test evidence plus future approved research layout |
| 2 Modular structure | PARTIAL | Feature/layer package structure; REF-001 split evidence | Building-block contracts remain incomplete | DOCS-002 | Public-block contract inventory and review |
| 2 150-line rule | COMPLIANT | ADR-005; Phase 4D1A–D1D audits; permanent regression test | Zero `src/` or `tests/` Python violations across 98 files | REF-001 | Phase 4D3 194-test acceptance and independent count audit |
| 2 Docstrings/comments/quality | PARTIAL | Many module/class/function docstrings; Ruff configured | Complete public-symbol/docstring/WHY audit absent | DOCS-002 | Automated inventory and review |
| 3 SDK/OOP | COMPLIANT | `PoliceThiefSDK` plus six cohesive services; CLI delegates a typed request | Legacy imports remain compatibility-only; public inventory test guards new operations | SDK-001 | Phase 4D2B facade, identity, and consumer-boundary tests |
| 4 Gatekeeper/rate/queues | COMPLIANT | Process-wide `ApiGatekeeper`; versioned rates; bounded outbound/inbound FIFO; drain; safe metrics | Frozen retry schedule remains in `McpPeerClient`, with every attempt gated, per higher authority | API-001 | Phase 4D2C queue/rate/failure and transport regression tests |
| 5 TDD and organization | PARTIAL | Phase 4D3 linked RED/GREEN commits, layered collection, shared fixtures, and source map | Historical pre-code TDD remains honestly unprovable | TST-001 | Continue linked RED/GREEN evidence for future changes |
| 5 Coverage/edge/failure reports | COMPLIANT | 93.91% branch run; live critical-path map; sanitized RED/GREEN retention policy and audit | Must remain enforced and automated by the separate RE-001 wrapper | QLT-001 | Phase 4D3 machine-readable and Markdown evidence |
| 6 Ruff | COMPLIANT | `pyproject.toml` exact broad rules; Phase 4D3 zero-error run | Must remain enforced | QLT-001 | Phase 4D3 recorded green command |
| 6 Configuration/secrets | COMPLIANT | Strict operational/rate loaders, tracked JSON examples, `.env-example`, ignore rules, sanitized scanner | Current offline/self-test modes require no credentials; future secret use remains environment-only | CFG-001 | Phase 4D2A/2C compatibility and secret-scan tests |
| 7 Version tracking | COMPLIANT | pyproject/package/config `1.0.0`; strict operational/rate schemas `1.0`; profile schemas remain separate | Unsupported schema/package/rate versions fail closed | CFG-001 | Phase 4D2A/2C coherence and rejection tests |
| 7 Git branches/commits/PRs/tags | PARTIAL | baseline tag, honest clean commits, CONTRIBUTING | Future PR/release review evidence absent | GIT-001 | Inspectable branch/PR/tag workflow evidence |
| 7 Prompt log | PARTIAL | Retrospective summaries and future template | Historical prompts cannot honestly be reconstructed | GIT-001 | Complete future entries linked to work |
| 7 uv-only workflow | COMPLIANT | `pyproject.toml`, `uv.lock`, documented `uv` commands | External submodule owns its own requirements and is outside project package authority | PKG-001 | Repository workflow scan and uv gates |
| 8 Research/sensitivity | PARTIAL | Experiments and phase reports | Safe reproducible publication, formal sensitivity and citations incomplete | RES-001 | Published inputs/seeds/results/analysis |
| 8 Notebooks/visualization | MISSING | Markdown reports only | `notebooks/`, reproducible figures and professional visuals absent | VIS-001 | Clean notebook rerun and accessible artifacts |
| 9 UI/CLI UX | PARTIAL | `peer_cli.py`, runbook, argparse help | Comprehensive workflow, errors, screenshots/applicability/accessibility absent | UX-001 | UX spec/tests and GUI rationale |
| 10 Costs/pricing | MISSING | No applicable measured cost report | Compute/storage/network/token applicability and forecast absent | COST-001 | Reproducible measured cost analysis |
| 11 Extensibility/maintainability | PARTIAL | `DecisionBackend`, `ScentModel`, profiles/policy factories | Lifecycle/hooks/middleware/compatibility policy incomplete | EXT-001 | Extension contract and tests |
| 12 ISO/IEC 25010 | MISSING | Quality traits appear across tests/docs | No systematic eight-characteristic assessment | ISO-001 | Evidence-backed internal assessment |
| 13 Package organization | PARTIAL | src layout, pyproject, `__init__`, `__version__` | Author metadata/export/path/dependency audit incomplete | PKG-001 | Package checklist evidence |
| 14 Concurrency/thread safety | COMPLIANT | Process-owned FastMCP daemon; bounded Gatekeeper workers/FIFO inboxes; atomic admission/close; deterministic race, cleanup and capacity tests | In-process FastMCP restart is deliberately unsupported; peer-process termination owns server cleanup | CON-001 | Phase 4D4 lifecycle/load/race audit and ownership diagram |
| 15 Building blocks | PARTIAL | PLAN module/I/O descriptions and typed interfaces | Per-public-block setup/validation/edge contracts incomplete | DOCS-002 | Audited block contracts |
| 16 Final checklist | PARTIAL | Detailed group mapping below | Multiple technical/research/operations gaps remain | GOV-001 | All group items separately satisfied |
| 17 Quick-reference enforcement | PARTIAL | pytest/Ruff/coverage/frozen/vector/config/SDK/Gatekeeper/line-limit commands | Unified release automation incomplete | RE-001 | Unified fail-closed offline quality gate |
| 18 References | NOT_APPLICABLE_WITH_RATIONALE | Guidelines supply a bibliography | Bibliography is source context, not an implementation requirement | GOV-001 | Rationale retained |
| 19 Applicability note | BLOCKED_BY_HIGHER_AUTHORITY | Baseline authority order and ADR-001 | Generic advice cannot override rules/frozen/negotiated semantics | HUM-001 | Higher-authority clarification or explicit agreement |

## Final Submission Checklist groups

| Checklist group/item | Status | Current evidence | Exact gap / rationale | TODO | Acceptance evidence required |
|---|---|---|---|---|---|
| 16.1 Documentation & structure | PARTIAL | Governance set, six PRDs, six Mermaid diagrams, prompt log | README incomplete; prompt history necessarily retrospective | DOC-001 | Manual review plus governance tests |
| 16.2 SDK architecture | COMPLIANT | Root `PoliceThiefSDK`, six services, typed CLI delegation | New operations must extend the guarded inventory | SDK-001 | Phase 4D2B interface/consumer tests |
| 16.2 OOP/no duplication | PARTIAL | Protocols/dataclasses/shared helpers | Project-wide duplication analysis absent | PKG-001 | Static/review evidence |
| 16.2 API gatekeeper/rates/queues | COMPLIANT | Versioned centralized FastMCP gate; bounded FIFO/backpressure/drain/metrics | No other production external API client exists | API-001 | Phase 4D2C deterministic and transport tests |
| 16.2 ≤150/docstrings/style | PARTIAL | Zero line-limit violations; Ruff clean | Complete public-symbol/docstring inventory remains incomplete | DOCS-002 | Docstring/block audit plus Ruff |
| 16.3 TDD | PARTIAL | Phase 4D3 linked RED/GREEN commits and layered tests | Historical sequence before the retrospective baseline is unprovable | TST-001 | Continue linked RED/GREEN commits |
| 16.3 Coverage/Ruff | COMPLIANT | ≥85 branch gate; Phase 4D3 93.91% and Ruff zero | Continue enforcement | QLT-001 | Phase 4D3 recorded green commands |
| 16.3 Edge cases/reports | COMPLIANT | Live critical-path expectations plus sanitized RED/GREEN retention and audit | Future changes must update mappings and evidence | QLT-001 | Phase 4D3 critical-path and machine-readable evidence |
| 16.4 Config/security/version | COMPLIANT | Strict operational loader, config example, `.env-example`, ignore rules, sanitized scan, coherence gates | MatchProfile and operational schemas remain deliberately separate | CFG-001 | Phase 4D2A version/secret tests |
| 16.4 uv/lock/project | COMPLIANT | `uv.lock`, `pyproject.toml`, commands | Keep project workflows uv-only | PKG-001 | Command scan |
| 16.5 Research/sensitivity | PARTIAL | Experiments/reports | Safe reproducible publication incomplete | RES-001 | Reviewed public evidence bundle |
| 16.5 Notebook/graphs/screens | MISSING | Mermaid architecture only | Analysis notebook/assets absent | VIS-001 | Deterministic notebook/figures |
| 16.5 Token cost | MISSING | None | No measured applicable cost analysis | COST-001 | Reviewed calculations |
| 16.6 Extension points | PARTIAL | Policy/scent interfaces | Compatibility/lifecycle policy incomplete | EXT-001 | Contract/tests |
| 16.6 Professional package | PARTIAL | Installable src package | Package checklist gaps | PKG-001 | Package audit |
| 16.6 Parallel/thread safety | COMPLIANT | Exact worker-plus-queue capacity, backpressure, shutdown and post-timeout reaping are tested | Server lifetime remains intentionally process-scoped | CON-001 | Phase 4D4 deterministic load/race evidence |
| 16.6 Building blocks | PARTIAL | PLAN responsibilities | Complete I/O/setup contracts absent | DOCS-002 | Documentation audit |
| 16.6 ISO 25010 | MISSING | No consolidated assessment | Eight characteristics unassessed | ISO-001 | Evidence matrix |
| 16.6 Git/license/attribution/deploy | PARTIAL | MIT, submodule credit, history, CONTRIBUTING | PR/release/deployment evidence incomplete | GIT-001 | Reviewed release record |
