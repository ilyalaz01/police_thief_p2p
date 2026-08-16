"""Operational startup configuration operations exposed through the SDK."""

from pathlib import Path

from ..configuration import (
    CONFIG_SCHEMA_VERSION,
    OperationalConfig,
    load_operational_config,
    scan_configuration_secrets,
)


class ConfigurationSDK:
    """Stable access to fail-closed startup metadata and sanitized scanning."""

    CONFIG_SCHEMA_VERSION = CONFIG_SCHEMA_VERSION
    OperationalConfig = OperationalConfig
    Path = Path
    load_operational_config = staticmethod(load_operational_config)
    scan_configuration_secrets = staticmethod(scan_configuration_secrets)
