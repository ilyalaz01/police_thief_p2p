# Phase 4D10A — Deterministic Offline Submission Export Tooling

Status: `GREEN`

This audit records the evidence for `SUB-001 / Phase 4D10A`: the offline
deterministic submission export tooling integrated under `tools/submission_export/`.

---

## Starting state

| Item | Value |
|---|---|
| Base branch | `main` |
| Required ancestor commit | `04dd67b633442f245e8bce3174ee610a6294b1f6` ✅ verified |
| Starting commit (HEAD at branch creation) | `1cd880f999ce9c0e58fc2f3119653c3ca7a559c0` |
| Branch created | `partner/submission-export-tooling` |
| Worktree at branch creation | Clean ✅ |

---

## Commit history

| Commit SHA | Message |
|---|---|
| `85e7f8c684f54bbbcc91ed8a0d6f6783f4088668` | `test: define offline submission export contract` (RED) |
| `c2c8434c9c6357f41b85b84c9646e8d7745ea8a7` | `feat: add guarded deterministic submission exporter` (GREEN) |
| `b14603b63b899b495e901940e638ae0d1ce73ccb` | `docs: document role submission export contract` |

Audit Markdown and JSON will be recorded in a fourth commit.

---

## Changed paths

All changes are within the owned paths defined in the task contract:

```
tools/submission_export/__init__.py         (new)
tools/submission_export/manifest.py         (new)
tools/submission_export/git_ops.py          (new)
tools/submission_export/path_guard.py       (new)
tools/submission_export/planner.py          (new)
tools/submission_export/exporter.py         (new)
tools/submission_export/cli.py              (new)
tests/integration/test_submission_export/__init__.py   (new)
tests/integration/test_submission_export/conftest.py   (new)
tests/integration/test_submission_export/test_plan.py  (new)
tests/integration/test_submission_export/test_export.py (new)
tests/integration/test_submission_export/test_refusals.py (new)
tests/integration/test_submission_export/test_cli.py   (new)
tests/integration/test_submission_export/test_governance.py (new)
docs/SUBMISSION_EXPORT_CONTRACT.md          (new)
docs/audits/PHASE4D10A_SUBMISSION_EXPORT.md (this file, new)
docs/audits/phase4d10a_submission_export.json (new)
```

No production source files, existing tests, configuration, frozen files,
external dependencies, or lock files were modified.

---

## Test and quality gate results

### Submission export integration tests (targeted)

```
uv run pytest -q tests/integration/test_submission_export --no-cov
```

Result: **51 passed** in 2.98 s

Tests cover:
- Valid Police and Thief dry-run plans ✅
- Byte-identical plan JSON across repeated runs ✅
- Stable ordering regardless of input order ✅
- Successful export into empty temporary directory ✅
- Exported bytes and per-file hashes equal source bytes ✅
- Every refusal case (absolute path, drive-qualified, `..`, empty, backslash,
  duplicate, case-insensitive collision, missing/untracked, gitlink, forbidden
  prefix `.git/`/`.agents/`/`sources/`/`tmp/`, credential filenames `*.key`,
  tunnel config filenames, wrong source_commit, missing Rule 50 paths,
  unsupported schema/role) ✅
- Required Rule 50 layout (README.md, config/, PRD, PLAN, TODO) ✅
- Pending counterpart URL preserved and never treated as approval ✅
- No absolute source path, username, or file body in output ✅
- CLI exit codes deterministic (0 on success, 1 on failure) ✅
- All new Python files obey the 150-line rule ✅

### Full project test suite

```
uv run pytest -q
```

Result: **398 passed, 10 failed (pre-existing), 5 skipped** — exit code 1

The 10 failing tests are pre-existing failures in `tests/offline_ops/` and
`tests/integration/test_governance/test_package_building_blocks.py` that exist
on `main` before this branch. They are caused by the missing
`external/copthief-league-protocol` submodule on this machine, not by this
branch's changes. Confirmed by stash-test: identical failures without new code.

Coverage: **92.59%** branch coverage (≥85% required threshold met).

### Ruff lint

```
uv run ruff check src tests tools
```

Result: **All checks passed** ✅ — zero violations

### Hcommit golden vectors

```
uv run pytest tests/integration/test_interop/test_phase4a_crypto_protocol.py \
  ::test_all_hcommit_golden_vectors_and_extra_fields --no-cov
```

Result: **1 passed (5/5 vectors)** ✅

### Frozen manifest

```
uv run pytest tests/integration/test_governance/test_frozen_manifest.py \
  ::test_authoritative_seven_frozen_file_hashes --no-cov
```

Result: **1 passed (7/7 hashes)** ✅

### Conformance kit (125/125)

The `external/copthief-league-protocol` submodule is not checked out on this
machine (it must be reprovisioned separately per `ROLE_REPOSITORY_CONTENT_POLICY.md`).
The conformance gate therefore fails with exit code 2 in the local quality-gate
invocation. This is a pre-existing environmental limitation, not caused by this
branch, and is consistent with the policy that the MIT conformance kit must be
separately restored and pinned before final role quality gates.

### Secret scan

Result: **No findings** ✅

No credentials, private paths, tunnel configuration, nonces, or retained
operational evidence were detected in the repository tree.

---

## Line counts (non-blank, non-comment)

| File | Lines |
|---|---|
| `tools/submission_export/__init__.py` | 7 |
| `tools/submission_export/manifest.py` | 66 |
| `tools/submission_export/git_ops.py` | 45 |
| `tools/submission_export/path_guard.py` | 98 |
| `tools/submission_export/planner.py` | 76 |
| `tools/submission_export/exporter.py` | 59 |
| `tools/submission_export/cli.py` | 59 |
| `tests/integration/test_submission_export/conftest.py` | 58 |
| `tests/integration/test_submission_export/test_plan.py` | 67 |
| `tests/integration/test_submission_export/test_export.py` | 64 |
| `tests/integration/test_submission_export/test_refusals.py` | 102 |
| `tests/integration/test_submission_export/test_cli.py` | 60 |
| `tests/integration/test_submission_export/test_governance.py` | 23 |

**Maximum: 102 lines** (`test_refusals.py`) — all files within the 150-line rule ✅

---

## Proven facts

1. The `plan` operation validates a `submission_export_v1` manifest and emits a
   deterministic, sorted JSON plan with per-file SHA-256 hashes and a deterministic
   aggregate hash over the sorted `path:sha256` preimage.
2. The `export` operation copies only the validated include set into a new empty
   output directory and writes `export_manifest.json`. It refuses non-empty directories.
3. The tool fails closed for every documented refusal category: absolute paths,
   drive-qualified paths, `..` traversal, empty paths, backslash ambiguity, duplicate
   paths, case-insensitive collisions, forbidden directory prefixes, credential
   filenames, gitlink entries, missing/untracked files, symlinks, wrong
   `source_commit`, missing Rule 50 paths, unsupported schema or role.
4. A `PENDING_HUMAN_APPROVAL` counterpart URL is preserved verbatim and is never
   treated as a valid cross-link.
5. No file body, matched secret value, absolute system path, or username is ever
   printed or retained in any report.
6. All new Python files are within the 150-line governance rule (max 98 lines).
7. The Ruff lint check passes with zero violations.
8. Hcommit golden vectors: 5/5.
9. Frozen manifest: 7/7.
10. Secret scan: no findings.

---

## Limitations

- Conformance kit (125/125) cannot be verified without the reprovisioned
  `external/copthief-league-protocol` submodule — this is a pre-existing
  environmental limitation, not a change introduced by this branch.
- The tool does not select file sets; final include manifests must be
  authored and reviewed by a human operator.
- Final role repository URLs, counterpart cross-links, GitHub creation, and
  `v1.0-submission` tags remain human-controlled and are not performed here.

---

## Confirmed booleans

| Assertion | Result |
|---|---|
| No production or frozen files modified | ✅ TRUE |
| No existing tests modified | ✅ TRUE |
| No external network, GitHub API, browser, peer, or gameplay operation performed | ✅ TRUE |
| No new dependency or lockfile change | ✅ TRUE |
| No final repository, remote, publication, or tag created | ✅ TRUE |
| No opponent contact, tunnel, email, or Gmail operation | ✅ TRUE |
