"""
Mock Async Generation Queue Manager for UCust AI Service.
Simulates background GPU queue processing and reverse HTTP webhook callbacks.
"""

import asyncio
import os
import time
import uuid
from typing import Any, Dict, Optional

from ai_mock.mock_orchestrator import MockUnifiedOrchestrator


class MockAsyncGenerationQueueManager:
    def __init__(self, orchestrator: Optional[MockUnifiedOrchestrator] = None):
        self.orchestrator = orchestrator or MockUnifiedOrchestrator()
        self.tasks_db: Dict[str, Dict[str, Any]] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def start_worker(self):
        if not self.is_running:
            self.is_running = True
            self.worker_task = asyncio.create_task(self._worker_loop())

    async def stop_worker(self):
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

    async def enqueue(self, payload: Dict[str, Any]) -> str:
        task_id = payload.get("task_id") or f"task_{uuid.uuid4().hex[:8]}"
        user_id = payload.get("user_id", "default_user")
        session_id = payload.get("session_id") or f"sess_{uuid.uuid4().hex[:8]}"
        callback_url = payload.get("callback_url")

        task_record = {
            "task_id": task_id,
            "user_id": user_id,
            "session_id": session_id,
            "status": "QUEUED",
            "progress": 0,
            "created_at": time.time(),
            "updated_at": time.time(),
            "callback_url": callback_url,
            "payload": payload,
            "result": None,
            "error": None
        }

        self.tasks_db[task_id] = task_record
        await self.queue.put(task_id)
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        record = self.tasks_db.get(task_id)
        if not record:
            return None
        return {
            "task_id": record["task_id"],
            "status": record["status"],
            "progress": record["progress"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "result": record["result"],
            "error": record["error"]
        }

    async def _worker_loop(self):
        while self.is_running:
            try:
                task_id = await self.queue.get()
                record = self.tasks_db.get(task_id)
                if not record:
                    self.queue.task_done()
                    continue

                # 1. Update to PROCESSING
                record["status"] = "PROCESSING"
                record["progress"] = 25
                record["updated_at"] = time.time()
                await asyncio.sleep(0.3)  # Simulate brief processing

                # 2. Execute Mock Generation
                record["progress"] = 75
                payload = record["payload"]
                task_type = payload.get("task_type", "generate_post")
                result_data = await self.orchestrator.execute_task(
                    task_type=task_type,
                    user_data=payload,
                    session_id=record["session_id"]
                )

                # 3. Mark COMPLETED
                record["status"] = "COMPLETED"
                record["progress"] = 100
                record["result"] = result_data
                record["updated_at"] = time.time()

                # 4. Trigger Reverse Webhook Push if callback_url provided
                cb_url = record.get("callback_url") or os.getenv("BACKEND_COLLECTOR_CALLBACK_URL")
                if cb_url:
                    asyncio.create_task(self._send_webhook(cb_url, record))

                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if task_id in self.tasks_db:
                    self.tasks_db[task_id]["status"] = "FAILED"
                    self.tasks_db[task_id]["error"] = str(e)
                    self.tasks_db[task_id]["updated_at"] = time.time()

    async def _send_webhook(self, callback_url: str, record: Dict[str, Any]):
        try:
            import httpx
            secret = os.getenv("INTERNAL_API_SECRET", "ucust-super-secret-service-token-2026")
            headers = {
                "Content-Type": "application/json",
                "X-Internal-Secret": secret
            }
            webhook_payload = {
                "task_id": record["task_id"],
                "user_id": record["user_id"],
                "session_id": record["session_id"],
                "task_type": record["payload"].get("task_type", "generate_post"),
                "status": "COMPLETED",
                "timestamp": int(time.time()),
                "result": record["result"]
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(callback_url, json=webhook_payload, headers=headers)
        except Exception:
            # Safe ignore if backend mock receiver is unreachable during testing
            pass
