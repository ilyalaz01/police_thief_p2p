"""Send-only Gmail REST transport built on the stdlib HTTPS helper."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .credentials import GmailCredentials
from .http_client import HttpResponse, post_form, post_json
from .sender import TransportStatusError

FormPoster = Callable[[str, dict[str, str]], HttpResponse]
JsonPoster = Callable[[str, dict[str, Any], str], HttpResponse]


class GmailApiTransport:
    """One callable that exchanges the refresh token and posts exactly one message."""

    def __init__(
        self,
        credentials: GmailCredentials,
        form_poster: FormPoster | None = None,
        json_poster: JsonPoster | None = None,
    ) -> None:
        """Initialize the transport; the posters are injectable for offline tests."""
        self.credentials = credentials
        self.form_poster = form_poster or (lambda url, fields: post_form(url, fields))
        self.json_poster = json_poster or (
            lambda url, payload, bearer: post_json(url, payload, bearer)
        )

    def access_token(self) -> str:
        """Exchange the stored refresh token for one short-lived access token."""
        status, body = self.form_poster(
            self.credentials.token_uri,
            {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "refresh_token": self.credentials.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if status != 200:
            raise TransportStatusError(status)
        token = body.get("access_token")
        if not isinstance(token, str) or not token:
            raise TransportStatusError(status)
        return token

    def __call__(self, raw: str) -> dict[str, Any]:
        """Send one already-built message and return only its provider identifiers."""
        token = self.access_token()
        status, body = self.json_poster(self.credentials.send_uri, {"raw": raw}, token)
        if status not in (200, 202):
            raise TransportStatusError(status)
        return {"id": body.get("id", ""), "threadId": body.get("threadId", "")}
