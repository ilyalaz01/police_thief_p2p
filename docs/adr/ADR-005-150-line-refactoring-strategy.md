# ADR-005: 150-line refactoring strategy

Status: ACCEPTED

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

Decision: accept only the Phase 4D1A test split. The two test modules were mechanically divided
by their existing concerns, shared helpers were centralized once, and the real two-process test
was isolated. The normalized 135-case collection multiset and the 46-entry AST definition
manifest remained identical; branch coverage remained 90.81%; every new test/support module is
at most 142 counted lines. The four production-file treatments remain proposals and are not
selected by this decision.

For any later interoperability/strategy proposal, capture imports, public symbols, seeded
outputs, exception text where contractual, artifacts, and wire bytes before moving code. Never
compress code to meet the limit.

Phase 4D1A acceptance evidence is recorded in
`../audits/PHASE4D1A_TEST_SPLIT.md`: 135/135 tests, 90.81% branch coverage, Ruff zero, Hcommit 5/5,
conformance 125/125, frozen 7/7, and exactly four unchanged production violations remaining.
