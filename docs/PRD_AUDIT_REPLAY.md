# PRD: Audit and Replay

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Background and contract

Commit-reveal binds an action payload before its nonce is disclosed; replay reconstructs legal
state and detects tampering. Inputs are sealed per-turn payloads/nonces, ordered records, claims,
and board configuration. Outputs are commitment validity, bad-step indices, replay state, and a
sanitized audit/result summary.

Requirements: exact reference Hcommit bytes, entire payload binding including extra fields,
ordered verification, deterministic replay, role/step validation, claim corroboration, and no
nonce exposure outside legitimate unchanged audit artifacts. The cryptographic construction and
audit behavior are frozen; details remain authoritative in [interop decisions](INTEROP_DECISIONS.md).

## Selection and evidence

The current approach isolates `canonical_json`, `hcommit`, `seal`, `verify_records`,
`verify_audit`, and `replay_sequence`. Evidence: five golden vectors, tamper tests,
`tests/unit/test_game/test_turns_and_replay.py`,
`tests/integration/test_artifacts/test_phase4a_boundary_audit_artifacts.py`, the
[Phase 4D1A test mapping](audits/PHASE4D1A_TEST_SPLIT.md), and 125/125 conformance vectors.
Alternatives such as a different canonical serializer, nonce placement, signature scheme, or
consensus preimage are rejected for the frozen profile.

Offline redacted validation, fail-closed security scanning, and the verified Replay application
are implemented. Remaining evidence is operational rather than a missing verifier: an authorized
other-team audit and a later counted series must still prove mutual agreement in their explicitly
approved artifact/consensus scope. Metrics are 5/5 local Hcommit vectors, 125/125 kit vectors,
deterministic replay, and rejection of any changed payload/nonce/order. Scenarios include
Unicode/float/extra fields, wrong nonce, modified payload, bad order, terminal claims, and replay
divergence.

Definition of Done: byte vectors remain exact, failure evidence is sanitized, audit and replay
tests cover success/error paths, conformance and seven frozen hashes pass, and no negotiated
scope changes without explicit agreement. Frozen boundary includes crypto, serialization,
deadline, audit, replay, and result semantics.
