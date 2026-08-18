# Offline Role Repository Assembly Runbook

Status: `LOCAL_ROLE_CANDIDATES_GREEN_PENDING_RECIPROCAL_URL_AND_PUBLICATION_APPROVAL`.

This runbook defines the smallest safe sequence for preparing candidate Police and Thief trees.
It implements no game rule, chooses no URL, creates no remote repository, and authorizes no tag or
external operation. Official Rules 49/50 and the authority order in
[`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md) remain controlling.

## 1. Freeze the accepted shared commit

Start only from a clean, accepted shared `main`. Record its full 40-character SHA as the exact
`source_commit` for both candidate manifests. Require that commit to contain the accepted content
policy, both role README overlays, and the integrated guarded exporter. Do not invent provenance or
continue from a dirty worktree.

## 2. Generate and review explicit manifests

Generate one explicit manifest for `police` and one for `thief` from the reviewed
[`role_content_policy.v1.json`](../data/submission/role_content_policy.v1.json). Each manifest must
list every selected regular file, the exact `source_commit`, Rule 50 required paths, and the role's
README overlay. Keep `counterpart_repository_url` exactly `PENDING_HUMAN_APPROVAL` during offline
preparation. Input ordering must not affect the deterministic plan.

The selected set excludes ignored/private paths, `tests/offline_ops/` synthetic secret-shaped
fixtures, `.gitmodules`, and Git gitlinks. A human reviews every path and hash before export.

## 3. Produce offline candidate snapshots

The integrated assembler generates both explicit manifests and composes the partner-owned
exporter without changing it:

```bash
uv run python -m tools.submission_assembly.cli tmp/role-candidates
```

Run only from an exact clean accepted commit into a new output path. The command prepares both
roles atomically, preserves the input/export/candidate manifests under each role's `evidence/`,
places only selected candidate bytes under `tree/`, replaces exactly the root README with the
reviewed role overlay, and scans each tree. Review every path and hash. A source-dirty state,
snapshot mismatch, path refusal, secret finding, or existing output root is a hard stop.

Phase 4D14A reproduced both 334-file snapshots from one implementation commit. Candidate
snapshots validate byte selection only. They do not replace shared Git history and are not
publishable repositories.

## 4. Create history-preserving role branches

Prepare two local history-preserving checkouts from the accepted shared commit. Keep the complete
accepted history and preserve contributor authorship. In focused reviewed commits, make each
regular-file tree match its approved candidate snapshot. Do not copy `.git` from an export, squash
shared history, rewrite authors, or fabricate earlier reviews.

Phase 4D14C completed this local step from accepted source `e3fda929...`: Police candidate
`c52f907...` and Thief candidate `fd87d62...`. These local branches are evidence only; neither was
pushed or assigned a final remote.

## 5. Apply the role README overlays

Use `submission/templates/police/README.md` as the future Police root `README.md` and
`submission/templates/thief/README.md` as the future Thief root `README.md`. While URLs remain
pending, the exact placeholder must stay visible and blocking. Confirm each README identifies only
its own runtime role/policy and retains the academic Dec-POMDP/FastMCP/strategy explanation,
embedded GUI/Replay evidence, Rule 50 links, license, credits, and operational limits.

## 6. Restore the pinned conformance submodule

The guarded exporter refuses gitlinks, so provision
`external/copthief-league-protocol` separately from its reviewed MIT upstream and pin the same
approved commit in each role repository. Restore `.gitmodules` only in this reviewed assembly
stage. Any URL or commit drift blocks the release gate.

## 7. Run independent role gates

In each candidate checkout, independently verify:

- Rule 50 layout and the exact role README overlay;
- full pytest with enforced statement/branch coverage and no unexpected skip/xfail;
- Ruff, Hcommit 5/5, frozen manifest 7/7, and conformance 125/125;
- secret/privacy/license/Markdown-link scans on the exact tracked tree;
- candidate regular-file bytes against the reviewed exporter plan;
- clean worktree, preserved shared ancestry, contributor authorship, and absence of
  `v1.0-submission`.

Retain separate Police and Thief audit JSON/Markdown. A green shared repository alone is not a
substitute for these two independent gates.

Run the shared read-only repository gate before the full role quality gate:

```bash
uv run python -m tools.submission_assembly.repository_cli \
  --role police \
  --candidate tmp/role-worktrees/police \
  --source-commit <accepted-shared-main-sha>
```

Repeat with `--role thief` and the Thief checkout. The verifier requires a clean accepted source
and clean candidate, exact ancestry/file bytes, the unchanged `.gitmodules` and gitlink pin,
pending counterpart placeholder, zero secret findings, and no final tag. It is read-only and
authorizes no remote or external operation.

Phase 4D14C ran both repository gates and both independent role quality gates. Each role collected
343 tests, passed 338 with five explicit redistribution/evidence skips, reached 91.10% coverage,
and passed Ruff, Hcommit 5/5, frozen 7/7, conformance 125/125 and its exact candidate secret scan.

## 8. Stop for exact-content and URL approval

Present both exact candidate commit SHAs, file/hash manifests, gate evidence, proposed repository
names, and reciprocal URLs to the human operator. Replace `PENDING_HUMAN_APPROVAL` only after both
exact URLs and both contents are approved together. Re-run both gates after changing the links.

Only a later explicit authorization may create remotes, push either repository, or create the
annotated `v1.0-submission` tags. The tags must point to the exact approved commits and must never
be moved silently.

## Hard stops and operation classes

No command in this runbook authorizes opponent contact, public transport, a real-team warm-up, a
counted league game, Gmail reporting, Moodle submission, repository publication, or a final tag.
Local simulator experiments, local interoperability tests, historical public self-tests,
uncounted warm-ups, and counted league operations remain distinct evidence classes.

Stop on a frozen hash change, policy change, unresolved interoperability difference, exporter
contract mismatch, secret/private path, missing submodule evidence, history/authorship loss,
counterpart disagreement, or absent exact-content approval.
