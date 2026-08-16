"""Internal value-owning work item for the API Gatekeeper queue."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkItem:
    """Hold one call only until its waiting caller receives the result."""

    api_call: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    operation: str
    done: threading.Event = field(default_factory=threading.Event)
    result: Any = None
    error: BaseException | None = None
