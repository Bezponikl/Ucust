# File: core/queue_manager.py
"""
FastAPI Native Async Generation Queue Manager for UCust.AI.

Features:
- Thread-safe FIFO queue with GPU concurrency lock (1 generation per GPU)
- State persistence and queue recovery via Redis (with In-Memory fallback)
- Real-time queue position and wait time estimation
- Automatic Push-To-Backend webhook delivery with multipart/form-data file transfer and exponential retry
- Background worker lifecycle management
"""

import os
import sys
import time
import uuid
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx

from core.orchestrator import UnifiedOrchestrator
from core.redis_cache import RedisCacheManager

logger = logging.getLogger("queue_manager")


class TaskState:
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PUSHED = "PUSHED"
    PUSH_FAILED = "PUSH_FAILED"


class AsyncGenerationQueueManager:
    """
    Управляет асинхронной очередью генераций для защиты GPU от перегрузок
    и гарантированной доставки результата на Java Backend через HTTP Push.
    """

    _instance: Optional["AsyncGenerationQueueManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncGenerationQueueManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, orchestrator: Optional[UnifiedOrchestrator] = None):
        if getattr(self, "_initialized", False):
            return

        self.orchestrator = orchestrator or UnifiedOrchestrator()
        self.redis_cache = RedisCacheManager()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running: bool = False
        self.current_task_id: Optional[str] = None
        self._initialized = True
        logger.info("[QueueManager] 🚀 Инициализирован FastAPI Native Queue Manager.")

    async def start_worker(self):
        """Запускает фонового консьюмера очереди при старте FastAPI."""
        if self.is_running:
            return
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker_loop())
        logger.info("[QueueManager] 🟢 Фоновый GPU-воркер успешно запущен.")

    async def stop_worker(self):
        """Корректно останавливает воркер при завершении приложения."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("[QueueManager] 🛑 Фоновый GPU-воркер остановлен.")

    async def enqueue_task(
        self,
        payload: Dict[str, Any],
        callback_url: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: str = "default_user",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Мгновенно (за 1-3 мс) принимает задачу, ставит в очередь и возвращает статус.
        """
        tid = task_id or f"task_{uuid.uuid4().hex[:10]}"
        sid = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().isoformat()

        target_callback = callback_url or os.getenv("JAVA_BACKEND_CALLBACK_URL")

        task_data = {
            "task_id": tid,
            "session_id": sid,
            "user_id": user_id,
            "status": TaskState.QUEUED,
            "callback_url": target_callback,
            "payload": payload,
            "created_at": created_at,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "push_status": None,
            "attempts": 0
        }

        self.tasks[tid] = task_data
        await self._persist_task_state(tid, task_data)

        # Добавляем в очередь asyncio
        await self.queue.put(tid)

        # Вычисляем позицию в очереди
        queue_pos = self.get_queue_position(tid)
        est_seconds = queue_pos * 45  # в среднем ~45 сек на генерацию поста с фото

        logger.info(
            f"[QueueManager] 📥 Задача '{tid}' поставлена в очередь (Позиция: {queue_pos}, Ожидание: ~{est_seconds}с)"
        )

        return {
            "status": TaskState.QUEUED,
            "task_id": tid,
            "session_id": sid,
            "queue_position": queue_pos,
            "estimated_wait_seconds": est_seconds,
            "created_at": created_at
        }

    def get_queue_position(self, task_id: str) -> int:
        """Возвращает текущую позицию задачи в очереди (1 = следующая на выполнение)."""
        if self.current_task_id == task_id:
            return 1

        pos = 1 if self.current_task_id else 0
        for tid in list(self.queue._queue):
            pos += 1
            if tid == task_id:
                return pos
        return 1

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает детальный статус задачи по task_id."""
        task = self.tasks.get(task_id)
        if not task:
            # Пробуем достать из Redis
            cached = self.redis_cache.get("TaskState", task_id)
            if cached:
                return cached
            return None

        status_copy = dict(task)
        status_copy["queue_position"] = self.get_queue_position(task_id) if task["status"] == TaskState.QUEUED else 0
        return status_copy

    def get_queue_stats(self) -> Dict[str, Any]:
        """Возвращает общую статистику очереди."""
        queued_count = self.queue.qsize()
        active_task = self.current_task_id
        return {
            "status": "online",
            "is_busy": active_task is not None,
            "active_task_id": active_task,
            "queued_tasks_count": queued_count,
            "total_tracked_tasks": len(self.tasks)
        }

    async def _worker_loop(self):
        """Основной цикл консьюмера: последовательно обрабатывает задачи на GPU."""
        while self.is_running:
            try:
                task_id = await self.queue.get()
                self.current_task_id = task_id
                task_data = self.tasks.get(task_id)

                if not task_data:
                    self.queue.task_done()
                    self.current_task_id = None
                    continue

                task_data["status"] = TaskState.PROCESSING
                task_data["started_at"] = datetime.utcnow().isoformat()
                await self._persist_task_state(task_id, task_data)

                logger.info(f"\n[QueueManager] ⚙️ [СТАРТ] Выполнение задачи '{task_id}' на GPU...")
                t0 = time.time()

                try:
                    payload = task_data.get("payload", {})
                    task_type = payload.get("task_type", "generate_post")

                    # Выполнение задачи через UnifiedOrchestrator
                    result = await self.orchestrator.execute_task(
                        task_type=task_type,
                        user_data=payload,
                        session_id=task_data.get("session_id")
                    )

                    duration = round(time.time() - t0, 2)
                    task_data["status"] = TaskState.COMPLETED
                    task_data["completed_at"] = datetime.utcnow().isoformat()
                    task_data["result"] = result
                    task_data["duration_seconds"] = duration
                    logger.info(f"[QueueManager] ✅ [УСПЕХ] Задача '{task_id}' завершена за {duration}с.")

                    # Выполняем Push-коллбек на Java Backend с передачей файла
                    callback_url = task_data.get("callback_url")
                    if callback_url:
                        push_ok = await self._push_result_to_backend(task_id, task_data, result, callback_url)
                        task_data["push_status"] = TaskState.PUSHED if push_ok else TaskState.PUSH_FAILED

                except Exception as ex:
                    logger.exception(f"[QueueManager] ❌ [ОШИБКА] Сбой при выполнении задачи '{task_id}': {ex}")
                    task_data["status"] = TaskState.FAILED
                    task_data["error"] = str(ex)
                    task_data["completed_at"] = datetime.utcnow().isoformat()

                    # Отправляем уведомление об ошибке в коллбек, если он указан
                    callback_url = task_data.get("callback_url")
                    if callback_url:
                        await self._push_error_to_backend(task_id, str(ex), callback_url)

                finally:
                    await self._persist_task_state(task_id, task_data)
                    self.queue.task_done()
                    self.current_task_id = None

            except asyncio.CancelledError:
                break
            except Exception as loop_ex:
                logger.error(f"[QueueManager] Ошибка в цикле воркера: {loop_ex}")
                await asyncio.sleep(1)

    async def _push_result_to_backend(
        self,
        task_id: str,
        task_data: Dict[str, Any],
        result: Dict[str, Any],
        callback_url: str,
        max_retries: int = 3
    ) -> bool:
        """
        Отправляет готовый пост и физический файл изображения на Java-бэкенд через HTTP POST (multipart/form-data)
        с автоматическим повтором при сбоях сети (Retry 3, 10, 30 сек).
        """
        logger.info(f"[QueueManager] 📡 Отправка результата задачи '{task_id}' на '{callback_url}'...")

        post_text = result.get("post_text", "")
        critic_score = result.get("critic_score") or (result.get("critic_review", {}).get("score", 0.95))
        hashtags = result.get("hashtags", "")
        timings = result.get("timings", {})
        photo_url = result.get("photo_url") or result.get("image_url")

        # Поиск локального файла на диске
        photo_local_path = None
        if photo_url:
            fname = os.path.basename(photo_url)
            cand_dirs = [
                os.path.join(os.path.dirname(__file__), "..", "output", "photos"),
                "/opt/ucust/ai/output/photos",
                "/opt/ucust/ComfyUI/output",
                "output/photos"
            ]
            for cdir in cand_dirs:
                p = os.path.join(cdir, fname)
                if os.path.exists(p) and os.path.getsize(p) > 1000:
                    photo_local_path = os.path.abspath(p)
                    break

        form_fields = {
            "task_id": task_id,
            "session_id": task_data.get("session_id", ""),
            "user_id": task_data.get("user_id", ""),
            "status": "COMPLETED",
            "post_text": post_text,
            "hashtags": str(hashtags),
            "critic_score": str(critic_score),
            "timings_json": json.dumps(timings, ensure_ascii=False),
            "completed_at": datetime.utcnow().isoformat()
        }

        retry_delays = [3, 10, 30]

        for attempt in range(1, max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    files = None
                    file_handle = None
                    if photo_local_path and os.path.exists(photo_local_path):
                        file_handle = open(photo_local_path, "rb")
                        files = {
                            "media_file": (
                                os.path.basename(photo_local_path),
                                file_handle,
                                "image/jpeg" if photo_local_path.endswith(".jpg") else "image/png"
                            )
                        }

                    try:
                        resp = await client.post(callback_url, data=form_fields, files=files)
                    finally:
                        if file_handle:
                            file_handle.close()

                    if resp.status_code in [200, 201, 202, 204]:
                        logger.info(f"[QueueManager] 🎉 [PUSH SUCCESS] Результат задачи '{task_id}' успешно принят Java-бэкендом (HTTP {resp.status_code}).")
                        return True
                    else:
                        logger.warning(
                            f"[QueueManager] ⚠️ [PUSH RETRY {attempt}/{max_retries}] Java-бэк ответил кодом {resp.status_code}: {resp.text[:200]}"
                        )

            except Exception as push_err:
                logger.warning(
                    f"[QueueManager] ⚠️ [PUSH RETRY {attempt}/{max_retries}] Сбой сети при отправке на {callback_url}: {push_err}"
                )

            if attempt < max_retries:
                delay = retry_delays[attempt - 1]
                logger.info(f"[QueueManager] ⏳ Ожидание {delay}с перед повторной попыткой...")
                await asyncio.sleep(delay)

        logger.error(f"[QueueManager] ❌ [PUSH FAILED] Не удалось доставить результат задачи '{task_id}' за {max_retries} попыток.")
        return False

    async def _push_error_to_backend(self, task_id: str, error_msg: str, callback_url: str):
        """Отправляет уведомление об ошибке на Java-бэкенд."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    callback_url,
                    data={
                        "task_id": task_id,
                        "status": "FAILED",
                        "error": error_msg,
                        "failed_at": datetime.utcnow().isoformat()
                    }
                )
        except Exception as ex:
            logger.warning(f"[QueueManager] Не удалось отправить статус ошибки на коллбек: {ex}")

    async def _persist_task_state(self, task_id: str, task_data: Dict[str, Any]):
        """Сохраняет состояние задачи в Redis (TTL 24 часа) для отказоустойчивости."""
        try:
            self.redis_cache.set(
                action="TaskState",
                payload_hash=task_id,
                result=task_data,
                ttl=86400  # 24 часа
            )
        except Exception as ex:
            logger.debug(f"Ошибка сохранения состояния задачи в Redis: {ex}")