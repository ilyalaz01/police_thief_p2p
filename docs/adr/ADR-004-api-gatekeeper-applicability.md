# ADR-004: API gatekeeper applicability

Status: PROPOSED

Context: `McpPeerClient` already centralizes FastMCP retries and monotonic deadlines.
`PeerInboxes` already use thread-safe queues. Rate limiting, bounded queue depth, backpressure,
draining, and call monitoring are not implemented.

Proposal: first decide whether peer game traffic, offline validator subprocesses, or future
third-party APIs fall under one gatekeeper. Evaluate a transport-specific admission layer versus
a generic facade. No architecture is selected.

Any change must preserve frozen retry count/interval, deadline, identical-redelivery,
duplicate/equivocation, future-window, and stale-frame behavior. Overflow cannot silently alter
turn order or extend deadlines. Acceptance requires load/race/failure tests, observable sanitized
metrics, bounded configuration, an approved ADR revision, and all interoperability gates.

