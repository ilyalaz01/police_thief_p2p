# Phase 4D6 - CLI Manual and Submission Readiness

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN** for `DOC-001` and `UX-001`. This phase does not close `GUI-001`, `SUB-001`,
`HUM-001`, real-team readiness, counted readiness, or final course-submission readiness.

## Authority review

The phase re-read the official 160-page PDF, including the development sequence, final checklist,
Appendix C submission requirements, Appendix E mandatory rules, and Appendix F parameters. It also
re-read `RULES_AND_INTEROP_BASELINE.md`, `docs/INTEROP_DECISIONS.md`, the Software Project
Guidelines, PRD/PLAN/TODO, compliance matrix, and the latest accepted Phase 4D5 audit.

The review found that generic guideline cleanup must not hide official final-delivery requirements:
Rule 49 requires separate Police and Thief GitHub repositories; the final checklist requires a
role-legal Live GUI, Replay evidence showing `Verified OK`, annotated submission tags, and at least
two counted games against different opponents. Gmail and counted operations remain human-gated.
These gaps now have explicit `GUI-001`, `SUB-001`, and existing `HUM-001` ownership.

## TDD evidence

RED commit `db8e8ea1e87238b8c5d61f9350e173c69ba2ad0e` added four requirements-level tests.
The first run failed because `peer_cli.build_parser` did not exist; no runtime was started.

GREEN commit `cb15a533297c8a5cb871abf477010fef5874451a` added a side-effect-free parser builder,
descriptive help for every accepted option, explicit authorization warnings, a complete current
README manual, and `docs/OFFICIAL_SUBMISSION_READINESS.md`. Established defaults and SDK
delegation remain unchanged. The warm-up command now uses the required `uv run` form.

## Acceptance results

| Check | Result |
|---|---|
| Focused CLI/manual/governance/configuration | PASS - 24/24 |
| CLI help | PASS - every option visible; no peer side effect |
| Full suite | PASS - 298/298, no failures |
| Branch coverage | PASS - 94.07%, threshold 85% |
| Ruff | PASS - zero errors |
| Hcommit | PASS - 5/5 |
| Frozen manifest | PASS - 7/7 exact |
| Conformance kit | PASS - 125/125 |
| Python 150-line gate | PASS - modified Python files max 124 counted lines |
| Clean-worktree composed quality gate | PASS - exit 0; secret scan zero findings |

The first composed run in the long-lived evidence workspace stopped only at the secret scan: it
found eight pre-existing ignored local evidence files across the sanitized categories
`tunnel_url` and `non_artifact_nonce`. Functional, Ruff, Hcommit, frozen, and conformance checks
all passed. No finding value was printed, no evidence file was deleted, and the scanner was not
weakened. The identical gate then passed in a clean detached worktree built from the accepted
commit. This distinguishes a publishable tracked checkout from intentionally retained local
operational evidence.

## Behavior and safety boundary

No game rule, scoring, strategy, `ScentTacticalPolice`, observation, scent, Hcommit, MatchProfile,
wire, retry, deadline, duplicate/equivocation, audit/replay, artifact schema/bytes/hash/consensus,
Rule 47, frozen file, dependency, or conformance-kit content changed. No peer, gameplay, public
request, tunnel, Gmail, external-team contact, league reporting, counted operation, tag, or final
role repository was created.

## Remaining blockers

- `GUI-001`: implement and test the mandatory role-legal Live GUI and artifact-backed Replay view;
- `RES-001`/`VIS-001`: publish safe reproducible analysis and professional figures;
- `SUB-001`: assemble, cross-link, independently verify, and later tag two final role repositories;
- `HUM-001`: obtain explicit bilateral compatibility evidence before another-team play;
- counted games, Gmail, and Moodle remain explicitly human-authorized operations.

The smallest justified next technical milestone is `GUI-001`; it addresses the largest remaining
official offline requirement without contacting another team or changing competitive behavior.
