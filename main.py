"""
Main module for the change detector.

Provides the main loop that periodically checks a webpage for changes
and sends notifications when changes are detected.
"""

import asyncio
import difflib
import logging
import random
import sys
from datetime import datetime
from urllib.parse import urlparse

import pytz
from curl_cffi.requests import AsyncSession

from config import (
    TIMEZONE,
    WEBHOOK_DISCORD,
    WEBPAGE_ELEMENT,
    WEBPAGE_RELOAD_STD,
    WEBPAGE_RELOAD_TIME,
    WEBPAGE_URL,
)
from notifiers import DiscordNotifier
from page_tracker import extract_element, normalize_html
from utils.logs import setup_logging


class ChangeDetector:
    """
    Main change detector class.

    Monitors a webpage for changes and sends notifications when detected.
    """

    def __init__(
        self,
        url: str,
        element_selector: str,
        reload_time_ms: int,
        reload_std_ms: float,
        webhook_url: str,
        timezone: str,
    ):
        """
        Initialize the change detector.

        :param url: The URL of the webpage to monitor.
        :param element_selector: CSS selector path for the element to track.
        :param reload_time_ms: Time between requests in milliseconds.
        :param reload_std_ms: Standard deviation for random delay (in milliseconds).
        :param webhook_url: Discord webhook URL for notifications.
        :param timezone: Timezone for logging.
        :raises ValueError: If required parameters are missing.
        """
        if not url:
            raise ValueError("WEBPAGE_URL is required")

        self._url: str = url
        self._element_selector: str = element_selector
        self._reload_time_ms: int = reload_time_ms
        self._reload_std_ms: float = reload_std_ms
        self._timezone: str = timezone
        self._tz = pytz.timezone(timezone)

        self._notifier: DiscordNotifier | None = None
        if webhook_url:
            self._notifier = DiscordNotifier(webhook_url, timezone)

        self._previous_content: str | None = None
        self._last_request_time: datetime | None = None
        self._success_count: int = 0
        self._error_count: int = 0
        self._logger = logging.getLogger(__name__)

    def _get_wait_time_ms(self) -> float:
        """
        Calculate the wait time until the next request.

        Adds a normally distributed random value to the base reload time.

        :return: Wait time in milliseconds.
        """
        base_time = self._reload_time_ms
        random_offset = random.gauss(0, self._reload_std_ms)
        wait_time = max(100, base_time + random_offset)  # Minimum 100ms
        
        return int(wait_time)

    async def _fetch_page(self, session: AsyncSession) -> str | None:
        """
        Fetch the webpage content.

        :param session: The async HTTP session.
        :return: The HTML content of the page, or None if the request failed.
        """
        try:
            response = await session.get(self._url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self._error_count += 1
            self._logger.error(f"Failed to fetch page: {e}")
            return None

    async def _check_for_changes(self, session: AsyncSession) -> bool:
        """
        Check if the webpage content has changed.

        :param session: The async HTTP session.
        :return: True if content changed, False otherwise.
        """
        current_time = datetime.now(self._tz)

        # Log time since last request
        if self._last_request_time:
            delta = (current_time - self._last_request_time).total_seconds()
            self._logger.debug(f"Time since last request: {delta:.2f}s")

        self._last_request_time = current_time

        # Fetch the page
        html_content = await self._fetch_page(session)
        if html_content is None:
            return False
        
        self._success_count += 1

        # Extract the target element
        try:
            element_html = extract_element(html_content, self._element_selector)
            normalized_content = normalize_html(element_html)
        except ValueError as e:
            self._error_count += 1
            self._logger.error(f"Failed to extract element: {e}")
            return False
        
        self._logger.debug(f"Normalized content: {normalized_content}")

        # First run - store initial content
        if self._previous_content is None:
            self._previous_content = normalized_content
            self._logger.info(
                f"Initial content stored. Success: {self._success_count}, Errors: {self._error_count}"
            )
            return False

        # Compare with previous content
        if normalized_content != self._previous_content:
            old_content = self._previous_content
            self._previous_content = normalized_content
            self._logger.info(
                f"CHANGE DETECTED! Success: {self._success_count}, Errors: {self._error_count}"
            )
            await self._notify_change(old_content, normalized_content)
            return True

        self._logger.info(
            f"No change. Success: {self._success_count}, Errors: {self._error_count}"
        )
        return False

    def _generate_diff(self, old_content: str, new_content: str, max_lines: int = 30) -> str:
        """
        Generate a unified diff between old and new content.

        Limits the output to a reasonable number of lines for display in notifications.

        :param old_content: The previous content.
        :param new_content: The new content.
        :param max_lines: Maximum number of diff lines to include (default: 30).
        :return: A formatted diff string.
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="Previous",
            tofile="Current",
            lineterm="",
            n=2,  # Context lines
        )

        diff_lines = list(diff)
        if len(diff_lines) > max_lines:
            diff_lines = diff_lines[:max_lines]
            diff_lines.append(f"\n... (truncated, showing first {max_lines} lines)")

        return "".join(diff_lines)

    def _extract_hostname(self, url: str) -> str | None:
        """
        Extract the hostname from a URL.

        :param url: The URL to parse.
        :return: The hostname, or None if parsing fails.
        """
        try:
            parsed = urlparse(url)
            return parsed.hostname
        except Exception:
            return None

    async def _notify_change(self, old_content: str, new_content: str):
        """
        Send a notification about the detected change.

        :param old_content: The previous content.
        :param new_content: The new content.
        """
        if self._notifier:
            try:
                hostname = self._extract_hostname(self._url)
                diff = self._generate_diff(old_content, new_content)

                await self._notifier.send_notification(
                    title="Page Change Detected",
                    message="The monitored webpage has been updated!",
                    url=self._url,
                    hostname=hostname,
                    diff=diff,
                )
                self._logger.info("Notification sent to Discord")
            except Exception as e:
                self._logger.error(f"Failed to send notification: {e}")
        else:
            self._logger.warning("No notifier configured, skipping notification")

    async def run(self):
        """
        Start the main monitoring loop.

        Continuously checks the webpage for changes at the configured interval.
        """
        self._logger.info(f"Starting change detector for {self._url}")
        self._logger.info(f"Element selector: {self._element_selector or 'entire body'}")
        self._logger.info(f"Reload interval: {self._reload_time_ms}ms (std: {self._reload_std_ms}ms)")

        async with AsyncSession(impersonate="firefox") as session:
            while True:
                changed = await self._check_for_changes(session)

                if changed:
                    # _notify_change is already called in _check_for_changes when change is detected
                    pass

                wait_time = self._get_wait_time_ms() / 1000.0
                await asyncio.sleep(wait_time)

    async def close(self):
        """
        Clean up resources.
        """
        if self._notifier:
            await self._notifier.close()


async def async_main():
    """
    Async entry point for the change detector.
    """
    setup_logging(TIMEZONE)
    
    detector = ChangeDetector(
        url=WEBPAGE_URL,
        element_selector=WEBPAGE_ELEMENT,
        reload_time_ms=WEBPAGE_RELOAD_TIME,
        reload_std_ms=WEBPAGE_RELOAD_STD,
        webhook_url=WEBHOOK_DISCORD,
        timezone=TIMEZONE,
    )

    try:
        await detector.run()
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("\nShutting down...")
    finally:
        await detector.close()


def main():
    """
    Entry point for the change detector.
    """
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()

