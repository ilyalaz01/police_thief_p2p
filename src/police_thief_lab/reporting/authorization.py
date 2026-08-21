"""One-time send-only Gmail consent: build the URL, catch the code, store the token."""

from __future__ import annotations

import urllib.parse
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from .credentials import SEND_SCOPE, TOKEN_URI, GmailCredentials
from .http_client import HttpResponse, post_form

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
PAGE = b"<html><body><h3>Authorization received. You can close this tab.</h3></body></html>"


def authorization_url(client_id: str, redirect_uri: str) -> str:
    """Build the consent URL requesting only the send scope and an offline refresh token."""
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SEND_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{AUTH_URI}?{query}"


class _CodeHandler(BaseHTTPRequestHandler):
    """Capture exactly one redirect and answer with a static page."""

    code: str | None = None

    def do_GET(self) -> None:  # noqa: N802 - required handler name
        """Store the authorization code from the loopback redirect."""
        query = urllib.parse.urlparse(self.path).query
        _CodeHandler.code = urllib.parse.parse_qs(query).get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - base signature
        """Silence the default request logging so no code reaches the terminal."""


def wait_for_code(port: int, timeout: float = 300.0) -> str:
    """Serve the loopback redirect once and return the captured authorization code."""
    _CodeHandler.code = None
    server = HTTPServer(("127.0.0.1", port), _CodeHandler)
    server.timeout = timeout
    try:
        server.handle_request()
    finally:
        server.server_close()
    if not _CodeHandler.code:
        raise TimeoutError("no authorization code was received on the loopback redirect")
    return _CodeHandler.code


def exchange_code(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    poster: Callable[[str, dict[str, str]], HttpResponse] | None = None,
) -> GmailCredentials:
    """Exchange one authorization code for the long-lived refresh token."""
    send = poster or (lambda url, fields: post_form(url, fields))
    status, body = send(
        TOKEN_URI,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    if status != 200:
        raise RuntimeError(f"authorization exchange refused with status {status}")
    refresh = body.get("refresh_token")
    if not isinstance(refresh, str) or not refresh:
        raise RuntimeError(
            "the exchange returned no refresh token; revoke the app in the Google account "
            "and authorize again so consent is granted fresh"
        )
    return GmailCredentials(client_id=client_id, client_secret=client_secret, refresh_token=refresh)
