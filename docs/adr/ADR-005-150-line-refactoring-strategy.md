# ADR-005: 150-line refactoring strategy

Status: PROPOSED

Context: an independent repository scan counted each nonblank line whose first non-whitespace
character is not `#`, excluding the external dependency tree. Exactly these files exceed 150:

| File | Count | Risk/proposed treatment |
|---|---:|---|
| `src/police_thief_lab/interop/runtime.py` | 565 | High-risk interoperability orchestration; characterize, then extract by phase only. |
| `src/police_thief_lab/policies/phase3b.py` | 303 | High-risk strategy behavior; frozen-output characterization before any split. |
| `src/police_thief_lab/interop/artifacts.py` | 168 | High-risk serialization/consensus; avoid until byte vectors pin every output. |
| `src/police_thief_lab/policies/belief.py` | 154 | Moderate/high strategy risk; possible mechanical model/helper split after characterization. |
| `tests/test_phase4a_interop.py` | 305 | Safer mechanical split by protocol/runtime scenario, preserving assertions. |
| `tests/test_phase4b_transport.py` | 441 | Safer mechanical split by transport/public-gate scenario, preserving fixtures/assertions. |

Proposal: split tests first, then the smallest non-frozen production candidate; never compress.
For interoperability/strategy files, capture imports, public symbols, seeded outputs, exception
text where contractual, artifacts, and wire bytes before moving code. No split is selected here.

All seven frozen hashes must remain unchanged; therefore frozen files cannot be refactored under
this proposal. Acceptance requires the same counting command/result ≤150, full suite/coverage,
Ruff, 5/5 Hcommit, 125/125 conformance, and frozen 7/7.

