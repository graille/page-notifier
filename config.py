"""
Configuration module for the change detector.

Loads environment variables from .env file and provides them as module-level constants.
Environment variables can be overridden by system environment variables (e.g., Docker).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists (system env vars take precedence)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

# Discord webhook URL for notifications
WEBHOOK_DISCORD: str = os.getenv("WEBHOOK_DISCORD", "")

# URL of the webpage to track
WEBPAGE_URL: str = os.getenv("WEBPAGE_URL", "")

# CSS selector path for the element to track (e.g., "#main|.content|#first_element")
# If empty or None, the entire body will be tracked
WEBPAGE_ELEMENT: str = os.getenv("WEBPAGE_ELEMENT", "")

# Time between requests in milliseconds
WEBPAGE_RELOAD_TIME: int = int(os.getenv("WEBPAGE_RELOAD_TIME", "60000"))

# Standard deviation for random delay added between requests (in milliseconds)
WEBPAGE_RELOAD_STD: float = float(os.getenv("WEBPAGE_RELOAD_STD", "500"))

# Timezone for datetime operations
TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Paris")

