# ADR-004: FastMCP API Gatekeeper

Status: ACCEPTED

## Context and applicability

The only external API client in tracked production code is FastMCP: tool discovery and four-tool
peer calls. Offline validators are local subprocesses, not APIs. There is no database, cloud, LLM,
email, or league-reporting client in production code. Any future external client must be added to
this inventory and routed through the SDK Gatekeeper before use.

`McpPeerClient` already owned higher-authority retry count/interval, monotonic deadline, and
identical-redelivery semantics. `PeerInboxes` were thread-safe but unbounded. Generic guideline
controls therefore had to be added without relocating or redefining those frozen semantics.

## Decision

All outbound FastMCP attempts, including `discover_tools`, pass through one process-wide
`ApiGatekeeper`. It provides:

- a versioned, file-loaded minute/hour policy for the `fastmcp` service;
- a bounded FIFO waiting queue and explicit `GatekeeperBackpressure` when that queue is full;
- configured worker concurrency and rate admission before every attempt;
- automatic FIFO draining plus an explicit bounded `drain` operation;
- bounded monitoring containing only operation label, outcome, duration, and exception type;
- aggregate queue/in-flight/success/failure/rate-wait/high-watermark status with no payload data.

The tracked policy is `config/rate_limits.v1.json`; an operator may override its path with
`POLICE_THIEF_RATE_LIMITS_PATH`. Missing, malformed, incompatible, unknown, or nonpositive fields
fail closed. Values are never embedded as fallback constants in the Gatekeeper.

Inbound `PeerInboxes` use the same configured maximum depth. FastMCP handlers perform blocking
`put`, providing FIFO backpressure without dropping, reordering, or inventing a wire response.
Queue status exposes counts only and never inspects messages.

## Higher-authority retry boundary

The Gatekeeper admits and monitors every original attempt, including retries, but does not create
additional retries. `McpPeerClient` retains the frozen retry count, interval, deadline check,
deep-copied identical payload, attempt timing, and exhaustion error. The rate policy is deliberately
high enough not to delay valid reference-profile traffic; lower operator values are explicit policy
choices and cannot extend the caller's existing transport rules.

This exception to the generic example is required by the source-authority hierarchy: moving retry
ownership into a generic layer would risk changing negotiated behavior. The result still has no
external API attempt that bypasses admission, rate enforcement, and monitoring.

## Consequences and evidence

The Gatekeeper is reachable through `PoliceThiefSDK.transport`. It does not authorize a network
operation and does not add a new external service. Lifecycle/race analysis beyond this bounded API
queue remains CON-001; release aggregation remains RE-001.

Phase 4D2C acceptance is recorded in
[the audit](../audits/PHASE4D2C_API_GATEKEEPER.md): committed RED evidence, deterministic FIFO/rate/
backpressure/drain/failure tests, 187/187 full tests, all frozen interoperability gates, and no
public or external-team operation.
