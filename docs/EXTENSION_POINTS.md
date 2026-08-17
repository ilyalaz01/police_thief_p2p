# Extension Points and Compatibility Policy

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Extensions are explicit typed substitutions for offline development. They are not permission to
alter frozen behavior, bypass role isolation, change wire/artifact bytes, or make a unilateral
interoperability decision.

## Supported extension points

| Interface | Lifecycle | Compatibility contract | Required tests |
|---|---|---|---|
| `DecisionBackend` | Construct one backend for a game/evaluation seed; call `choose_action` on each owned turn | **Observation-only** input; return a domain `Action` that is legal for that observation | happy/error policy tests, deterministic seed vector, observation-isolation and simulator legality |
| `ScentModel` | Select once from the agreed profile; call `initial` at setup and `advance` after the frozen cadence | A new scent profile changes negotiated semantics and requires **explicit bilateral agreement**; it cannot replace the frozen verified profile silently | unit vectors plus Hcommit/conformance/frozen gates and a controlled interoperability decision |
| `PolicyFactory` | Evaluation constructs a fresh backend from an integer seed for each game | Local simulator/evaluation only; registration does not make a policy the competitive champion | repeatability, both roles, invalid output and cross-play aggregation |
| Evaluation scenarios | Pass an explicit scenario/config set into local evaluation | Scenario data cannot weaken frozen action validation or claim public/league evidence | deterministic scenario and boundary-condition tests |
| `MatchProfile` documents | Load before peer side effects and compare byte identity during negotiation | Existing fields retain their pinned meaning; any new/different term is blocking until explicit bilateral agreement | strict schema rejection, byte/hash identity, peer refusal on mismatch |

`ScentTacticalPolice` remains the frozen Police champion. Adding another backend to a local policy
catalogue does not promote it and does not authorize a search/ML experiment.

## Plugins, hooks and middleware applicability

- **plugins:** a dynamic plugin loader is intentionally not applicable to the competitive runtime.
  Unreviewed runtime code would undermine frozen hashes, role isolation and bilateral profile
  identity. New offline policies are ordinary typed `DecisionBackend` implementations reviewed in
  source and exposed through `PoliciesSDK` only after tests.
- **hooks:** generic before/after gameplay hooks are intentionally absent. The bounded runtime
  lifecycle and its single-concern mixins are internal orchestration, not public mutation hooks.
  Diagnostics and the role-safe live publisher are observation sinks and cannot modify gameplay.
- **middleware:** `ApiGatekeeper` is the one applicable external-call middleware. It controls
  admission, FIFO queuing, rate limits, deadlines and sanitized monitoring. No extension may insert
  another retry, reorder, deadline-extension or wire-transformation layer.

These applicability decisions satisfy the guideline's architectural intent without building a
dangerous plugin system solely for appearance.

## Compatibility and review rules

1. Start with a failing contract test and record RED/GREEN commits.
2. Keep consumers on `PoliceThiefSDK`; do not add business logic to CLI or presentation code.
3. Preserve `Observation` as the only policy-visible game state.
4. Run the full suite, Ruff, Hcommit 5/5, frozen manifest 7/7 and conformance 125/125.
5. Treat profile, scent, turn, wire, commitment, artifact, tie or consensus differences as
   negotiated changes. Missing or differing peer approval blocks the operation.
6. A local simulator experiment is not an interoperability test; localhost interoperability is not
   public transport; a public self-test is not an external-team warm-up; an uncounted warm-up is not
   a counted league operation.

No extension API grants Gmail, tunnel, opponent-contact, real-team, reporting or counted-match
authorization.
