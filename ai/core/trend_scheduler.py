import asyncio
import json
from datetime import datetime
from typing import List
from collectors.trend_collector import TrendCollector
from core.redis_cache import RedisCacheManager

DEFAULT_NICHES = [
    "IT и Автоматизация",
    "Салоны красоты и Бьюти",
    "Рестораны и Кофейни",
    "Недвижимость и Строительство",
    "E-commerce и Одежда",
    "Фитнес и Здоровье"
]

class WeeklyTrendScheduler:
    """
    Планировщик фонового еженедельного сбора трендов.
    Сохраняет тренды в Redis (TTL 7 дней) и pgvector для мгновенной выдачи клиентам.
    """
    def __init__(self, redis_cache: RedisCacheManager = None, vector_store = None):
        self.collector = TrendCollector()
        self.redis = redis_cache or RedisCacheManager()
        self.vector_store = vector_store
        self.is_running = False

    async def update_all_trends(self, niches: List[str] = None):
        """
        Сканирует интернет по всем нишам и сохраняет кэш на 7 дней.
        """
        target_niches = niches or DEFAULT_NICHES
        print(f"[WeeklyTrendScheduler] 🕒 Запуск еженедельного обновления трендов для {len(target_niches)} ниш...")
        
        for niche in target_niches:
            trends_data = await self.collector.fetch_niche_trends(niche)
            
            # Сохраняем в Redis на 7 дней (7 * 24 * 3600 = 604800 секунд)
            cache_key = f"niche_trend:{niche.lower().replace(' ', '_')}"
            self.redis.set_cached_result("WeeklyTrends", cache_key, trends_data, ttl=604800)
            
            # Если подключен pgvector, индексируем для семантического поиска
            if self.vector_store:
                try:
                    from storage.vector_store import VectorRecord
                    emb = self.vector_store.embed_text(trends_data.get("summary", ""))
                    record = VectorRecord(
                        text_id=f"trend_{niche}_{datetime.utcnow().strftime('%Y_%W')}",
                        embedding=emb,
                        metadata={"niche": niche, "type": "trend", "data": trends_data}
                    )
                    self.vector_store.add_embedding(record)
                except Exception as e:
                    print(f"[WeeklyTrendScheduler] ⚠️ Ошибка сохранения в pgvector: {e}")

        print("[WeeklyTrendScheduler] ✅ Все еженедельные тренды успешно обновлены и закешированы!")

    async def get_trends_for_niche(self, niche: str) -> dict:
        """
        Мгновенно достает готовые тренды из Redis. 
        Если кэш пуст — сканирует на лету и сохраняет.
        """
        cache_key = f"niche_trend:{niche.lower().replace(' ', '_')}"
        cached = self.redis.get_cached_result("WeeklyTrends", cache_key)
        
        if cached:
            print(f"[WeeklyTrendScheduler] ⚡ Тренды для '{niche}' мгновенно отданы из кэша Redis.")
            return cached
            
        print(f"[WeeklyTrendScheduler] 🔍 Тренды для '{niche}' не найдены в кэше. Запускаем сбор на лету...")
        trends_data = await self.collector.fetch_niche_trends(niche)
        self.redis.set_cached_result("WeeklyTrends", cache_key, trends_data, ttl=604800)
        return trends_data

    async def run_cron_loop(self, interval_seconds: int = 604800):
        """
        Фоновый бесконечный цикл (Cron), который просыпается раз в неделю.
        """
        self.is_running = True
        while self.is_running:
            await self.update_all_trends()
            print(f"[WeeklyTrendScheduler] 💤 Сплю до следующей недели ({interval_seconds} сек)...")
            await asyncio.sleep(interval_seconds)
