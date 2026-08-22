# Counted Series Runbook

> A counted series is **six sub-games** against one opponent, played once per opponent, and
> reported by e-mail. Everything below is the operator procedure for one such series.
> Nothing here authorizes starting one: that is a separate explicit decision.

## What the official book fixes

| Item | Value | Status | Source |
|---|---|---|---|
| Sub-games in a series against one opponent | 6 | fixed | Table 18, printed p. 138 |
| Minimum counted matches to pass | 2, against different opponents | fixed | Table 18 |
| Maximum matches per team | 10 | fixed | Table 18 |
| Reward for beating a new opponent | 10 | fixed | Table 18 |
| Aggregate tie across the series | 2 points to each team | fixed | tie rule, printed p. 70 |
| Response timeout / watchdog | 30 s / 60 s | negotiable | Table 19, printed p. 138 |
| One counted match per opponent; uncounted warm-ups allowed | — | rule 52 | Appendix E |
| Report is JSON, attached, one per team, agreed with the opponent | — | rules 32–36, 51 | Appendix E |
| Agent reporting address | `rmisegal+uoh26finalgame@gmail.com` | — | Table 20, printed p. 141 |

The declaration, config and log artifacts are published in the role repositories; only the final
result JSON is mailed.

## Before the first sub-game

Both teams must have exchanged, in writing:

- complete declarations — group id, name, members, both repository URLs, both MCP URLs, model and
  hardware — each side loads the other's file with `--peer-declaration`;
- the byte-identical Appendix-B `config/game.json` and its SHA-256;
- the role schedule. It is derived, not negotiated: the alphabetically first group id plays police
  in the odd sub-games. For `il-nv-ai` against `vm__fabi` that is games 1, 3 and 5;
- the three graded league fields and each team's declared counted-game count;
- confirmation that both sides treat the series as counted.

## Playing the six sub-games

`tmp/publish/go_series.sh` drives the whole series from one terminal: it raises a single tunnel
that serves all six sub-games, preflights both endpoints, then walks sub-game by sub-game. Before
each one it waits for the operator, because both peers must start inside our 65-second
negotiation window. Each sub-game runs from the role repository checkout that matches that game's
role, so the commit recorded per sub-game is the exact published commit that played it (rule 53).

A sub-game that fails transport is a deterministic technical failure. It is never resumed and
never relabelled.

## Assembling the report

```bash
uv run python -m police_thief_lab.series_cli \
  --our-declaration <ours.json> --peer-declaration <theirs.json> \
  --appendix-b <agreed game.json> \
  --profile interop/fixtures/phase4a5_reference_profile.json \
  --result out/g01/peer-result.json ... --result out/g06/peer-result.json \
  --out out/bundle
```

The assembler refuses any sub-game whose audit or replay did not verify, whose roles differ from
the sealed schedule, or whose score differs from the official table. It prints the aggregate, the
six per-sub-game consensus hashes and the final series consensus hash. Exchange those hashes with
the opponent: rule 35 voids the match and scores both teams zero if the two reports disagree.

## Mailing the result

Draft first, read it in Gmail, then send:

```bash
uv run python -m police_thief_lab.report_cli \
  --result out/bundle/artifacts/result_<game_id>.json \
  --reporting-config <your reporting.json> \
  --credentials <your gmail_credentials.json> --draft
```

Replace `--draft` with `--send --audit <path>` once the draft looks right. Both teams send their
own report separately; a missing report from either side voids the game.
