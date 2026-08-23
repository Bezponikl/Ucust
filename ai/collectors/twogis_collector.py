import asyncio
from typing import List, Dict, Any

class TwoGisCollector:
    """
    Парсер отзывов с 2GIS.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def collect_reviews_async(self, organization_url_or_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Асинхронно собирает отзывы по ссылке на организацию в 2GIS.
        В будущем здесь будет подключение к 2GIS API или парсинг через Playwright.
        """
        print(f"[TwoGisCollector] 🗺️ Подключение к 2GIS для: {organization_url_or_id}")
        await asyncio.sleep(1) # Имитация сетевой задержки
        
        # Моковые отзывы для демонстрации пайплайна
        mock_reviews = [
            {"text": "Ребята крутые, сделали нам бота за два дня.", "rating": 5, "author": "Дмитрий"},
            {"text": "Очень удобно, что можно всё настроить под себя. Рекомендую.", "rating": 5, "author": "Ольга"},
        ]
        
        print(f"[TwoGisCollector] ✅ Собрано {len(mock_reviews)} отзывов из 2GIS.")
        return {
            "source": "2gis",
            "url": organization_url_or_id,
            "reviews": mock_reviews[:limit]
        }
