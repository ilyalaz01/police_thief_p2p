# Real-Team Warm-up Runbook

> **UNCOUNTED WARM-UP ONLY. Do not send league mail and do not reuse these commands for a counted match.**

## Exchange and lock before starting

Send the opponent: session label `UNCOUNTED`, game/config ID, our HTTPS `/mcp` URL, role,
Git commit, and an explicitly approved copy of the offline compatibility worksheet described in
`docs/REAL_TEAM_COMPATIBILITY_WORKSHEET.md` and templated at
`interop/templates/real_team_uncounted_compatibility_worksheet.json`. The repository template is
not an agreement or signature and must remain pending and blocked. Obtain the same items from
them. Never send a tunnel credential, token, nonce, private audit record, or hidden coordinate.

Both sides must explicitly agree to: 7x7; `row_col_zero_based`; Police `[0,0]`; Thief `[3,3]`;
quota 14; `ADJACENT_ONLY`; reference-v3 alternating with Thief first and sender-local steps;
survival/move limit 35; `subtractive_chebyshev_v1`; setting `New York`; minimum center 0.5;
connect/turn/audit/retry/retry-count settings; artifact `reference-v3-artifact-1.1`; object-style
`mutual_agreement`; consensus scope `reference_symmetric_outcome_without_tie` with status
`LOCAL_PROPOSAL_PENDING_EXPLICIT_BILATERAL_AGREEMENT`; mandatory Rule 47; both public MCP URLs;
both Git commits. This local scope does not silently add or remove a caller-supplied `tie`; it
excludes `tie` from its consensus preimage. If the opponent proposes any different scope,
explicitly refuse and reconcile it before play rather than assuming equivalence. Exchange the
exact official 14-term object and its canonical terms SHA-256 from
`official_reference_terms_lock`; both sides must explicitly approve both. If the optional stronger
extension is required for the pairing, separately exchange and approve the exact
`MatchProfile.bytes()` value and SHA-256 from `runtime_extended_profile_lock`. An unmodified
professor peer's omission of that extended lock is not approval and remains pending until
explicitly resolved. The raw fixture digest in `fixture_file_provenance` is local-only provenance,
not a bilateral hash, and must not be offered as one.

Each operator must supply that operator's own team's exact commit through that peer's
`--git-commit` argument and enable `--real-team`. An operator does not supply the opponent's
commit. The commit is opaque negotiation identity metadata and is preserved exactly; it is not
part of the shared profile, config bytes/hash, game UID, or final consensus scope. The gate refuses
an omitted or empty local/remote commit and `UNRESOLVED_SELF_TEST_NO_GIT_METADATA` before gameplay.
Do not infer a commit from the filesystem or alter the value supplied by either team.

## Provider-neutral startup

Expose each local listener with an operator-chosen HTTPS tunnel. Configure its origin as
`http://127.0.0.1:<PORT>` and preserve the `/mcp` path. Keep credentials outside the repository and
use non-debug tunnel logging. Verify the public URL ends exactly in `/mcp`.

Police:

```bash
.venv/bin/python -m police_thief_lab.peer_cli \
  --role police --profile interop/fixtures/phase4a5_reference_profile.json \
  --host 127.0.0.1 --port <LOCAL_PORT> \
  --advertised-url https://<OUR_PUBLIC_HOST>/mcp \
  --opponent-url https://<THEIR_PUBLIC_HOST>/mcp --public \
  --git-commit <OUR_EXACT_ADVERTISED_COMMIT> --real-team \
  --artifacts <SAFE_OUTPUT>/police --output <SAFE_OUTPUT>/police.json
```

Thief uses the identical command with `--role thief`, its own port/advertised URL, and the Police
opponent URL. The strategy and protocol configuration do not change for public transport.

Successful negotiation logs `event=negotiated`, the runtime extended profile
`identity.config_sha256`, role, phase, and redacted
opponent endpoint. It must not print opponent coordinates or nonces. Confirm both displayed hashes
are identical before accepting the first Thief turn when both peers advertise that optional
extended lock.

## Abort and verify

Before counted play, abort safely by stopping either peer and its tunnel. A warm-up transport loss
must become a deterministic technical failure; never resume it as a counted result. Preserve
redacted peer output and all four artifacts under an explicitly `UNCOUNTED` directory. Do not email
them.

Post-game checklist: both peers terminal; Thief acted first; all commitments verify after nonce
reveal; scent profile matches; Rule 46/47 semantics match; replay says verified; declaration,
config, log, and result re-read; config hashes match; object `mutual_agreement` hashes match the
agreed explicit scope; each schema 1.1 config artifact's `config_sha256` matches the canonical
official 14-term hash; no credentials/nonces appear in operator diagnostics. A counted match needs
a separate authorization and counted profile after a successful other-team warm-up.
