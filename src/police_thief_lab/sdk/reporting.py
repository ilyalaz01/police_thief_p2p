"""Official result-reporting operations exposed through the SDK."""

from __future__ import annotations

from ..reporting import (
    GmailResultSender,
    ReportingConfig,
    ReportingNotAuthorizedError,
    ResultMessage,
    SendFailedError,
    TransportStatusError,
    build_result_message,
    load_reporting_config,
)


class ReportingSDK:
    """Stable entry points for building and, once authorized, sending the result mail."""

    GmailResultSender = GmailResultSender
    ReportingConfig = ReportingConfig
    ReportingNotAuthorizedError = ReportingNotAuthorizedError
    ResultMessage = ResultMessage
    SendFailedError = SendFailedError
    TransportStatusError = TransportStatusError
    build_result_message = staticmethod(build_result_message)
    load_reporting_config = staticmethod(load_reporting_config)
