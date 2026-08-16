# Phase 4D1C — REF-001 Artifact Encoding Helper Extraction

Result: **GREEN mechanical extraction**. REF-001 remains **IN_PROGRESS** because runtime.py and
phase3b.py still exceed 150 counted lines. No later production slice is selected.

## Commits and boundary

- `f11b67a` — `test: characterize artifact byte and consensus contracts`
- `8984125` — `refactor: extract artifact encoding helpers`
- `docs: record phase4d1c artifact split evidence` — this report commit

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
