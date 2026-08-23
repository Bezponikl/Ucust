import json
from typing import Any, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class RedisCacheManager:
    """
    Менеджер кэширования этапов Оркестратора.
    Использует Redis для хранения State Hashing.
    """
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.connected = False
        self._fallback_cache = {}
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
                # Проверяем соединение
                self.redis_client.ping()
                self.connected = True
                print("[RedisCacheManager] 🟢 Успешное подключение к Redis.")
            except redis.ConnectionError:
                print("[RedisCacheManager] ⚠️ Redis недоступен по сети. Fallback на In-Memory.")
        else:
            print("[RedisCacheManager] ⚠️ Модуль 'redis' не установлен (pip install redis). Fallback на In-Memory.")

    def get_cached_result(self, action: str, payload_hash: str) -> Optional[dict]:
        """
        Проверяет, есть ли уже вычисленный результат для данного действия и хэша.
        """
        key = f"trace:{action}:{payload_hash}"
        if self.connected:
            cached = self.redis_client.get(key)
            if cached:
                print(f"[RedisCacheManager] ⚡ Найдено в кэше! Action: {action}, Hash: {payload_hash[:8]}")
                return json.loads(cached)
        else:
            cached = self._fallback_cache.get(key)
            if cached:
                print(f"[RedisCacheManager] ⚡ Найдено в локальном кэше! Action: {action}, Hash: {payload_hash[:8]}")
                return cached
        return None

    def set_cached_result(self, action: str, payload_hash: str, result: Any, ttl: int = 3600):
        """
        Сохраняет результат работы агента в Redis (по умолчанию на 1 час).
        """
        key = f"trace:{action}:{payload_hash}"
        if self.connected:
            self.redis_client.setex(key, ttl, json.dumps(result, ensure_ascii=False))
        else:
            self._fallback_cache[key] = result
            
        print(f"[RedisCacheManager] 💾 Результат закеширован. Action: {action}, Hash: {payload_hash[:8]}")
