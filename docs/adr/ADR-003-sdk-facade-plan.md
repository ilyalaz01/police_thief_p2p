# ADR-003: Single SDK facade

Status: ACCEPTED

## Context

The package historically exposed core simulation types at its root while evaluation,
interoperability, artifacts, configuration, policy diagnostics, and CLI startup required imports
from internal modules. The Software Project Guidelines require one SDK entry point and prohibit
business logic in CLI/UI layers. Existing imports and frozen behavior still had to remain valid.

## Decision

`PoliceThiefSDK` is the documented single consumer entry point. It composes six stateless,
single-concern services:

- `domain`: types, rules, scent, turn model, simulation, and replay;
- `policies`: supported policy constructors and observation-only diagnostics;
- `evaluation`: game, batch, cross-play, and rendering operations;
- `artifacts`: commit/reveal, audit/replay, scoring, serialization scopes, and schema 1.1 builders;
- `transport`: profiles, protocol, endpoints, FastMCP transport, and typed peer startup;
- `configuration`: versioned startup metadata and sanitized secret scanning.

Service attributes are aliases to the existing classes/functions wherever possible, so signatures,
exceptions, bytes, outputs, and patch points do not acquire wrapper behavior. The root package
exports `PoliceThiefSDK` and `PeerLaunchRequest`. Legacy imports remain compatible for existing
tests/internal integrations, but new consumer documentation uses only the root SDK.

The CLI now performs argument parsing only. It creates `PeerLaunchRequest` and delegates once to
`PoliceThiefSDK.transport.launch_peer`. Config-mode matching, advertised-URL defaulting, profile
timeout reading, endpoint validation, and runtime invocation live behind that SDK boundary.

## Boundaries and consequences

The facade adds no game or interoperability rule and changes no existing business implementation.
It does not select Gatekeeper admission/rate/queue policy; that remains ADR-004/API-001. It does not
authorize public transport, real-team contact, gameplay, reporting, or counted operations.

Every project-authored Python file remains at most 150 counted lines. The service split avoids a
god object while retaining a single root entry. Any new public business operation must be added to
the appropriate service and the inventory regression test before a consumer uses it directly.

## Evidence

Phase 4D2B used a committed RED import contract, a complete callable inventory, identity checks
against the established functions/classes, a tracked-CLI import boundary, and the full project
suite. See [the audit](../audits/PHASE4D2B_SDK_FACADE.md).
