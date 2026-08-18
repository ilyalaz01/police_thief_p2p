# Submission Export Contract

Status: `TOOLING_INTEGRATED_PENDING_HUMAN_MANIFEST_AND_APPROVAL`

This document defines the scope, manifest schema, path/security policy,
operation semantics, and reproducible commands for the offline deterministic
submission exporter in `tools/submission_export/`.

---

## Official rules supported

**Rule 49** requires two separate GitHub repositories — one for Police and one for Thief —
with cross-links in both READMEs and both groups' four repository links in the submitted JSON.

**Rule 50** requires at minimum `README.md`, a `config/` directory, PRD, PLAN, and TODO in
each repository.

This tooling validates that a human-authored explicit manifest selects at least those files
and that every selected file is real, tracked, and free of security/privacy violations.

**This tooling does not:**
- choose which files go into either role repository;
- assign URLs or cross-links;
- create remotes, push repositories, or apply tags;
- approve any content for final submission;
- perform any external network, peer, Gmail, tunnel, or gameplay operation.

All of those actions remain human-controlled and are blocked until explicit authorization.

---

## Manifest schema

The exporter accepts exactly one JSON manifest file matching `submission_export_v1`:

```json
{
  "schema": "submission_export_v1",
  "role": "police",
  "source_commit": "<full 40-character hex SHA of current HEAD>",
  "include": [
    "README.md",
    "config/operational.self-test.v1.json",
    "docs/PLAN.md",
    "docs/PRD.md",
    "docs/TODO.md"
  ],
  "required_paths": ["README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"],
  "counterpart_repository_url": "PENDING_HUMAN_APPROVAL"
}
```

Field semantics:

| Field | Type | Requirement |
|---|---|---|
| `schema` | string | Must be exactly `"submission_export_v1"` |
| `role` | string | Must be `"police"` or `"thief"` |
| `source_commit` | string | Exact 40-character hex SHA; must equal current `HEAD` at run time |
| `include` | array of string | Explicit sorted POSIX paths; never inferred |
| `required_paths` | array of string | Paths the manifest author declares required; all must be in `include` |
| `counterpart_repository_url` | string | May be `"PENDING_HUMAN_APPROVAL"` during offline preparation |

The tool sorts `include` internally; input ordering does not affect plan output.

---

## Deterministic hashing preimage

The per-file hash is `SHA-256(file bytes)` as a lowercase hex digest.

The aggregate manifest hash is computed as:

```
SHA-256( SORT_BY_PATH( concat( "<path>:<sha256>\n" for each file ) ) )
```

This preimage is deterministic: given the same file set and bytes, the aggregate hash is
always identical regardless of input ordering, platform, or run time.

---

## Path and security policy

The exporter **fails closed** for:

| Category | Examples |
|---|---|
| Absolute or drive-qualified | `/etc/passwd`, `C:file.txt` |
| `..` traversal component | `../private/file` |
| Empty path or backslash | `""`, `docs\PRD.md` |
| Duplicate paths | Same path listed twice |
| Case-insensitive collision | `README.md` and `readme.md` in the same set |
| Forbidden directory prefixes | `.git/`, `.agents/`, `.codex/`, `sources/`, `reports/`, `tmp/`, `temp/`, `artifacts/`, `logs/` |
| Credential filenames | `*.pem`, `*.key`, `id_rsa*`, `.env`, `*tunnel*.yml`, etc. |
| Missing or untracked files | Paths not present in the git index as regular files |
| Gitlink entries | Submodule entries (mode 160000) |
| Symlinks | Files tracked as symlinks (mode 120000) or resolved symlinks on disk |
| Wrong `source_commit` | Manifest SHA does not equal current `HEAD` |
| Missing Rule 50 paths | No `README.md`, no `config/` file, no `docs/PRD.md`, `docs/PLAN.md`, or `docs/TODO.md` |
| Output path escape | Destination path resolves outside the output root |
| Unsupported schema or role | Any value other than `submission_export_v1` or `police`/`thief` |

Error messages report the **category and safe relative path only** — never a file body,
matched secret value, absolute system path, or username.

---

## Plan vs export

### `plan`

Validates the manifest and emits a deterministic JSON plan without copying files.
The plan includes:

- `schema`: `"submission_export_plan_v1"`
- `role`, `source_commit`, `counterpart_repository_url` (verbatim from manifest)
- `files`: sorted list of `{"path": "...", "sha256": "..."}` entries
- `aggregate_hash`: deterministic SHA-256 over the sorted preimage

Running `plan` twice on the same input produces byte-identical JSON.

### `export`

Runs `plan` first. If all checks pass, copies each file from the repository root into an
empty output directory, preserving the POSIX path structure, then writes
`export_manifest.json` in the output root.

**The exporter refuses a non-empty output directory.** It never overwrites existing files.

---

## Reproducible `uv run` commands

Generate and review a plan (no files copied):

```bash
uv run python -m tools.submission_export.cli \
  plan path/to/police_manifest.json
```

Export the validated file set to an empty directory:

```bash
uv run python -m tools.submission_export.cli \
  export path/to/police_manifest.json /path/to/empty/output/
```

Run the integration tests for this tooling only:

```bash
uv run pytest -q tests/integration/test_submission_export --no-cov
```

---

## What remains human-controlled

The following actions require explicit human review and authorization **after** this tooling
produces a reviewed plan:

1. **Authoring the explicit include manifests** — no file set is inferred or selected here.
2. **Reviewing every path and hash** in the plan before running export.
3. **Creating the two role repositories** on GitHub.
4. **Choosing the exact counterpart repository URLs** and replacing `PENDING_HUMAN_APPROVAL`.
5. **Adding cross-links** in both role READMEs (Rule 49 is not satisfied by a placeholder).
6. **Running independent role quality gates** (pytest, Ruff, Hcommit 5/5, frozen 7/7,
   conformance 125/125, secret/link/license scans) in each candidate checkout.
7. **Pushing content and creating `v1.0-submission` tags** only after exact-content approval.
8. **Restoring the pinned conformance submodule** (`external/copthief-league-protocol`)
   separately before each role gate; the exporter refuses gitlink entries.

No step in this tooling performs or authorizes any of the above.
