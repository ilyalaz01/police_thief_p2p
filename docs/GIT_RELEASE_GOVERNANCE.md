# Git, Pull Request, and Release Governance

This document defines the inspectable development workflow for the shared Police–Thief repository.
It closes `GIT-001`; it does **not** create the two final role repositories or authorize the final
`v1.0-submission` tags. Those actions remain under `SUB-001` and require exact-content approval.

## Authority and honesty boundary

The official assignment rules and [`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md)
remain above these generic engineering controls. Git history is evidence, not a place to repair the
past cosmetically. Never backdate, reassign authorship, force-push accepted history, fabricate a
review, or reconstruct prompt bodies that were not retained.

The formal PRD/PLAN/TODO baseline was retrospective. That limitation remains visible. Phase 4D11
proves the workflow used after recovery; it does not claim that the prototype originally followed
the recovered process.

## Accepted evidence at the Phase 4D11 cutoff

The evidence cutoff is merge commit `c1e0d5f7930ab24e1dd5106ced4b55347e344374`.

| Control | Inspectable evidence | Decision |
|---|---|---|
| Feature branches | Focused branches were merged into `main` through PR-shaped merge commits | Accepted |
| Coherent commits | RED tests, implementation/refactor, corrections, and evidence use separate messages | Accepted |
| Pull Requests | 18 accepted first-parent PR merges: #1–#10 and #12–#19 | Accepted |
| Automated review | PR #19 passed the same fail-closed release quality gate used locally | Accepted |
| Human review | Formal independent GitHub review is not present on every historical PR | Recorded exception; never fabricated |
| Attribution | Eight `ndvp39@gmail.com` authored commits are reachable from accepted `main` | Accepted; authorship preserved |
| Significant tag | `team-baseline-v1` is an annotated tag pointing to validated commit `96d3878…` | Accepted |
| Final tags | `v1.0-submission` is absent | Correctly blocked under `SUB-001` |

PR numbers are identifiers, not a required continuous sequence. The absent #11 does not erase the
18 inspectable accepted PR merges. The retained JSON audit records the exact list.

## Required change workflow

1. Start a focused topic branch from the latest accepted `main`.
2. Link the change to a PRD/PLAN/TODO item and any controlling ADR or interoperability decision.
3. For behavioral changes, retain a failing characterization/contract commit before implementation.
4. Keep authorship truthful and commits coherent; do not squash or reassign another contributor's
   work without explicit agreement.
5. Run focused tests, the full pytest/coverage gate, Ruff, Hcommit vectors, the frozen manifest,
   conformance vectors, and the sanitized public-snapshot secret scan.
6. Open a PR that states scope, evidence, risks, frozen boundaries, and remaining blockers.
7. Request another contributor's review when available. If schedule requires self-merge, record the
   exception and require a green automated quality gate plus an explicit evidence review.
8. Merge normally without force, then verify local `main`, `origin/main`, PR state, and worktree.

CI checks out full history and tags (`fetch-depth: 0`) because a shallow clone cannot independently
verify merge lineage, contributor provenance, or annotated tags. Credentials are not persisted.

## Tag and release policy

`team-baseline-v1` demonstrates the annotated-tag mechanism for the shared validated baseline. It
is not a final academic submission tag.

The exact name `v1.0-submission` is reserved for each final Police and Thief repository. Create it
only after all of the following are true:

- role export manifests are approved and both repositories pass their own offline quality gates;
- required README, `config/`, PRD, PLAN, TODO, cross-link, GUI, and Replay materials are present;
- secret/privacy/license review passes on the exact commit in each repository;
- both exact commit SHAs receive explicit human content approval.

Tags must be annotated, must identify the approved commit exactly, and must never be moved silently.
The final remote creation, push, and tag are external submission operations, not Phase 4D11 work.

## Reproduction commands

```bash
git log --first-parent --merges --oneline main
git log --format='%H %an <%ae> %s' main
git cat-file -t team-baseline-v1
git rev-parse 'team-baseline-v1^{}'
git show-ref --verify refs/tags/v1.0-submission
uv run pytest -q tests/integration/test_governance/test_git_release_governance.py --no-cov
uv run python -m tools.offline_ops.cli quality-gate
```

The `show-ref` command is expected to return non-zero until `SUB-001` is accepted. This expected
absence is a release guard, not a failed Phase 4D11 acceptance check.
