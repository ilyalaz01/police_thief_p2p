# Phase 4D1C — REF-001 Artifact Encoding Helper Extraction

Result: **GREEN mechanical extraction**. REF-001 remains **IN_PROGRESS** because runtime.py and
phase3b.py still exceed 150 counted lines. No later production slice is selected.

## Commits and boundary

- `f11b67a` — `test: characterize artifact byte and consensus contracts`
- `8984125` — `refactor: extract artifact encoding helpers`
- `92f526c` — `docs: record phase4d1c artifact split evidence`
- `87fca2e` — `style: expand artifact compatibility imports`
- `7963023` — `test: split artifact contract without compression`
- `docs: correct phase4d1c formatting evidence` — this correction commit

`LINKS_REMARK`, `pretty_bytes`, `canonical_sha256`, `consensus_sha256`, `artifact_links`,
`_hardware`, `_group`, and `_ended_at` moved without body/value changes from `artifacts.py` to
the private `artifact_encoding.py` and are imported back under the same names. All four builders,
scoring, aggregation, game-ID derivation, consensus-scope selection, and both writers remain in
`artifacts.py`. Counts changed from 168 to 139 plus 35; the new characterization test counts 97.

## Characterization evidence

All callable signatures and the `write_reference_v3_artifacts` default of
`max_tokens_per_game=0` match before/after. `_ended_at` retains valid timestamp calculation and
its TypeError/ValueError return-original fallback. The eight moved AST/value entries use
`ast.dump(..., include_attributes=False)`, sorted compact JSON framing, and match SHA-256
`9fbc2558bc35ede430993a685c4d8abb7cd0763be0180df2b0d3e2fd26f7cfdf` before and after.
`LINKS_REMARK` UTF-8 bytes independently hash to
`ac09408f8e04aaee502523a06ba49fec1dbeb5beaa9d13a294e9241920d1d7b2`.

| Domain | SHA-256 values in declaration, config, log, result order |
|---|---|
| Compact insertion-order builder objects | `01ab9bf1…`, `d9cf2e52…`, `4c6dee80…`, `a84671f0…` |
| Pretty UTF-8 builder bytes | `bcddd47d…`, `c0b0afcb…`, `c004244f…`, `4e9012aa…` |
| Reference-writer files | same four pretty hashes, official filename order |
| Local-writer files | `71d2edca…`, `66e1743d…`, `e933c34b…`, `e67a41ef…` |

The canonical configuration preimage is
`{"board_size":7,"setting":"ירושלים🙂"}` and hashes to
`bddf21fe4533895b25d06a8785cca7bc49938243d100549c4dd88d9167dfd1b3`. The exact spaced,
sorted-key consensus preimage is pinned by the characterization and hashes to
`55bdb77b8be204338518d6da3ce9a67e42d9868d2a50ee0d525a3d2756061178`. Full hashes, schema-prose
hashes, filenames, order, and behavior records are in the paired JSON report and test module.

Characterization also pins symmetric game IDs, capture/survival/unknown scoring, winning and tied
aggregation, caller-supplied `tie` preservation, and exclusion of `tie`, tokens, audit,
timestamps, and Git metadata from `reference_symmetric_outcome_without_tie`.

## Acceptance gates

| Gate | Result |
|---|---|
| Full suite | PASS — 148/148, no skip/xfail |
| Configured branch coverage | PASS — 91.17% (≥91.00%) |
| New characterization | PASS — 4/4 |
| Four-builder pinned-professor differential | PASS — no skip |
| B0 consensus and B1 profile domains | PASS — 7/7 |
| Ruff `src tests` | PASS — zero errors |
| Hcommit | PASS — 5/5 |
| Conformance | PASS — 125/125 |
| Frozen manifest | PASS — 7/7 |
| File ceilings | PASS — 139, 35, and 97 |
| Forbidden-path diff | PASS — empty |

The repository-wide over-150 roster is now exactly:

- `src/police_thief_lab/interop/runtime.py` — 565
- `src/police_thief_lab/policies/phase3b.py` — 303

No schema prose/version/field/order, filename, default, timestamp, score, aggregate, ID,
serialization, tie handling, scope, Rule 47, runtime, professor, conformance-kit, fixture, vector,
log, transport, crypto, profile, strategy, dependency, lockfile, or gameplay behavior changed.
No network, external contact, gameplay, merge, push, or tag occurred.

## Phase 4D1C.1 formatting correction

The Phase 4D1C semantic acceptance was green, but its initial `artifacts.py` import and
`tests/test_artifact_contract.py` layout violated the explicit no-compression requirement. This
correction expands the compatibility imports and replaces that test file with normally formatted
modules. It changes no production executable AST, test function AST, assertion, fixture value,
hash, or collected case.

Collection framing is independently reproducible: take each `pytest --collect-only -q --no-cov`
output line containing `::`, remove only the source path through the first `::`, sort the resulting
identifiers, serialize them as compact JSON with separators `(',', ':')` and
`ensure_ascii=False`, encode as UTF-8 with no delimiter or final newline, then SHA-256 the bytes.
Before and after contain 148 entries and hash to
`ee75bcee8c8b79457c56927b5d8cb6d8bba198905c97f06c89288fc49fbf4d6b`.

The test-function manifest walks every `FunctionDef` and `AsyncFunctionDef` in the original file
or its four replacements, dumps each with `ast.dump(..., include_attributes=False)`, sorts the
seven dump strings, serializes and encodes with the same compact-JSON/UTF-8/no-final-newline
framing, and hashes to
`3d512d38eb1ff571df531df4fb4466e0aaab1300a062556584da9da3a372c86e` before and after.
For the production check, parsing `artifacts.py`, removing top-level `Import` and `ImportFrom`
nodes, and dumping the remaining `Module` with `include_attributes=False` hashes to
`9b56ed24a9106e8af8197498e580eea96419cad260a3a03f4970a11d25809f35` before and after.

Corrected counted-line totals are 148 for `artifacts.py`, 34 for
`artifact_contract_hashes.py`, 74 for `artifact_contract_support.py`, 89 for
`test_artifact_contract_api.py`, and 108 for `test_artifact_contract_bytes.py`. Their maximum
physical test/support line lengths are respectively 98, 92, 98, and 99 characters. The corrected
full suite passes 148/148 with no skips or xfails and 91.18% branch coverage. Standard Ruff,
unsuppressed I001 for `artifacts.py`, unsuppressed E501 for all replacement files, the professor
differential, B0/B1 7/7, Hcommit 5/5, conformance 125/125, and frozen manifest 7/7 all pass.
