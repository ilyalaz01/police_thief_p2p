# Phase 4D13B — Verified Six-Game Localhost Series

Status: **GREEN_LOCALHOST_ONLY**.

Classification: `UNCOUNTED_LOCALHOST_SELF_TEST`. This phase completes the offline technical
adapter under `LGE-001`; it does not establish real-team approval, public transport readiness,
reporting authorization, or a counted result.

## Proven execution

- The accepted single-game file boundary ran unchanged six times.
- Every sub-game used two independent child processes and two real `127.0.0.1` FastMCP endpoints:
  twelve peer processes in total.
- All twelve peer results reached `phase=verified`; both audit and deterministic replay passed for
  every peer.
- The frozen `ScentTacticalPolice` played Police and the existing deterministic Thief backend
  played Thief. Physics, scent, Hcommit, wire, retry/deadline, audit/replay, and schema-1.1 builders
  were not modified.
- A failed-peer characterization path refused the series and left no final output directory.
- Final publication used a staging directory and occurred only after all six rows were validated.

## Series result

The conspicuously synthetic groups were `alpha001` and `bravo002`. Roles alternated under the
already named local schedule profile. All six games ended in capture:

| Sub-game | Police | Thief | Score |
|---:|---|---|---|
| 1 | `alpha001` | `bravo002` | 20–5 |
| 2 | `bravo002` | `alpha001` | 20–5 |
| 3 | `alpha001` | `bravo002` | 20–5 |
| 4 | `bravo002` | `alpha001` | 20–5 |
| 5 | `alpha001` | `bravo002` | 20–5 |
| 6 | `bravo002` | `alpha001` | 20–5 |

The aggregate was 75–75 with three sub-game wins each. The adapter did not invent a two-point tie
interpretation: `winner_group` is null and settlement remains
`BLOCKED_PENDING_EXPLICIT_BILATERAL_TIE_POLICY`.

Canonical identifiers:

- game ID: `alpha001-vs-bravo002`;
- game UID: `c7cfa730-f46b-4fc9-a5e4-43ac61cf8c53`;
- mutual result SHA-256: `d5a8d71eb9d6a54421e53d8924a7479b999b7d187a780945c942dacdb59eac54`.

## Configuration and artifact domains

- Both temporary role trees contained byte-identical full Appendix-B schema-1.2 files at
  `config/game.json`, 911 UTF-8 bytes with SHA-256
  `358f29da2ce5777b0697a8f4201b00404a56732e5bb57e15b806122c92c9f734`.
- The full file remained separate from the flat fourteen terms used by the pinned schema-1.1
  builders and from extended `MatchProfile` bytes.
- Each role produced one declaration, six flat-term config artifacts, six verified logs, and one
  final result: 14 official artifacts per role.
- The two result files were byte-identical and confirmed the same mutual hash.
- The MIT conformance checker passed both 14-file directories and the cross-team join reported
  `ALL SETS AGREE`.
- The temporary run created 31 files total: 28 official artifacts, two full config files, and one
  sanitized evidence summary.

The runtime logs necessarily contained revealed audit nonces. They were used only inside bounded
temporary test directories, were not committed, and were deleted after extracting the value-free
summary. No live nonce body is retained in this report or its adjacent JSON.

## Validation

- Full suite: **449/449 passed**, no skips or xfails.
- Combined branch coverage: **91.09%**; required threshold 85%.
- Ruff over `src`, `tests`, and `tools`: zero errors.
- Hcommit golden vectors: 5/5.
- Pinned conformance kit: 125/125.
- Authoritative frozen manifest: 7/7 exact.
- Both artifact hygiene/conformance checks: pass; two-set join: pass.
- Every project-authored Python source/test file remains at or below 150 counted lines.
- Git-tracked snapshot secret scan: pass with zero findings.

## Boundaries and remaining blockers

The fixture repositories use `github.com/example`, endpoints use the reserved `.invalid` domain,
commits are explicit local-test strings, and matching approvals exercise code paths only. They are
not actual operator values or opponent consent.

Before another-team use, humans must still supply real identities/repositories/commits/endpoints
and explicitly agree on the full config bytes, role schedule, Rule 47, scent/barrier profile,
artifact schema/consensus scope, and tie settlement. Public URLs and transport require a separate
authorization. Gmail/OAuth, external contact, reporting, counted play, and final submission tags
were not started.

The smallest safe next offline step is `SUB-001`: integrate the accepted deterministic exporter,
build both role candidate trees, and run their independent gates without creating remotes or tags.
