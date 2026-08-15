# RULES_AND_INTEROP_BASELINE.md

> Status: **implementation baseline for Phase 1**
>
> Project: Police–Thief P2P, book/code v3.0.0
> Verified reference repository commit: `960499fd5e8777b4929625f5d8fdcf2ab4677b54`
> Verified conformance-kit commit: `be96e57e357d59386c486a907e210e050d74c114`
>
> This document is not a replacement for the official PDF. It is a normalized engineering baseline produced from the official PDF, professor reference implementation, inter-team conformance kit, WhatsApp league discussion, and completed interoperability verification.

---

## 1. Source authority

When sources disagree, use this order:

1. **Official PDF v3.0.0**
   - Appendix E = mandatory rules.
   - Appendix F = authoritative quantitative parameters/statuses.
   - Appendix E/F override illustrative examples elsewhere in the book.
2. **Professor reference implementation**
   - Use it for executable behavior when the mandatory PDF does not fully define byte-level or operational behavior.
   - It does not override an explicit mandatory Appendix E/F rule.
3. **Inter-team conformance kit**
   - Use it for byte-level interoperability and compatibility testing.
   - It is not a competing specification.
4. **WhatsApp league agreements**
   - Use them for actual inter-team conventions/negotiation.
   - A proposal in chat is not automatically mandatory.
5. **Software Project Guidelines**
   - Architectural/style guidance from the professor, not automatically a current-project rule.
6. **Research reports**
   - Ideas and candidate techniques, never project rules.

**NotebookLM is not an independent authority.** Its answers are summaries of whichever sources were loaded into that notebook. Verify important claims against PDF/code/tests.

---

## 2. Core game model

### 2.1 Process model

- Police and Thief run as **two separate processes**.
- No shared memory, shared variables, or direct access to the opponent's private state.
- Each peer has its own local truth.
- Communication is peer-to-peer through FastMCP.
- The live GUI must not reveal an objective full hidden board.

### 2.2 Partial observability

The true world contains both agents' actual positions, barriers, counters, and other physical state.

A policy must **not** receive the opponent's hidden true coordinate.

The agent reasons from its own local state, opponent scent, free-language hints/messages, public barriers/declarations, history, and derived belief.

Keep these concepts separate:

```text
true state     = hidden physical reality used by the environment
observation    = information legally visible to one role
history        = previous observations/actions/messages
belief         = probability distribution / estimate over hidden opponent state
```

The simulator may internally hold complete truth, but the strategy/policy interface must expose only role-legal observations.

---

## 3. Movement and turn baseline

### 3.1 Legal movement

Mandatory movement set:

```text
N
S
E
W
STAY
```

- No diagonal movement.
- Movement must remain in bounds.
- Movement into blocked cells is illegal.
- Illegal actions must never silently corrupt state.

### 3.2 Turn cadence

**Implementation baseline:** `REFERENCE_V3_ALTERNATING`

```text
Thief acts first
→ sends TurnMessage
→ Police receives it
→ Police acts
→ sends TurnMessage
→ Thief receives it
→ Thief acts
→ ...
```

This is:
- the behavior of the tested professor reference implementation;
- consistent with the professor NotebookLM description;
- consistent with the league team's game-day template saying `Thief moves first`;
- consistent with teams using the 4-tool reference-compatible wire.

Do **not** implement a simultaneous joint-action resolver in Phase 1.

Status: `VERIFIED_REFERENCE_INTEROP / LEAGUE_BASELINE`

This is not being claimed as a separately worded Appendix E mandatory rule; it is the executable/reference-compatible cadence used for interoperability.

---

## 4. Barriers and capture

### 4.1 Mandatory facts

- Barrier placements are public.
- Their declared location must be truthful.
- Barriers are persistent.
- Barrier quota follows the negotiated/shared config and may not violate Appendix F minimums.
- A barrier placed on the Thief's current cell causes immediate capture (Appendix E Rule 46).
- A Thief with no legal move is captured (Appendix E Rule 47).
- Capture claims must be truthful.

### 4.2 Important implementation correction

The tested professor reference implementation does **not** fully enforce every mandatory edge rule:
- it does not implement Rule 47 boxed-in capture;
- its barrier API rejects placing a barrier on Police's own cell.

Therefore our rules engine must enforce the **mandatory PDF Rule 47**, even if the reference baseline omits it.

### 4.3 Own-cell barrier ambiguity

There is a genuine interoperability disagreement:

```text
professor reference / NotebookLM:
    adjacent-only barrier placement

league negotiation form:
    own cell + 4 orthogonally adjacent cells
```

Do not hard-code this deep inside the engine.

Represent it explicitly:

```text
barrier_placement_mode:
    ADJACENT_ONLY
    OWN_PLUS_ADJACENT
```

Default for an unmodified professor/reference-v3 opponent:

```text
ADJACENT_ONLY
```

Before a real opponent match, confirm this setting in the shared negotiation/config.

Status: `NEGOTIATED / KNOWN EDGE-CASE AMBIGUITY`

This ambiguity must **not block Phase 1**, because the rule can be parameterized and tested in both modes.

---

## 5. Hcommit / Commit–Reveal

### Status

`VERIFIED_REFERENCE_INTEROP`

### Exact reference-compatible construction

Given a revealed payload dictionary and nonce:

```text
canonical = json.dumps(
    payload,
    sort_keys=True,
    ensure_ascii=False,
    separators=(",", ":")
)

preimage = canonical + "|" + nonce
Hcommit = SHA256(UTF8(preimage))
```

Important details:

- Hash the entire revealed payload dictionary.
- Dict keys are sorted.
- No formatting whitespace in canonical JSON.
- `ensure_ascii=False`.
- Native UTF-8 is used.
- Nonce is **outside** the JSON.
- Exactly one ASCII `|` separates canonical JSON and nonce.
- Python-compatible JSON float serialization is part of the interoperability dialect.
- Extra payload fields change the hash.

The book contains incompatible illustrative commit examples. For interoperability, use the tested `reference-v3` construction above.

### Verification evidence

Completed verification produced:
- `125/125` conformance-vector checks;
- `750/750` seeded differential commitment cases;
- Unicode/Hebrew/emoji cases;
- floats;
- nested structures;
- fixed golden vectors.

Evidence:
- `reports/INTEROP_VERIFICATION_REPORT.md`
- `docs/INTEROP_DECISIONS.md`
- `interop/golden_vectors/hcommit_reference_vs_kit.json`

### Engineering requirement

Implement Hcommit behind a small isolated crypto API and make the golden-vector suite part of CI/tests.

Do not rewrite or "simplify" the serializer.

---

## 6. Scent / pheromone model

### Official fixed facts

Appendix F fixes:
- field size: `5×5`;
- center intensity: `0.9`;
- decay parameter: `0.10`.

Appendix E Rule 23 requires the full scent emission/decay model to be cryptographically locked before play.

### Why it is configurable

The official book dialect and executable reference dialect are observably different.

Therefore scent is: `NEGOTIATED_PER_MATCH`

### Reference-v3 dialect

Use this when playing an unmodified professor/reference-v3 peer:

```text
name: subtractive_chebyshev_v1
falloff: Chebyshev rings
I = 0.9
rings: 0.9 / 0.6 / 0.3
precision: round to 3 decimals
deposit merge: max(old, deposit)
update: deposit at post-action position, then subtract 0.1
clamp: max(0, value)
edges: clip outside board
barriers: no effect on scent
STAY/HOLD: emits scent
cadence: per sender action/message
```

A freshly transmitted center after deposit+decay is therefore `0.8`.

### Book dialect

The book describes a different model using the printed 5×5 kernel and multiplicative decay in the conformance interpretation.

Keep scent behavior behind a replaceable interface, e.g.:

```text
ScentModel
├── ReferenceSubtractiveChebyshevV1
└── BookMultiplicativeV1
```

Never silently choose one when the opponent declares another.

### Verification evidence

See:
- `interop/fixtures/scent_reference_scenarios.json`
- `reports/INTEROP_VERIFICATION_REPORT.md`

---

## 7. FastMCP wire

### Status

`VERIFIED_REFERENCE_INTEROP`

### Endpoint

Reference-compatible HTTP FastMCP endpoint:

```text
/mcp
```

### Reference tools

```text
negotiate(message: dict)
receive_turn(message: dict)
submit_audit(payload: dict)
receive_control(message: dict)   # optional/best-effort
```

Each reference handler queues the object and returns:

```json
{"ok": true}
```

### TurnMessage baseline

Required logical keys:

```text
step
sender
hint
smell_grid
commit
timestamp
```

Reference output also includes nullable:

```text
barrier_placed
capture_claim
claim_response
win_claim
```

### Delivery robustness

The professor sender retries requests, but the professor receiver itself is not safely idempotent.

Adopt the conformance-kit receiver rules:

- same `step` + same `commit` redelivery → absorb as duplicate;
- same `step` + different `commit` → reject as equivocation;
- bounded future-step buffering;
- stale unknown frames → discard/reject safely;
- duplicate traffic must not extend deadlines.

### Verification evidence

Completed:
- professor localhost MCP tests: `4/4`;
- conformance-kit tests: `167 passed`, with `6` HTTP-only skips in that run;
- safe uncounted six-sub-game self-play completed successfully.

---

## 8. Shared config and artifacts

### Mandatory official facts

The two peers must use the same shared game config **byte-for-byte**.

Official artifact filename patterns:

```text
declaration_<game_id>.json
config_<game_id>_g<NN>.json
log_<game_id>_g<NN>.json
result_<game_id>.json
```

Both teams independently submit agreeing final results after mutual audit.

### Serialization reality

There are several distinct serialization scopes in the reference implementation:

1. pretty disk JSON;
2. compact canonical object hashing;
3. a separate consensus-signature serialization.

Do not treat those as interchangeable.

### Status

`NEGOTIATED_PER_MATCH`

This status applies to:
- exact artifact schema/version when implementations differ;
- exact final consensus scope;
- whether specific pretty-file bytes beyond mandatory shared config are compared.

It does **not** make the official filenames or shared-config byte identity optional.

### Known mismatch

The professor reference and played conformance-kit convention differ on whether `tie` is included in the symmetric sub-game row used for final consensus hashing.

Before a counted match, agree on:
- artifact schema/version;
- consensus field scope;
- exact config bytes;
- a worked consensus vector if needed.

---

## 9. Pre-match interoperability profile

Every real opponent pairing should resolve the following before play:

```text
wire_profile
commit_profile
scent_profile
barrier_placement_mode
artifact_schema
final_consensus_scope
timeouts
shared config bytes/hash
```

Recommended default when facing a team that says it is "reference compatible":

```text
wire_profile = reference-v3
commit_profile = reference-v3
scent_profile = subtractive_chebyshev_v1
turn_model = alternating_thief_first
barrier_placement_mode = ADJACENT_ONLY unless explicitly agreed otherwise
```

Still verify the opponent's declared profile; do not infer compatibility from a team name.

---

## 10. Phase 1 implementation scope

The next coding phase is deliberately narrow.

### Build now

#### Domain model

Create clear immutable/validated domain types for at least:

```text
Role
Position
Direction
MoveType
Action
Barrier
GameConfig
WorldState / SimulatorState
LocalState
Observation
TerminalReason
Score
```

#### Rules engine

Implement and test:

- bounds;
- orthogonal movement;
- STAY;
- blocked cells;
- barrier placement;
- configurable barrier placement mode;
- barrier persistence;
- Rule 46 barrier-on-Thief capture;
- Rule 47 boxed-in capture;
- survival threshold;
- move counters;
- scoring;
- terminal-state precedence.

#### Deterministic simulator

Create a fast local simulator using:

```text
REFERENCE_V3_ALTERNATING
Thief first
```

Requirements:

- deterministic when given seed/config/actions;
- internally allowed to know full truth;
- strategy interface must not receive hidden opponent truth;
- produce role-specific observations;
- configurable scent model;
- configurable barrier placement policy;
- no MCP dependency required for core game physics.

#### Tests

Write strong tests before strategy work.

At minimum cover:
- every movement direction;
- STAY;
- edges/corners;
- barriers;
- existing barrier;
- Rule 46;
- Rule 47;
- survival exactly at threshold;
- capture vs terminal timing in the alternating model;
- deterministic replay of an action sequence;
- observation information-leak tests;
- both barrier placement modes;
- reference scent worked vectors;
- Hcommit golden vectors if crypto is included in this phase.

### Optional only for smoke testing

A tiny random/legal baseline may be implemented only if useful to prove the simulator can finish games.

Do not optimize it yet.

---

## 11. Do NOT build yet

Do not implement or commit to:

- neural networks;
- PPO/DQN/etc.;
- self-play training;
- POMCP/IS-MCTS production search;
- opponent modelling;
- teacher/student distillation;
- LLM-controlled movement;
- final GUI;
- Gmail sending;
- ngrok/tunneling deployment;
- production league automation;
- large project-wide architecture generated before the simulator is validated.

These come after the game laboratory is reliable.

---

## 12. Architectural principle for later AI experiments

Keep the future decision backend replaceable:

```text
Observation + History
        ↓
Belief / state estimator
        ↓
DecisionBackend
        ↓
Action
```

Possible future `DecisionBackend` implementations:

```text
RandomBaseline
HeuristicBaseline
GraphSearch
BeliefSearch
POMCP / IS-MCTS candidate
NeuralPolicyValue
NeuralGuidedSearch
```

The rules engine, simulator, observation model, protocol, and evaluation harness must not depend on one particular AI approach.

---

## 13. Phase 1 acceptance criteria

Phase 1 is complete only when:

- all core rules have tests;
- tests are deterministic;
- repeated simulation with same seed/actions gives identical result;
- strategy code cannot access hidden opponent coordinates;
- Rule 46 passes;
- Rule 47 passes;
- reference alternating turn order is reproduced;
- barrier mode is explicit/configurable;
- reference scent worked vectors pass;
- the core simulator can run without MCP, GUI, Gmail, LLM, or network;
- no unresolved rule is hidden in an arbitrary hard-coded assumption.

Then stop and report before starting advanced strategy work.

---

## 14. Current state of the five original interoperability blockers

| Original blocker | Human meaning | Current status |
|---|---|---|
| Hcommit bytes | Both teams must hash exactly the same bytes | `VERIFIED_REFERENCE_INTEROP` |
| Scent law | Both teams must calculate the same smell field | `NEGOTIATED_PER_MATCH` |
| Turn/collision resolution | Both teams must agree what physically happens in a turn | Alternating Thief-first baseline established; own-cell barrier remains configurable/negotiated |
| MCP wire/schema | Both programs must speak the same network language | `VERIFIED_REFERENCE_INTEROP` |
| Artifact canonicalization | Both sides must agree what exact config/result/log representation is hashed/compared | `NEGOTIATED_PER_MATCH` |

The project is now ready to begin **Phase 1 core implementation**.
