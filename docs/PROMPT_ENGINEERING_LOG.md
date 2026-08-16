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
