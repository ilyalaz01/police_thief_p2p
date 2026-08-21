"""Minimal stdlib HTTPS helper so reporting needs no third-party dependency."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_TIMEOUT_SECONDS = 30.0
HttpResponse = tuple[int, dict[str, Any]]


def _decode(body: bytes) -> dict[str, Any]:
    """Parse a JSON body, tolerating an empty or non-JSON provider response."""
    if not body:
        return {}
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def post(
    url: str,
    body: bytes,
    content_type: str,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> HttpResponse:
    """POST once over HTTPS and return the status with the decoded JSON body.

    The response body is parsed but never logged here; the caller decides what, if
    anything, is safe to retain. Transport errors surface as status 599.
    """
    if not url.startswith("https://"):
        raise ValueError("reporting refuses a non-HTTPS endpoint")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", content_type)
    for name, value in (headers or {}).items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), _decode(response.read())
    except urllib.error.HTTPError as error:
        return int(error.code), _decode(error.read())
    except (urllib.error.URLError, TimeoutError):
        return 599, {}


def post_form(
    url: str, fields: dict[str, str], timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> HttpResponse:
    """POST one application/x-www-form-urlencoded body."""
    encoded = urllib.parse.urlencode(fields).encode("utf-8")
    return post(url, encoded, "application/x-www-form-urlencoded", timeout=timeout)


def post_json(
    url: str, payload: dict[str, Any], bearer: str, timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> HttpResponse:
    """POST one JSON body with a short-lived bearer credential."""
    encoded = json.dumps(payload).encode("utf-8")
    return post(url, encoded, "application/json", {"Authorization": f"Bearer {bearer}"}, timeout)
