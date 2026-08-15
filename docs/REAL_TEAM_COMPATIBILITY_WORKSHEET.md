# Real-Team Compatibility Worksheet

This is an **offline operator worksheet**, not an agreement, signature, protocol artifact, wire
message, or approval. The immutable template is
`interop/templates/real_team_uncounted_compatibility_worksheet.json` and is deliberately
`BLOCKED_PENDING_HUMAN_INPUT`.

No authoritative compatibility-sheet format exists in the pinned professor reference or
conformance kit. The kit does define a promoted two-field pairing declaration for the wire
handshake (`sub_game_number` and `role`) and its playbook gives a prose first-contact outline.
Neither is a general compatibility worksheet, so this template does not copy, replace, extend,
sign, or transmit either one.

The template keeps three hash domains separate. `fixture_file_provenance` is the raw 717-byte
fixture and is `LOCAL_ONLY_NOT_NEGOTIATED`; it is never a bilateral config/profile hash.
`runtime_extended_profile_lock` is derived only through `MatchProfile.bytes()` and records the
772-byte value advertised as `identity.config_bytes_hex` plus `identity.config_sha256`. It is an
optional stronger extension, and professor omission is not implicit approval.
`official_reference_terms_lock` is the 14-key `MatchProfile.reference_terms()` object serialized
through the existing `canonical_json`; this 284-byte domain supplies the schema 1.1 config
artifact hash. Team identity, repository, exact Git commit, role, public `/mcp` endpoint,
approvals, and evidence are empty. Transport and operator data remain outside every profile and
terms lock.

Rule 47 is mandatory and has no disable choice. The local consensus proposal is
`reference_symmetric_outcome_without_tie`, status
`LOCAL_PROPOSAL_PENDING_EXPLICIT_BILATERAL_AGREEMENT`, with its exact B0 vector linked in the
template. Missing responses and any different scope remain blocking.

Operators must separately approve the exact 14 terms, their exact canonical hash, and—if used—the
stronger extended profile bytes/hash. No approval in one domain implies approval in another.

Do not populate the repository template. If later authorized, operators may work from a separate
copy. A populated copy is ready only after every required bilateral field and decision is
explicitly completed and accepted; names or typed text are not cryptographic signatures. The
template itself always remains pending and blocked.
