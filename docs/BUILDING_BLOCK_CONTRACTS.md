# Production Building-Block Contracts

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

This catalogue documents the stable production blocks reachable through `PoliceThiefSDK`. It is
descriptive evidence, not a new source of game or interoperability rules. The authority hierarchy
in [`RULES_AND_INTEROP_BASELINE.md`](../RULES_AND_INTEROP_BASELINE.md) always wins.

## SDK facade

`PoliceThiefSDK` is a stateless composition root. Setup constructs six concern-specific services;
it performs no network, filesystem, gameplay, or authorization side effect. Consumers use the
facade while legacy module imports remain compatible.

| Block | Input | Output | Setup | Validation | Edge behavior |
|---|---|---|---|---|---|
| `DomainSDK` | Typed config, state, role, action and scent-profile values | Domain types, legal-action queries, simulation and replay results | Stateless aliases to frozen domain implementations | Frozen rules validate actions, positions, starts and terminal states | Illegal actions raise the established domain exception; no hidden truth crosses `Observation` |
| `PoliciesSDK` | Role-local `Observation`, seed and explicit policy parameters | Legal `Action`, belief distributions and explainable diagnostics | A fresh policy instance is constructed per evaluation/runtime use | Policies must accept only role-local evidence and the simulator revalidates actions | Empty beliefs, blocked cells and terminal observations retain their characterized behavior |
| `EvaluationSDK` | Configs, seeds, policy factories and optional local scenarios | Per-game results, batches, matrices, JSON and Markdown | Entirely local and deterministic for equal inputs | Factories must produce a `DecisionBackend`; simulator rules reject illegal output | Empty/low-sample aggregates expose their documented values; evaluation is never a counted game |
| `ArtifactsSDK` | Verified runtime summaries, identities, terms and explicit consensus values | Hashes, audit/replay results and schema 1.1 objects/files | Callers supply paths and already-negotiated metadata | Canonical, consensus and pretty-JSON scopes stay separate; professor differential tests pin builders | Caller-supplied `tie` is preserved but excluded from the accepted B0 consensus preimage |
| `TransportSDK` | `PeerLaunchRequest`, endpoints, profile, deadlines and Gatekeeper policy | Local server/client objects or terminal peer result | Process/network startup occurs only when the explicit launch operation is called | URL, profile, real-team Git provenance, bounded queue and deadline gates fail closed | A launch request grants no public, real-team, Gmail, warm-up or counted authorization |
| `ConfigurationSDK` | Versioned operational JSON path or configuration text for scanning | Validated immutable config or sanitized findings | No side effect before schema and mode validation | Unsupported schema/mode, unknown fields and credential-like assignments are rejected | Scanner findings retain metadata only, never the matched value |

## Presentation blocks

| Block | Input | Output | Setup | Validation | Edge behavior |
|---|---|---|---|---|---|
| Live view | One role-local view snapshot and loopback host/port | Atomic bounded JSON plus accessible HTML | Publisher path is operator supplied; HTTP server is loopback only | Strict allowlist rejects opponent truth, wire bodies, URLs, commits and nonces | Missing/malformed snapshots show a safe unavailable/error state |
| Replay view | Completed log and matching board configuration | Verified frames and HTML containing `Verified OK` only after verification | Offline file input; no peer or tunnel | Audit and deterministic replay must both pass | Malformed, unverified or mismatched logs never display a verified state |

## Frozen inline-docstring exception

The following files are protected by the authoritative seven-file SHA-256 manifest. Adding inline
docstrings would change their bytes and fail the required 7/7 gate. Each therefore uses this
**hash-preserving external contract**; the exception list is checked directly against the frozen
manifest and cannot silently grow.

| Frozen path | Input / Setup | Output | Validation / Edge behavior |
|---|---|---|---|
| `src/police_thief_lab/models.py` | Official typed values and negotiated setup | Immutable domain/config/state/observation values | Construction invariants remain pinned; `WorldState` never enters policy input |
| `src/police_thief_lab/rules.py` | Typed action, role, state and config | Legal actions, next positions, terminal predicates and official score | Illegal or out-of-bounds actions retain exact exceptions and frozen scoring |
| `src/police_thief_lab/scent.py` | Agreed scent profile and prior field | Initial/advanced scent field | Only verified profile names are accepted; MCP scent semantics remain unchanged |
| `src/police_thief_lab/turns.py` | Frozen state and alternating-turn context | Next role and terminal cadence | Reference-v3 Thief-first cadence remains exact |
| `src/police_thief_lab/simulator.py` | Config plus role-local decision backends | Deterministic state transitions and replay | Backend output is revalidated; physics and observation isolation remain frozen |
| `src/police_thief_lab/policies/tactical.py` | Police `Observation` and seed | Legal Police action | This is the frozen `ScentTacticalPolice` champion; no tuning or replacement occurs here |
| `src/police_thief_lab/interop/crypto.py` | JSON payload, nonce and reveal records | Canonical JSON, commitment and verification result | Hcommit 5/5 vectors pin encoding and mismatch reporting |

## Documentation inventory policy

The governance inventory parses every project-authored production module under `src/` and
`tools/`. Every editable module, class, function and method must have an inline docstring. Tests
remain executable specifications with descriptive test names; the seven exact frozen files use the
external contracts above. New exceptions are forbidden unless a higher-authority immutable byte
contract is added with its own regression evidence.
