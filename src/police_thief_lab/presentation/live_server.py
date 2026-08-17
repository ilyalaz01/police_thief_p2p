"""Loopback-only HTTP boundary for the browser Live GUI."""

from __future__ import annotations

import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .live_feed import load_live_feed
from .live_html import render_live_html


class _LiveServer(ThreadingHTTPServer):
    daemon_threads = True


def _handler(snapshot: Path) -> type[BaseHTTPRequestHandler]:
    html = render_live_html().encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                "connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
            request_path = urlsplit(self.path).path
            if request_path == "/":
                self._send(200, html, "text/html; charset=utf-8")
                return
            if request_path == "/snapshot.json":
                try:
                    payload = json.dumps(
                        load_live_feed(snapshot), ensure_ascii=False, separators=(",", ":")
                    ).encode("utf-8")
                except (OSError, ValueError, json.JSONDecodeError):
                    payload = b'{"error":"snapshot unavailable"}'
                    self._send(503, payload, "application/json; charset=utf-8")
                    return
                self._send(200, payload, "application/json; charset=utf-8")
                return
            self._send(404, b"not found", "text/plain; charset=utf-8")

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return Handler


def build_live_server(snapshot: Path, host: str, port: int) -> ThreadingHTTPServer:
    """Build a local viewer server and refuse every non-loopback bind address."""
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError("live viewer host must be a loopback IP address") from exc
    if not address.is_loopback:
        raise ValueError("live viewer host must be loopback-only")
    if not 0 <= port <= 65535:
        raise ValueError("live viewer port must be between 0 and 65535")
    return _LiveServer((host, port), _handler(snapshot))


def run_live_server(snapshot: Path, host: str, port: int) -> None:
    """Serve until interrupted, without opening a browser or external socket."""
    server = build_live_server(snapshot, host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
