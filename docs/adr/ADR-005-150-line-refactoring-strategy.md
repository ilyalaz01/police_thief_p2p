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

Decision: accept the Phase 4D1A test split. The two test modules were mechanically divided
by their existing concerns, shared helpers were centralized once, and the real two-process test
was isolated. The normalized 135-case collection multiset and the 46-entry AST definition
manifest remained identical; branch coverage remained 90.81%; every new test/support module is
at most 142 counted lines.

Also accept the Phase 4D1B belief-only slice: after contract characterization, `_open_cells`,
`_field_error`, and `_entropy` moved unchanged to a private support module and were imported back
under the same names. `belief.py` fell from 154 to 133 counted lines and `belief_support.py`
contains 26. Public imports, signatures/defaults, exceptions, exports, deterministic vectors,
mathematics, policies, and frozen behavior remained unchanged. The runtime, phase3b, and artifact
treatments remain proposals and are not selected by this decision.

Also accept the Phase 4D1C artifact-encoding slice: after byte, schema, writer, consensus,
profile-domain, professor-differential, and AST characterization, `LINKS_REMARK` plus seven
formatting helpers moved unchanged to `artifact_encoding.py` and were imported back under the
same names. `artifacts.py` fell from 168 to 139 counted lines; the support module contains 35.
All schema 1.1 objects, bytes, ordering, IDs, scores, ties, fallbacks, hashes, filenames, and
consensus scope remained exact. Runtime and phase3b remain unselected proposals.

For any later interoperability/strategy proposal, capture imports, public symbols, seeded
outputs, exception text where contractual, artifacts, and wire bytes before moving code. Never
compress code to meet the limit.

Phase 4D1A acceptance evidence is recorded in
`../audits/PHASE4D1A_TEST_SPLIT.md`: 135/135 tests, 90.81% branch coverage, Ruff zero, Hcommit 5/5,
conformance 125/125, frozen 7/7, and exactly four unchanged production violations remaining.
Phase 4D1B evidence is recorded in `../audits/PHASE4D1B_BELIEF_SPLIT.md`: 144/144 tests, 91.06%
branch coverage, the same frozen/conformance gates, and exactly three production violations
remaining.
Phase 4D1C evidence is recorded in `../audits/PHASE4D1C_ARTIFACT_SPLIT.md`: 148/148 tests, 91.17%
branch coverage, pinned-professor/B0/B1 byte gates, and exactly two production violations
remaining.
