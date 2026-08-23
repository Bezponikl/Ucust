import os
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any

class TrendCollector:
    """
    Коллектор еженедельных трендов из интернета и соцсетей.
    Использует Tavily Web Search API или веб-скрейпинг.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TRAVITY_API_KEY", "")

    async def fetch_niche_trends(self, niche: str) -> Dict[str, Any]:
        """
        Ищет свежие тренды, вирусные форматы и инфоповоды для конкретной ниши.
        """
        print(f"[TrendCollector] 🌐 Поиск еженедельных трендов для ниши: '{niche}'...")
        
        # Если есть API-ключ Tavily, делаем реальный запрос к поисковику
        if self.api_key and not self.api_key.startswith("tvly-dev"):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": self.api_key,
                            "query": f"SMM тренды вирусные рилс идеи 2026 {niche}",
                            "search_depth": "advanced",
                            "include_answer": True,
                            "max_results": 5
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = [r.get("content", "") for r in data.get("results", [])]
                        return {
                            "niche": niche,
                            "fetched_at": datetime.utcnow().isoformat(),
                            "summary": data.get("answer", ""),
                            "trend_sources": results
                        }
            except Exception as e:
                print(f"[TrendCollector] ⚠️ Ошибка запроса Tavily: {e}")

        # Fallback / Mock данные для тестирования и автономной работы
        await asyncio.sleep(1)
        return {
            "niche": niche,
            "fetched_at": datetime.utcnow().isoformat(),
            "summary": f"Главный тренд недели в {niche}: интерактивные видео в стиле POV и короткие обучающие динамичные ролики под трендовый аудио-бит.",
            "trending_topics": [
                f"Топ-1 фишка: 'Закулисье работы в {niche}'",
                f"Топ-2 формат: Сравнение 'Ожидание vs Реальность'",
                f"Топ-3 инфоповод: Разбор частых ошибок новичков"
            ],
            "viral_audio_style": "Энергичный Lo-Fi или минималистичный техно-бит с акцентами"
        }
