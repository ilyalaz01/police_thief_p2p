# Phase 4G — Official Result Reporting, Offline

Classification: **implementation complete, no send performed**. Authorized by the operator on 2026-08-21.
No credential exists, no OAuth flow exists, no transport contacts Google, and nothing was sent.

## What was built

`src/police_thief_lab/reporting/` separates three concerns and keeps each testable without a
network: the versioned operator configuration (`reporting-1.0`), deterministic message
construction, and the send-only boundary.

The message follows the settled league convention recorded in the pinned kit `SPEC.md` §6.1: the
mutually agreed result JSON is both the body and the single named attachment, and declaration,
config and log artifacts stay in the role repositories rather than the mail.

The sender is refused by construction. Without an explicitly supplied transport every `send`
raises `ReportingNotAuthorizedError`, and only `dry_run` is available. Calls that do happen go
through the existing Gatekeeper, retry 429/500/502/503/504 with exponential backoff bounded by
configuration, fail immediately on any other status, and enforce one accepted send per `game_id`.
The audit record carries the provider message id and never a token, header or body — a regression
asserts that a token returned by a transport cannot reach the summary.

`python -m police_thief_lab.report_cli` prints what would be sent and has no send switch.

## Evidence

`tests/integration/test_reporting/test_result_reporting.py` covers the identical body and
attachment bytes, the single-attachment shape, refusal of a result without `mutual_agreement`,
refusal to send without authorization, the one-send-per-game limit, backoff on retryable statuses,
no retry on a permanent status, configuration refusals, and credential redaction.

## Recorded gap, not resolved locally

Kit `SPEC.md` §6.2 names three fields inside `final_result` as graded league inputs:
`games_played_including_this`, `first_meeting_between_groups` and `diversity_reward_applied`. Our
schema-1.1 result artifact does not carry them. Adding them changes an artifact both teams agreed
on and touches the consensus preimage, so it is an `LGE-001` and next-opponent-agreement matter,
not a local edit before a counted series.

## The send path is complete

`credentials.py`, `http_client.py`, `gmail_transport.py` and `authorization.py` finish the chain
using only the standard library, so the single-dependency boundary is unchanged. The transport
exchanges the stored refresh token for a short-lived access token and posts the already-built raw
message to `users.messages.send`; any non-success status surfaces as a bare status code.
`mail_authorize_cli` performs the one-time consent for the `gmail.send` scope alone through a
loopback redirect and refuses to store anything if Google returns no refresh token.
`tests/integration/test_reporting/test_gmail_transport.py` covers the exchange order, the posted
body, every failure status, consent-URL scope, credential round-trip and redaction.

## What still blocks a counted report

Only operator actions: creating the Google OAuth client, granting the one-time consent, filling
the reporting configuration with the official league address, and deciding that a specific counted
game may be reported. The procedure is written out in `docs/OFFICIAL_RESULT_REPORTING.md`.
A Testing-mode consent screen expires the refresh token after seven days; publish it or re-run the
consent if a later send is refused with an invalid-grant status.
