# Offline Role Repository Assembly Runbook

Status: `LOCAL_DRAFT_PENDING_EXPORTER_INTEGRATION_AND_HUMAN_APPROVAL`.

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

After the partner-owned exporter is accepted, run its documented deterministic `plan` operation
for each explicit manifest. Compare the plan against the content policy, then run `export` into two
new empty temporary roots. Preserve both plan manifests and aggregate hashes as evidence. A
snapshot mismatch, path refusal, secret finding, or non-empty output root is a hard stop.

These candidate snapshots validate byte selection only. They do not replace shared Git history and
are not publishable repositories.

## 4. Create history-preserving role branches

Prepare two local history-preserving checkouts from the accepted shared commit. Keep the complete
accepted history and preserve contributor authorship. In focused reviewed commits, make each
regular-file tree match its approved candidate snapshot. Do not copy `.git` from an export, squash
shared history, rewrite authors, or fabricate earlier reviews.

## 5. Apply the role README overlays

Use `submission/templates/police/README.md` as the future Police root `README.md` and
`submission/templates/thief/README.md` as the future Thief root `README.md`. While URLs remain
pending, the exact placeholder must stay visible and blocking. Confirm each README identifies only
its own runtime role/policy and retains Rule 50 links, GUI/Replay instructions, license, credits,
and operational limits.

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
