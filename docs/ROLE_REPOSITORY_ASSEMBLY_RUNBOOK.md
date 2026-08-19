# Offline Role Repository Assembly Runbook

Status: `PUBLICATION_COMPLETE_PENDING_FINAL_SUBMISSION_TAG_AUTHORIZATION`.

This runbook defines the smallest safe sequence for preparing candidate Police and Thief trees.
The exact reciprocal URLs are approved and both verified role candidates are publicly published.
The user authorized that publication, but no final submission tag or external game operation.
Official Rules 49/50 and the authority order in
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
README overlay. During the earlier offline-only preparation, the counterpart value remained
exactly `PENDING_HUMAN_APPROVAL`; after explicit approval it must equal the role-specific URL in
the policy. Input ordering must not affect the deterministic plan.

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

Use `submission/templates/police/README.md` as the Police root `README.md` and
`submission/templates/thief/README.md` as the Thief root `README.md`. Confirm each README uses its
exact approved counterpart URL and identifies only
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
approved counterpart URL, zero secret findings, and no final tag. It is read-only and
authorizes no remote or external operation.

Phase 4D14C ran both repository gates and both independent role quality gates. Each role collected
343 tests, passed 338 with five explicit redistribution/evidence skips, reached 91.10% coverage,
and passed Ruff, Hcommit 5/5, frozen 7/7, conformance 125/125 and its exact candidate secret scan.

## 8. Stop for exact-content and URL approval

This historical approval stop is now satisfied: the operator approved these empty public
repositories and publication of candidates that pass the updated gates:

- Police: `https://github.com/ilyalaz01/police_thief_p2p-police`;
- Thief: `https://github.com/ilyalaz01/police_thief_p2p-thief`.

Push each verified candidate non-forcibly to its matching `main`, verify the public reciprocal
links and CI, and record exact public commit evidence. Stop before creating annotated
`v1.0-submission` tags; tag authorization remains separate and the tags must never move silently.

Phase 4D14E completed this sequence from accepted shared source `cff96c44...`: Police public
`main` is `42c5367...`, Thief public `main` is `f279dc2...`, both exact repository and local quality
gates passed, both reciprocal links are public, and both GitHub CI reruns passed. The initial CI
attempts transparently failed because the existing annotated `team-baseline-v1` governance tag
had not been published. Publishing that unchanged historical tag fixed clean-clone governance;
no role branch byte or commit changed and no `v1.0-submission` tag was created.

## Hard stops and operation classes

No command in this runbook authorizes opponent contact, public game transport, a real-team
warm-up, a counted league game, Gmail reporting, Moodle submission, or a final tag. Repository
publication is authorized only for the two named role candidates after both gates pass.
Local simulator experiments, local interoperability tests, historical public self-tests,
uncounted warm-ups, and counted league operations remain distinct evidence classes.

Stop on a frozen hash change, policy change, unresolved interoperability difference, exporter
contract mismatch, secret/private path, missing submodule evidence, history/authorship loss,
counterpart disagreement, or absent exact-content approval.
