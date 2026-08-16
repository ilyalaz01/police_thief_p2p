# Phase 4D1B — REF-001 Belief Helper Extraction

Result: **GREEN characterization-driven refactor**. REF-001 remains **IN_PROGRESS** because three
production files still exceed 150 counted lines. No subsequent production slice is selected.

## Commits and mechanical boundary

- `0177c96` — `test: characterize belief policy contract`
- `273a723` — `refactor: extract private belief calculation helpers`
- `docs: record phase4d1b belief split evidence` — this report commit

`_open_cells`, `_field_error`, and `_entropy` moved without body changes from
`src/police_thief_lab/policies/belief.py` to the private
`src/police_thief_lab/policies/belief_support.py`. They are imported back under the same names.
`BeliefDiagnostics`, `BeliefEstimator`, `CurrentScentBelief`, `TrajectoryBeamBelief`,
`scent_weights`, and `_Trajectory` remain in `belief.py`.

Counted lines changed from `belief.py` 154 to `belief.py` 133 plus `belief_support.py` 26. Counting
includes each nonblank line whose first non-whitespace character is not `#`; neither module was
compressed.

## Pre-refactor contract and vectors

The public belief names were `BeliefDiagnostics`, `BeliefEstimator`, `CurrentScentBelief`,
`TrajectoryBeamBelief`, and `scent_weights`. The module also exposed its imported `Observation`,
`Position`, `Protocol`, `ReferenceSubtractiveChebyshevV1`, `blocked`, `dataclass`, `math`,
`neighbours`, and `time` names; their availability was recorded before movement. Package
`policies.__all__` remained byte-for-byte/order identical with 21 entries.

| Contract | Before and after |
|---|---|
| `CurrentScentBelief` constructor | `() -> 'None'` |
| `TrajectoryBeamBelief` constructor | `(history_k: 'int' = 6, beam_width: 'int' = 128) -> 'None'` |
| `scent_weights` | `(observation: 'Observation') -> 'dict[Position, float]'` |
| invalid `history_k`/`beam_width` | `history_k and beam_width must be positive` |

Deterministic vectors use sorted position/value lists and trajectory position lists, encoded as
compact sorted-key JSON and SHA-256 hashed. Diagnostics include update count, hypothesis count,
and entropy; measured elapsed time is deliberately excluded.

| Vector | SHA-256 before and after |
|---|---|
| Current positive scent | `815223cd2f4dd8c6d2e51fac2ce1879f04ec05733af1f2d4642840dcfde422aa` |
| Current empty scent | `4a00b8abf1902a917730683133aed588d4b976dcedeed30d6677a10ace584100` |
| Trajectory initialization | `2fe7e6590d5e2d9bfdefd564b01fd9d03ef502eba68329d623d785b62974c5be` |
| Trajectory second update | `0cd0fc67b1b1b49c458da3779f9e5ebfa1ecd05a0ad959b44a53f09c2626463b` |

The characterization also proves normalized distributions, defensive distribution copies,
immutable trajectory exposure, `scent_weights` compatibility, positive/empty scent behavior,
four invalid-constructor cases, truth-free diagnostics, and no hidden-truth input or output.

## Acceptance gates

| Gate | Result |
|---|---|
| Full suite | PASS — 144/144, no skip/xfail |
| Configured branch coverage | PASS — 91.06% (≥90.80%) |
| Characterization plus Phase 3A/3B | PASS — 20/20 |
| Existing Phase 3A/3B | PASS — 12/12 |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance | PASS — 125/125 |
| Frozen manifest | PASS — 7/7 |
| Production module ceiling | PASS — 133 and 26 |
| Forbidden/frozen path diff | PASS — empty |

The repository-wide over-150 roster is now exactly:

- `src/police_thief_lab/interop/runtime.py` — 565
- `src/police_thief_lab/policies/phase3b.py` — 303
- `src/police_thief_lab/interop/artifacts.py` — 168

No mathematics, iteration ordering, floating-point operation, action, heuristic, constant,
diagnostic meaning, seeded behavior, rule, observation, scent, evaluation, profile, MCP,
serialization, artifact, transport, interoperability, dependency, experiment result, or frozen
file changed. No network, external contact, gameplay, merge, push, or tag occurred.
