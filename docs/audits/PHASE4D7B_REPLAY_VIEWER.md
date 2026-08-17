# Phase 4D7B - Role-Safe Presentation and Replay Viewer

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN for the Replay Viewer slice; `GUI-001` remains IN_PROGRESS**.

This phase does not claim a completed Live GUI, accepted screenshots, another-team readiness,
counted readiness, or final-submission readiness.

## Authority and design boundary

The implementation was derived from official Chapter 7 and the final checklist, then checked
against the project authority baseline, interoperability decisions, current PRD/PLAN/TODO, and the
accepted runtime/audit architecture. Chapter 7 requires two deliberately different views:

- live presentation is local truth only: own position, public obstacles/barriers, and the peer's
  opponent-belief/heatmap; objective opponent position is forbidden;
- post-game Replay may show both tracks only after the revealed log has been cryptographically and
  physically verified; one failure invalidates the complete replay as `TAMPERED`.

`RoleLocalView` therefore has no opponent-position field. `ReplayView` is a separate post-game
model, and its serialized form excludes source records and nonces.

## TDD evidence

RED commit `4780b4bd83b33d1205d4a09286c6f81953d81e99` added role-boundary, tamper,
physics, standalone-HTML, and CLI contracts. Collection failed only because the new presentation
package and viewer command did not yet exist.

GREEN commit `a8cb8b730ec4c6d004ddd91f70d1bae021dfa19f` added:

- immutable live and replay presentation models;
- accepted commit and deterministic-physics verification before rendering;
- sanitized replay-frame construction for flat schema 1.1 and retained nested local profiles;
- a responsive standalone HTML app with both post-game agents, obstacles/barriers, accessible
  Previous/Next controls, and `Verified OK`/`TAMPERED` status;
- an offline fail-closed viewer CLI and user documentation.

The HTML contains no CDN, analytics, remote asset, input record, or nonce. A tampered replay is
still rendered for evidence but the command exits `2`.

## Acceptance results

| Check | Result |
|---|---|
| Focused presentation tests | PASS - 7/7 |
| Full suite | PASS - 305/305, no failures |
| Branch coverage | PASS - 93.44%, threshold 85% |
| Ruff | PASS - zero errors |
| Governance/link tests after docs | PASS - 25/25 |
| Hcommit | PASS - accepted golden-vector test (5/5 vectors) |
| Frozen manifest | PASS - 7/7 exact |
| Conformance kit | PASS - 125/125 |
| Python 150-line gate | PASS - new maximum 95 counted lines |
| Clean-checkout composed quality gate | PASS - exit 0; secret scan zero findings |

The composed gate passed at the exact GREEN commit in a detached tracked checkout. Its optional
match-artifact check was correctly skipped because no match path was requested; pytest, Ruff,
Hcommit, frozen manifest, conformance, and secret scan all passed.

An offline smoke run consumed one existing ignored completed-game Phase 4A.5 artifact pair and
produced `Verified OK` without exposing a nonce. This proves compatibility with a retained real
project log shape; it is not a new game, public transport test, warm-up, or counted operation.

## Visual evidence limitation

The generated HTML was structurally and interactively covered by tests. The in-app browser refused
the local `file://` page under its browser security policy, so this phase does **not** claim visual
screenshot acceptance. No policy bypass or alternate external upload was attempted. Reviewed
Live/Replay screenshots remain explicit `GUI-001` acceptance work.

## Frozen and operational boundary

No game rule, scoring, strategy, `ScentTacticalPolice`, observation type, scent, Hcommit,
MatchProfile, wire, retry/deadline/duplicate behavior, runtime turn flow, artifact schema/bytes/hash,
consensus scope, Rule 47, frozen file, or dependency declaration changed. The clean-checkout
validation initialized the already-declared conformance-kit submodule; it did not modify it.

No peer, gameplay, public tunnel, public opponent endpoint, Gmail, external-team contact, league
reporting, warm-up, counted operation, submission repository, or tag was started.

## Remaining `GUI-001` blockers

- bind role-legal view snapshots to each independent peer without changing protocol semantics;
- display the live belief heatmap plus exact `YOUR TURN` and `LOCKED` states;
- test that runtime data cannot inject objective opponent truth or nonce-bearing records;
- retain reviewed public-safe Live GUI and Replay `Verified OK` screenshots.

The next smallest justified slice is the local runtime-to-view snapshot adapter and live app. It
requires no opponent, public transport, Gmail, counted play, or strategy change.

