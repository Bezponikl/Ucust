"""
File: ai/bridge/comfy_bridge.py
Асинхронный клиент для взаимодействия с ComfyUI (REST + WebSockets).
"""

from __future__ import annotations

import os
import uuid
import json
import logging
import asyncio
import httpx
import websockets
from typing import Optional, Dict, Any

try:
    from core.lazy_rendering_controller import ImageGenerationSpec
    from bridge.comfy_workflow_templates import WorkflowBuilder
except ImportError:
    from ai.core.lazy_rendering_controller import ImageGenerationSpec
    from ai.bridge.comfy_workflow_templates import WorkflowBuilder

logger = logging.getLogger("ComfyUIBridge")


class ComfyUIBridge:
    """
    Асинхронный мост для взаимодействия с ComfyUI:
    - Собирает Prompt API граф через WorkflowBuilder
    - Отправляет задачу в очередь ComfyUI (POST /prompt)
    - Слушает WebSocket поток событий (progress, executed, execution_error)
    - Скачивает готовый бинарник изображения (GET /view?filename=...)
    - Поддерживает dev_simulation_mode для безопасного выполнения без GPU/OOM
    """

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        h = host or os.getenv("COMFYUI_HOST", "127.0.0.1")
        p = port or int(os.getenv("COMFYUI_PORT", "8188"))
        self.server_address = f"{h}:{p}"
        self.client_id = str(uuid.uuid4())

    async def render_image(
        self,
        spec: ImageGenerationSpec,
        post_id: str,
        dev_simulation_mode: bool = False
    ) -> bytes:
        """
        Полный цикл: Сборка графа -> Отправка -> Ожидание по WS -> Скачивание бинарника.
        """
        if dev_simulation_mode:
            logger.info(f"🛠️ [DEV MODE] Симуляция рендера для поста {post_id}. (0 GPU)")
            await asyncio.sleep(0.5)
            # Возвращаем минимальный валидный 1x1 PNG байт-стрим с метаданными поста
            mock_bytes = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
                b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
                b"::UCUST_SIMULATED_RENDER::" + post_id.encode("utf-8")
            )
            return mock_bytes

        # 1. Формируем API-граф
        prompt_workflow = WorkflowBuilder.build_payload(
            prompt=spec.prompt,
            negative_prompt=spec.negative_prompt,
            width=spec.width,
            height=spec.height,
            seed=spec.seed,
            filename_prefix=f"ucust_post_{post_id}"
        )

        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        
        try:
            async with websockets.connect(ws_url, max_size=None) as websocket:
                # 2. Постановка в очередь ComfyUI (REST)
                prompt_id = await self._queue_prompt(prompt_workflow)
                logger.info(f"📤 Задача {prompt_id} отправлена в ComfyUI (Post ID: {post_id})")

                output_filename = None
                
                # 3. Слушаем события в реальном времени
                while True:
                    out = await websocket.recv()
                    if not isinstance(out, str):
                        continue
                        
                    message = json.loads(out)
                    msg_type = message.get("type")
                    data = message.get("data", {})

                    # Отслеживаем прогресс
                    if msg_type == "progress":
                        current = data.get("value", 0)
                        maximum = data.get("max", 1)
                        logger.debug(f"⏳ Рендер {prompt_id}: {current}/{maximum} шагов")

                    # Фиксация успешного завершения графа
                    if msg_type == "executed" and data.get("prompt_id") == prompt_id:
                        images = data.get("output", {}).get("images", [])
                        if images:
                            output_filename = images[0].get("filename")
                            logger.info(f"✅ Рендер завершен. Сохранен как: {output_filename}")
                        break
                        
                    # Обработка внутренних ошибок ComfyUI
                    if msg_type == "execution_error" and data.get("prompt_id") == prompt_id:
                        error_details = data.get("exception_message", "Unknown Error")
                        raise RuntimeError(f"ComfyUI Execution Error: {error_details}")

                if not output_filename:
                    raise RuntimeError("Событие executed получено, но имя файла отсутствует.")

                # 4. Скачивание готового изображения в ОЗУ
                return await self._fetch_image(output_filename)
                
        except (ConnectionRefusedError, OSError):
            logger.error(f"❌ ComfyUI недоступен по адресу {self.server_address}")
            raise RuntimeError(f"ComfyUI Server is offline at {self.server_address}.")
        except Exception as e:
            logger.error(f"❌ Ошибка в процессе рендера: {str(e)}")
            raise

    async def _queue_prompt(self, workflow: dict) -> str:
        """Отправка графа в очередь сервера."""
        url = f"http://{self.server_address}/prompt"
        payload = {"prompt": workflow, "client_id": self.client_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return response.json().get("prompt_id")

    async def _fetch_image(self, filename: str) -> bytes:
        """Скачивание бинарного файла из папки output ComfyUI."""
        url = f"http://{self.server_address}/view?filename={filename}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()
            return response.content
