# Phase 4D7C - Runtime-Fed Role-Safe Live GUI

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN; `GUI-001` is DONE for the shared-code baseline**.

This phase does not claim final two-repository submission, another-team compatibility, public
transport readiness, a warm-up, a counted game, reporting, or authorization.

## Authority and privacy boundary

The implementation follows the official Chapter 7 split already established in Phase 4D7B:

- Live displays only one peer's own position, public blocked cells/barriers, legal scent-derived
  belief, step, and turn/terminal status;
- Replay displays both post-game tracks only after commitment and deterministic-physics
  verification succeeds;
- neither presentation path changes or redefines game rules, negotiated profile terms, Hcommit,
  scent semantics, the wire protocol, artifact bytes, or the frozen competitive policy.

The runtime constructs each Live update from its existing `_observation()` boundary and
`scent_weights(observation)`. The exact allow-list feed schema contains no objective opponent
coordinate, wire record, commitment, nonce material, URL, or peer identity. An extra root, update,
or view field fails closed before HTTP delivery.

## TDD and implementation evidence

RED commit `a15413c21d62599d38442113ceb969fe898c1f8a` added contracts for:

- atomic bounded role-safe feed publication and rejection of injected hidden truth;
- heatmap/status/history HTML with accessible controls;
- loopback-only HTTP serving plus no-store and browser security headers;
- runtime-to-feed integration for both roles and all required banners;
- CLI/SDK propagation of an optional `--live-view` path.

GREEN commit `917254e38721eed4de9b5b45496cdb6844b54ea9` added the feed, Live HTML,
loopback server, runtime presentation adapter, CLI command, and a mechanical `run_peer` extraction
that kept `runtime.py` below the permanent 150-line limit. The established runtime import path and
signature remain characterized; the exact contract payload is now 2,403 bytes with SHA-256
`1da7d86790a4fef7cbf07c8ccd545b3b1a07969bff9b59d3b654eed240dd562f` because the optional
`live_view_path` parameter is public.

## Visible correction evidence

The first full run after implementation collected 311 tests: 309 passed and two governance
contracts failed. One detected `runtime.py` at 164 counted lines; the other detected the expected
public-signature fingerprint change. The accepted correction extracted `runtime_entry.py` without
compressing code and pinned the new exact fingerprint. The next full run passed 311/311.

The first screenshot-retention run passed 25 checks and failed one because browser screenshot bytes
were JPEG while the filenames claimed PNG. The files and documentation were corrected to `.jpg`;
the rerun passed 26/26. No format check was weakened.

The composed gate in the long-lived development workspace passed pytest, Ruff, Hcommit, frozen,
and conformance but correctly failed its scan on eight pre-existing ignored Phase 4B public-
transport evidence files. A path/category-only inspection localized them to historical ignored
logs/reports with `tunnel_url`; no matched value was printed, copied, or committed. Those retained
local artifacts were not deleted or treated as publishable.

A clean tracked snapshot of the exact GREEN commit then passed the complete composed quality gate
with zero secret findings. In the current evidence worktree, the composed gate's pytest check and a
separate collection check together prove 312/312, while the screenshot/governance focused suite
passed 26/26. GitHub CI will repeat the full tracked gate after the evidence commit.

## Acceptance results

| Check | Result |
|---|---|
| Current full suite | PASS - 312/312; no failures |
| Full suite at GREEN source before evidence guard | PASS - 311/311; no failures |
| Branch coverage | PASS - 92.51%; threshold 85% |
| Current GUI/governance focused suite | PASS - 26/26 |
| Ruff | PASS - zero errors |
| Hcommit | PASS - 5/5 |
| Frozen manifest | PASS - 7/7 exact |
| Conformance kit | PASS - 125/125 |
| Python 150-line gate | PASS - changed-module maximum 125 counted lines |
| Clean tracked composed quality gate | PASS - exit 0; secret scan zero findings |

The clean composed gate's optional match-artifact check was correctly skipped because no match path
was requested. It did not skip pytest, Ruff, Hcommit, frozen, conformance, or secret scanning.

## Local runtime and visual acceptance

Exactly one synthetic localhost two-peer integration game was used to produce temporary Live feeds
and completed schema 1.1 artifacts. Both roles completed a deterministic capture flow. Police and
Thief feeds each contained `YOUR TURN`, `LOCKED`, and `GAME OVER`; all updates retained one role and
passed strict reloading. The temporary full artifacts were removed after the nonce-free Replay
model and screenshots were produced.

The loopback Live server and a temporary loopback static Replay server were inspected in the
in-app browser. DOM review confirmed:

- Live status `YOUR TURN`, Police local marker, heatmap, observable-state text, and history controls;
- Replay status `Verified OK`, both post-game agents, result, and playback controls.

Reviewed public-safe evidence:

- `docs/images/live-gui-local-truth.jpg` - 1,265 x 712, 44,664 bytes;
- `docs/images/replay-verified-ok.jpg` - 1,265 x 712, 44,307 bytes.

The images use synthetic group labels and contain no credential, live public endpoint, nonce,
private correspondence, or real opponent identity. They prove GUI presentation and local replay
verification only; they do not prove another-team interoperability or counted play.

## Frozen and operational boundary

All seven frozen hashes remained exact. No rule, score, strategy, `ScentTacticalPolice`, Phase 1
physics, scent, MatchProfile/config bytes, Hcommit, wire field, retry/deadline/duplicate behavior,
artifact schema/bytes/hash, consensus scope, Rule 47 decision, dependency, or conformance-kit source
changed.

No Gmail, opponent contact, public request, tunnel, real-team warm-up, league reporting, counted
game, submission tag, or new AI/ML/search work occurred.

The smallest safe offline continuation is the combined package/building-block/extension audit
(`PKG-001`, `DOCS-002`, `EXT-001`) while the independent partner workstream completes cost and ISO
evidence. External operations and `SUB-001` remain separately gated.
