# Police and Thief Repository Content Policy

Status: `EXACT_ROLE_URLS_APPROVED_AND_EMPTY_PUBLIC_REPOSITORIES_CREATED`.

This document selects a safe, reproducible shared content boundary for the two role repositories.
The operator approved the exact reciprocal URLs and creation/publication of the two repositories;
both public repositories were created empty so accepted history can be preserved. Publication
still requires updated candidates and repeated gates. No final submission tag is authorized.
The machine-readable policy is
[`data/submission/role_content_policy.v1.json`](../data/submission/role_content_policy.v1.json).

## Official requirements

Official Rule 49 requires separate Police and Thief GitHub repositories, cross-links in both
READMEs, and both groups' four repository links in the submitted JSON. Rule 50 requires, at
minimum, `README.md`, a `config/` directory, PRD, PLAN, and TODO in each repository.

The official requirements do not authorize copying private sources or changing game behavior.
The authority order in [`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md) remains
controlling. The two exports must preserve the accepted physics, observations, Hcommit, scent,
MCP, artifact, replay, profile, consensus, and scoring semantics.

## Content decision

Both repositories use the same validated common engine, SDK, interoperability runtime, GUI,
Replay viewer, public research evidence, tests, and release tooling. Duplicating the verified
shared implementation is safer than inventing divergent role copies. Role identity remains an
explicit runtime input and a role-specific README/manifest concern.

The Police role uses the frozen accepted `ScentTacticalPolice`. The current P2P Thief runtime uses
`RandomLegalThief`; this is an observed integration default, **not** a newly selected champion and
not permission to change competitive policy. Any future policy change requires a separately
controlled experiment and explicit acceptance.

The common candidate retains:

- license, contribution, package, lock, CI, environment-placeholder, and authority files;
- all public `src/`, core/integration/system tests, SDK, GUI, Replay, and offline tools;
- versioned `config/`, PRD/PLAN/TODO, ADRs, quality/security/release documents and audits;
- curated public research designs, results, notebook, figures, and safe interop fixtures/vectors.
- both reviewed README overlays under `submission/templates/`, so the retained governance tests
  can verify the two academic manuals from either role candidate.

## Exclusions and separate provisioning

The exporter must never read ignored `sources/`, `reports/`, `tmp/`, `temp/`, agent state,
credentials, retained logs, tunnels, operational evidence, or professor-owned code. Those paths
are outside the Git index and are also forbidden by the exporter contract.

`tests/offline_ops/` is excluded from the role snapshot because it intentionally contains
synthetic secret-shaped fixtures. The production `tools/offline_ops/` gate remains included, and
the shared repository retains the complete tests and their evidence. This avoids turning known
scanner test values into final role-repository findings.

`tests/integration/test_submission_assembly/` and `tools/submission_assembly/` are also excluded
from the final role trees. They are shared-repository construction/gate machinery, not Police or
Thief runtime content. The guarded partner exporter and ordinary release tooling remain included.
The shared repository retains and tests this assembly machinery, while the final role gate runs it
from the exact accepted source checkout against each candidate checkout.

The guarded snapshot exporter also refuses Git submodule entries. Therefore `.gitmodules` and the
`external/copthief-league-protocol` gitlink are outside its copied snapshot. Before either final
role quality gate, the approved MIT conformance kit must be restored separately at the reviewed
pinned commit from `https://github.com/Imreec/copthief-league-protocol`. That later provisioning is
not performed or authorized by this policy.

## History-preserving assembly

The deterministic exporter is a byte-selection and validation tool; it must not replace Git
history. Final role assembly must start from the approved shared history so contributor authorship
and accepted PR evidence remain inspectable. Role-specific changes then use new reviewed commits.

The candidate role-specific academic root README overlays are retained at
`submission/templates/police/README.md` and `submission/templates/thief/README.md`. The complete
offline, history-preserving sequence is documented in
[`ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md`](ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md). These files contain
the required Dec-POMDP, FastMCP/Gatekeeper, role-strategy, Live GUI, and Replay evidence and now
pin the approved reciprocal repository URLs:

- Police repository: `https://github.com/ilyalaz01/police_thief_p2p-police`;
- Thief repository: `https://github.com/ilyalaz01/police_thief_p2p-thief`.

For each role, the future operator must:

1. choose the exact accepted shared `HEAD` and generate ignored explicit exporter manifests;
2. run the integrated deterministic assembler, review every selected path/hash, and create both
   offline exports atomically;
3. prepare a history-preserving local role branch whose regular-file tree matches that export;
4. add the role-specific README title, launch example, and the real counterpart URL;
5. restore and pin the approved conformance-kit submodule separately;
6. run the role repository's full tests, Ruff, Hcommit 5/5, frozen 7/7, conformance 125/125,
   link/license/privacy checks, and compare the final tree to the reviewed plan;
7. use the approved empty public remotes only after both updated candidates pass all gates;
8. stop before `v1.0-submission` tags pending separate explicit approval.

## Deliberate hard stops

- Creation and publication of the two named role repositories are authorized; final
  `v1.0-submission` tags are not.
- No Gmail, opponent contact, tunnel, public warm-up, or counted game is authorized here.
- No hidden or bilateral interoperability choice is resolved here.
- No new AI/search/ML policy or Thief champion is selected here.
- Missing exporter evidence, a different file set, or any secret/privacy finding blocks assembly.

Phase 4D14A integrates the partner-authored guarded exporter through
`tools.submission_assembly`. It produces separate `tree/` and `evidence/` directories, changes
only the root README after byte-checked export, and scans each exact candidate tree. Those
snapshots are still not Git repositories and do not satisfy the later history, submodule, URL,
remote, gate, or tag requirements.

Phase 4D14B adds a read-only Git repository gate. The accepted source selects 329 regular files;
the earlier 327 count preceded the two Phase 4D14B evidence files and is transparently corrected
in Phase 4D14C. The gate retains `.gitmodules` and the pinned conformance gitlink, preserves
accepted ancestry, permits only the reviewed root README overlay, scans the candidate, and refuses
a premature `v1.0-submission` tag.

Phase 4D14C validates the initial local Police and Thief candidates with preserved history and
independent quality gates. Phase 4D14D records the operator-approved reciprocal URLs and two empty
public repositories. The candidates must now integrate this accepted source and pass both gates
again before publication. Reviewed tags remain a separate blocked `SUB-001` action.
