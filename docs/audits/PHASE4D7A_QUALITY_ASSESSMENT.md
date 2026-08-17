# Phase 4D7A — Reproducible Quality, Cost, and ISO Assessment

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN — COST-001 and ISO-001 implemented; all gates pass.**

This phase does not claim ISO certification, production readiness, counted-game readiness,
external-team compatibility, or final-submission readiness. Gaps are recorded honestly below.

## Authority and design boundary

The implementation was derived from the Software Project Guidelines (items 10 and 12), then
checked against `RULES_AND_INTEROP_BASELINE.md`, `docs/INTEROP_DECISIONS.md`,
`docs/TODO.md` (COST-001, ISO-001), and `docs/GUIDELINES_COMPLIANCE_MATRIX.md`.

The cost analysis is bounded to the accepted scoped offline runs only. No vendor prices,
email accounts, Gmail operations, tunnel credentials, or league token totals were invented.
The ISO assessment is internal only; no certification body was engaged.

## TDD evidence

RED commit `6c65779` added all eight governance tests in
`tests/integration/test_governance/test_quality_assessment.py`. Collection failed because
`tools/quality_assessment` did not yet exist (`ModuleNotFoundError`).

GREEN commit `c142b4c` added:

- `tools/quality_assessment/__init__.py` — package init (4 counted lines);
- `tools/quality_assessment/measure.py` — stdlib-only measurement tool (141 counted lines);
- `docs/COST_AND_CAPACITY_ANALYSIS.md` — two-scenario cost analysis with `$0 observed`
  external LLM spend, a storage formula (`C_storage = S_GB * P_gb_mo * N_months`), and
  a symbolic future LLM formula using `T_in`, `T_out`, `P_in`, `P_out`;
- `docs/ISO_IEC_25010_ASSESSMENT.md` — internal eight-characteristic assessment with honest
  status, evidence, gap, and owner for each characteristic; research publication (`RES-001`)
  explicitly kept open.

## Measurement tool

```bash
uv run python tools/quality_assessment/measure.py --repo-root .
```

- Reads only Git-tracked files via `git ls-files -z`.
- Never traverses `.git`, caches, virtual environments, or untracked content.
- Produces deterministic JSON with sorted keys and UTF-8 encoding.
- Emits no absolute paths, usernames, credentials, nonces, or file contents.
- Returns a non-zero exit code with a clear message for non-Git directories.
- Omitting `--timestamp` makes repeated runs on the same commit byte-identical.

Output snapshot (tracked on this branch):

```
tracked_file_count: 233
tracked_byte_total: 1_064_600
python.source_file_count: 59
python.test_file_count: 70
python.source_nonblank_noncomment_lines: 4211
python.test_nonblank_noncomment_lines: 4517
test_function_count.count: 270 (method: counted_def_test_in_tracked_py_files)
```

## Validation commands and results

```
uv run pytest tests/integration/test_governance/test_quality_assessment.py -q
→ 8 passed

uv run pytest -q
→ 308 passed, 5 skipped, 0 failed (313 total = 305 original + 8 new)

uv run pytest --cov=src/police_thief_lab --cov-branch --cov-report=term-missing -q
→ 93.44% branch coverage, threshold 85%

uv run ruff check src tests tools/quality_assessment
→ All checks passed

uv run python tools/quality_assessment/measure.py --repo-root .
→ Valid deterministic JSON, exit 0

uv run python -m tools.offline_ops.cli quality-gate
→ exit 0; pytest pass, ruff pass, hcommit_vectors pass,
  frozen_manifest pass, conformance_kit pass, scan_secrets pass (zero findings)
```

Hcommit: 5/5 | Frozen manifest: 7/7 | Conformance: 125/125

## Acceptance results

| Check | Result |
|---|---|
| Focused quality-assessment tests | PASS — 8/8 |
| Full suite | PASS — 308 passed, 5 skipped, 0 failed |
| Branch coverage | PASS — 93.44%, threshold 85% |
| Ruff | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Frozen manifest | PASS — 7/7 exact |
| Conformance kit | PASS — 125/125 |
| Composed quality gate | PASS — exit 0, all sub-checks pass |
| Python 150-line gate (new files) | PASS — max 141 counted lines (`measure.py`) |
| Secret scan | PASS — zero findings |

**Note on full-suite count:** The base commit `091bc4985f` was validated at 305/305 on
Linux/CI. On this Windows environment the submodule `external/copthief-league-protocol` must
be initialized with `git submodule update --init --recursive` before the composed gate and
conformance checks pass. After initialization, all gates pass. Final count is
305 (original) + 8 (new) = 313 total, 308 pass, 5 skip (professor differential tests —
expected skip in a public clone), 0 fail.

## Changed paths

Owned paths only — no shared, frozen, or forbidden path was modified.

```
tools/quality_assessment/__init__.py          (new)
tools/quality_assessment/measure.py           (new)
docs/COST_AND_CAPACITY_ANALYSIS.md            (new)
docs/ISO_IEC_25010_ASSESSMENT.md              (new)
tests/integration/test_governance/test_quality_assessment.py  (new)
docs/audits/PHASE4D7A_QUALITY_ASSESSMENT.md   (new — this file)
docs/audits/phase4d7a_quality_assessment.json (new)
```

## Proven facts

- `tools/quality_assessment/measure.py` produces deterministic, byte-identical JSON output
  for repeated calls on the same commit when `--timestamp` is omitted.
- Only Git-tracked files appear in the output; `.git/`, `__pycache__`, and `.venv` are absent.
- All output paths are repository-relative POSIX strings with no absolute-root fragment.
- A non-Git directory causes a non-zero exit and a clear error message.
- `docs/COST_AND_CAPACITY_ANALYSIS.md` contains `$0 observed` external LLM spend, symbolic
  formula variables `T_in`, `T_out`, `P_in`, `P_out`, a storage formula
  `C_storage = S_GB * P_gb_mo * N_months`, and an unmeasured-inputs section with formulas and
  a collection plan for storage, tunnel, CI, human time, and counted-league scenarios.
- `docs/ISO_IEC_25010_ASSESSMENT.md` is labeled "Internal engineering assessment; not an ISO
  certification" and covers all eight ISO/IEC 25010 characteristics; research publication
  (`RES-001`) is explicitly kept open as a remaining gap.
- All new Python files are at or below 150 nonblank/non-comment lines.

## Limitations

- The cost analysis reports `$0 observed` for the accepted scoped offline runs only. It does
  not cover development tooling, electricity, hardware, networking, human time, or future
  operations.
- Student ChatGPT/Codex/Claude subscription usage is excluded from runtime totals; no
  attributable usage record was supplied.
- CPU time, RAM, public latency, and multi-game capacity are unmeasured; they are listed with
  formulas and a collection plan in `docs/COST_AND_CAPACITY_ANALYSIS.md`.
- No vendor or model is selected for the hypothetical future LLM scenario; symbolic variables
  and a clearly-labeled fictional example are used instead.
- The ISO assessment is internal. No external audit, certification body, or third-party review
  was performed.
- Live GUI, counted games, bilateral real-team compatibility, research publication, and final
  submission assembly remain open under `GUI-001`, `HUM-001`, `RES-001`, and `SUB-001`.

## Frozen and operational boundary

No game rule, scoring, strategy, `ScentTacticalPolice`, observation type, scent, Hcommit,
MatchProfile, wire, retry/deadline/duplicate behavior, runtime turn flow, artifact schema,
consensus scope, frozen file, or dependency declaration changed.

No peer, gameplay, public tunnel, public opponent endpoint, Gmail, external-team contact,
league reporting, warm-up, counted operation, submission repository, or tag was started.
