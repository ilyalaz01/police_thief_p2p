# Phase 4D10 — Measured Local Cost and Capacity Evidence

Status: **GREEN**. `COST-001` is DONE for the applicable accepted runtime scope.

This phase measured one fixed local simulator workload. It did not measure or start MCP transport,
a public endpoint, an external-team warm-up, a counted game, Gmail, tunnelling, or league
reporting. It does not assign a vendor price, electricity tariff, hardware depreciation, or student
development-tool subscription cost.

## Authority and frozen boundary

The work follows the generic Software Project Guidelines cost/capacity requirement only where it
does not conflict with `RULES_AND_INTEROP_BASELINE.md`, `docs/INTEROP_DECISIONS.md`, the frozen
manifest, or human-gated operations. Production `src/`, the seven frozen files, `ScentTacticalPolice`,
Phase 1 physics, Hcommit, scent, MCP, retry/deadline, artifact, and consensus behavior were not
changed.

## RED → GREEN history

- `eb6dae0` preregistered the design and added nine acceptance tests. RED was retained as two
  collection errors because the runtime measurement modules did not exist.
- `0575847` added four stdlib-only measurement modules. Seven implementation-focused tests passed;
  the evidence acceptance test intentionally remained RED until a real retained run existed.
- `8018cdd` retained the measured samples and updated the living cost, PRD, PLAN, TODO, ISO,
  compliance, and readiness documents.

No retrospective timing values were inserted into the preregistered design.

## Preregistered design

- Scope: `LOCAL_SIMULATOR_EXPERIMENT`.
- Production source tree: `3de0e42237792aa717d19d792ad18f44cced2be4`.
- Pairing: frozen `ScentTacticalPolice` versus `ScentEvasionThief` on the default declared config.
- Warm-up: 20 unretained games using a disjoint seed range.
- Timing: 200 games without memory tracing.
- Memory: 30 separate `tracemalloc` games whose distorted timings were discarded.
- Percentiles: nearest rank.
- Design SHA-256: `55bedd12918cdc4a7bb7763a3a9ab71a758ce41956611a3efea82e0f55d9b65a`.
- Raw evidence SHA-256: `9c17d0874ca6ee2266ff855f755a63857042b400b217c18297134352e6188e7c`.

## Observed result

Environment retained without host identity: Linux x86_64, Python 3.13.12, 20 logical CPUs.

| Metric | Mean | P50 | P95 | Maximum |
|---|---:|---:|---:|---:|
| Wall latency | 20.337 ms | 16.509 ms | 36.509 ms | 51.659 ms |
| CPU time | 20.203 ms | 16.395 ms | 36.382 ms | 51.143 ms |
| Peak Python allocations | 0.0230 MiB | 0.0226 MiB | 0.0255 MiB | 0.0256 MiB |
| Compact local result | 431.62 bytes | 432 bytes | 432 bytes | 432 bytes |

Sequential throughput was 49.171 local games/second. All 200 timed games had zero illegal actions.
The retained samples independently reproduce every summary value through pure tests.

## Implementation and safety

- `runtime_models.py` provides pure records and nearest-rank arithmetic.
- `runtime_design.py` rejects stale source trees, unsupported policies/configs, and malformed
  sample counts.
- `runtime_probe.py` keeps warm-up, timing, and memory seed ranges separate.
- `runtime_cli.py` emits public-safe JSON, refuses overwrite/path escape, and records no hostname,
  username, absolute path, credential, endpoint, nonce, or file body.
- Timing samples exclude `tracemalloc` overhead. Memory is explicitly Python allocator peak, not
  process RSS.

## Validation

The final acceptance commands and exact totals are recorded in the machine-readable audit:

- focused contract and retained-sample recomputation: 9/9 passed;
- full suite: 343/343 passed, with no skips or xfails;
- combined statement/branch coverage: 92.5868% (85% threshold);
- Ruff: zero errors;
- Hcommit: 5/5;
- frozen manifest: 7/7 exact;
- conformance: 125/125;
- exact staged/public snapshot: zero secret findings using the same documented exclusion for the
  scanner's own synthetic fixtures as CI.

The composed local-root gate passed pytest, Ruff, Hcommit, frozen manifest, and conformance, then
correctly failed closed on eight ignored historical Phase 4B/tunnel evidence findings outside the
Git index. No matched value was printed or retained. This is not relabelled as a clean-root pass;
the exact staged/public snapshot was separately scanned and had zero findings. A clean-clone CI
run remains the final publication check.

Every new Python file remains below 150 counted lines; the maximum is 103 in `runtime_probe.py`.

## Proven facts

- The exact accepted `src/` tree was measured without modifying it.
- Warm-ups are executed but absent from retained samples.
- Timing and memory use disjoint fixed seed ranges.
- Raw samples reproduce their committed arithmetic exactly.
- The measured path performs zero network, external API, Gmail, tunnel, or opponent operations.
- Actual accepted runtime LLM calls/tokens remain zero; `$0 observed` retains its scoped meaning.

## Limitations

- This is one machine, one Python version, one fixed policy/config pairing, and sequential load.
- `tracemalloc` excludes interpreter/native/process RSS.
- Public MCP latency, parallel multi-game scaling, invoices, power draw, tariffs, and human time are
  not inferred.
- A linear projection is not a guarantee of future throughput.
- The result does not authorize or prove an external-team or counted operation.
