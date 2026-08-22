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

## The complete send path

`credentials.py`, `http_client.py`, `gmail_transport.py` and `authorization.py` complete the
chain with the Python standard library only — no third-party Google package is added, so the
dependency boundary is unchanged.

- `authorization.py` builds a consent URL that requests **only** `gmail.send`, catches the
  loopback redirect once, and exchanges the code for a refresh token. If Google returns no
  refresh token it fails loudly instead of storing a short-lived one.
- `credentials.py` holds exactly three operator values, refuses an empty or placeholder value,
  refuses a non-HTTPS endpoint, writes the file owner-readable where the OS allows it, and its
  `redacted()` summary never contains a secret.
- `gmail_transport.py` exchanges the refresh token for a short-lived access token and posts the
  already-built `raw` message to `users.messages.send`. Any non-success status surfaces as a bare
  status code, never a body.

## Operator procedure, once and then per counted game

### One time — create the send-only credential

1. Open <https://console.cloud.google.com/> and create a project (any name).
2. **APIs & Services → Library**, search **Gmail API**, press **Enable**.
3. **APIs & Services → OAuth consent screen**: choose **External**, fill the app name, your user
   support e-mail and developer e-mail, and save. Under **Audience / Test users** add the Gmail
   address you will send from.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**, application type
   **Desktop app**. Download the JSON it offers; that file is the `--client-file` below.
5. Run the one-time consent, from the repository root:

   ```bash
   uv run python -m police_thief_lab.mail_authorize_cli \
     --client-file /path/to/downloaded_client.json \
     --out ~/police-thief-secrets/gmail_credentials.json
   ```

   A browser opens. Google will warn that the app is unverified — that is expected for your own
   desktop client; choose **Advanced → Go to … (unsafe)** and then **Allow**. The command prints a
   redacted summary and writes the credential file.

**Consent-screen caveat:** while the consent screen stays in **Testing**, Google expires the
refresh token after seven days. Either publish the consent screen before relying on it, or
re-run the one-time step if the send later fails with an invalid-grant status.

### Per counted game

1. Fill your copy of `config/reporting.example.json` with the official league address and your
   sending address. Keep it outside the repository.
2. Inspect first — this never sends:

   ```bash
   uv run python -m police_thief_lab.report_cli \
     --result <artifacts>/result_<game_id>.json \
     --reporting-config ~/police-thief-secrets/reporting.json
   ```

3. Confirm the printed body size, recipient, subject and attachment name, and that the result is
   the one both teams agreed.
4. Send exactly once, for an authorized counted game only:

   ```bash
   uv run python -m police_thief_lab.report_cli \
     --result <artifacts>/result_<game_id>.json \
     --reporting-config ~/police-thief-secrets/reporting.json \
     --credentials ~/police-thief-secrets/gmail_credentials.json \
     --send --audit <evidence>/mail_<game_id>.json
   ```

   The sender enforces one accepted send per `game_id` inside a run. The audit record holds the
   provider message id and no credential.

## What is deliberately missing

- No credential, client file or refresh token exists anywhere in the repository, and none may be
  committed: `.gitignore` already excludes `credentials*.json`, `secrets*.json` and `.env*`.
- Nothing has been sent from this project. The code path is complete and tested against injected
  transports; a passing test is not operational evidence of a delivered mail.
- The first live send remains a separate operator decision for an authorized counted game.

## Recorded gap, not silently resolved

The pinned kit (`SPEC.md` section 6.2) names three fields inside `final_result` as graded league
inputs: `games_played_including_this`, `first_meeting_between_groups` and
`diversity_reward_applied`. Our schema-1.1 result artifact does not carry them, and the warm-up
opponent did not raise it because the warm-up was uncounted. Adding them changes an artifact both
teams agreed on and touches the consensus scope, so it is a bilateral matter for `LGE-001` and the
next opponent agreement — not a local edit to slip in before a counted series.
