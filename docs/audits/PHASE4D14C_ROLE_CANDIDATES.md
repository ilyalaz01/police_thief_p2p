# Phase 4D14C — History-Preserving Role Candidates

Status: **GREEN for both local role candidates; final URLs, remotes and tags remain blocked**.

Classification: `OFFLINE_ROLE_REPOSITORY_ACCEPTANCE`.

## Decision

Accept the local Police and Thief candidates. Both are real history-preserving Git worktrees from
the exact accepted shared source commit. They contain one truthful role-assembly commit each,
retain contributor history, reproduce the reviewed bytes, keep the same conformance gitlink, and
pass independent repository and quality gates. This is local release evidence, not Rule 49
publication, real-team readiness, or authorization for any external operation.

## Accepted source and candidates

The common source is merge commit `e3fda929d84d62ea8b25324f92478285a64c2ac7`, accepted through
PR #29 after its public CI quality gate completed successfully.

| Role | Branch | Candidate commit | Root README SHA-256 | Candidate aggregate SHA-256 |
|---|---|---|---|---|
| Police | `codex/submission-police-candidate` | `c52f9078b682e8a8e8731045f61a89b9d9b5c3cc` | `6c1491f537f613f457befc7747ffdab0932f63f02d954c319fe9e6a00fde4bef` | `3e0eaaf155595fe67af26c362d20d0bf72c34fa601e5fbce56fde4f805dfc9d3` |
| Thief | `codex/submission-thief-candidate` | `fd87d62d3c05f18c5fedc68547228f6bb71e403d` | `483d676bd357425c698a1d7fb5b4cc16eda0cf40a7644d3967a922813b7ec59f` | `c441719d758f7570174c15369cee71d98916ee95f4b9d38a385091e0db3d469d` |

For both candidates, the accepted source is an ancestor and the candidate worktree is clean. The
existing shared history was not squashed, rebased, backdated, or reassigned. All 13 commits under
the pre-existing partner author identities remain present in each history.

## Exact content and count correction

The accepted source selects 329 regular files. Phase 4D14B originally reported 327 because its
Markdown and JSON evidence files were committed after the implementation-time measurement. Each
candidate has 330 regular files after retaining unchanged `.gitmodules`, plus exactly one gitlink
at `external/copthief-league-protocol`, for 331 tracked entries. The gitlink remains pinned to
`be96e57e357d59386c486a907e210e050d74c114`.

Only the root README differs between roles. The documented construction-only paths and synthetic
secret-shaped offline-ops tests are absent. Runtime source, ordinary tests, the partner-authored
guarded exporter, docs, GUI/Replay evidence, research, configuration, license and contribution
history remain present.

## Independent validation

Both read-only repository gates passed: exact ancestry, regular-file set, bytes, role README,
`.gitmodules`, gitlink pin, secret scan, pending counterpart URL and absent final tag.

| Check | Police | Thief |
|---|---:|---:|
| Collected tests | 343 | 343 |
| Passed | 338 | 338 |
| Expected skips | 5 | 5 |
| Failed / xfailed | 0 / 0 | 0 / 0 |
| Statement/branch coverage | 91.10% | 91.10% |
| Ruff | PASS | PASS |
| Hcommit vectors | 5/5 | 5/5 |
| Frozen manifest | 7/7 | 7/7 |
| Conformance kit | 125/125 | 125/125 |
| Candidate secret scan | PASS | PASS |

The five skips are explicit and expected in a publishable role checkout: one professor-builder
differential cannot run because professor-owned source is not redistributed, three parameterized
checks omit retained Phase 4B operational reports, and one check omits retained public-run logs.
The same differential already passed against the pinned local professor source before assembly;
the candidate source bytes are unchanged. The final Thief pytest was run alone after an earlier
parallel diagnostic produced a localhost-port warning; the accepted sequential run had no warning.

The quality-gate `match_artifact` item was not requested and is reported as optional/skipped. No
game or result path was supplied, so this is not a skipped code test and does not claim gameplay.

## Remaining hard stops

- Both role READMEs still contain `PENDING_HUMAN_APPROVAL`; no reciprocal URL is claimed.
- No final Police or Thief remote exists, no candidate branch was pushed, and no
  `v1.0-submission` tag exists.
- Actual identity, repository, hardware, endpoint and compatibility values still require human
  input and explicit bilateral approval.
- Gmail/OAuth, opponent contact, public transport, warm-up, counted play, reporting and Moodle
  submission remain separately unauthorized.
- The frozen Police champion, Phase 1 physics, Hcommit, scent, MCP, artifact and consensus
  semantics were not changed.

The smallest next step requires a human decision: approve both exact candidate commits and both
exact reciprocal repository URLs together. Only then may the two README links be substituted and
both gates rerun before any remote creation, publication or annotated tag.
