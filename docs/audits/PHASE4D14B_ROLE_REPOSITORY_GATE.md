# Phase 4D14B — History-Preserving Role Repository Gate

Status: **GREEN locally; actual role branches and public PR acceptance remain pending**.

Classification: `OFFLINE_ROLE_REPOSITORY_GATE_PREPARATION`.

## Outcome

Phase 4D14B closes the gap between a byte snapshot and a real Git repository candidate. It adds a
read-only verifier and operator CLI, then proves both roles against temporary Git clones with
shared history and the pinned conformance gitlink. It creates no final remote or tag.

## TDD evidence

RED commit `bb631ad` added the real-Git contract first. Collection failed because the role-manual
contract and repository verifier did not exist. GREEN commit `4c41d01` added those boundaries and
updated the reviewed final-role exclusions. A small follow-up aligned the existing safe wording
`not authorization`; the five final verifier/CLI contracts pass.

## Gate contract

For each role, the verifier requires:

- the accepted shared source commit remains an ancestor of the candidate commit;
- the exact reviewed 327 regular files, plus unchanged `.gitmodules`;
- the exact original conformance-kit gitlink path and object ID;
- every selected byte equals source except root `README.md`, which must equal the reviewed role
  overlay;
- clean source and candidate worktrees, zero secret findings, pending reciprocal URL, and absent
  `v1.0-submission` tag.

The policy excludes `tests/offline_ops/` synthetic secret fixtures and shared-only
`tests/integration/test_submission_assembly/` / `tools/submission_assembly/` construction code.
Runtime source, shared tests, partner exporter, release gate, documentation, GUI/Replay evidence,
research, config, license and contribution history remain selected.

## Validation and boundary

- Real temporary-Git verifier/CLI contracts: 5/5.
- Affected submission/governance contracts: 42/42.
- Every new/changed Python file remains below 150 counted lines; Ruff passes.
- Full suite: 458/458 with no skip or xfail and 91.10% combined statement/branch coverage.
- Hcommit: 5/5; frozen manifest: 7/7; pinned conformance kit: 125/125.
- The exact tracked snapshot secret scan and public PR CI remain the final acceptance checks after
  this evidence commit.

This phase prepares but does not claim the actual Police/Thief branch gates. No URL, remote,
publication, final tag, opponent contact, Gmail, public transport, gameplay, counted operation,
policy change, or negotiated interoperability decision occurred.
