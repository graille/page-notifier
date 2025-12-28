"""
Discord notifier module.

Provides Discord webhook integration for sending change notifications.
"""

import aiohttp
from datetime import datetime

import pytz

from notifiers.base import BaseNotifier


class DiscordNotifier(BaseNotifier):
    """
    Discord webhook notifier.

    Sends formatted embed messages to a Discord channel via webhook.
    """

    def __init__(self, webhook_url: str, timezone: str = "UTC"):
        """
        Initialize the Discord notifier.

        :param webhook_url: The Discord webhook URL.
        :param timezone: The timezone for timestamps (default: UTC).
        :raises ValueError: If webhook_url is empty or invalid.
        """
        if not webhook_url:
            raise ValueError("Discord webhook URL cannot be empty")

        self._webhook_url: str = webhook_url
        self._timezone: str = timezone
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create the aiohttp session.

        :return: The aiohttp client session.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def send_notification(
        self,
        title: str,
        message: str,
        url: str,
        hostname: str | None = None,
        diff: str | None = None,
    ):
        """
        Send a Discord embed notification about a page change.

        :param title: The title of the notification.
        :param message: The main message content describing the change.
        :param url: The URL of the page that changed.
        :param hostname: The hostname of the page (optional).
        :param diff: A diff showing the changes (optional).
        :raises aiohttp.ClientError: If the request to Discord fails.
        """
        tz = pytz.timezone(self._timezone)
        timestamp = datetime.now(tz).isoformat()

        fields = [
            {
                "name": "🔗 Page URL",
                "value": f"[Click here to view]({url})",
                "inline": False,
            }
        ]

        if hostname:
            fields.append(
                {
                    "name": "🌐 Hostname",
                    "value": f"`{hostname}`",
                    "inline": True,
                }
            )

        if diff:
            # Discord has a limit of 1024 characters per field value
            # Truncate if necessary and add ellipsis
            diff_value = diff if len(diff) <= 1024 else diff[:1021] + "..."
            fields.append(
                {
                    "name": "📝 Changes",
                    "value": f"```diff\n{diff_value}\n```",
                    "inline": False,
                }
            )

        embed = {
            "title": f"🔔 {title}",
            "description": message,
            "color": 0x5865F2,  # Discord blurple
            "fields": fields,
            "footer": {
                "text": "Change Detector",
            },
            "timestamp": timestamp,
        }

        payload = {
            "embeds": [embed],
        }

        session = await self._get_session()
        async with session.post(self._webhook_url, json=payload) as response:
            response.raise_for_status()

    async def close(self):
        """
        Close the aiohttp session.

        Should be called when the notifier is no longer needed.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

