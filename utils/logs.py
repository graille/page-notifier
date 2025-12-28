"""
Logging utilities module.

Provides custom logging formatters and configuration for the change detector.
"""

import logging
import sys
from datetime import datetime

import pytz


class TimezoneFormatter(logging.Formatter):
    """
    Custom formatter that uses a specific timezone for timestamps.

    Formats log messages with the pattern: [{timestamp}] - {level} - {message}
    """

    def __init__(self, timezone: str):
        """
        Initialize the timezone formatter.

        :param timezone: The timezone name (e.g., 'Europe/Paris').
        """
        super().__init__()
        self._tz = pytz.timezone(timezone)

    def format(self, record):
        """
        Format the log record with custom timestamp and format.

        Matches the original format: [{timestamp}] - {level} - {message}

        :param record: The log record.
        :return: Formatted log message.
        """
        dt = datetime.fromtimestamp(record.created, tz=self._tz)
        timestamp = dt.strftime("%d-%m-%Y %H:%M:%S")
        level_name = record.levelname
        message = record.getMessage()
        return f"[{timestamp}] - {level_name} - {message}"


def setup_logging(timezone: str, level: str = "INFO"):
    """
    Configure the logging system with custom timezone-aware formatter.

    Sets up a StreamHandler on stdout for Docker compatibility and configures
    the root logger with the specified level.

    :param timezone: The timezone name for timestamps.
    :param level: The logging level (default: INFO).
    """
    formatter = TimezoneFormatter(timezone)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    logger.addHandler(handler)

