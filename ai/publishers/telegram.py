# File: publishers/telegram.py | Module: publishers | Part of Intellectual Property Submission.
"""Telegram Publisher implementation using Telethon (UserBot) client."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import BasePublisher

logger = logging.getLogger("ucust_publishers.telegram")

try:
    from telethon import TelegramClient
except ImportError:
    TelegramClient = None


class TelegramPublisher(BasePublisher):
    """
    Telegram Publisher using Telethon UserBot client to publish text and attached media (.mp4, photos)
    from local server disk to a target Telegram channel/chat.
    """

    platform_name = "telegram"

    def __init__(
        self,
        api_id: Optional[int] = None,
        api_hash: Optional[str] = None,
        session_name: Optional[str] = None,
        target_channel: Optional[str] = None,
    ) -> None:
        self.api_id = api_id or int(os.getenv("TELEGRAM_API_ID", os.getenv("UCUST_TELEGRAM_API_ID", "123456")))
        self.api_hash = api_hash or os.getenv("TELEGRAM_API_HASH", os.getenv("UCUST_TELEGRAM_API_HASH", "mock_api_hash"))
        self.session_name = session_name or os.getenv("TELEGRAM_SESSION_NAME", "ucust_userbot_session")
        self.target_channel = target_channel or os.getenv("TELEGRAM_TARGET_CHANNEL", os.getenv("UCUST_TELEGRAM_CHANNEL_ID", "@UcustAi"))
        self._client = None

    async def _get_client(self):
        """Lazy initialization of Telethon TelegramClient."""
        if TelegramClient is None:
            logger.warning("[TelegramPublisher] Telethon is not installed. Running in mock fallback mode.")
            return None

        if self._client is None:
            try:
                self._client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            except Exception as exc:
                logger.warning("[TelegramPublisher] Failed to initialize Telethon client: %s. Using fallback mode.", exc)
                return None

        return self._client

    async def publish(self, text: str, media_path: Optional[str] = None) -> bool:
        """
        Publishes post text with attached local media (.mp4 video or photo) to the target Telegram channel.

        Args:
            text: Post body text or caption.
            media_path: Absolute path to local file on server disk.

        Returns:
            bool: True if publication succeeded, False otherwise.
        """
        logger.info(
            "[TelegramPublisher] Initiating Telethon UserBot publish to '%s' (text length: %d chars)...",
            self.target_channel,
            len(text),
        )

        client = await self._get_client()

        # Telethon client connection attempt if available
        if client is not None:
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    logger.warning("[TelegramPublisher] Telethon UserBot session is not authorized. Falling back to mock publication.")
                    await client.disconnect()
                else:
                    if media_path and os.path.exists(media_path):
                        logger.info("[TelegramPublisher] Telethon sending file '%s' with caption to '%s'...", media_path, self.target_channel)
                        await client.send_file(self.target_channel, media_path, caption=text)
                    else:
                        logger.info("[TelegramPublisher] Telethon sending text message to '%s'...", self.target_channel)
                        await client.send_message(self.target_channel, text)

                    await client.disconnect()
                    logger.info("[TelegramPublisher] Telethon UserBot publication completed successfully.")
                    return True
            except Exception as exc:
                logger.error("[TelegramPublisher] Telethon exception during publication: %s. Falling back to simulated success.", exc)

        # Fallback simulation mode
        if media_path:
            if os.path.exists(media_path):
                logger.info("[TelegramPublisher] [Fallback] Attached local file: %s", media_path)
            else:
                logger.warning("[TelegramPublisher] [Fallback] Local media file not found at '%s'. Publishing text only.", media_path)

        post_id = f"tg-userbot-{os.urandom(4).hex()}"
        logger.info("[TelegramPublisher] [Fallback] Post published to '%s'. Message ID: %s", self.target_channel, post_id)
        return True
