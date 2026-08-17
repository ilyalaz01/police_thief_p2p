# Release Engineering and Offline Operations

Operator manual for the `tools/offline_ops` CLI implementing
`RELEASE_ENGINEERING_WORKSTREAM.md`. This subsystem provides reproducible
local verification, fail-closed release checks, safe validation of
completed match artifacts, and deterministic operator packages. It
**composes** the project's existing validators (pytest, Ruff, the Hcommit
golden vectors, the frozen production-file manifest, and the MIT-licensed
conformance kit) rather than reinterpreting game, wire, or artifact
semantics. It is network-free and independent of strategy development and
live match operations; it never touches `src/police_thief_lab/**`.

## Setup

Requirements: the same as the rest of the project — Python 3.11+, Git, and
`uv`. No additional dependency is introduced by this subsystem.

```bash
git clone --recurse-submodules https://github.com/ilyalaz01/police_thief_p2p.git
cd police_thief_p2p
uv sync
```

If the repository was already cloned without `--recurse-submodules`, run
`git submodule update --init --recursive` once — the conformance kit at
`external/copthief-league-protocol` is required by `quality-gate` and by
`validate-match`/`package-match`.

## Commands

All commands are one Python entry point, invoked as a module so no
separate console-script installation is required:

```bash
uv run python -m tools.offline_ops.cli <command> [arguments]
```

The CLI is built on `argparse`, `pathlib`, and `subprocess` argument
arrays only. It never constructs a shell command string and never
performs network I/O.

### `quality-gate`

```bash
uv run python -m tools.offline_ops.cli quality-gate [--match-path PATH] [--timeout SECONDS]
```

Composes, without reimplementing:

| Check ID | What it runs |
| --- | --- |
| `pytest` | `uv run pytest` (full suite, configured branch coverage) |
| `ruff` | `uv run ruff check src tests` |
| `hcommit_vectors` | the Hcommit golden-vector test in `tests/integration/test_interop/test_phase4a_crypto_protocol.py` |
| `frozen_manifest` | the frozen seven-file hash test in `tests/integration/test_governance/test_frozen_manifest.py` |
| `conformance_kit` | `external/copthief-league-protocol/verify_vectors.py` |
| `match_artifact` | `validate-match` on `--match-path`, or `SKIPPED` if omitted |
| `scan_secrets` | this tool's own scanner over the repository, excluding `tests/offline_ops` (see [Security limits](#security-limits)) |

`--timeout` (default 600s) bounds every composed subprocess check. A
missing, skipped, timed-out, or unrunnable required validator is reported
as `UNAVAILABLE`, never as a silent `PASS`.

### `validate-match PATH`

```bash
uv run python -m tools.offline_ops.cli validate-match PATH
```

Validates one schema 1.1 four-artifact-family directory (`declaration_`,
`config_`, `log_`, `result_`). Two checks run in sequence:

1. `artifact_hygiene` — this tool's own fail-closed filesystem pass:
   rejects missing directories, symlinks, path-escaping entries,
   unrecognized/unexpected files (including nested directories), oversized
   files, an oversized total, and too many files. See
   [Security limits](#security-limits) for the exact caps.
2. `artifact_conformance` — only runs if hygiene passed. Composes the
   existing MIT-licensed
   `external/copthief-league-protocol/tools/check_artifacts.py` checker
   (schema/key/id/uid/consistency checks per the book's App. E/F rules).
   **Never reimplemented.**

An unsafe directory is never handed to the third-party checker: if
hygiene fails, `artifact_conformance` is reported `SKIPPED`.

### `package-match PATH --output PATH`

```bash
uv run python -m tools.offline_ops.cli package-match PATH --output OUTPUT_PATH
```

Runs `validate-match` first. If it passes, atomically creates `OUTPUT_PATH`
containing exactly:

- the validated artifact files, byte-for-byte unchanged;
- `package_manifest.json` — a redacted JSON manifest;
- `package_report.md` — an equivalent redacted Markdown report.

The manifest/report contain only filenames, byte lengths, SHA-256 values,
check identifiers, statuses, durations, and exit codes — **never** file
contents, identity blocks, audit records, commit values, MCP URLs, or
nonce values. Terminal-audit nonces that legitimately appear inside a
validated `log_*.json` artifact remain only in that unchanged file; they
are never copied into the generated manifest or report.

`OUTPUT_PATH` is never overwritten: if it already exists, the command
fails closed (exit 7) without touching it. The package is built in a
uniquely-named staging directory next to `OUTPUT_PATH` and renamed into
place only once every file is written; a failure at any point removes the
staging directory and leaves `OUTPUT_PATH` untouched.

### `scan-secrets PATH`

```bash
uv run python -m tools.offline_ops.cli scan-secrets PATH
```

Recursively scans `PATH` (pruning `.git`, `.venv`, cache directories, and
the pinned `external` submodule) and fails closed on:

- private keys, AWS/GitHub/Slack-style tokens, JWTs, `Authorization`
  headers, generic `key`/`token`/`password` assignments;
- tunnel URLs (`*.ngrok.io`, `*.trycloudflare.com`, `*.loca.lt`, …) and
  tunnel configuration filenames;
- cache/temp files (`*.pyc`, `*.tmp`, `.DS_Store`, …);
- symlinks and path-escaping entries;
- a `"nonce"` key inside a `.json` file that is neither a canonical
  artifact filename nor under `interop/` (this project's own sanctioned
  golden-vector/fixture location).

Findings are reported by category and filename only; a matched value is
never printed, retained, or written to any report.

## Output format

Every command renders one sanitized JSON report to stdout:

```json
{
  "command": "quality-gate",
  "exit_code": 0,
  "checks": [
    {
      "check_id": "ruff",
      "status": "pass",
      "explanation": "ruff passed",
      "duration_seconds": 0.11,
      "exit_code": 0
    }
  ]
}
```

`status` is one of `pass`, `fail`, `skipped`, `unavailable`. Every report
renders from the same typed result model
(`tools/offline_ops/models.py`) — raw subprocess stdout/stderr is never
captured into a report. `package-match`'s manifest/report additionally
carry a `files` list (see [`package-match`](#package-match-path---output-path)).

## Exit codes and recovery

| Exit code | Meaning | Recovery |
| --- | --- | --- |
| 0 | Every requested required check passed. | Nothing to do. |
| 2 | Invalid invocation or configuration. | Check the command/arguments; run `--help`. |
| 3 | One or more quality checks failed. | Read the failing check's `check_id` and re-run that validator directly (e.g. `uv run pytest`, `uv run ruff check src tests`) for full output. |
| 4 | The secret or privacy scan failed. | Inspect the flagged file(s) locally (the report never contains the matched value); remove or rotate the credential, then re-run. |
| 5 | Match directory or package validation failed. | Re-run `validate-match PATH` directly; fix the flagged hygiene or conformance issue and retry. |
| 6 | A requested required validator or dependency is unavailable. | Confirm `uv` is on `PATH`, the conformance-kit submodule is initialized, and no check exceeded `--timeout`. |
| 7 | A report or package output could not be written safely. | Choose a new `--output` path (an existing path is never overwritten) or resolve the underlying filesystem error. |

## Security limits

- **No network I/O.** Every check is a local subprocess or a local
  filesystem scan.
- **No repository secrets are used or required**, locally or in CI.
- **Fail-closed on missing dependencies.** A validator that cannot run is
  `UNAVAILABLE`, never a silent pass.
- **Filesystem caps** (`tools/offline_ops/match_artifacts/hygiene.py`):
  10,000,000 bytes per artifact file, 50,000,000 bytes total, 500 files
  per match directory.
- **Scan scope.** `scan-secrets` prunes `.git`, `.venv`/`venv`, Python/tool
  caches, and the pinned `external` submodule (an independently-versioned,
  third-party MIT-licensed kit outside this workstream's authority).
  `quality-gate`'s own repository-wide scan additionally excludes
  `tests/offline_ops` — this tool's own tests necessarily contain
  synthetic secret-like fixtures to exercise the scanner; a direct
  `scan-secrets` invocation is unaffected and still scans exactly the path
  it is given.
- **Redaction is structural, not best-effort.** Reports are built from a
  typed result model that never stores raw subprocess output or file
  bodies, so there is no sensitive text to accidentally include.
- **Module boundary.** This workstream creates or modifies only
  `.github/workflows/**`, `tools/offline_ops/**`, `tests/offline_ops/**`,
  `docs/RELEASE_ENGINEERING.md`, `scripts/offline_ops/**`, and
  `interop/fixtures/offline_ops/**`. It never modifies game rules,
  strategy, the wire protocol, cryptography, or the conformance-kit
  submodule's contents.

## Continuous integration

`.github/workflows/quality-gate.yml` is a thin wrapper: checkout (with
submodules) → `uv sync --locked` → `uv run python -m tools.offline_ops.cli
quality-gate`. It is the same code path as the local command above, not a
second implementation. The workflow uses read-only repository contents
permission, pins `actions/checkout` and `astral-sh/setup-uv` to a specific
commit SHA (with the corresponding version as a comment) and pins the `uv`
and Python versions explicitly, uses no repository secrets, performs no
peer/tunnel/mail/league/gameplay operation, and uploads no match artifact
or private report. Checkout retains full history and tags (`fetch-depth: 0`)
so the [Git governance contract](GIT_RELEASE_GOVERNANCE.md) can verify real
merge lineage, contributor attribution, and annotated tags; credentials are
still never persisted.

A CI failure on `pytest` that does not reproduce locally on your platform
most likely reflects a genuine environment difference (for example, text
encoding defaults) rather than this workstream; `quality-gate` reports
each composed check independently so the failing one is always named.
