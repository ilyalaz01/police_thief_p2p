# Phase 4D12B — Role README Overlays and Assembly Runbook

Status: **GREEN locally; PR quality-gate acceptance required before merge**.

Classification: `OFFLINE_SUBMISSION_ASSEMBLY_PREPARATION`.

## Outcome

Phase 4D12B supplies independently testable, future-root README overlays for the Police and Thief
repositories and an ordered offline assembly runbook. This is necessary Rule 49/50 preparation,
not cosmetic documentation and not final-repository readiness.

Both overlays are standalone user manuals for the validated shared implementation. They state the
exact role/runtime-policy truth, retain safe offline install/test/GUI/Replay commands, link the
Rule 50 materials, and keep the counterpart URL at `PENDING_HUMAN_APPROVAL`. The assembly runbook
preserves shared history/authorship, separates exporter bytes from Git history, restores the
approved conformance submodule separately, and stops before remotes or final tags.

## Source and authority review

The phase used official Rules 49/50, `RULES_AND_INTEROP_BASELINE.md`, the accepted Phase 4D12A
content policy, the live PRD/PLAN/TODO/readiness ledger, release/Git governance, current runtime
construction, and the independent partner export-tool contract. Generic README conventions did
not alter game, interop, policy, or authorization facts.

## TDD evidence

RED commit `bbfd555` added five contracts first. All five failed: both overlays and the assembly
runbook were absent, while the content policy still carried an unresolved overlay marker.

GREEN commit `89a9c48` added the two templates, runbook, exact policy paths, and the content-policy
cross-reference. The combined Phase 4D12A/4D12B submission contracts passed 10/10. The new test is
103 counted lines; the Police/Thief templates are 88/89 physical lines and the runbook is 94.

## Proven facts

- Police identifies `ScentTacticalPolice` only as `FROZEN_ACCEPTED`.
- Thief identifies `RandomLegalThief` only as `CURRENT_DEFAULT_NOT_NEW_CHAMPION`.
- Both overlays include the Rule 50 minimum links and safe offline commands.
- Both expose the pending counterpart value and explicitly reject it as a Rule 49 cross-link.
- The ordered runbook requires exact provenance, explicit manifests, deterministic snapshots,
  history-preserving role branches, submodule reprovisioning, two independent gates, and final
  human content/URL approval.
- No production source or partner-owned exporter path changed.

## Not proven and still blocked

The templates are candidate bytes, not the actual final root READMEs. Exporter integration, exact
include manifests, candidate role trees, reciprocal URLs, independent role quality gates, remotes,
and annotated `v1.0-submission` tags remain under `SUB-001`. No placeholder satisfies Rule 49.

No peer, tunnel, public request, opponent contact, Gmail action, gameplay, counted operation,
repository creation/publication, or tag occurred.

## Final validation

- Focused Phase 4D12A/4D12B contracts: 10/10 passed.
- Full suite: 358/358 passed, no skips or xfails.
- Combined statement/branch coverage: 92.58684863523573% (threshold: 85%).
- Ruff over `src`, `tests`, and `tools`: zero errors.
- Hcommit golden vectors: 5/5; authoritative frozen manifest: 7/7.
- MIT conformance kit: 125/125.
- Repository quality gate and documented scanner policy: PASS, zero findings.
- Production-source diff and partner-owned exporter-path diff: empty.

The adjacent JSON retains the same boundary and machine-readable results. Public PR CI remains the
independent acceptance gate before merge.
