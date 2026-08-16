# PRD: Release Engineering and Offline Operations

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **PLANNED**; no implementation exists.

## Background and contract

Release engineering should compose existing validators into a deterministic, network-free,
fail-closed operator surface. Inputs are repository state and, optionally, one completed schema
1.1 artifact directory. Outputs are sanitized typed JSON/Markdown results and an optional
byte-preserving deterministic package.

Requirements and exact command/exit-code contracts are authoritative in the existing
[workstream specification](RELEASE_ENGINEERING_WORKSTREAM.md). They include quality-gate,
validate-match, package-match, scan-secrets, path/symlink/size defenses, atomic no-overwrite
output, and a thin no-secret CI wrapper.

## Alternatives, decision, and evidence

No implementation approach is accepted yet. The proposed boundary is a Python offline tool that
invokes existing project and kit validators with subprocess argument arrays. Alternatives are
manual commands (insufficient consistency) and reimplemented validators (unacceptable semantic
risk). Evidence today is only the individual working validators and the PLANNED specification.

Unresolved: module/API design, typed result schema, limits/timeouts, CI action pinning, and review.
Performance metrics will include deterministic output, stable exit codes, validator duration,
bounded file sizes/count, and zero sensitive body retention. Correctness scenarios are all cases
listed in the workstream, including missing tools, traversal, secrets, timeout, and overwrite.

Definition of Done: all workstream tests pass network-free; local and CI call the same entry;
reports are equivalent and sanitized; package contents are byte-identical; full suite, Ruff,
Hcommit, conformance, and frozen hashes pass. Frozen boundary: no production, game, transport,
crypto, artifact, profile, strategy, or external dependency changes.

