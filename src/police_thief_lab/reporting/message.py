"""Deterministic construction of the one official result e-mail per counted game."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any

from .config import ReportingConfig

JSON_MEDIA_TYPE = ("application", "json")


@dataclass(frozen=True, slots=True)
class ResultMessage:
    """One fully built, inspectable message that no transport has seen yet."""

    game_id: str
    recipient: str
    sender: str
    subject: str
    body: str
    attachment_name: str
    raw: str

    def inspection(self) -> dict[str, Any]:
        """Return an operator-readable summary that never contains a credential."""
        return {
            "game_id": self.game_id, "to": self.recipient, "from": self.sender,
            "subject": self.subject, "attachment_name": self.attachment_name,
            "body_bytes": len(self.body.encode("utf-8")), "raw_bytes": len(self.raw),
        }


def _game_id(result: dict[str, Any]) -> str:
    """Read the exact game identifier the artifact already carries."""
    value = result.get("game_id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("result artifact has no usable game_id")
    return value


def build_result_message(result_bytes: bytes, config: ReportingConfig) -> ResultMessage:
    """Build the settled report shape: result JSON as body and as the single attachment.

    The body and the attachment carry the identical bytes of the mutually agreed result
    artifact. Declaration, config and log artifacts are published in the role repositories
    and are deliberately never mailed.
    """
    result = json.loads(result_bytes.decode("utf-8"))
    if not isinstance(result, dict):
        raise ValueError("result artifact must be one JSON object")
    if "mutual_agreement" not in result:
        raise ValueError("result artifact carries no mutual_agreement block")
    game_id = _game_id(result)
    body = result_bytes.decode("utf-8")
    attachment_name = config.attachment_name_template.format(game_id=game_id)
    message = EmailMessage()
    message["To"] = config.league_recipient
    message["From"] = config.sender_address
    message["Subject"] = config.subject_template.format(game_id=game_id)
    message.set_content(body)
    message.add_attachment(
        result_bytes, maintype=JSON_MEDIA_TYPE[0], subtype=JSON_MEDIA_TYPE[1],
        filename=attachment_name,
    )
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    return ResultMessage(
        game_id=game_id, recipient=config.league_recipient, sender=config.sender_address,
        subject=message["Subject"], body=body, attachment_name=attachment_name, raw=raw,
    )
