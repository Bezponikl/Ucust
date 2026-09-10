"""
UCust AI Collectors & Parsers Hub
Пакет сборщиков данных: Telegram, VK, Сайты, Документы, Карты (2GIS/Яндекс), Тренды и Праздники.
"""

from collectors.telethon_collector import TelethonCollector
from collectors.vk_collector import VkApiCollector, VKCollector
from collectors.website_collector import WebsiteCollector
from collectors.document_collector import DocumentCollector
from collectors.twogis_collector import TwoGisCollector, TwoGISCollector
from collectors.yandex_collector import YandexMapsCollector, YandexCollector
from collectors.trends_collector import TrendsCollector
from collectors.event_holiday_collector import EventHolidayCollector

__all__ = [
    "TelethonCollector",
    "VkApiCollector",
    "VKCollector",
    "WebsiteCollector",
    "DocumentCollector",
    "TwoGisCollector",
    "TwoGISCollector",
    "YandexMapsCollector",
    "YandexCollector",
    "TrendsCollector",
    "EventHolidayCollector"
]
