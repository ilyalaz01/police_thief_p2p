# Phase 4D13A — Official Series Entry Contract

Status: **GREEN locally; PR CI required before merge**.

Classification: `OFFLINE_LGE_ENTRY_CONTRACT`. `LGE-001` remains **IN_PROGRESS**. This phase proves
safe preparation and refusal behavior; it does not prove a completed six-sub-game runtime series,
bilateral approval, real-team readiness, reporting, or counted play.

## Authority and decision boundary

The implementation follows `RULES_AND_INTEROP_BASELINE.md`, the official PDF Appendix B and
Appendix F, `docs/INTEROP_DECISIONS.md`, the pinned professor behavior, and the pinned conformance
kit in that order. ADR-007 records the architecture without selecting an unresolved rule:

- the full Appendix-B schema-1.2 object is separate from both the flat fourteen professor terms
  and the extended runtime `MatchProfile`;
- the single-game professor/runtime path remains unchanged and still declares `num_games=1`;
- the outer series uses a derived copy of the flat terms with `num_games=6` for game UID;
- compact canonical Appendix-B bytes and sorted-first Police-on-odd scheduling are named local
  profiles that require matching peer values and explicit bilateral approval;
- a tied series remains blocked because `series_add`, `series_replace`, and `per_subgame` are live
  interpretations. No implicit tie award is applied.

## Proven implementation

- `LeagueSDK` is the seventh stateless service on the single public SDK facade.
- The exact Appendix-B field inventory, fixed constants, positive negotiated values, and
  Gatekeeper minima fail closed. Unknown fields, wrong fixed values, below-minimum values,
  non-finite numbers, mismatched serialization profiles/hashes, and missing explicit approval are
  rejected.
- Candidate bytes are immutable. A public worked vector reproduces 911 UTF-8 bytes and SHA-256
  `358f29da2ce5777b0697a8f4201b00404a56732e5bb57e15b806122c92c9f734`; it is explicitly labeled
  `LOCAL_PROPOSAL_PENDING_EXPLICIT_BILATERAL_AGREEMENT`.
- Exactly six sealed slots alternate roles. An injected offline runner is invoked once per slot
  and any mismatched sub-game number or role mapping is rejected.
- Capture/survival rows must reproduce official 20/5 and 5/10 role scores. Aggregate totals,
  sub-game wins, row ties, winner, series-tie state, and exact six-game token totals are
  deterministic. Equal totals stay blocked pending an explicit tie policy.
- Final declaration inputs validate exact eight-character no-space group IDs, non-empty members,
  HTTPS GitHub role repositories, credential-free HTTPS `/mcp` URLs, model, hardware, and an exact
  opaque commit from both teams for every sub-game. Commit values are preserved rather than
  guessed or forced into a locally invented hash format.

## TDD and regression history

- RED `4601857`: three missing-package collection errors proved the new contract did not exist.
- GREEN `46cba50`: implemented the isolated league package and SDK service.
- ADR/docs `347ebbd`: recorded the three config domains and remaining operational blockers.
- Regression `f48b1e8`: kept the Phase 4D10 source SHA and measured samples immutable while moving
  the current-tree equality check to the new-measurement execution gate. Historical evidence can
  be read, but it cannot be rerun against changed code under an old preregistration.
- Vector `1f53568`: pinned the reproducible local Appendix-B candidate.

## Explicitly not proven

- No adapter has yet run the accepted single-game peer six times or produced six verified logs,
  six audits/replays, and one final series result.
- No real group identity, repository, commit, hardware, endpoint, or opponent value was supplied.
- No peer approved the Appendix-B bytes, starting-role profile, tie policy, Rule 47, artifact
  consensus scope, or any other compatibility worksheet field.
- No full schema-1.2 file was substituted into the pinned schema-1.1 professor builders.
- No public transport, tunnel, peer process, gameplay, external-team contact, Gmail/OAuth action,
  league reporting, counted match, repository publication, or tag occurred.

## Validation

- Final full suite: **396/396 passed**, no skips or xfails.
- Combined statement/branch coverage: **91.99%**; required threshold 85%.
- Ruff over `src`, `tests`, and `tools`: zero errors.
- Pinned professor four-builder differential: passed without skip.
- Hcommit vectors: 5/5; authoritative frozen manifest: 7/7 exact.
- Pinned conformance kit: 125/125.
- Every project-authored `src`/`tests` Python file remains at or below 150 counted lines; the
  largest new production file is 148 lines and the largest new test file is 131 lines.
- Exact Git-tracked public snapshot secret scan: pass, zero findings, with only the scanner's own
  synthetic `tests/offline_ops` fixtures excluded under the existing documented policy.
- The worktree was clean before evidence retention; partner-owned submission-export paths were
  not changed.

The adjacent JSON retains the same machine-readable decision. The smallest justified next step is
an offline/localhost `LGE-001` adapter that invokes the unchanged single-game boundary for all six
sealed slots and proves logs, audits/replays, declaration/config placement, aggregate result, and
failure recovery. It must stop before public transport, real identity entry, bilateral approval,
Gmail, external contact, reporting, or counted play.
