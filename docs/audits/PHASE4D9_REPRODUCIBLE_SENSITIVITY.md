# Phase 4D9 — Reproducible Policy Sensitivity Publication

> Retrospective project baseline created after the validated prototype.
> The Phase 4D9 design itself was committed before its first simulator run.

Status: **GREEN**. `RES-001` and `VIS-001` are DONE on the shared offline baseline. `COST-001`
remains IN_PROGRESS because CPU, RAM, and latency are not measured by this study.

## Authority and operation class

This phase implements Software Project Guidelines sections 8 and 16.5 under the authority boundary
in `RULES_AND_INTEROP_BASELINE.md`. Every experiment is a
`LOCAL_SIMULATOR_EXPERIMENT`. It is not a local interoperability test, public transport test,
uncounted warm-up, or counted league operation.

The frozen `ScentTacticalPolice` remains the champion. No rule, physics, scent, Hcommit, MCP, wire,
profile, artifact, tie, consensus, retry, deadline, policy implementation, dependency, or lockfile
changed.

## Preregistration and TDD evidence

RED commit `155666a` created five publication contracts. The first run produced **1 passed,
4 failed** because the generator, results, figures, and notebook did not exist.

Before any simulator game, commit `74ea8f9` retained the bounded design in
`data/research/sensitivity_design.v1.json`. It also corrected an old broad `research/` ignore
pattern that had initially hidden the nested design path. This correction preceded the first game
and is retained transparently.

GREEN commit `caf13d3` added the public-SDK generator and curated publication. The five focused
contracts passed, including a complete byte-identical regeneration.

Review then found that the notebook-equivalent did not embed its already generated figures or
explicitly assess the three preregistered hypotheses. RED commit `476cc6d` reproduced that missing
contract as **1 failed**. GREEN commit `2d817b7` embedded both figures with detailed captions and
added bounded descriptive hypothesis assessment; all five contracts passed again.

The first composed full gate exposed one living-document regression: the accepted literal
`GUI-001: DONE` had been reformatted while reconciling Phase 4D9. It also reported eight scanner
findings that were all in pre-existing ignored local Phase 4B evidence or an ignored historical
workspace copy, not in the tracked publication. The literal was restored and its targeted
governance test passed. The ignored files were preserved rather than deleted or published.

## Controlled design

- Method: paired one-factor-at-a-time screening; no Sobol/global-sensitivity claim.
- Parameters: board size 7/9/11 and survival threshold 35/50/70.
- Baseline: board size 7 and survival threshold 35.
- Existing Police policies: `ScentTacticalPolice` and `ScentGreedyPolice`.
- Existing Thief policies: `BarrierAwareThief` and `ScentEvasionThief`.
- Pairing: 40 deterministic seeds × three scalable start scenarios.
- Settings: five unique OAT configurations.
- Published games: 2,400; illegal actions: 0.

Only outcome/score/action-count fields are retained. The dataset contains no objective opponent
position, `WorldState`, nonce, endpoint, token, personal path, correspondence, or professor-owned
body.

## Results and bounded interpretation

The publication contains 2,400 raw rows, 20 aggregate rows, and 16 elementary-effect rows.
Every aggregate has 120 games and a Wilson 95% score interval.

- All 8/8 measured board-size effects are negative in this grid.
- Four of eight survival-threshold effects are positive; four are zero at the observed ceiling.
- Tactical leads in three policy/setting cells, Greedy leads in three, and four tie.
- The largest observed baseline-relative capture shift is −23.3 percentage points for
  `ScentTacticalPolice` against `ScentEvasionThief` at board size 11.

These are descriptive results for the declared local grid. They do not prove causality, interaction
effects, unseen-terrain performance, another-team performance, or a better competitive policy.

## Public artifacts and reproduction

- design: `data/research/sensitivity_design.v1.json`;
- manifest: `results/research/phase4d9_manifest.json`;
- raw rows: `results/research/phase4d9_sensitivity.json`;
- aggregate CSV: `results/research/phase4d9_summary.csv`;
- figures: `assets/research/capture_by_board_size.svg` and
  `assets/research/capture_by_survival_threshold.svg`;
- analysis: `notebooks/POLICY_SENSITIVITY_ANALYSIS.md`.

Reproduction command:

```bash
uv run python -m tools.research.cli
```

The command uses the public `PoliceThiefSDK` only, starts no peer or network process, and rewrites
only the curated publication paths declared in the generator.

## Validation

| Check | Result |
|---|---|
| Phase 4D9 focused contracts | PASS — 5/5 |
| Byte-identical full regeneration | PASS |
| Published record/summary/effect counts | PASS — 2,400 / 20 / 16 |
| Full pytest after document correction | PASS — 334/334 |
| Branch coverage | PASS — 92.59% (threshold 85%) |
| Ruff `src tests` in composed gate | PASS — zero errors |
| Ruff `tools/research tests/integration/test_research` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Frozen production manifest | PASS — 7/7 exact |
| MIT conformance kit | PASS — 125/125 |
| New research Python files over 150 counted lines | PASS — 0; maximum 136 |
| Figure size/accessibility metadata | PASS — two 1200×700 SVGs with title/description |
| Retained live sensitive values | PASS — none |
| Staged public snapshot secret scan | PASS — 272 files, zero findings |

## Proven versus not proven

Proven: bounded deterministic OAT execution, public-safe row projection, raw-to-summary provenance,
stable serialization/hashes, exact regeneration, Wilson intervals, elementary effects, accessible
figures, explicit hypotheses/limitations, and unchanged frozen hashes.

Not proven: global variance-based sensitivity, factor interactions, causal effects, statistical
power beyond this grid, timing/capacity, real-team compatibility, public transport readiness,
uncounted warm-up readiness, counted-game readiness, Gmail reporting, or final submission.

## Operations and next step

No peer, tunnel, public request, Gmail action, external-team contact, warm-up, league report,
counted game, new AI/ML/search, or submission repository/tag operation occurred. Local simulator
execution occurred only for the declared study and deterministic regeneration tests.

The smallest justified next offline milestone is `COST-001`: measure bounded local CPU time, peak
RAM, and local latency/capacity without contacting a peer or inventing vendor prices.
