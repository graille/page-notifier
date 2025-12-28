"""
Notifiers module for sending change notifications.

This module provides different notification backends (Discord, etc.).
"""

from notifiers.base import BaseNotifier
from notifiers.discord import DiscordNotifier

__all__ = ["BaseNotifier", "DiscordNotifier"]

