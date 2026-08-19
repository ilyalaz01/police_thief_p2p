# Phase 4D14E — Public Role Repository Publication

Status: **GREEN for official Rules 49 and 50; final submission tags and external operations remain
blocked**.

Classification: `PUBLIC_ROLE_REPOSITORY_ACCEPTANCE`.

## Decision

Accept the two public role repositories at the exact commits below. They preserve accepted shared
history and partner authorship, contain the approved reciprocal links and Rule 50 materials, keep
the conformance kit pinned, pass independent local repository/quality gates, and pass clean public
GitHub CI reruns.

| Role | Public repository | Public `main` | Counterpart | Public CI |
|---|---|---|---|---|
| Police | `https://github.com/ilyalaz01/police_thief_p2p-police` | `42c5367d690abda6b01c6aa91499491526123ed8` | Thief URL exact | [PASS](https://github.com/ilyalaz01/police_thief_p2p-police/actions/runs/32230351200) |
| Thief | `https://github.com/ilyalaz01/police_thief_p2p-thief` | `f279dc2c736df1b234f857de6e085e38fbdb73f1` | Police URL exact | [PASS](https://github.com/ilyalaz01/police_thief_p2p-thief/actions/runs/32230359324) |

Both candidates descend from accepted shared merge `cff96c44ee4a91f34f2fa6adbd2f83e3f1f9d0a3`.
The exact repository gates report 334 regular files, preserved history, the correct reciprocal
URL, pinned submodule, zero secret findings and no `v1.0-submission` tag. Candidate aggregate
SHA-256 values are `40288da6649bb12d54d3cf81aa64f11f6d630bf3b5a85e0ebfce7e036965cc67`
for Police and `1609bd2804a0fb43b620d7a5d3d72071b185ab97a811e33a3d41c5b6c3bd5e74`
for Thief.

## Independent validation

Each published candidate collected 343 tests and completed the full quality gate independently.
Both reached 91.09503616862061% combined statement/branch coverage and passed pytest, Ruff,
Hcommit 5/5, frozen manifest 7/7, conformance 125/125 and candidate secret scanning. The optional
match-artifact check was correctly skipped because no game was started.

The first clean public CI attempt in each repository failed only the Git governance test: the
branch history had been published, but the existing annotated `team-baseline-v1` tag had not. A
fresh public clone reproduced exactly one failure and four passes. The unchanged accepted tag
object `e8fea4afe22cb503503a2ce071b86a409c73db23` targeting
`96d3878ed1ac3776810284be7c23315ba3ad53e1` was then published non-forcibly to both repositories.
A second fresh public clone passed 5/5 governance tests, and both full GitHub CI reruns passed.
No branch commit or file byte changed during that correction.

## Remaining hard stops

- No annotated `v1.0-submission` tag exists; creating one in either repository requires separate
  explicit authorization.
- No Gmail/OAuth, opponent contact, tunnel, public game transport, warm-up, counted play,
  reporting, or Moodle submission was started or authorized.
- Actual team identities, endpoints, commits and bilateral Rule 47/profile/consensus decisions
  remain human/external inputs; nothing here converts a local proposal into agreement.
- The frozen Police champion, Phase 1 physics, Hcommit, scent, MCP, artifact, consensus, audit,
  replay and scoring semantics are unchanged.
