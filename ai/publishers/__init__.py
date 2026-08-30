# File: publishers/__init__.py | Module: publishers | Part of Intellectual Property Submission.
"""Social Media Publishers package for UCust.AI supporting Telegram, VK, Instagram, OK, and MAX Messenger."""

from .base import BasePublisher
from .instagram import InstagramPublisher
from .max import MaxPublisher
from .ok import OdnoklassnikiPublisher
from .telegram import TelegramPublisher
from .vk import VkPublisher


def get_publisher(platform_name: str) -> BasePublisher:
    """
    Factory function to dynamically instantiate a publisher connector by string platform identifier.
    Supported identifiers: 'telegram', 'vk', 'instagram', 'ok', 'max'.
    """
    name = platform_name.lower().strip()
    registry = {
        "telegram": TelegramPublisher,
        "tg": TelegramPublisher,
        "vk": VkPublisher,
        "vkontakte": VkPublisher,
        "instagram": InstagramPublisher,
        "ig": InstagramPublisher,
        "ok": OdnoklassnikiPublisher,
        "odnoklassniki": OdnoklassnikiPublisher,
        "max": MaxPublisher,
        "max_messenger": MaxPublisher,
    }
    publisher_cls = registry.get(name)
    if publisher_cls is None:
        raise ValueError(f"Unsupported publisher platform: '{platform_name}'. Supported: {list(set(registry.keys()))}")
    return publisher_cls()


__all__ = [
    "BasePublisher",
    "InstagramPublisher",
    "MaxPublisher",
    "OdnoklassnikiPublisher",
    "TelegramPublisher",
    "VkPublisher",
    "get_publisher",
]
