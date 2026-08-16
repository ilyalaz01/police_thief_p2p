"""FastMCP peer mailbox and synchronous outbound client."""

from __future__ import annotations

import asyncio
import copy
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from fastmcp import Client, FastMCP

from ..gatekeeper import ApiGatekeeper, default_gatekeeper
from ..gatekeeper_models import default_rate_limit_path, load_rate_limit_config


@dataclass(slots=True)
class PeerInboxes:
    max_depth: int | None = None
    agreements: queue.Queue = field(init=False)
    turns: queue.Queue = field(init=False)
    audits: queue.Queue = field(init=False)
    controls: queue.Queue = field(init=False)

    def __post_init__(self) -> None:
        depth = self.max_depth
        if depth is None:
            depth = load_rate_limit_config(default_rate_limit_path(), "fastmcp").queue_max
        if depth < 1:
            raise ValueError("peer inbox depth must be positive")
        self.max_depth = depth
        self.agreements = queue.Queue(depth)
        self.turns = queue.Queue(depth)
        self.audits = queue.Queue(depth)
        self.controls = queue.Queue(depth)

    def queue_status(self) -> dict[str, int]:
        """Return sanitized queue depths without inspecting retained messages."""
        return {
            "agreements": self.agreements.qsize(),
            "turns": self.turns.qsize(),
            "audits": self.audits.qsize(),
            "controls": self.controls.qsize(),
            "maximum": int(self.max_depth),
        }


def build_server(role: str, inboxes: PeerInboxes) -> FastMCP:
    mcp = FastMCP(name=f"police-thief-phase4a-{role}")

    @mcp.tool
    def negotiate(message: dict) -> dict:
        inboxes.agreements.put(message)
        return {"ok": True}

    @mcp.tool
    def receive_turn(message: dict) -> dict:
        inboxes.turns.put(message)
        return {"ok": True}

    @mcp.tool
    def submit_audit(payload: dict) -> dict:
        inboxes.audits.put(payload)
        return {"ok": True}

    @mcp.tool
    def receive_control(message: dict) -> dict:
        inboxes.controls.put(message)
        return {"ok": True}

    return mcp


def start_server(role: str, host: str, port: int) -> PeerInboxes:
    inboxes = PeerInboxes()
    app = build_server(role, inboxes)
    threading.Thread(
        target=lambda: app.run(
            transport="http",
            host=host,
            port=port,
            path="/mcp",
            show_banner=False,
            log_level="error",
        ),
        daemon=True,
    ).start()
    return inboxes


def discover_tools(url: str, gatekeeper: ApiGatekeeper | None = None) -> list[str]:
    """Perform a real FastMCP initialize/list-tools exchange and return tool names."""
    async def discover() -> list[str]:
        async with Client(url) as client:
            return sorted(tool.name for tool in await client.list_tools())

    gate = gatekeeper or default_gatekeeper()
    return gate.execute(lambda: asyncio.run(discover()), operation="fastmcp.discover_tools")


class McpPeerClient:
    def __init__(
        self,
        url: str,
        connect_timeout: float,
        retry: float,
        retry_count: int = 100,
        gatekeeper: ApiGatekeeper | None = None,
    ) -> None:
        self.url, self.connect_timeout, self.retry = url, connect_timeout, retry
        self.retry_count = retry_count
        self.last_attempts = 0
        self.last_attempt_ms: list[float] = []
        self.gatekeeper = gatekeeper or default_gatekeeper()

    def _invoke(self, tool: str, argument: str, value: dict[str, Any]) -> None:
        async def invoke() -> None:
            async with Client(self.url) as client:
                await client.call_tool(tool, {argument: value})

        asyncio.run(invoke())

    def call(self, tool: str, value: dict[str, Any], timeout: float | None = None) -> float:
        argument = "payload" if tool == "submit_audit" else "message"
        deadline = time.monotonic() + (timeout or self.connect_timeout)
        frozen = copy.deepcopy(value)
        started = time.perf_counter()
        self.last_attempts = 0
        self.last_attempt_ms = []
        while True:
            attempt_started = time.perf_counter()
            self.last_attempts += 1
            try:
                self.gatekeeper.execute(
                    self._invoke,
                    tool,
                    argument,
                    copy.deepcopy(frozen),
                    operation=f"fastmcp.{tool}",
                )
                self.last_attempt_ms.append((time.perf_counter() - attempt_started) * 1000)
                return (time.perf_counter() - started) * 1000
            except Exception as exc:
                self.last_attempt_ms.append((time.perf_counter() - attempt_started) * 1000)
                retries_used = self.last_attempts - 1
                if retries_used >= self.retry_count or time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"{tool} transport exhausted after {self.last_attempts} attempts"
                    ) from exc
                time.sleep(min(self.retry, max(0.0, deadline - time.monotonic())))
