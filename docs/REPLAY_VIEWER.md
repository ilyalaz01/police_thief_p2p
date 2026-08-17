# Offline Replay Viewer

## Purpose and authority

The Replay Viewer implements the retrospective half of the official Chapter 7 observability
requirement. It answers whether a completed revealed log happened as claimed. It is not a live
bird's-eye view, does not authorize gameplay, and does not modify the frozen commitment dialect or
game physics.

The live and replay boundaries are deliberately different:

- `RoleLocalView` contains only the peer's own position, public obstacles/barriers, legal belief
  values, step, and turn banner. It has no opponent-position field.
- `ReplayView` is created only from a completed revealed log. It may show both tracks after Python
  has recomputed every commitment and deterministic transition.

## Build a viewer

Use the schema 1.1 log and matching config from the same completed sub-game:

```bash
uv run python -m police_thief_lab.viewer_cli replay \
  --log artifacts/log_<game-id>_g01.json \
  --config artifacts/config_<game-id>_g01.json \
  --output artifacts/replay_<game-id>_g01.html
```

Open the resulting HTML file with a normal browser. The app is standalone: it has no CDN, remote
font, analytics, network request, or runtime dependency. `Previous step` and `Next step` move across
the post-game board states. Police, Thief, static blocked cells, and placed barriers are visibly
distinct.

## Verification and exit codes

Before rendering, the command calls the accepted commitment verifier and deterministic replay
physics. The output model intentionally excludes input records and nonces.

| Exit | Meaning | HTML banner |
|---:|---|---|
| `0` | Every commitment and replay transition verified | `Verified OK` |
| `2` | At least one commitment, structure, or physics check failed | `TAMPERED` |

`TAMPERED` invalidates the whole replay. The viewer does not offer a repair, override, warning-only
mode, or implicit acceptance path.

## Supported inputs and limitations

The viewer accepts the current flat schema 1.1 config fields (`board_size`, `cop_start`,
`thief_start`) and the older local runtime's nested `board_config` for retained regression evidence.
It consumes `records` from the log root and uses the summary result only as display metadata.

Phase 4D7B does not complete `GUI-001`. Still required:

- connect the role-local snapshot model to each independent peer runtime;
- render the live belief/scent heatmap and exact `YOUR TURN`/`LOCKED` status;
- prove that no live opponent coordinate can cross that boundary;
- capture reviewed public-safe Live GUI and Replay `Verified OK` screenshots.

No public transport, external opponent, Gmail, league reporting, or counted operation is needed to
test this viewer.
