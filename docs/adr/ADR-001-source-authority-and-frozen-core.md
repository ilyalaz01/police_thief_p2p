# ADR-001: Source authority and frozen core

Status: ACCEPTED

Context: generic engineering guidance can conflict with mandatory game rules or byte contracts.

Decision: use, in order, Official PDF v3 Appendix E/F; pinned professor reference; conformance
kit; explicit WhatsApp agreements; Software Project Guidelines; research reports. Freeze existing
game/interoperability semantics, the champion, and seven manifest hashes unless a separately
authorized higher-authority change is reviewed.

Consequences: generic guidelines cannot justify semantic refactoring. Conflicts fail closed and
are documented/negotiated. Evidence: `RULES_AND_INTEROP_BASELINE.md`, `CONTRIBUTING.md`, and
`tests/test_frozen_manifest.py`.

