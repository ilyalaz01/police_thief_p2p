# Interop Decisions

Verification date: 2026-08-12. These decisions target book/code v3.0.0, professor commit `960499fd5e8777b4929625f5d8fdcf2ab4677b54`, and conformance-kit commit `be96e57e357d59386c486a907e210e050d74c114`.

## Hcommit

STATUS: `VERIFIED_REFERENCE_INTEROP`

Algorithm: `SHA256(UTF8(canonical_json(payload) + "|" + nonce))`.

Canonical JSON: Python `json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`. Sort by Unicode code point; use native UTF-8; use Python-compatible shortest round-trip float spellings. The nonce is outside JSON after one ASCII pipe. Hash the entire revealed payload, including unknown/extra fields. The reference compares ordinary hex strings, not constant-time.

Evidence: professor `domain/crypto.py:20-46`; kit `verify_vectors.py:47-75`; 125 kit checks passed; five local vectors and 750 seeded differential cases passed in `interop/golden_vectors/hcommit_reference_vs_kit.json`.

## Scent

STATUS: `NEGOTIATED_PER_MATCH`

Official constants: 5×5, center 0.9, decay 0.10 (PDF Appendix F, table 16, PDF p.153). Rule 23 requires the model to be cryptographically locked before play (PDF p.145).

Default for a reference-v3 opponent: lock `subtractive_chebyshev_v1`: Chebyshev falloff `round(max(0, I - I/3*d), 3)`, max-merge, then subtract 0.1 and clamp at zero, once on every sender action (including HOLD/final). Board edges clip; barriers do nothing to scent.

Do not silently substitute the book dialect. `multiplicative_book_v1` uses the printed 5×5 kernel, multiplicative decay, and once-per-full-turn cadence. Exchange locked-model hashes; refuse only if both declare and differ.

Evidence: professor `domain/smell.py:22-58`, `peer/turn_sender.py:59-69`; kit `vectors/pheromone.json`, `vectors/scent_book_v3.json`, and `vectors/locked_model.json`; worked grids in `interop/fixtures/scent_reference_scenarios.json`.

## Turn Resolution

STATUS: `UNRESOLVED`

Implement the official/reference alternating model, not an invented simultaneous resolver: Thief owns the first turn token; receipt of a turn makes the receiver move. One local action is applied and sealed before it is sent. Capture is settled by an honest response to Police's cell claim, a barrier on Thief's cell (Rule 46), or Thief having no orthogonal escape (Rule 47). Police barriers are public, persistent, quota-limited, and placed instead of movement.

The professor engine has no shared world state and cannot define swaps, both entering a third cell, or barrier-versus-simultaneous-departure. Before playing any peer that models simultaneous commitments, explicitly agree on turn cadence and collision ordering.

Smallest open question: “Are actions alternating with Thief first, as in reference v3, or simultaneous; if simultaneous, what exact order resolves movement, barrier placement, capture, and survival when they coincide?”

Evidence: professor `peer/runtime.py:3-7`, `domain/own_state.py:35-73`, `peer/turn_handler.py:41-60`; PDF Rules 13–16 and 46–47 (pp.144,149); fixtures in `interop/fixtures/turn_resolution_scenarios.json`.

## MCP Wire

STATUS: `VERIFIED_REFERENCE_INTEROP`

Endpoint/transport: FastMCP 3.4.3 HTTP at `/mcp`.

Tools: `negotiate(message: dict)`, `receive_turn(message: dict)`, `submit_audit(payload: dict)`, and optional `receive_control(message: dict)`. Each returns `{"ok": true}` after queueing. Turn messages have ten keys: `step`, `sender`, `hint`, `smell_grid`, `commit`, `timestamp`, plus nullable `barrier_placed`, `capture_claim`, `claim_response`, `win_claim`.

Outbound calls retry the identical in-memory dict every configured interval until deadline. The professor receiver queues duplicates without idempotency or step/equivocation checks. For league compatibility implement the kit's at-least-once contract: absorb same-step/same-commit redelivery; reject different-commit equivocation; buffer bounded future steps; do not extend the deadline for tolerated duplicate traffic.

Evidence: professor `infra/mcp_server.py:47-75`, `infra/mcp_client.py:21-108`, `domain/protocol.py:12-40`; kit `vectors/turn_message.json` and `vectors/delivery_contract.json`. Professor localhost MCP tests passed 4/4; kit suite passed 167 with 6 HTTP-only skips.

## Artifacts

STATUS: `NEGOTIATED_PER_MATCH`

Official filenames: `declaration_<game_id>.json`, `config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, `result_<game_id>.json` (PDF Appendix F table 20, p.157). The shared config must be byte-identical (Rule 11, p.144), attached per game, and cryptographically locked.

Reference disk JSON: UTF-8, `ensure_ascii=False`, indent 2, insertion order, no EOF newline. Object hashes/config locks use compact sorted canonical JSON. The legacy Hebrew report consensus signature alone uses sorted JSON with default spaces and sign-then-insert. Final `mutual_agreement` must hash only symmetric outcome fields, never per-peer timestamps/tokens.

Key reordering, whitespace, EOF newline, or Unicode escaping preserve parsed meaning but change file-byte hashes. Do not compare pretty artifact file bytes unless the match explicitly requires it; compare the agreed canonical object or named symmetric scope. Agree before play on the exact result schema/scope because the professor artifact schema and played kit convention are not fully identical.

Evidence: professor `report/emit.py:34-39,95-123`, `report/artifact_helpers.py:14-44`, `report/report_writer.py`; kit `vectors/report_consensus.json`; mutations in `interop/fixtures/artifact_mutations.json`.

## Full Counted-Series Shared Configuration

STATUS: `UNRESOLVED_FOR_COUNTED_SERIES`

The official PDF Appendix B describes a byte-identical `config/game.json` schema 1.2 containing
board, movement, scoring, pheromone, league, timeout, token-budget, and Gatekeeper fields. Appendix
F fixes a six-sub-game series and the quantitative minima/fixed values. The pinned professor
negotiation and schema-1.1 artifact builders instead expose the tested flat 14-term agreement,
while our stronger runtime lock separately serializes the extended `MatchProfile`.

These are three named scopes, not interchangeable serializations:

1. official full Appendix-B shared configuration for a counted series;
2. professor-compatible 14-term negotiation/config-artifact body;
3. local extended runtime profile bytes.

Current code proves scopes 2 and 3 and retains scope 1 separately. Phase 4D13B runs six localhost
sub-games as twelve processes and carries identical scope-1 bytes at `config/game.json` beside
two mutually agreeing 14-artifact schema-1.1 sets. This is synthetic self-test evidence: no real
peer has approved the proposed serialization, schedule, tie policy, or consensus scope. Do not add
fields to the pinned professor body,
drop official fixed fields, or hash one scope while labeling it as another. `LGE-001` must define
an outer counted-series/config contract with differential and frozen regression tests. Explicit
bilateral agreement is still required for negotiable values and serialization choices, but it
cannot waive fixed Appendix-E/F requirements.
