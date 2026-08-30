# File: publishers/base.py | Module: publishers | Part of Intellectual Property Submission.
"""Abstract Base Publisher contract for social media publishing."""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Optional

logger = logging.getLogger("ucust_publishers")


class BasePublisher(ABC):
    """Abstract contract for social media publisher integrations (Telegram Telethon, VK API, etc.)."""

    platform_name: str = "base"

    @abstractmethod
    async def publish(self, text: str, media_path: Optional[str] = None) -> bool:
        """
        Publishes text content with optional attached local media file to the social platform.

        Args:
            text: The text content or caption of the post.
            media_path: Absolute local path to the generated media file (.mp4, .wav, .png).

        Returns:
            bool: True if publication succeeded, False otherwise.
        """
        raise NotImplementedError
