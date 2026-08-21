# Official Result Reporting

> **Nothing in this document sends anything.** The implemented slice builds and inspects the
> official mail offline. There is no credential, no OAuth flow, no network call, and no send path
> reachable from the CLI. A live send is a separate, explicitly authorized operation.

## What the official mail is

The settled league convention, verified against both teams' counted-series mails and recorded in
the pinned conformance kit (`SPEC.md` section 6.1):

- one e-mail per team per counted series, to the official league address;
- the mutually agreed result JSON as the **body** and the identical bytes as the **single named
  attachment**;
- declaration, config and log artifacts are **published in the role repositories and never
  mailed**; the result's repository links are how a grader reaches them.

Both teams send independently. Two reports that disagree are punished exactly like a score
mismatch, so the bytes must be the mutually agreed result, not a locally rebuilt one.

## What is implemented

`src/police_thief_lab/reporting/` provides three separated concerns:

- `config.py` — the operator boundary: league recipient, sending address, subject and attachment
  templates, one-accepted-send-per-game limit, retry attempts and backoff bounds. It is versioned
  (`reporting-1.0`), refuses an unknown schema, a missing value or a malformed address, and holds
  **no credential**. `config/reporting.example.json` is the blank template.
- `message.py` — deterministic message construction. The body and the attachment carry the
  identical result bytes. A result without a `mutual_agreement` block or without a `game_id` is
  refused before a message exists.
- `sender.py` — the send-only boundary. It requires an explicitly supplied transport; constructed
  without one, every `send` raises `ReportingNotAuthorizedError` and only `dry_run` works. Calls
  pass through the existing Gatekeeper. Retryable statuses (429, 500, 502, 503, 504) back off
  exponentially up to the configured ceiling; any other status fails immediately without a retry.
  One accepted send per `game_id` is enforced in the sender itself. The returned audit record
  carries the provider message id and never a token, header or body.

`python -m police_thief_lab.report_cli --result <result.json> --reporting-config <config.json>`
prints exactly what would be sent and optionally writes the base64url raw message for inspection.
It has no send switch by design.

## What is deliberately missing

- No OAuth client, consent flow, refresh token or credential file exists anywhere in the tree.
- No transport implementation talks to Google. The sender takes one as an argument, and the only
  transports in the repository are test doubles.
- Nothing has been sent. No mock result is operational evidence.

## Recorded gap, not silently resolved

The pinned kit (`SPEC.md` section 6.2) names three fields inside `final_result` as graded league
inputs: `games_played_including_this`, `first_meeting_between_groups` and
`diversity_reward_applied`. Our schema-1.1 result artifact does not carry them, and the warm-up
opponent did not raise it because the warm-up was uncounted. Adding them changes an artifact both
teams agreed on and touches the consensus scope, so it is a bilateral matter for `LGE-001` and the
next opponent agreement — not a local edit to slip in before a counted series.

## Operator steps, when a counted series is actually authorized

1. Copy `config/reporting.example.json` outside the repository and fill in the real league address
   and your sending address. Never commit the filled copy.
2. Build and inspect the message with `report_cli` and confirm the body equals the agreed result.
3. Only then, as a separate decision, set up a least-privilege send-only Gmail credential, supply a
   transport that performs `users.messages.send` with the built `raw` value, and record the audit
   result. That step is out of scope here and must not be started without explicit authorization.
