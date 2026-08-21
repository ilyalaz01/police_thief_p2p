"""One-time send-only Gmail authorization; run it once, then never again."""

from __future__ import annotations

import argparse
import json
import webbrowser
from pathlib import Path

from .sdk import PoliceThiefSDK

DEFAULT_PORT = 8765


def build_parser() -> argparse.ArgumentParser:
    """Build the documented authorization parser without any side effect."""
    parser = argparse.ArgumentParser(
        description="This command performs the one-time send-only Gmail consent.",
        epilog=(
            "It requests only the gmail.send scope, stores the refresh token in the file you "
            "name, and sends no mail. Keep that file outside the repository."
        ),
    )
    parser.add_argument(
        "--client-file",
        type=Path,
        required=True,
        help="OAuth client JSON downloaded from the Google Cloud console",
    )
    parser.add_argument("--out", type=Path, required=True, help="path for the credential file")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="loopback redirect port")
    parser.add_argument(
        "--no-browser", action="store_true", help="print the URL instead of opening a browser"
    )
    return parser


def _client(path: Path) -> tuple[str, str]:
    """Read the client id and secret from the console-provided JSON."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    section = raw.get("installed") or raw.get("web") or raw
    client_id, client_secret = section.get("client_id"), section.get("client_secret")
    if not client_id or not client_secret:
        raise ValueError("client file has no client_id/client_secret; download the OAuth client")
    return client_id, client_secret


def main() -> int:
    """Run the consent once and store only the resulting refresh token."""
    args = build_parser().parse_args()
    sdk = PoliceThiefSDK().reporting
    client_id, client_secret = _client(args.client_file)
    redirect_uri = f"http://127.0.0.1:{args.port}/"
    url = sdk.authorization_url(client_id, redirect_uri)
    print("Open this URL and approve the send-only access:")
    print(url)
    if not args.no_browser:
        webbrowser.open(url)
    print(f"Waiting for the redirect on {redirect_uri} ...")
    code = sdk.wait_for_code(args.port)
    credentials = sdk.exchange_code(client_id, client_secret, code, redirect_uri)
    written = sdk.save_gmail_credentials(args.out, credentials)
    print(json.dumps({"credential_file": str(written), **credentials.redacted()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
