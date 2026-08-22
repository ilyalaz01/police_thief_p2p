"""Official result-reporting operations exposed through the SDK."""

from __future__ import annotations

from ..reporting import (
    GmailApiTransport,
    GmailCredentials,
    GmailResultSender,
    ReportingConfig,
    ReportingNotAuthorizedError,
    ResultMessage,
    SendFailedError,
    TransportStatusError,
    authorization_url,
    build_result_message,
    exchange_code,
    load_gmail_credentials,
    load_reporting_config,
    save_gmail_credentials,
    wait_for_code,
)


class ReportingSDK:
    """Stable entry points for building and, once authorized, sending the result mail."""

    GmailApiTransport = GmailApiTransport
    GmailCredentials = GmailCredentials
    GmailResultSender = GmailResultSender
    ReportingConfig = ReportingConfig
    ReportingNotAuthorizedError = ReportingNotAuthorizedError
    ResultMessage = ResultMessage
    SendFailedError = SendFailedError
    TransportStatusError = TransportStatusError
    authorization_url = staticmethod(authorization_url)
    build_result_message = staticmethod(build_result_message)
    exchange_code = staticmethod(exchange_code)
    load_gmail_credentials = staticmethod(load_gmail_credentials)
    load_reporting_config = staticmethod(load_reporting_config)
    save_gmail_credentials = staticmethod(save_gmail_credentials)
    wait_for_code = staticmethod(wait_for_code)
