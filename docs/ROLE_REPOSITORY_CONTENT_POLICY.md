# Police and Thief Repository Content Policy

Status: `LOCAL_CANDIDATE_PENDING_EXPORT_TOOL_INTEGRATION`.

This document selects a safe, reproducible shared content boundary for the two future role
repositories. It does not create them, choose their URLs, publish an export, or authorize a tag.
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

## Exclusions and separate provisioning

The exporter must never read ignored `sources/`, `reports/`, `tmp/`, `temp/`, agent state,
credentials, retained logs, tunnels, operational evidence, or professor-owned code. Those paths
are outside the Git index and are also forbidden by the exporter contract.

`tests/offline_ops/` is excluded from the role snapshot because it intentionally contains
synthetic secret-shaped fixtures. The production `tools/offline_ops/` gate remains included, and
the shared repository retains the complete tests and their evidence. This avoids turning known
scanner test values into final role-repository findings.

The guarded snapshot exporter also refuses Git submodule entries. Therefore `.gitmodules` and the
`external/copthief-league-protocol` gitlink are outside its copied snapshot. Before either final
role quality gate, the approved MIT conformance kit must be restored separately at the reviewed
pinned commit from `https://github.com/Imreec/copthief-league-protocol`. That later provisioning is
not performed or authorized by this policy.

## History-preserving assembly

The deterministic exporter is a byte-selection and validation tool; it must not replace Git
history. Final role assembly must start from the approved shared history so contributor authorship
and accepted PR evidence remain inspectable. Role-specific changes then use new reviewed commits.

The candidate role-specific root README overlays are retained at
`submission/templates/police/README.md` and `submission/templates/thief/README.md`. The complete
offline, history-preserving sequence is documented in
[`ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md`](ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md). These files contain
only pending counterpart placeholders and do not satisfy Rule 49 before exact URL approval.

For each role, the future operator must:

1. choose the exact accepted shared `HEAD` and generate an ignored explicit exporter manifest;
2. run deterministic `plan`, review every selected path/hash, and create an offline export;
3. prepare a history-preserving local role branch whose regular-file tree matches that export;
4. add the role-specific README title, launch example, and the real counterpart URL;
5. restore and pin the approved conformance-kit submodule separately;
6. run the role repository's full tests, Ruff, Hcommit 5/5, frozen 7/7, conformance 125/125,
   link/license/privacy checks, and compare the final tree to the reviewed plan;
7. obtain exact-content human approval before creating remotes, publishing, or tagging.

Until actual URLs are chosen, both counterpart fields remain exactly
`PENDING_HUMAN_APPROVAL`. A placeholder is not a cross-link and never satisfies Rule 49.

## Deliberate hard stops

- No final repository or `v1.0-submission` tag is authorized here.
- No Gmail, opponent contact, tunnel, public warm-up, or counted game is authorized here.
- No hidden or bilateral interoperability choice is resolved here.
- No new AI/search/ML policy or Thief champion is selected here.
- Missing exporter evidence, a different file set, or any secret/privacy finding blocks assembly.
