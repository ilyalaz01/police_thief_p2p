# Phase 4D11 — Git and Release Governance Audit

Status: **GREEN locally; PR quality-gate acceptance required before merge**.

Classification: `OFFLINE_REPOSITORY_GOVERNANCE_AUDIT`.

## Outcome

`GIT-001` is closed for the shared development repository with inspectable branch, coherent
commit, PR/CI, contributor-attribution, annotated-tag, and exception evidence. The audit does not
rewrite history and does not claim that retrospective PRD/TDD/prompt records existed before the
prototype.

The final `v1.0-submission` tag remains absent. Phase 4D11 neither creates the two official role
repositories nor authorizes their publication or tagging; those actions remain under `SUB-001`.

## Authority and scope

The official assignment PDF/Appendices E/F and `RULES_AND_INTEROP_BASELINE.md` remain controlling.
This phase changes no production source, rule, physics, strategy, observation, Hcommit, scent, MCP,
artifact, profile, UID, consensus, audit, replay, scoring, or transport behavior.

No peer, tunnel, public request, opponent contact, Gmail action, gameplay, counted operation,
external role repository, force-push, or tag operation occurred.

## Inspectable cutoff evidence

- Cutoff: `c1e0d5f7930ab24e1dd5106ced4b55347e344374`, the accepted PR #19 merge.
- Accepted first-parent PR merges: 18, exact PR numbers #1–#10 and #12–#19.
- Accepted commits authored as `ndvp39@gmail.com`: 8 reachable from `main`.
- `team-baseline-v1` is an annotated tag object `e8fea4a…` pointing at validated commit
  `96d3878…`.
- PR #19 passed GitHub Actions run `32066390100` before its normal non-force merge.
- The exact final tag `v1.0-submission` is absent and explicitly human-gated.

An independent GitHub reviewer is not visible on every historical PR. That is retained as an
exception. The project does not fabricate approvals; future changes request another contributor
when available and otherwise require a documented self-merge exception plus green automated and
evidence review.

## TDD and corrections

Commit `bf4de8d` introduced the governance contract first. The retained RED run produced three
expected failures: shallow CI checkout, missing machine-readable audit, and GIT-001 still open.
Two independent assertions already passed: the annotated tag was real and accepted PR/partner
history was visible.

The initial GREEN attempt exposed a Git-version difference: absent `show-ref --verify` returned
128 rather than the assumed 1. The test now uses portable empty `git tag --list` output without
weakening the absence check. Focused contract: 5/5.

The first full suite produced 347 passes and one stale governance-format failure because a matrix
TODO cell contained `GIT-001 (DONE)` instead of the exact live ID `GIT-001`. The cell was corrected;
the combined new/existing governance subset then passed 13/13. This was a documentation-link
contract correction, not a production behavior change.

## Controls added

- CI checkout now uses `fetch-depth: 0`, retains tags, keeps recursive submodules, and still does
  not persist credentials.
- `docs/GIT_RELEASE_GOVERNANCE.md` defines branch, commit, TDD, review, merge, attribution,
  exception, and final-tag gates.
- A regression test inspects real Git objects/history rather than trusting prose alone.
- TODO, compliance, readiness, plan, release manual, README index, and prompt log agree on the
  remaining `SUB-001`/`HUM-001` boundary.

## Acceptance decision

Accept Phase 4D11 locally only when the final rerun recorded below is green. Merge remains subject
to the public PR quality gate. A green merge closes shared-repository Git governance; it does not
make the project ready for another-team play or final academic submission.

## Final local validation

- Full suite: 348/348 passed, no skips or xfails.
- Combined statement/branch coverage: 92.58684863523573% (required threshold: 85%).
- Focused Git governance contract: 5/5; combined new/existing governance subset: 13/13.
- Ruff over `src`, `tests`, and `tools`: zero errors.
- Hcommit golden vectors: 5/5; authoritative frozen manifest: 7/7.
- MIT conformance kit: 125/125.
- Staged/public snapshot scan under the documented CI exclusion of synthetic
  `tests/offline_ops` scanner fixtures: PASS with zero retained findings.
- Production-source diff from the accepted cutoff: empty.

The direct snapshot scan without that CI exclusion failed closed on eight deliberately synthetic
test-fixture findings and retained no matched values. This expected direct-scan result is disclosed,
not relabelled as clean. Ignored historical local transport evidence is outside the Git index and
is likewise not relabelled as a clean repository-root scan. The CI-policy result covers the exact
bytes proposed for commit, including this disclosure, and excludes the pinned third-party submodule
per scanner policy.

## Remaining blockers

1. `SUB-001`: deterministic construction and independent validation of separate Police and Thief
   repositories, followed by exact-content human approval before remote/tag operations.
2. `HUM-001`: bilateral compatibility approvals and explicit authorization before any other-team
   warm-up, public transport, Gmail, or counted match.

The adjacent JSON record retains the same machine-readable decision and validation values.
