# External-Agent Continuation Handoff

**Purpose:** This document transfers operational context to a new coding agent that will guide
the student through the final Police–Thief P2P project work. Read this file completely before
suggesting a change, contacting a team, starting a tunnel, or running a game.

**Handoff snapshot:** 2026-08-19. Shared repository `main` was clean at
`6f9d96f730beb5a38d3afd9896db263f9a8225cd` when this handoff was written.

## 1. Working relationship and operating rules

The user is a student and project owner. Explain conclusions in **plain Russian** unless they ask
otherwise. Write source code, repository documentation, prompts for coding agents, and messages
to other technical teams in **English** unless the user asks for Hebrew or Russian.

The user wants a practical guide: do not assume they know Git, MCP, tunnels, hashes, or the course
terminology. Lead with what is true, what is safe to do next, and what the user needs to provide.
Be concise, concrete, and evidence-based.

These boundaries are mandatory:

- Do not invent a game rule, a team identity, a hardware declaration, a Git commit, a hash, an
  agreement, or an opponent response.
- Do not silently resolve a negotiated interoperability difference. Record it, explain it, and
  stop that operation until both teams explicitly agree.
- Keep the frozen competitive Police policy `ScentTacticalPolice` unchanged during integration.
  Do not begin new AI/search/ML/strategy work merely because it sounds useful.
- Do not start Gmail/OAuth, send email, contact an opponent, start a public tunnel, or begin a
  counted game unless the user explicitly selects that exact operation. The user may personally
  contact classmates through WhatsApp without asking the agent; this restriction is about the
  agent acting externally on its own.
- Never describe a local simulator, localhost interoperability test, public self-test, uncounted
  real-team warm-up, or counted league operation as if it were any other category.
- For every terminal-agent report, validate the cited evidence first; then explain in Russian:
  facts, assumptions, accept/reject decision, remaining blockers, and the smallest next prompt
  with tests and a hard stop.
- Preserve unrelated user/partner work. Check `git status`, branch, and recent history before
  editing. Use small, reviewable commits and normal non-force pushes/PRs.

## 2. Source authority: read this before interpreting a rule

The controlling hierarchy is in
[`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md), section 1:

1. `sources/police_thief_p2p.pdf` — official book v3.0.0; Appendix E/F mandatory/fixed values.
2. Pinned professor reference implementation in `external/Game-P2P-Cop-Chase/` for executable
   behavior where the PDF is not byte-level specific. Never modify it.
3. Pinned MIT conformance kit in `external/copthief-league-protocol/` for interoperability bytes
   and vectors. Never treat it as a competing specification.
4. Explicit bilateral WhatsApp/team agreements for negotiated matters only.
5. `sources/SOFTWARE_PROJECT_GUIDELINES.md` for architecture/quality guidance.
6. Research reports are ideas, not rules.

`NotebookLM` is not an independent authority. A chat proposal is not an agreement. An omitted
field is not approval.

## 3. Read order for a new agent

Do not try to infer the project from source code first. Read these in order:

1. [`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md) — authoritative normalized
   game/interoperability baseline, including Rule 47 and frozen boundaries.
2. [`sources/police_thief_p2p.pdf`](../sources/police_thief_p2p.pdf) — official project book.
   Use the PDF skill/tooling if a page-level claim matters.
3. [`docs/INTEROP_DECISIONS.md`](INTEROP_DECISIONS.md) — verified choices and unresolved
   compatibility questions.
4. [`docs/OFFICIAL_SUBMISSION_READINESS.md`](OFFICIAL_SUBMISSION_READINESS.md) — current delivery
   ledger; it distinguishes technical proof from real-team/counted readiness.
5. [`docs/REAL_TEAM_WARMUP_RUNBOOK.md`](REAL_TEAM_WARMUP_RUNBOOK.md) and
   [`docs/REAL_TEAM_COMPATIBILITY_WORKSHEET.md`](REAL_TEAM_COMPATIBILITY_WORKSHEET.md) — the real
   opponent procedure and meaning of the worksheet.
6. [`interop/templates/real_team_uncounted_compatibility_worksheet.json`](../interop/templates/real_team_uncounted_compatibility_worksheet.json)
   — immutable blank template. Never populate it in place; make a separate untracked operator copy
   only after the user authorizes a specific warm-up.
7. [`docs/PRD.md`](PRD.md), [`docs/PLAN.md`](PLAN.md), [`docs/TODO.md`](TODO.md), and
   [`docs/GUIDELINES_COMPLIANCE_MATRIX.md`](GUIDELINES_COMPLIANCE_MATRIX.md) — architecture,
   roadmap, and honest guideline status.
8. [`README.md`](../README.md), [`docs/SDK.md`](SDK.md), and
   [`docs/BUILDING_BLOCK_CONTRACTS.md`](BUILDING_BLOCK_CONTRACTS.md) — supported public surfaces.
9. Evidence reports listed in section 6 below.

The earlier user-provided `NEW_CHAT_PROJECT_ORCHESTRATOR_HANDOFF.md` was located outside this
repository (`C:\\Users\\ilyal\\Downloads\\...`) and is not currently tracked here. If it is
available in the new agent's environment, read it as historical context; this repository and the
authority hierarchy above remain controlling.

## 4. Directory map

| Location | Meaning | Handling |
|---|---|---|
| `src/police_thief_lab/` | Project implementation: game, policies, interop runtime, SDK, league helpers, GUI/replay | Edit only through scoped tasks with regressions. |
| `tests/` | Unit/integration/regression tests; `tests/offline_ops/` includes explicitly synthetic scanner fixtures | Preserve test meaning; do not weaken tests to make a change pass. |
| `interop/` | Profiles, golden vectors, protocol artifacts, compatibility template and sanitized retained logs | The source of most byte-level interoperability facts. |
| `external/Game-P2P-Cop-Chase/` | Pinned professor source | Read-only/frozen. |
| `external/copthief-league-protocol/` | MIT conformance-kit Git submodule | Read-only dependency; initialize recursively after a fresh clone. |
| `docs/` | PRDs, roadmap, runbooks, release/governance evidence and audits | Update when an accepted change materially alters a claim. |
| `reports/` | Historical Phase 4A–4C evidence | Read as evidence; do not rewrite history. |
| `sources/` | Official PDF, Software Project Guidelines, archived league discussion | Read-only project sources. |
| `submission/` | Role-repository templates/export boundary | Do not use it to overwrite public role repos blindly. |
| `config/` | Operational/rate-limit configuration examples | Not the full negotiated per-match configuration. |

## 5. Architecture in plain terms

The program is a deterministic Police–Thief game. Police and Thief are separate processes; neither
may access the other's hidden position. They exchange messages through FastMCP HTTP at `/mcp`.
The Thief moves first; each side observes only legal information, seals actions using Hcommit,
and later audits/replays the game.

Important fixed/verified behavior:

- Frozen Police policy: `ScentTacticalPolice`.
- Deterministic Thief default: `LookaheadEvasionThief`, adopted 2026-08-21 through the Phase 4E
  controlled experiment and explicit operator acceptance; `--thief-policy` overrides it.
- Reference-v3 Hcommit, scent, MCP/retry, audit/replay, and schema-1.1 artifact behavior have
  regression coverage. See `docs/INTEROP_DECISIONS.md`.
- **Rule 47 is mandatory:** a Thief with no legal move is captured, even though the professor
  reference does not fully implement it.
- Barrier placement for the reference profile is `ADJACENT_ONLY`; a different opponent mode is a
  negotiated incompatibility, not a local change to slip in.
- The CLI entry is `python -m police_thief_lab.peer_cli`. Its `--real-team` mode refuses an empty,
  placeholder, or missing local/peer `--git-commit` before gameplay.

Three different configuration/hash domains must never be conflated:

1. Official Appendix-B full shared `config/game.json` for a six-sub-game series.
2. Professor-compatible canonical 14 terms used on the reference wire/schema-1.1 config artifact.
3. Extended local `MatchProfile.bytes()` runtime lock.

The detailed domains and hashes are in the worksheet and in
`reports/PHASE4C_ENTRY_GATE_B1_PROFILE_HASH_DOMAINS.md`. In particular, the fixture file digest is
local provenance only; it is **not** a negotiated game configuration hash.

## 6. What is already proven (do not redo it casually)

Read the referenced report before changing the relevant domain.

| Capability | Evidence | Status |
|---|---|---|
| Deterministic game core, role-legal observations, audit/replay, artifact builders | `reports/PHASE4A_LOCAL_INTEGRATION.md`, `reports/PHASE4A5_REFERENCE_CROSSPLAY.md` | Proven locally/reference-compatible. |
| Public HTTPS FastMCP traversal for one self-to-self game | `reports/PHASE4B3_PUBLIC_PREFLIGHT.md` | Proven as an **uncounted public self-test**, not with another team. Two tunnels, MCP preflight, audit/replay, artifacts passed. |
| Real-team exact Git commit gate | `reports/PHASE4C_ENTRY_GATE_A.md` | Proven offline. Local and peer commits must be supplied by their own operators. |
| Consensus scope reconciliation and worksheet domains | `reports/PHASE4C_ENTRY_GATE_B0_CONSENSUS.md`, `reports/PHASE4C_ENTRY_GATE_B1_PROFILE_HASH_DOMAINS.md` | Local proposal only; bilateral approval still required. |
| Software-guideline recovery, SDK/config/Gatekeeper/GUI/replay/research/quality work | `docs/GUIDELINES_COMPLIANCE_MATRIX.md` and matching `docs/audits/` reports | Completed where marked `COMPLIANT`; do not fabricate historical development provenance. |
| Six sub-game coordinator and artifacts | `docs/audits/PHASE4D13B_LOCALHOST_SERIES.md` | Proven as `UNCOUNTED_LOCALHOST_SELF_TEST` only. |
| Separate public Police/Thief repositories (Rules 49/50) | `docs/audits/PHASE4D14E_ROLE_PUBLICATION.md` | Published and CI-green at the audited commits below. |

Last audited public role repository commits (verify remote state again before relying on them):

- Police: `https://github.com/ilyalaz01/police_thief_p2p-police` at
  `42c5367d690abda6b01c6aa91499491526123ed8`.
- Thief: `https://github.com/ilyalaz01/police_thief_p2p-thief` at
  `f279dc2c736df1b234f857de6e085e38fbdb73f1`.

The shared repository intentionally contains no real team IDs, members, hardware, live endpoints,
or opponent data. This is correct: those values must be operator supplied.

## 7. What is not done / not claimed

- Superseded on 2026-08-21: three uncounted real-team games against `vm__fabi` completed in
  both roles with verified audit, replay and artifacts. See
  `docs/audits/PHASE4F_REAL_TEAM_UNCOUNTED_WARMUP.md`. Still uncounted and unreported.
- No bilateral worksheet has been populated/approved.
- No stable live real-team endpoints or real identity/declaration inputs have been supplied.
- No counted match, league result, Gmail/OAuth implementation, or Gmail send has occurred.
- The full six-game adapter is proven on localhost. There is no accepted claim that a public
  real-team six-game coordinator has been run end-to-end. Do not call one public sub-game a full
  six-game rehearsal.
- `v1.0-submission` tags are deliberately absent; creating them requires a separate user decision
  after final review.
- A full-series aggregate tie still requires an explicit bilateral settlement policy. Never award
  a tie implicitly.

These are evidence gaps, not reasons to rewrite the frozen game core.

## 8. Real-team uncounted warm-up: safe procedure

The intended workflow has two levels:

1. **Public uncounted preflight / one sub-game.** Proves that two real teams' processes can reach
   each other, negotiate, play, audit, replay, and create artifacts. It is useful and must be
   labelled uncounted; it is not a counted or full-series claim.
2. **Full six-sub-game uncounted rehearsal.** Needed before treating the operational process as
   ready for a counted series. It requires full declaration data, a pairing-specific shared config,
   role schedule, per-game commits, and a resolved tie policy. Do not promise it is automatic until
   the actual public orchestration path has been verified.

Before level 1, obtain a written response from one designated operator of the opponent team. Ask
them to have their technical agent compare the named files; do not ask humans to hand-copy hashes.

Minimum required before a real-team one-game warm-up:

- session label `UNCOUNTED`; no lecturer email/reporting;
- both teams' official group ID/name, role for this game, role repository URL, and exact commit of
  the checkout that will actually run;
- explicit acceptance or an explicit difference for Rule 47, Hcommit/wire, turn order, scent,
  barrier mode, artifact schema, consensus/tie treatment, and hashes in the worksheet;
- a separately filled operator copy of the worksheet plus written approvals. The repository
  template remains blank and blocked;
- two live public credential-free `https://.../mcp` endpoints. URLs are not discovered
  automatically: each team starts its own server and tunnel, exchanges its own URL, and passes the
  other team's URL as `--opponent-url`.

Needed additionally before a full six-game rehearsal/counted work: member names, both role repo
URLs, both role endpoints/topology, CPU/RAM/GPU declaration, model declaration, agreed token cap,
six game/role/commit rows, full Appendix-B config bytes/hash, role schedule, and tie settlement.

Never request or retain tunnel credentials, API keys, tokens, nonces, hidden coordinates, serial
numbers, private logs, or real opponent data in Git.

### The practical public run order

After the user explicitly authorizes a specific warm-up and both teams supplied an approved
worksheet:

1. Re-validate actual Git commit values with `git rev-parse HEAD` in each running checkout. Do not
   use a remembered commit if the checkout changed.
2. Create a new, local untracked output directory labelled `UNCOUNTED` for this pairing/time.
3. Start both role-appropriate local FastMCP listeners.
4. Start one HTTPS tunnel per active listener. The public URL must end in `/mcp`. Keep secrets out
   of the terminal capture. The historical cloudflared 421 issue was solved with documented
   `--http-host-header` origin configuration; preflight the actual endpoint instead of assuming a
   tunnel is healthy.
5. Verify both public endpoints perform real MCP `initialize` and `list-tools` before starting a
   game. A bare HTTP GET response is not an MCP preflight.
6. Start the two peer commands concurrently: each uses its own URL as `--advertised-url`, the
   other URL as `--opponent-url`, `--public`, `--real-team`, and its own exact `--git-commit`.
7. If one peer/tunnel dies, record a deterministic technical failure. Do not resume or relabel it
   as a counted result.
8. On success verify: both terminal results; audit/replay; matching configuration hash; expected
   schema-1.1 artifacts; mutual consensus hash under the expressly agreed scope; no secrets/nonces
   in retained diagnostics.
9. Retain only redacted evidence and summaries. Do not commit live URLs, nonces, tokens, or an
   opponent's private data.

The exact current CLI shape is documented in `docs/REAL_TEAM_WARMUP_RUNBOOK.md`. Use it rather
than reconstructing a command from memory.

## 9. Interpreting the compatibility worksheet

The worksheet is an **offline operator checklist**, not a wire artifact, not a magic signature,
and not an official form issued by the professor. Its job is to make real disagreements visible
before play. Make a copy only after authorization; retain written approval alongside it.

Key facts to explain to the user:

- `group_id`: exact official eight-character code, no spaces; get it from course registration,
  not from a GitHub username.
- `group_name`: readable team name.
- `members`: registered student names; required for full official declaration, not the first
  connection test.
- `repository_urls`: evidence of which code is being used; they do not connect the peers.
- `git_commit`: exact version that executes; obtain with `git rev-parse HEAD`; each operator
  supplies their own team's commit, not the other team's.
- `hardware`: CPU/RAM/GPU of the machine actually running that team; full declaration only.
- `HTTPS /mcp URL`: live address created by that team's tunnel at start time; it is necessary for
  connectivity and does not appear by itself.
- `Rule 47`: if the Thief has no legal move, capture occurs. Mandatory, no opt-out.
- `consensus scope`: a separately agreed list of result fields that both sides hash after play.
  The local proposal is `reference_symmetric_outcome_without_tie`; the caller-supplied `tie` stays
  in a result row but is excluded from that particular consensus preimage. It is not universally
  approved just because local tests passed.

## 10. Quality checks and Git discipline

On a normal full shared checkout:

```powershell
git submodule update --init --recursive
uv sync --locked
uv run pytest
uv run ruff check src tests tools
uv run python external/copthief-league-protocol/verify_vectors.py
```

Check the current repository README and relevant audit/runbook before adding any more expensive
or special-purpose check. A clean working tree and green tests do not authorize an external
operation.

Before reviewing an agent's claimed phase result, require the exact commands, test counts,
coverage, changed paths, commit SHA, and retained evidence paths. Verify the changes against the
phase acceptance criteria rather than accepting a narrative.

## 11. Recommended immediate next action

Do not start a public game yet. The useful immediate human task is to send the team's
`UNCOUNTED_WARMUP_REQUEST_V1` message below to a prospective opponent. Replace only the marked
operator-supplied values; do not invent them.

```text
Hi! We would like to run an UNCOUNTED Police–Thief P2P warm-up with your team.

Purpose: verify public connectivity, protocol compatibility, audit/replay, and artifacts.
This is not a league result: no lecturer email, Gmail, or counted reporting will occur.

Please forward this technical block to the operator/agent responsible for your implementation.

UNCOUNTED_WARMUP_REQUEST_V1

OUR TEAM
group_id: <OUR OFFICIAL 8-CHARACTER ID>
group_name: <OUR GROUP NAME>
members: <REGISTERED MEMBER NAMES>
police_repository: https://github.com/ilyalaz01/police_thief_p2p-police
planned_police_commit: 42c5367d690abda6b01c6aa91499491526123ed8
thief_repository: https://github.com/ilyalaz01/police_thief_p2p-thief
planned_thief_commit: f279dc2c736df1b234f857de6e085e38fbdb73f1
runtime_decision_model: deterministic-python (no external LLM API during gameplay)
live_role_for_first_game: TO_BE_AGREED
live_https_mcp_url: PROVIDED_AT_SESSION_START

PLEASE REPLY WITH
group_id:
group_name:
members:
police_repository:
police_commit:
thief_repository:
thief_commit:
runtime_model:
endpoint_topology: SINGLE_URL or SEPARATE_POLICE_AND_THIEF_URLS
preferred_role_for_first_game: POLICE or THIEF
available_time: include timezone
live_https_mcp_url: provide at session start; it must end in /mcp

Please compare your implementation with our reference profile, worksheet, and consensus vector:
https://github.com/ilyalaz01/police_thief_p2p/blob/6f9d96f730beb5a38d3afd9896db263f9a8225cd/interop/fixtures/phase4a5_reference_profile.json
https://github.com/ilyalaz01/police_thief_p2p/blob/6f9d96f730beb5a38d3afd9896db263f9a8225cd/interop/templates/real_team_uncounted_compatibility_worksheet.json
https://github.com/ilyalaz01/police_thief_p2p/blob/6f9d96f730beb5a38d3afd9896db263f9a8225cd/interop/fixtures/final_consensus_scope_worked_vector.json

For each item answer ACCEPT or DIFFERENCE with details:
- reference-v3 Hcommit and MCP wire;
- Thief-first alternating turns;
- subtractive_chebyshev_v1 scent;
- ADJACENT_ONLY barriers;
- mandatory Rule 47 (boxed-in Thief is captured);
- schema 1.1 artifacts and object mutual_agreement;
- consensus scope reference_symmetric_outcome_without_tie;
- tie stays in the result row but is excluded from that consensus preimage;
- canonical 14-term hash:
  b97de3f6bb3e3aaed0c3f2e6ab2eee05d65aa1e7853e009ef448c42058c340c0;
- consensus worked-vector hash:
  e57d51d77fa31327be5e106b57d26342f38269b75845303349bda488f6ce2989.

Do not silently approximate a difference. Do not send credentials, tunnel tokens, nonces, hidden
coordinates, private logs, or serial numbers.

Finish with exactly one status:
READY_FOR_UNCOUNTED_PREFLIGHT
or
DIFFERENCES_REQUIRE_RECONCILIATION
```

When the user pastes the opponent's response, the next agent should:

1. Parse it into facts, omissions, and proposed differences.
2. Reject missing group/commit/approval fields; never fill them with placeholders.
3. Compare every declared protocol/profile/consensus item with the authority files.
4. Explain the result to the user in Russian.
5. If and only if the user explicitly authorizes the uncounted warm-up, create a separate local
   worksheet copy and supply exact redacted commands/checklist for the two operators.
6. After the run, validate artifacts/audit/replay and classify the result honestly.

## 12. How to be useful to this user

The user benefits from a calm guide who turns a confusing engineering process into a short
checklist. Do not dump raw jargon without saying what it means. At the same time, do not hide a
blocker: say whether it is technical, a missing human value, an unagreed rule, or an external
authorization.

Preferred final-report structure for every material operation:

1. **Result:** accepted/rejected/not yet authorized.
2. **Proven:** short evidence-based bullets.
3. **Not proven:** clearly labelled assumptions/gaps.
4. **Blockers:** the exact missing input or decision.
5. **Next smallest action:** one concrete step, tests, and hard stop.

This handoff does not authorize Gmail, public transport, opponent contact, counted play, tags, or
any weakening of the frozen interoperability baseline.
