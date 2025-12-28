"""
Base notifier module.

Provides the abstract base class for all notification backends.
"""

from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """
    Abstract base class for notification backends.

    All notification implementations (Discord, Slack, Email, etc.) should inherit
    from this class and implement the required methods.
    """

    @abstractmethod
    async def send_notification(
        self,
        title: str,
        message: str,
        url: str,
        hostname: str | None = None,
        diff: str | None = None,
    ):
        """
        Send a notification about a page change.

        :param title: The title of the notification.
        :param message: The main message content describing the change.
        :param url: The URL of the page that changed.
        :param hostname: The hostname of the page (optional).
        :param diff: A diff showing the changes (optional).
        :raises NotImplementedError: If the method is not implemented by subclass.
        """
        raise NotImplementedError("Subclasses must implement send_notification")

    @abstractmethod
    async def close(self):
        """
        Close any open connections or resources.

        Should be called when the notifier is no longer needed.
        """
        raise NotImplementedError("Subclasses must implement close")

