# PRD: Game Core and Observability

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Background and contract

The game is an alternating, partially observable dynamical system. The environment may know full
truth; a decision backend receives only its role's observation/history. Inputs are `GameConfig`,
`WorldState`, role, and typed `Action`; outputs are validated state transitions, role-local
`Observation`, terminal reason, and `Score`.

Requirements: orthogonal move/STAY, bounds, persistent barriers, both placement modes, Rules 46
and 47, survival threshold, deterministic replay, explicit terminal precedence, and no opponent
coordinate in strategy inputs. Constraints and frozen boundary are the authoritative rules,
seven frozen files, alternating Thief-first semantics, scoring, scent interface, and frozen
`ScentTacticalPolice`; link rather than restate details in
[the baseline](../RULES_AND_INTEROP_BASELINE.md).

## Approach, alternatives, and evidence

The selected current approach is immutable typed models, pure rule helpers, `Simulator`, and
`ReferenceV3Alternating`, with a `DecisionBackend` protocol. Evidence:
`tests/unit/test_game/test_rules.py`, `tests/unit/test_game/test_models.py`,
`tests/unit/test_game/test_observation.py`, `tests/unit/test_game/test_turns_and_replay.py`, and
frozen-manifest tests.
Rejected for the current profile: a simultaneous shared-world resolver, because it conflicts with
the executable reference cadence; a full-truth policy interface, because it violates isolation.

Unresolved: own-cell barrier behavior is negotiated; simultaneous opponents require a separate
agreement; documentation/refactoring coverage remains planned.

Metrics: deterministic equality for repeated inputs; zero illegal accepted actions; zero hidden
coordinate exposure; exact boundary/terminal tests; frozen hashes 7/7. Test scenarios include
each direction/STAY, edge/corner, existing/outside barrier, Rule 46/47, threshold timing,
observation leakage, replay, and both placement modes.

Definition of Done for future changes: authority reviewed, RED/GREEN evidence recorded, all core
and frozen tests green, no semantic/hash drift, public interfaces documented, and any negotiation
impact recorded in an ADR and profile review.
