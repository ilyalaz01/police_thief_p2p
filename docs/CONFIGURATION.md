# Operational Configuration

Operational configuration classifies a peer startup without changing game rules, negotiated
profiles, wire bytes, artifact bytes, strategy, or authorization. The accepted design is
[ADR-006](adr/ADR-006-versioned-configuration-boundary.md).

## Supported schema

The loader accepts one strict JSON object. Missing and unknown fields fail closed.

```json
{
  "schema_version": "1.0",
  "package_version": "1.0.0",
  "operation_mode": "self_test",
  "secret_source": "environment_only",
  "retain_sensitive_values": false
}
```

The tracked example is `config/operational.self-test.v1.json`. Supported modes are `offline`,
`self_test`, and `real_team`. `counted` is intentionally unsupported. A `real_team` value only
selects stricter local preflight behavior; it is not permission to contact another team, start a
tunnel, report to the league, or play a game.

## CLI selection

Pass the file explicitly:

```bash
uv run python -m police_thief_lab.peer_cli \
  --operational-config config/operational.self-test.v1.json \
  <existing peer arguments>
```

Or set the path in the process environment:

```bash
POLICE_THIEF_CONFIG_PATH=config/operational.self-test.v1.json \
  uv run python -m police_thief_lab.peer_cli <existing peer arguments>
```

The CLI validates configuration before reading the match profile or creating peer/runtime
objects. Self-test invocation requires `self_test`; `--real-team` requires `real_team`. Omitting
the operational config preserves the existing CLI behavior.

## Rate-limit policy

## Declaration input

`config/declaration.example.json` is a blank-valued template for the operator declaration file
consumed by `--declaration`. It supplies the members, repository URLs, MCP identities, model and
hardware fields that the schema-1.1 declaration artifact requires and that the peer cannot invent.

Copy it outside the repository, fill in real values, and pass the copy. The loader refuses a file
with any missing or unfilled value, so an incomplete declaration fails before gameplay instead of
producing an artifact full of nulls. Without the flag the peer keeps its historical self-test
identity, which is correct for local and public self-tests and insufficient for a counted game.
A filled copy contains real member names and must never be committed.

`config/rate_limits.v1.json` is a separate strict schema for external-call capacity. It currently
defines the `fastmcp` minute/hour limits, worker concurrency, bounded queue depth, and bounded
monitoring retention. Override only its path, not individual values, with:

```bash
POLICE_THIEF_RATE_LIMITS_PATH=config/rate_limits.v1.json
```

Malformed, missing, unknown, incompatible, boolean, zero, and negative fields fail closed. The
same queue depth bounds inbound peer mailboxes. The rate file cannot contain URLs, credentials,
game/profile fields, retry/deadline values, or authorization. Frozen retries remain profile-owned.

## Secrets and `.env-example`

The current offline and self-test workflows require no credentials. `.env-example` therefore
contains only optional operational/rate config paths. The application does not automatically load
`.env`; an operator may create a locally ignored `.env` for their own shell tooling.

If a future approved workflow needs a secret, the value must come from the process environment,
must never be added to JSON or `.env-example`, and must never be retained in reports. The scanner
in `police_thief_lab.configuration` returns sanitized `path:line:category` findings and never the
matching value.

## Compatibility and authority boundary

The schema version and installed package version must match exactly. No automatic migration or
best-effort fallback is allowed. Operational configuration cannot contain or override fixed game
constants, the 14 canonical terms, MatchProfile fields, endpoints, retry/deadline semantics,
Rule 47, consensus scope, or any frozen policy. Those remain governed by the repository's
[source-authority hierarchy](../RULES_AND_INTEROP_BASELINE.md).

## Validation

```bash
uv run pytest -q tests/integration/test_configuration/test_configuration.py --no-cov
uv run pytest -q tests/integration/test_configuration/test_gatekeeper.py \
  tests/integration/test_configuration/test_gatekeeper_config.py --no-cov
uv run pytest
uv run ruff check src tests
```
