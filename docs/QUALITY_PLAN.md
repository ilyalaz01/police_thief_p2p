# Quality Plan

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Future implementation follows RED → GREEN → REFACTOR: add a failing requirement-level test or
characterization first, make the smallest change, then refactor with all gates green. Exceptions
require a proposed/accepted ADR before merge; retrospective tests must be labeled honestly.

## Test and coverage policy

Unit tests will mirror source modules and isolate I/O; integration tests will cover component
contracts/process boundaries; system tests will cover complete offline peer/artifact flows.
Ordinary tests are deterministic and network-free. External services are mocked or replaced by
local fakes; separately authorized interoperability procedures are not part of the default suite.

Configured global branch coverage must remain ≥85%. Reviews map critical paths—rules 46/47,
terminal precedence, observation isolation, profile mismatch, retries/deadlines,
duplicate/equivocation, audit/replay, artifact hash domains—to explicit branch and meaningful path
scenarios. Ruff uses the exact `pyproject.toml` rules and permits zero violations.

Regression gates include seven frozen SHA-256 files, five Hcommit golden cases and extra-field
binding, 125/125 pinned conformance vectors, deterministic artifacts, and documentation governance
tests. No expected check may be skipped or unavailable in release evidence.

Security checks will scan tracked/release inputs for credentials, private keys, authorization
headers, private paths/bodies, personal correspondence, live endpoints, and non-artifact
operational nonces. Findings are reported by category/path only, never echoed. Documentation tests
parse JSON, resolve relative links, enforce status/traceability/ADR/diagram rules, and reject
historical or readiness fabrication.

## Failure evidence and release criteria

Keep sanitized command, tool/version, commit, status, counts, duration, and failure category.
Never retain sensitive stdout/artifact bodies. A failure remains visible until superseded by a
linked green rerun; a missing validator is not a pass.

Release eligibility requires clean reviewed branch/PR evidence; full pytest and ≥85% branch
coverage; Ruff zero; Hcommit 5/5; conformance 125/125; frozen 7/7; governance/link/JSON/security
checks; version/changelog/config compatibility; and no unresolved P0 release blocker. Phase 4D0
documentation GREEN is not overall release or match readiness.

### Sanitized report retention

Local pytest may emit JUnit XML into an ignored temporary or operator-selected report directory.
The committed audit retains only command identity, tool/version, commit, counts, duration,
coverage percentage, status, and a non-sensitive failure category.
The committed audit must not contain raw stdout or stderr.
It also excludes test payloads, artifact bodies, paths outside the repository, endpoints,
credentials, authorization headers, nonces, or match commit identity values.

A failed run remains retained in the phase audit until a linked successful rerun supersedes it;
the linked successful rerun never deletes or relabels the earlier failure. Detailed temporary
JUnit XML may be deleted after the sanitized summary is reviewed. Missing, skipped, timed-out, or
unavailable required validators are failures, not passes. The release-engineering workstream may
automate this policy but may not weaken or duplicate the underlying validators.

## Pull-request checklist

- Requirements/TODO/ADR and authority are linked; scope and exclusions are explicit.
- RED/GREEN/REFACTOR or justified characterization evidence is attached.
- Unit/integration/system success and failure paths match risk.
- Coverage/Ruff/frozen/Hcommit/conformance/documentation/security gates pass.
- No semantic, dependency, config, secret, privacy, endpoint, nonce, or artifact surprise exists.
- User docs, risk, rollback/recovery, remaining blockers, owner, and evidence are current.
- At least Shared Review approves; higher-risk interoperability changes obtain architecture and
  explicit human/negotiation review.
