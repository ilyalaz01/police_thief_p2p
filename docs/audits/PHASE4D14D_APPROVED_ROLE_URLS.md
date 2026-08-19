# Phase 4D14D — Approved Reciprocal Role URLs

Status: **GREEN for the shared URL/publication contract; candidate update and publication pending**.

Classification: `ROLE_REPOSITORY_PUBLICATION_PREFLIGHT`.

## Decision

Accept the exact reciprocal repository identities below. The user explicitly authorized creating
both as public repositories and publishing verified role candidates. Both repositories were
created empty without starter commits, so the accepted shared history can be preserved.

- Police: `https://github.com/ilyalaz01/police_thief_p2p-police`
- Thief: `https://github.com/ilyalaz01/police_thief_p2p-thief`

The machine policy and both role README overlays now contain the exact counterpart URLs. Tests
require the URLs to match by role and forbid the former placeholder in either final manual.

## Authorization boundary

Authorized: creation of these two public repositories and non-force publication of each role
candidate only after its updated repository and quality gates pass.

Not authorized: `v1.0-submission` tags, Gmail/OAuth, opponent contact, public game transport,
another-team warm-up, counted play, reporting, Moodle submission, a new strategy, or any change to
negotiated interoperability semantics.

## Acceptance sequence

1. accept this shared source through its full tests and public CI;
2. integrate that accepted source into both history-preserving role branches;
3. resolve only policy-defined candidate exclusions, apply the exact role overlay, and run both
   repository/quality gates independently;
4. publish each GREEN branch non-forcibly to its matching empty repository;
5. verify public reciprocal links, exact commits and both CI runs; then stop before tags.

The frozen Police champion, Phase 1 physics, Hcommit, scent, MCP, artifact, consensus, audit,
replay and scoring semantics are unchanged.
