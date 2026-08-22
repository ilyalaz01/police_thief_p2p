"""Send-only Gmail boundary with an explicit authorization and retry contract."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from ..gatekeeper import ApiGatekeeper, default_gatekeeper
from .config import ReportingConfig
from .message import ResultMessage

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
Transport = Callable[[str], dict[str, Any]]


class ReportingNotAuthorizedError(RuntimeError):
    """Raised when a send is attempted without an explicitly supplied transport."""


class SendFailedError(RuntimeError):
    """Raised when every permitted attempt failed; the message was not accepted."""


class TransportStatusError(RuntimeError):
    """Transport-reported HTTP status, raised by the caller-supplied transport."""

    def __init__(self, status: int) -> None:
        """Retain only the status code; never a body, token, or header."""
        super().__init__(f"transport status {status}")
        self.status = status


class GmailResultSender:
    """One send-only boundary: one accepted message per game, retries, no credentials."""

    def __init__(
        self,
        config: ReportingConfig,
        transport: Transport | None = None,
        gatekeeper: ApiGatekeeper | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Initialize the sender; without a transport every send is refused."""
        self.config = config
        self.transport = transport
        self.gatekeeper = gatekeeper or default_gatekeeper()
        self.sleep = sleep
        self.accepted: dict[str, int] = {}

    def dry_run(self, message: ResultMessage) -> dict[str, Any]:
        """Return exactly what would be sent without contacting any service."""
        return {"operation": "dry_run", "sent": False, **message.inspection()}

    def draft(self, message: ResultMessage) -> dict[str, Any]:
        """Place the message in the operator's drafts; nothing is delivered to the league."""
        if self.transport is None or not hasattr(self.transport, "create_draft"):
            raise ReportingNotAuthorizedError(
                "no authorized transport with a draft boundary was supplied"
            )
        response = self.gatekeeper.execute(
            self.transport.create_draft, message.raw, operation="gmail.drafts.create"
        )
        return {
            "operation": "draft", "sent": False, "delivered": False,
            "provider_message_id": str(response.get("id", "")),
            **message.inspection(),
        }

    def send(self, message: ResultMessage) -> dict[str, Any]:
        """Send one message through the supplied transport under the retry contract."""
        if self.transport is None:
            raise ReportingNotAuthorizedError(
                "no authorized transport supplied; reporting stays a dry run"
            )
        already = self.accepted.get(message.game_id, 0)
        if already >= self.config.max_sends_per_game:
            raise SendFailedError(
                f"{message.game_id} already reached its {already}-send limit"
            )
        attempts, backoff, statuses = 0, self.config.initial_backoff_seconds, []
        while attempts < self.config.retry_attempts:
            attempts += 1
            try:
                response = self.gatekeeper.execute(
                    self.transport, message.raw, operation="gmail.messages.send"
                )
            except TransportStatusError as error:
                statuses.append(error.status)
                if error.status not in RETRYABLE_STATUSES or attempts >= self.config.retry_attempts:
                    raise SendFailedError(
                        f"send refused after {attempts} attempts, statuses {statuses}"
                    ) from error
                self.sleep(backoff)
                backoff = min(backoff * 2, self.config.max_backoff_seconds)
                continue
            self.accepted[message.game_id] = already + 1
            return {
                "operation": "send", "sent": True, "attempts": attempts,
                "retried_statuses": statuses,
                "provider_message_id": str(response.get("id", "")),
                **message.inspection(),
            }
        raise SendFailedError(f"send exhausted {attempts} attempts, statuses {statuses}")
