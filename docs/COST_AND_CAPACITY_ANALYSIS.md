# Cost and Capacity Analysis

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

**Internal engineering document. Not a vendor invoice, cost audit, or operational authorization.**

This document separates observed repository-derivable facts from unmeasured inputs, symbolic
formulas, and a measurement plan. No vendor prices are invented or copied from illustrative
examples elsewhere. All monetary figures are either `$0 observed` (from accepted scoped runs)
or labeled hypothetical.

---

## Reproduction command

Run from the repository root in a clean Git worktree:

```bash
uv run python tools/quality_assessment/measure.py --repo-root .
```

The tool reads only Git-tracked files via `git ls-files`. It emits deterministic JSON with sorted
keys and UTF-8 encoding. Omitting `--timestamp` makes repeated runs on the same commit produce
byte-identical output. The output is safe to commit; it contains no absolute paths, usernames,
credentials, nonces, or file contents.

---

## Scenario 1 — Observed accepted implementation

These facts apply to the scoped accepted offline evidence runs recorded in the project audits.
They are not universal or future-operation claims.

| Cost category | Observed value | Basis |
|---|---|---|
| External LLM API calls (runtime) | 0 observed | `pyproject.toml` declares no OpenAI or Anthropic runtime dependency; peer identity records `deterministic-python`; schema 1.1 artifacts record token totals as `0` |
| Input tokens (runtime) | 0 observed | No accepted artifact contains a non-zero token count |
| Output tokens (runtime) | 0 observed | No accepted artifact contains a non-zero token count |
| External LLM charge (scoped runs) | **$0 observed** | Zero API calls × any price = $0 for the accepted scoped runs |
| Claude / OpenAI / other LLM API | 0 observed runtime calls; 0 observed runtime tokens; **$0 observed** in accepted scoped runs | See row above |
| Student ChatGPT / Codex / Claude subscription | **Unavailable — excluded from runtime totals** | No attributable usage record was supplied; classified as development-tooling data, not runtime cost |
| Gmail API operations | 0 observed | No Gmail credentials or send operation performed; remains BLOCKED in `docs/OFFICIAL_SUBMISSION_READINESS.md` |
| Public tunnel / ngrok | 0 current | Historical public self-test evidence only; not a current claimed cost |
| Counted league operations | 0 | No counted game performed; BLOCKED pending bilateral authorization |
| GitHub repository and CI billing | Unmeasured — excluded from runtime totals | No GitHub billing record was supplied; public visibility does not prove account-level cost |

**Limitation:** `$0 observed` applies only to the accepted scoped runs listed above. Development
electricity, networking, hardware depreciation, human time, and future operations are not covered.

---

## Scenario 2 — Future optional LLM scenario

This scenario uses symbolic variables only. No vendor or model is selected for the project.
A dated official vendor price sheet and an explicitly selected model would be required before
converting any forecast into a current monetary claim.

### Formula

```
cost = (T_in / 1_000_000) * P_in + (T_out / 1_000_000) * P_out
```

Where:
- `T_in` — total input tokens per scoped run (integer; owner-supplied)
- `T_out` — total output tokens per scoped run (integer; owner-supplied)
- `P_in` — vendor price per 1 M input tokens in USD (owner-supplied from dated price sheet)
- `P_out` — vendor price per 1 M output tokens in USD (owner-supplied from dated price sheet)

### Worked hypothetical example (explicitly fictional prices)

Suppose — hypothetically and for illustration only — a future deployment uses:

- `T_in = 50_000` input tokens per game
- `T_out = 10_000` output tokens per game
- `P_in = $1.00` per 1 M tokens (fictional)
- `P_out = $3.00` per 1 M tokens (fictional)

Then:

```
cost = (50_000 / 1_000_000) * 1.00 + (10_000 / 1_000_000) * 3.00
     = 0.05 + 0.03
     = $0.08 per game  (hypothetical — not a real forecast)
```

These numbers are invented for structural illustration. Do not treat them as project
measurements or vendor quotes.

---

## Repository-derivable metrics (measured)

The following can be measured reproducibly from the Git-tracked repository. Run
`uv run python tools/quality_assessment/measure.py --repo-root .` to reproduce.

| Metric | Source |
|---|---|
| Tracked file count | `git ls-files \| wc -l` |
| Tracked byte total | sum of `stat().st_size` for all tracked files |
| File counts and byte totals by area (`src/`, `tests/`, `docs/`, etc.) | tool output `areas` key |
| Python source / test file counts | tool output `python` key |
| Nonblank / non-comment line counts | tool output `python` key |
| Largest tracked files by byte size | tool output `largest_files_by_bytes` key |
| Test function count | `def test_` occurrences in tracked test `.py` files |

---

## Measured local simulator runtime — Phase 4D10

This bounded run measures the **instrumented local simulator**, not MCP, a public endpoint, an
uncounted warm-up, or a counted league operation. The preregistered design is retained at
`data/quality/runtime_measurement_design.v1.json`; all raw samples and their arithmetic summary are
retained at `docs/audits/phase4d10_runtime_samples.json`.

### Scope and method

- Exact production `src/` tree: `3de0e42237792aa717d19d792ad18f44cced2be4`.
- This is immutable historical provenance, not a claim that later repository versions have the
  same tree. The retained design remains readable, while the measurement CLI refuses any new run
  unless its preregistered source identity equals the then-current `src` tree; the old design SHA
  and samples are never rewritten to make later code appear preregistered.
- Pairing: frozen `ScentTacticalPolice` versus `ScentEvasionThief`, default Appendix-F-compatible
  local config and disjoint fixed seed ranges.
- 20 warm-up games ran first and were not retained or counted as measurements.
- 200 timing games measured `perf_counter_ns` wall latency and `process_time_ns` CPU time without
  memory tracing.
- 30 separate games measured `tracemalloc` peak Python allocations; their distorted timings were
  discarded.
- Percentiles use the declared nearest-rank method. Result size is compact deterministic JSON for
  the local `GameResult`, not a schema 1.1 match artifact or full audit log.
- Environment: Linux x86_64, Python 3.13.12, 20 logical CPUs. No hostname, username, absolute path,
  credential, endpoint, nonce, or opponent data is retained.

### Observed values

| Metric | Mean | P50 | P95 | Maximum |
|---|---:|---:|---:|---:|
| Wall latency per local game | 20.337 ms | 16.509 ms | 36.509 ms | 51.659 ms |
| CPU time per local game | 20.203 ms | 16.395 ms | 36.382 ms | 51.143 ms |
| Peak Python allocations (`tracemalloc`, separate pass) | 0.0230 MiB | 0.0226 MiB | 0.0255 MiB | 0.0256 MiB |
| Compact local result size | 431.62 bytes | 432 bytes | 432 bytes | 432 bytes |

Observed sequential throughput was **49.171 local games/second** across the 200 timing samples.
All 200 games completed with zero illegal actions. The memory figure is not process RSS, total
interpreter memory, or hardware memory consumption.

### Bounded linear projections

These projections divide game count by the observed sequential throughput. They assume the same
machine, policies, config and workload, and do not claim parallel scaling.

| Local games | Estimated sequential wall time | Compact result bytes only |
|---:|---:|---:|
| 100 | 2.034 s | approximately 43.2 kB |
| 1,000 | 20.337 s | approximately 432 kB (0.412 MiB) |
| 10,000 | 203.372 s (3.390 min) | approximately 4.32 MB (4.116 MiB) |

The measured path imports no network client and made zero external API, tunnel, Gmail, or opponent
calls; public/network latency is therefore outside this result rather than silently reported as
zero latency. No vendor price or electricity cost was inferred from CPU time. Converting the CPU
measurement to energy still requires an operator-supplied hardware power measurement or declared
TDP proxy, and converting energy to money requires a dated tariff.

---

## Unmeasured inputs — formulas and collection plan

These quantities cannot be truthfully derived from the repository alone.

| Unmeasured item | Formula / symbol | Collection plan |
|---|---|---|
| Whole-process RSS | `M_rss` MB/game | Use an approved OS-level profiler; current evidence measures Python allocations only |
| Electricity per game | `E = T_cpu * W_tdp / 3_600_000` kWh (`T_cpu` in seconds, `W_tdp` in watts) | `T_cpu` is now measured; hardware power/TDP and tariff remain operator inputs |
| Artifact / result storage | `C_storage = S_GB * P_gb_mo * N_months` (S_GB = stored GB, P_gb_mo = price per GB per month, N_months = retention period) | Measure artifact directory size after matches; obtain host/cloud storage pricing |
| Public tunnel cost | `C_tunnel = N_hours * P_tunnel_hr` | Obtain vendor pricing; measure active tunnel hours |
| CI compute (GitHub Actions) | `C_ci = N_minutes * P_ci_min` | Obtain GitHub billing report; measure workflow minutes |
| Human operator time | `C_human = H * R` (H = hours, R = hourly rate) | Time-tracked separately by each operator |
| Counted league operation | `C_league = C_tunnel + C_gmail + C_human + C_llm + C_storage` (if applicable) | Requires each sub-component to be measured first |

---

## Operation-class distinctions

| Operation | Network | Counts | Cost scope |
|---|---|---|---|
| Local simulator experiment | None | No | Repository-derivable only |
| Local interoperability / system test | Loopback | No | Repository-derivable only |
| Historical public self-test | Public HTTPS (own peers) | No | Historical evidence; not a current cost claim |
| Real-team uncounted warm-up | Public opponent endpoints | No | Tunnel + human time; unmeasured |
| Counted league game | Public endpoints + Gmail | Yes | All categories; unmeasured without invoices |

---

## Capacity discussion (qualitative)

The current Gatekeeper and inbox limits are defined in `config/rate_limits.v1.json` and
documented in `docs/CONCURRENCY_AND_CAPACITY.md`. The exact formula is:

```
max_accepted_outbound = concurrent_max + queue_max
```

Per-queue inbound capacity follows the configured `queue_max` independently for each of the four
wire tools. Phase 4D10 now supplies sequential local-game throughput and latency for one fixed
policy/config pairing. Gatekeeper throughput, public MCP latency, process RSS, and parallel
multi-game scaling remain separate measurements and are not inferred from the local simulator run.

---

## Limitations summary

- No electricity invoice, cloud invoice, GitHub invoice, or vendor bill was supplied.
- Phase 4D10 wall/CPU latency and Python-allocation peaks are one-machine measurements, not
  universal performance guarantees or public-transport measurements.
- Absence of a bill is not proof that every underlying resource is universally free.
- The generic cost table in the Software Project Guidelines is an illustrative example; its
  sample numbers are not this project's measurements and were not copied here.
- `$0 observed` is a statement about accepted scoped offline runs only, not about development
  tooling, hardware, electricity, networking, or any future operation.
- All unmeasured items remain open and are listed with formulas and a collection plan above.
