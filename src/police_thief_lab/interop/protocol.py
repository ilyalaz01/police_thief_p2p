"""Reference TurnMessage and robust at-least-once receiver."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class ProtocolViolation(ValueError):  # noqa: N818 - protocol term
    """Represent ProtocolViolation as one cohesive typed implementation boundary."""
    pass


class Equivocation(ProtocolViolation):
    """Represent Equivocation as one cohesive typed implementation boundary."""
    pass


@dataclass(frozen=True, slots=True)
class TurnMessage:
    """Represent TurnMessage as one cohesive typed implementation boundary."""
    step: int
    sender: str
    hint: str
    smell_grid: dict[str, float]
    commit: str
    timestamp: str
    barrier_placed: list[int] | None = None
    capture_claim: list[int] | None = None
    claim_response: dict[str, Any] | None = None
    win_claim: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Perform to dict through the documented TurnMessage contract."""
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> TurnMessage:
        """Perform from dict through the documented TurnMessage contract."""
        required = {"step", "sender", "hint", "smell_grid", "commit", "timestamp"}
        missing = required - value.keys()
        if missing:
            raise ProtocolViolation(f"missing TurnMessage keys: {sorted(missing)}")
        known = set(cls.__dataclass_fields__)
        msg = cls(**{key: item for key, item in value.items() if key in known})
        if (
            msg.step < 0
            or len(msg.commit) != 64
            or any(c not in "0123456789abcdef" for c in msg.commit)
        ):
            raise ProtocolViolation("invalid step or commitment")
        if not msg.timestamp or not all(
            isinstance(v, int | float) for v in msg.smell_grid.values()
        ):
            raise ProtocolViolation("invalid timestamp or scent values")
        return msg


class TurnInbox:
    """Deduplicate, reject equivocation, and buffer a bounded future window."""

    def __init__(self, next_step: int = 1, window: int = 4) -> None:
        """Initialize TurnInbox with its validated setup values and private state."""
        self.next_step = next_step
        self.window = window
        self.played: dict[int, str] = {}
        self.buffered: dict[int, TurnMessage] = {}
        self.absorbed = 0

    def offer(self, raw: dict[str, Any]) -> list[TurnMessage]:
        """Validate and classify an inbound turn under the ordering and duplicate contract."""
        message = TurnMessage.from_dict(raw)
        existing = self.played.get(message.step)
        buffered = self.buffered.get(message.step)
        if existing is not None or buffered is not None:
            prior = existing if existing is not None else buffered.commit
            if prior != message.commit:
                raise Equivocation(f"different commitment for step {message.step}")
            self.absorbed += 1
            return []
        if message.step < self.next_step:
            self.absorbed += 1
            return []
        if message.step > self.next_step + self.window:
            raise ProtocolViolation("future step exceeds reorder window")
        if message.step > self.next_step:
            self.buffered[message.step] = message
            return []
        ready = [message]
        while True:
            current = ready[-1]
            self.played[current.step] = current.commit
            self.next_step = current.step + 1
            following = self.buffered.pop(self.next_step, None)
            if following is None:
                break
            ready.append(following)
        return ready

    def mark_local(self, step: int, commit: str) -> None:
        """Advance the global sequence across the local action not received on the wire."""
        if step != self.next_step:
            raise ProtocolViolation(f"local step {step} is not expected step {self.next_step}")
        self.played[step] = commit
        self.next_step = step + 1
