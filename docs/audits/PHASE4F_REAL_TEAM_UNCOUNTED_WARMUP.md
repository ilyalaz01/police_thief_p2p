# Phase 4F — Real-Team Uncounted Warm-up

Classification: **UNCOUNTED real-team warm-up**, 2026-08-21, against group `vm__fabi`.
Not a league result. No lecturer report, no Gmail, no counted claim.

## What ran

Three public games over two HTTPS tunnels, each an independent single sub-game under
`game_id il-nv-ai-vs-vm__fabi`, `game_uid 00aec465-1e83-befa-15ed-a5d427995ffc`, with the agreed
14-term configuration hash `b97de3f6…c340c0` written into every schema-1.1 config artifact.

| Run | Our role | Outcome | Score | Records | Audit | Replay | Consensus hash |
|---|---|---|---|---:|---|---|---|
| game 1, run 1 | thief | barrier_on_thief, step 15 | 5–20 | 32 | verified | verified | `def4df4d…a893d8` |
| game 1, run 2 | thief | barrier_on_thief, step 15 | 5–20 | 32 | verified | verified | `def4df4d…a893d8` |
| game 2 | police | police_capture, step 10 | 20–5 | 20 | verified | verified | `1be7dd12…8dde00` |

Run 2 repeated run 1 against a different opponent commit and reproduced the identical outcome and
consensus hash. Every consensus value was recomputed independently from the result artifact rather
than read back from it.

The real-team Git gate accepted the opponent's exact commit from `identity.github_commit` on every
run: `44225aec…`, `c69a134b…`, `0e463ce5…`. Ours were `f279dc2c…` (thief) and `42c5367d…` (police),
each from the checkout that actually executed.

## What it proves

Public FastMCP traversal, negotiation on the signed terms, Rule 46 in both directions, commit and
reveal, mutual audit, deterministic replay and schema-1.1 artifacts all work against another
team's independent implementation — not only against our own processes.

## What it does not prove

- No opponent consensus hash has been compared against ours yet.
- No bilateral counter-signed worksheet exists; the repository template stays blank and blocked.
- Each run was one sub-game. No public six-sub-game series has been run with a real team.
- Nothing here is counted, reported, or mailed.

## Defects it exposed

- Our thief final omitted the kit-required `claim` cell; fixed, see `docs/INTEROP_DECISIONS.md`.
- Our declaration carried empty members, `local-unpublished` repositories and null hardware, and
  the hardcoded localhost hint; `--declaration` and `--hint` now supply real values.
- Our thief ran the integration default policy; see `PHASE4E_THIEF_POLICY_SELECTION.md`.
- Our `submit_audit` was unacknowledged inside the audit timeout in both game-1 runs and
  acknowledged in game 2 after the opponent fixed their handler.
