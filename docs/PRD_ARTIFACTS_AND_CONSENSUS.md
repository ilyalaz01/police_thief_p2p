# PRD: Artifacts and Consensus

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Background and I/O

Artifacts preserve declaration, shared configuration, audit log, and final result. Inputs are
agreed terms, identities, game IDs, summaries/records, scores, and the explicitly selected
consensus scope. Outputs are schema 1.1 JSON files with official names and relevant canonical or
file hashes.

Requirements: exact filename grammar; byte-identical shared config; distinct pretty-file,
canonical-object, and consensus serialization domains; deterministic IDs/scores; mutual audit;
and symmetric final agreement. Constraints: schema/profile/scope are negotiated per match and
cannot be inferred from semantic JSON equality.

## Selection, evidence, and open decisions

Implemented builders in `interop/artifacts.py` use official schema 1.1 and the local
`reference_symmetric_outcome_without_tie` proposal. Evidence: artifact round-trip/mutation tests,
final-scope worked vector, local integration reports, and kit verification. See
[interop decisions](INTEROP_DECISIONS.md) rather than duplicating schemas.

Alternatives include the kit row with `tie`, raw-file agreement, and other schema versions. They
remain unselected pending explicit bilateral agreement. The repository worksheet is always
blocked and is not an agreement.

The current runtime produces one schema-1.1 sub-game result at a time. It does not yet orchestrate
the official fixed six-sub-game series or produce the full Appendix-B schema-1.2 shared file.
Those delivery domains remain explicit under `LGE-001`; they cannot be silently folded into the
pinned reference builders or their frozen consensus preimage.

Metrics: deterministic bytes/hashes for named domains; four expected artifact families; schema
parse; cross-links and consensus hash verified; zero unexpected/private fields in reports.
Scenarios include key reordering, whitespace/newline, Unicode escaping, optional-field mutation,
hash mismatch, missing/extra file, and divergent consensus scope.

Definition of Done: selected schema/scope explicitly approved, worked vector exchanged, official
terms bytes/hash agreed separately from optional extended profile, validators pass, artifacts
remain unchanged through packaging, and no readiness claim precedes human approval. Frozen and
negotiated boundaries cover all artifacts, serialization, profiles, hashes, and consensus.
