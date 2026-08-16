# Police-Thief SDK

`PoliceThiefSDK` is the documented single entry point for project business operations. Import it
from the package root:

```python
from police_thief_lab import PoliceThiefSDK

sdk = PoliceThiefSDK()
```

The facade is stateless. It delegates to the already-tested implementations, preserving their
signatures, exceptions, deterministic outputs, and byte contracts.

## Services

| Service | Responsibility |
|---|---|
| `sdk.domain` | Domain types, rules, scent, turn model, simulator, replay |
| `sdk.policies` | Police/Thief policy constructors and observation-only diagnostics |
| `sdk.evaluation` | Single games, batches, cross-play, JSON and Markdown rendering |
| `sdk.artifacts` | Commit/reveal, audit/replay, scores, hashes, schema 1.1 artifacts |
| `sdk.transport` | Match profiles, protocol types, Gatekeeper, endpoints, FastMCP and peer launch |
| `sdk.configuration` | Versioned operational config and sanitized secret scanning |

## Local deterministic example

```python
from police_thief_lab import PoliceThiefSDK

sdk = PoliceThiefSDK()
result = sdk.evaluation.run_game(
    sdk.domain.GameConfig(),
    seed=7,
    police_factory=sdk.policies.ScentTacticalPolice,
    thief_factory=sdk.policies.RandomLegalThief,
)
print(result.terminal_reason, result.police_score, result.thief_score)
```

This example is a local simulator operation. It is not an interoperability test, public transport
test, uncounted warm-up, or counted league operation.

## Typed peer delegation

The CLI constructs `PeerLaunchRequest` and calls `sdk.transport.launch_peer(request)`. Direct SDK
users can do the same, but the request itself grants no authorization. Existing real-team gates,
Rule 47, profile agreement, Git provenance, and explicit human approvals remain mandatory.

```python
from pathlib import Path

from police_thief_lab import PeerLaunchRequest, PoliceThiefSDK

request = PeerLaunchRequest(
    role="police",
    profile=Path("interop/fixtures/phase4a_local_profile.json"),
    host="127.0.0.1",
    port=8801,
    opponent_url="http://127.0.0.1:8802/mcp",
    artifacts=Path("local-artifacts"),
    output=Path("local-result.json"),
)
# Execute only inside an explicitly authorized operation:
# PoliceThiefSDK().transport.launch_peer(request)
```

The commented call is intentionally not a copy-paste authorization. Consult the operational
runbook before any process, network, tunnel, opponent, or league activity.

## Compatibility policy

Legacy module imports remain available to avoid breaking validated tests and integrations. New
consumer code should use the root facade. New business operations must be exposed through one
service and added to `tests/test_sdk_contract.py`; CLI/UI code must continue to contain only input
handling and SDK delegation.
