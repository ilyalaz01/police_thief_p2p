# Phase 4D14A — Deterministic Role Candidate Assembly

Status: **GREEN locally; public PR quality-gate acceptance required before merge**.

Classification: `OFFLINE_SUBMISSION_CANDIDATE_SNAPSHOTS`.

## Outcome

Phase 4D14A integrates the partner-authored guarded exporter without rewriting it and produces
atomic, deterministic Police and Thief snapshot trees from one exact clean commit. It advances
`SUB-001`; it does not create the final repositories or satisfy Rule 49.

## TDD and implementation boundary

RED commit `a8cdc3e` added the two-role contract first. Collection failed with
`ModuleNotFoundError` because `tools.submission_assembly` did not exist. GREEN commit `836be0f`
added a separate policy/assembly layer, retained the exporter as the only file-copy/plan engine,
and moved no game, policy, protocol, artifact, or frozen behavior.

The assembler refuses dirty source state or an existing output path, resolves the reviewed policy
to two explicit exporter inputs, builds both roles in one staging root, replaces exactly each root
README with its reviewed overlay, verifies every other selected hash, directly scans each tree,
and publishes the pair only after both pass. Evidence remains outside each candidate `tree/`.

## Reproduced snapshot evidence

The clean implementation commit `836be0fd3fcc733467a3bb60baf2c9c5a1f51236` produced:

| Role | Files | Base export aggregate | Candidate aggregate | Secret scan |
|---|---:|---|---|---|
| Police | 334 | `1a6e7515106fbe93885f02b7cb1749654c18a2154b3a6591cf501cc6a0be9169` | `2e960b3779f3c92f28ffb2042f88b9625305ce33d16388ede8a4e159b0d6c6d1` | PASS |
| Thief | 334 | `1a6e7515106fbe93885f02b7cb1749654c18a2154b3a6591cf501cc6a0be9169` | `d1ecb4e5de579e120780d541b266fc8d51973270d54768128d2b8bf4be482f4f` | PASS |

Both explicit manifests and reproduced evidence bytes were identical across two runs. Both trees
contain Rule 50 paths, retain the two academic README templates needed by governance tests, omit
the intentionally secret-shaped `tests/offline_ops/` fixtures, and keep the counterpart value
exactly `PENDING_HUMAN_APPROVAL`.

## Acceptance and remaining boundary

Focused submission-assembly tests pass 14/14. The final branch state passes 453/453 tests with no
skip or xfail and 91.10% combined statement/branch coverage. Ruff passes over `src`, `tests`, and
`tools`; Hcommit is 5/5, the frozen manifest is 7/7, and the pinned conformance kit is 125/125.
An exact `git archive` snapshot excluding only the documented synthetic `tests/offline_ops/`
scanner fixtures passed the fail-closed secret scan with zero findings.

The first aggregate local gate correctly exposed two governance failures: the root manual had
lost the exact required phrase `two separate role repositories`, and five new private helpers
lacked docstrings. Both were corrected and their focused contracts pass 10/10 before the final
full run. That aggregate invocation also scanned ignored retained public-test evidence and old
temporary snapshots in the developer workspace, reporting only sanitized categories/paths. Those
ignored files are not in Git or either candidate; the exact tracked-snapshot scan is the applicable
publication evidence. No finding value was retained.

The outputs are byte snapshots, not Git repositories. Shared history/authorship, the pinned
conformance gitlink, two independent role quality gates, exact reciprocal URLs, remotes, and
annotated `v1.0-submission` tags remain Phase 4D14B/human work. No Gmail, peer, public request,
tunnel, gameplay, counted operation, repository publication, or tag occurred.
