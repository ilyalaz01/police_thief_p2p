# Critical-Path Test Map

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

This map turns the coverage percentage into inspectable scenario evidence. Each row identifies a
high-risk path, its expected success or failure result, and one primary automated regression test.
The listed tests are deterministic and offline; public transport and real-team operations are not
part of this suite.

| Path ID | Required scenario and expected result | Primary automated evidence |
|---|---|---|
| `RULES-46-47` | Rules 46 and 47 terminate before another strategy call; no later action is accepted | `tests/integration/test_interop/test_phase4a_runtime_rules.py::test_rule46_and_rule47_terminal_are_processed_before_strategy` |
| `OBSERVATION-ISOLATION` | A policy-visible observation contains no opponent position | `tests/unit/test_game/test_observation.py::test_observation_schema_has_no_opponent_position` |
| `PROFILE-MISMATCH` | Non-identical negotiated profile bytes fail before gameplay | `tests/integration/test_interop/test_phase4a_runtime_network.py::test_real_negotiation_mismatch_is_rejected_before_play` |
| `RETRY-DEADLINE` | A turn timeout uses the original monotonic deadline and terminates deterministically | `tests/integration/test_interop/test_phase4a_runtime_rules.py::test_turn_timeout_path_uses_monotonic_deadline` |
| `DUPLICATE-EQUIVOCATION` | Duplicate delivery is absorbed; conflicting same-step data is rejected | `tests/integration/test_interop/test_phase4a_crypto_protocol.py::test_delivery_duplicate_equivocation_buffer_stale_and_window` |
| `AUDIT-REPLAY` | Changed nonce/payload or illegal replay is rejected without strategy leakage | `tests/integration/test_artifacts/test_phase4a_boundary_audit_artifacts.py::test_tampered_nonce_payload_and_replay_are_rejected` |
| `ARTIFACT-HASH-DOMAINS` | Fixture, extended runtime profile, and canonical terms retain distinct exact hashes | `tests/integration/test_artifacts/test_profile_hash_domains.py::test_three_hash_domains_have_exact_distinct_lengths_bytes_and_hashes` |
| `BACKPRESSURE` | A full inbound queue refuses excess work without dropping or reordering accepted items | `tests/integration/test_configuration/test_gatekeeper.py::test_inbound_peer_queues_apply_bounded_fifo_backpressure_without_dropping` |
| `LOCAL-PROCESS` | Two independent loopback peers complete one full offline game | `tests/system/test_phase4a_process.py::test_two_real_independent_processes_complete_localhost_game` |
| `GIT-IDENTITY-GATE` | Real-team mode rejects unresolved commit identity before gameplay | `tests/integration/test_interop/test_phase4b_identity_gates.py::test_real_team_gate_refuses_unresolved_local_commit_before_listener` |
| `CONSENSUS-SCOPE` | The local proposal produces pinned bytes and hash without an implicit tie | `tests/integration/test_artifacts/test_final_consensus_scope.py::test_final_consensus_scope_worked_vector_exact_bytes_and_hash` |
| `SECRET-BOUNDARY` | Secret scanning reports category and location, never the detected value | `tests/integration/test_configuration/test_configuration.py::test_secret_scan_reports_location_and_category_without_value` |

## Review rules

- A percentage alone does not close a row; expected success and failure behavior must remain
  asserted by a live test.
- A renamed or removed test must update this map in the same change. Governance tests verify the
  nine highest-risk primary references automatically.
- A skipped, unavailable, externally dependent, or nondeterministic check is not release evidence.
- New negotiated semantics require explicit bilateral agreement and authority review before this
  map or any implementation changes.
