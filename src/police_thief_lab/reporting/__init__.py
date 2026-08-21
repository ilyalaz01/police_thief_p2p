"""Official counted-series result reporting boundary."""

from .config import SCHEMA_VERSION, ReportingConfig, load_reporting_config
from .message import ResultMessage, build_result_message
from .sender import (
    RETRYABLE_STATUSES,
    GmailResultSender,
    ReportingNotAuthorizedError,
    SendFailedError,
    TransportStatusError,
)

__all__ = [
    "ReportingNotAuthorizedError",
    "SendFailedError",
    "GmailResultSender",
    "RETRYABLE_STATUSES",
    "ReportingConfig",
    "ResultMessage",
    "SCHEMA_VERSION",
    "TransportStatusError",
    "build_result_message",
    "load_reporting_config",
]
