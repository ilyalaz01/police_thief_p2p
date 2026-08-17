# PRD: Policy Evaluation

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Background and I/O

Policies approximate decisions under partial observability; seeded cross-play estimates outcome
and timing distributions without granting oracle state. Inputs are `Observation`, seed/history,
scenario, and policy configuration. Outputs are legal `Action`s, per-game `GameResult`, aggregate
`BatchResult`, matrices, diagnostics, and report data.

Requirements: backend replaceability, legal role-scoped input, deterministic seeds, paired
comparisons, failure visibility, timing, and reproducible aggregation. Constraints: no strategy
change in this phase; the Police champion is frozen; research reports are evidence, not rules.

## Current selection and evidence

Current modules provide baseline/tactical/partition/belief/search policies and an evaluation
runner/matrix. This is selected as the implemented laboratory, not as a claim that every policy
is optimal. Evidence: `tests/integration/test_evaluation/test_evaluation.py`,
`tests/unit/test_policies/test_phase2_5.py`, `tests/unit/test_policies/test_phase3a.py`,
`tests/unit/test_policies/test_phase3b.py`, experiment scripts, phase reports, and the Phase 4D9
preregistered public-safe sensitivity publication.

Alternatives include exhaustive belief search, neural policies, and online learning; none is
selected. The 2,400-game paired OAT publication compares existing policies and parameters without
training or changing one; it is screening, not Sobol/global sensitivity. Formal performance
budgets remain under `COST-001`. The characterized `belief.py` and `phase3b.py` structural splits
are complete under REF-001.

Metrics: identical seeded results; 100% returned actions legal; no hidden-state path; paired win,
capture, survival, score, turns, and latency summaries. Tests cover seed repetition, ablations,
strong opponents, budgeted search, oracle exclusion, and legality.

Definition of Done: predeclared hypothesis/config/seeds, TDD evidence, raw-to-summary provenance,
sensitivity results, review for leakage, full quality gates, and no frozen-policy hash change.
Timing/capacity measurement remains explicitly separate under `COST-001`. Frozen boundary: rules,
observations, champion, profiles, and interoperability semantics.
