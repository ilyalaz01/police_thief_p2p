# ADR-006: Versioned configuration boundary

Status: PROPOSED

Context: `pyproject.toml` and package `__version__` both report 1.0.0, and profile/fixture schemas
carry versions, but there is no `config/`, `.env-example`, general versioned configuration loader,
rate-limit configuration, or runtime compatibility validator.

Proposal: inventory only truly configurable operational values; define typed/versioned schemas
outside frozen match/profile bytes; validate versions before side effects; keep secrets solely in
environment variables. Options include JSON dataclasses, TOML, or a narrow loader. None is chosen.

Constraints: do not migrate game constants fixed by higher authority, do not change existing
profile serialization/hashes/defaults, and do not add dependencies without separate approval.
Acceptance requires an accepted schema/version policy, migration/compatibility tests, secret
placeholders and documentation, and all frozen/interoperability gates.

