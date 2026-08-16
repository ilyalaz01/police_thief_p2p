# ADR-003: SDK facade plan

Status: PROPOSED

Context: package exports cover core simulation, while evaluation, interoperability, artifacts,
and CLI workflows require internal imports; the SDK requirement is therefore partial.

Proposal: characterize all public consumers, define a stable facade that delegates to existing
modules, and migrate consumers incrementally without moving business logic into CLI/UI. Options
are one class, cohesive sub-facades, or documented package functions. No option is selected.

Constraints: preserve imports, frozen hashes, protocol/strategy behavior, and error contracts.
Acceptance would require an approved interface inventory, characterization tests, migration plan,
and full validation. This ADR authorizes no implementation.

