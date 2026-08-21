"""Official counted-series result reporting boundary."""

from .authorization import authorization_url, exchange_code, wait_for_code
from .config import SCHEMA_VERSION, ReportingConfig, load_reporting_config
from .credentials import (
    SEND_SCOPE,
    GmailCredentials,
    load_gmail_credentials,
    save_gmail_credentials,
)
from .gmail_transport import GmailApiTransport
from .message import ResultMessage, build_result_message
from .sender import (
    RETRYABLE_STATUSES,
    GmailResultSender,
    ReportingNotAuthorizedError,
    SendFailedError,
    TransportStatusError,
)

__all__ = [
    "GmailApiTransport",
    "GmailCredentials",
    "GmailResultSender",
    "RETRYABLE_STATUSES",
    "ReportingConfig",
    "ReportingNotAuthorizedError",
    "ResultMessage",
    "SCHEMA_VERSION",
    "SEND_SCOPE",
    "SendFailedError",
    "TransportStatusError",
    "authorization_url",
    "build_result_message",
    "exchange_code",
    "load_gmail_credentials",
    "load_reporting_config",
    "save_gmail_credentials",
    "wait_for_code",
]
