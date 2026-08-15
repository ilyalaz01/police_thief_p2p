# Release Engineering and Offline Operations Workstream

Status: `PLANNED`

## Purpose

This subsystem provides reproducible local verification, fail-closed release checks, safe
validation of completed match artifacts, and deterministic operator packages. It composes the
existing project and conformance validators without redefining game or interoperability rules.

The subsystem is intentionally independent from strategy development and live match operations.
It can be implemented and reviewed without changing the simulator, policies, protocol, runtime,
transport, cryptography, artifact builders, or negotiated profiles.

## Source authority

Implementation must preserve the hierarchy in `RULES_AND_INTEROP_BASELINE.md`. The official game
specification and existing validators remain authoritative for game and artifact semantics.
Release tooling may orchestrate those validators but must not replace them with new
interpretations.

The professor-owned reference repository is not redistributable and must not be copied, vendored,
downloaded by CI, or reimplemented. The MIT conformance kit is available through the pinned
`external/copthief-league-protocol` submodule.

## Module boundary

Implementation changes are limited to:

- `.github/workflows/**`
- `tools/offline_ops/**`
- `tests/offline_ops/**`
- `docs/RELEASE_ENGINEERING.md`
- `scripts/offline_ops/**`
- `interop/fixtures/offline_ops/**`

Changes outside this boundary require a separate architecture review. In particular, this
workstream does not modify:

- `src/police_thief_lab/**`
- game rules, scoring, strategy, or frozen policies;
- profile, consensus, serialization, cryptography, audit, or replay semantics;
- external dependencies or submodule contents;
- Gmail, league reporting, tunnels, opponent contact, or gameplay.

## Required command surface

Provide one cross-platform, network-free Python entry command. It must use `pathlib` and
subprocess argument arrays rather than shell-specific command strings. The exact invocation must
be documented in `docs/RELEASE_ENGINEERING.md`.

### `quality-gate`

Compose the established checks:

- project pytest with configured branch coverage;
- Ruff;
- Hcommit golden vectors;
- frozen production-file manifest;
- conformance-kit `verify_vectors.py`;
- optional completed-artifact validation;
- repository/package secret scan.

A required validator that is missing, skipped, timed out, or unable to run is not a PASS.

### `validate-match PATH`

Validate one completed schema 1.1 four-artifact directory through the existing MIT checker.
Reject missing, duplicate, unexpected, malformed, oversized, symlinked, or path-escaping files.
Reports must not reproduce JSON bodies, identity blocks, audit records, commit values, MCP URLs,
or nonce values.

Official terminal-audit logs legitimately contain revealed nonces. They may remain only inside a
validated unchanged log artifact and must never be copied into generated reports. Existing
validators determine audit validity.

### `package-match PATH --output PATH`

Validate first, then atomically create a new deterministic package containing only:

- the exact four validated artifacts, byte-for-byte unchanged;
- one redacted JSON validation manifest;
- one equivalent redacted Markdown report.

Reports may contain filenames, byte lengths, SHA-256 values, validator identities, durations,
statuses, and exit codes. Existing output paths must never be overwritten.

### `scan-secrets PATH`

Fail closed on credentials, authorization headers, access tokens, private keys, tunnel
configuration, caches, temporary files, unexpected files, path traversal, and non-artifact nonce
material. Test data must use synthetic placeholders only.

## Result contract

Markdown and JSON reports must be rendered from one typed result model. Every check has a stable
identifier, status, sanitized explanation, duration, and exit code. Raw stdout or stderr from
sensitive inputs must not be retained.

| Exit code | Meaning |
|---:|---|
| 0 | Every requested required check passed. |
| 2 | Invalid invocation or configuration. |
| 3 | One or more quality checks failed. |
| 4 | Secret or privacy scan failed. |
| 5 | Match directory or package validation failed. |
| 6 | A requested required validator or dependency is unavailable. |
| 7 | A report or package output could not be written safely. |

## CI contract

GitHub Actions must be a thin wrapper over the same local command. The workflow must:

- use read-only repository contents permission;
- pin action revisions and dependency inputs;
- use no repository secrets;
- perform no peer, tunnel, mail, league, or gameplay operation;
- upload no match artifact or private report;
- contain no second CI-only implementation of the gate.

Ordinary dependency installation and repository checkout are allowed CI setup operations.

## Required tests

Deterministic offline tests cover:

- dispatch and every documented exit code;
- missing validators and timeouts;
- subprocess paths containing spaces;
- equivalent sanitized Markdown and JSON reports;
- invalid JSON and missing, extra, or duplicate files;
- symlink, traversal, file-count, per-file-size, and total-size rejection;
- credential, authorization, private-key, tunnel, and unexpected-nonce detection;
- terminal-audit nonces remaining confined to an unchanged valid log and absent from reports;
- atomic output creation and overwrite refusal;
- deterministic valid synthetic fixtures;
- CI invoking the same local entry point.

Tests use no network, real credentials, operational nonces, personal data, private artifacts, or
professor-owned code.

## Definition of Done

- All changes stay inside the module boundary.
- Missing dependencies and invalid inputs fail closed with stable exit codes.
- Existing validators are composed rather than reimplemented.
- Package artifacts remain byte-identical to validated inputs.
- Generated reports contain no artifact bodies or sensitive values.
- Local and CI execution use the same implementation.
- Existing project tests, coverage, Ruff, Hcommit, conformance, and frozen hashes remain green.
- `docs/RELEASE_ENGINEERING.md` documents setup, commands, output, recovery, and security limits.
