# PRD: Release Engineering and Offline Operations

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **IMPLEMENTED AND ACCEPTED FOR OFFLINE USE**.

## Background and contract

Release engineering composes existing validators into a deterministic, network-free, fail-closed
operator surface. Inputs are repository state and, optionally, one completed schema
1.1 artifact directory. Outputs are sanitized typed JSON/Markdown results and an optional
byte-preserving deterministic package.

Requirements and exact command/exit-code contracts are authoritative in the existing
[workstream specification](RELEASE_ENGINEERING_WORKSTREAM.md). They include quality-gate,
validate-match, package-match, scan-secrets, path/symlink/size defenses, atomic no-overwrite
output, and a thin no-secret CI wrapper.

## Alternatives, decision, and evidence

The accepted boundary is the stdlib-oriented `tools/offline_ops` package. It invokes existing
project and kit validators with subprocess argument arrays, exposes `quality-gate`,
`validate-match`, `package-match`, and `scan-secrets`, and uses the same entry point from the thin
GitHub Actions workflow. Manual command aggregation was rejected as inconsistent; reimplementing
the validators was rejected as semantic risk. Phase 4D5 records the port, path reconciliation,
cross-Python correction, 96 workstream tests, and composed public/local gate evidence.

The implementation has typed sanitized result schemas, deterministic exit codes, limits/timeouts,
path/symlink/size defenses, atomic no-overwrite packaging, pinned CI actions, and value-free secret
findings. It does not implement the separate final role-tree exporter (`SUB-001`) or Gmail sender
(`MAIL-001`).

Accepted Definition of Done: all workstream tests pass network-free; local and CI call the same entry;
reports are equivalent and sanitized; package contents are byte-identical; full suite, Ruff,
Hcommit, conformance, and frozen hashes pass. Frozen boundary: no production, game, transport,
crypto, artifact, profile, strategy, or external dependency changes.
