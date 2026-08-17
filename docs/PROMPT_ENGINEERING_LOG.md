# Prompt Engineering Log

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Retrospective limitation

No complete historical prompt log existed. Verbatim historical prompts, approvals, dates, and
iterations cannot be reconstructed and are not claimed. This log contains only high-level process
summaries supported by existing phase reports. It excludes private chat bodies, personal
messages, credentials, partner instructions, live endpoints, and operational nonces.

The known process mistake is that implementation preceded formal PRD/PLAN/TODO approval. The
corrective action is this honest retrospective baseline plus a rule that every future significant
prompt links an approved requirement, plan/ADR as applicable, TODO ID, verification, and resulting
commit/PR.

## Evidence-derived summaries

| Phase evidence | Goal summary | Lesson supported by evidence |
|---|---|---|
| Phase 1/core reports and tests | Establish deterministic rules, legal observations and replay. | Higher-authority edge rules and hidden-state boundaries need explicit regression tests. |
| Phase 2/3 reports and experiments | Compare baselines, belief and search under seeded evaluation. | Separate research proposals from frozen competitive choices; retain seeded evidence. |
| Interop verification/Phase 4A | Resolve byte contracts and complete local two-peer flow. | Similar-looking serialization domains and reference/book behavior must remain named. |
| Phase 4B/4C reports | Validate transport gates and prepare blocked human worksheets. | Technical validation never substitutes for bilateral approval or authorization. |
| Phase 4D0 audit | Recover requirements, architecture, quality and task governance. | Retrospective documentation must state its timing and leave technical gaps open. |
| Phase 4D1A test split | Mechanically split oversized interoperability tests under REF-001. | Path-normalized collection and AST manifests make organization-only moves independently verifiable. |
| Phase 4D1A.1 correction | Repair live test references and specify the AST digest preimage. | Governance should validate live backticked test paths, and evidence hashes need exact framing rules. |
| Phase 4D1B belief split | Characterize the belief contract, then extract three private pure helpers. | Pin outputs, signatures, exceptions, exports, and diagnostics before moving strategy calculations. |
| Phase 4D1C artifact split | Characterize schema, writer, hash, and consensus bytes before moving encoding helpers. | Introspected signatures and AST/constant manifests catch context-sensitive movement errors such as annotation evaluation. |
| Phase 4D1C.1 correction | Restore normal formatting while preserving production and test AST manifests. | Line limits need explicit anti-compression checks, including physical length and unsuppressed lint gates. |
| Phase 4D1D Phase 3B split | Pin 27 seeded model/usage/depth combinations, public API, diagnostics and errors before extracting models, replies and scoring. | Strategy refactors need output-level vectors, not only ordinary unit coverage. |
| Phase 4D1D runtime split | Pin runtime signatures/conversions and rerun isolated-process, terminal, audit/replay and schema 1.1 flows while separating responsibilities. | Unicode defaults and module-global patch points are observable contracts; compare them explicitly before accepting a structural split. |
| Phase 4D2A operational config | Commit a failing config-contract test, then add a strict loader, CLI preflight, safe example and value-redacting scan under CFG-001/ADR-006. | Keep operational metadata outside MatchProfile bytes; strict version/mode rejection before side effects is safer than implicit migration. |
| Phase 4D2B SDK facade | Commit a failing single-entry inventory, then compose six concern-specific services and reduce CLI to typed delegation under SDK-001/ADR-003. | Alias proven implementations instead of wrapping behavior; separate facade completeness from future Gatekeeper policy. |
| Phase 4D2C API Gatekeeper | Commit a failing centralized-call contract, then add file-loaded rates, bounded FIFO/backpressure/drain/value-free metrics and gate every FastMCP attempt under API-001/ADR-004. | Preserve higher-authority retry ownership while gating each attempt; bound inbound mailboxes without dropping or reordering messages. |
| Phase 4D3 test quality | Reorganize tests into unit/integration/system layers and add critical-path/coverage evidence without changing collection intent. | Compare normalized collection and behavior before treating a test move as semantics-preserving. |
| Phase 4D4 concurrency | Reproduce Gatekeeper close/admission races, then make capacity, shutdown and worker reaping deterministic. | Concurrency acceptance needs explicit ownership, exact capacity, race barriers and eventual cleanup evidence. |
| Phase 4D5 partner release integration | Port the partner-owned offline-ops boundary onto current main, preserve authorship, repair stale paths/encoding, and validate the same CI gate. | Clean-port stale work rather than rebasing through unrelated architecture; test contracts must normalize cross-Python AST representation. |
| Phase 4D6 CLI/manual | Re-read official and guideline sources, add RED contracts for discoverable safe CLI help and a complete manual, then expose higher-authority submission blockers. | Guideline closure must not hide official two-repository, GUI/Replay, counted-game, or reporting requirements; validate publishable state in a clean checkout while preserving ignored local evidence. |
| Phase 4D7B Replay shell | Derive a role-safe view boundary and standalone post-game Replay app from official Chapter 7, then verify it on synthetic tamper cases and a retained completed-game log. | Keep live partial truth structurally separate from post-game truth; verify before rendering and never embed revealed nonces in the HTML app. |
| Phase 4D7C Live GUI | Add RED role-safe feed/runtime/loopback contracts, connect observations to an atomic bounded feed, visually review localhost Live/Replay apps, and retain synthetic screenshots. | Treat presentation as another privacy boundary: use an exact allow-list schema, reject extra fields, bind only to loopback, and preserve protocol/profile/strategy bytes. |

## Template for every future significant prompt

Copy one entry; summaries are preferred over sensitive prompt bodies.

### PE-YYYY-NNN — Short title

- Date: YYYY-MM-DD (actual entry date)
- Author/operator: role or approved public identifier
- Context: requirement/TODO/ADR/evidence links
- Goal: measurable intended outcome
- Constraints: authority, frozen boundary, privacy, scope and hard stops
- Output: files/results produced; no sensitive body
- Verification: exact `uv` commands and observed counts/status
- Refinements: concise iteration summaries and why they were needed
- Decision: accepted/rejected/proposed plus rationale and approver evidence
- Commit/PR link: immutable identifier when one exists
- Lessons learned: reusable prompting/process guidance
