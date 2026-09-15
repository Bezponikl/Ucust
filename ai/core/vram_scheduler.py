"""
Auto-Calibrating VRAM Scheduler & Resource-Aware Queue Dispatcher for UCust AI.
================================================================================
Features:
1. Low-overhead hardware VRAM polling via pynvml / PyTorch with Emulated fallback.
2. Real-time Spike Tracker (vram_spy) capturing peak memory consumption at 100ms ticks.
3. EMA (Exponential Moving Average) dynamic cost calibration per task type.
4. Non-blocking parallel I/O scraper pool (0.0 GB cost) & VRAM-gated GPU compute pool.
5. Startup GPU Warmup Routine to prevent cold-start CUDA context allocation OOMs.
6. Diagnostic telemetry for real-time dashboard monitoring.
"""

import asyncio
import logging
import os
import sys
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional

logger = logging.getLogger("vram_scheduler")


class VRAMScanner:
    """
    Сканер видеопамяти с 3-уровневым безопасным фоллбэком:
    1. pynvml (NVIDIA Management Library) — 0.05 мс вызов напрямую к драйверу.
    2. torch.cuda (PyTorch Runtime) — при недоступности pynvml.
    3. Emulated Mode — для локальной разработки без дискретной видеокарты.
    """

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self.backend = "unknown"
        self.gpu_name = "Emulated GPU (CPU Mode)"
        self._nvml_handle = None

        # 1. Попытка pynvml
        try:
            import pynvml
            pynvml.nvmlInit()
            self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
            raw_name = pynvml.nvmlDeviceGetName(self._nvml_handle)
            self.gpu_name = raw_name.decode("utf-8") if isinstance(raw_name, bytes) else str(raw_name)
            self.backend = "pynvml"
            logger.info(f"[VRAMScanner] 🟢 Инициализирован NVML backend для GPU: {self.gpu_name}")
            return
        except Exception as e:
            logger.debug(f"[VRAMScanner] NVML недоступен ({e}), пробуем PyTorch CUDA...")

        # 2. Попытка torch.cuda
        try:
            import torch
            if torch.cuda.is_available():
                self.gpu_name = torch.cuda.get_device_name(device_index)
                self.backend = "torch_cuda"
                logger.info(f"[VRAMScanner] 🟢 Инициализирован PyTorch CUDA backend для GPU: {self.gpu_name}")
                return
        except Exception as e:
            logger.debug(f"[VRAMScanner] PyTorch CUDA недоступен ({e}).")

        # 3. Emulated Mode
        self.backend = "emulated"
        self.gpu_name = "Emulated NVIDIA A100-SXM4-80GB"
        logger.info(f"[VRAMScanner] 🟡 Запущен в Emulated Mode ({self.gpu_name}) для локальной разработки.")

    def get_vram_info(self) -> Dict[str, float]:
        """Возвращает информацию о видеопамяти в гигабайтах."""
        if self.backend == "pynvml" and self._nvml_handle:
            try:
                import pynvml
                info = pynvml.nvmlDeviceGetMemoryInfo(self._nvml_handle)
                total_gb = info.total / (1024 ** 3)
                used_gb = info.used / (1024 ** 3)
                free_gb = info.free / (1024 ** 3)
                return {
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "usage_percent": round((used_gb / max(total_gb, 0.001)) * 100, 1),
                    "backend": "pynvml",
                    "gpu_name": self.gpu_name
                }
            except Exception:
                pass

        if self.backend == "torch_cuda":
            try:
                import torch
                free_bytes, total_bytes = torch.cuda.mem_get_info(self.device_index)
                total_gb = total_bytes / (1024 ** 3)
                free_gb = free_bytes / (1024 ** 3)
                used_gb = total_gb - free_gb
                return {
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "usage_percent": round((used_gb / max(total_gb, 0.001)) * 100, 1),
                    "backend": "torch_cuda",
                    "gpu_name": self.gpu_name
                }
            except Exception:
                pass

        # Emulated Mode: эмулируем 80GB карту с 28.5GB занятыми под базовые модели
        return {
            "total_gb": 80.0,
            "used_gb": 28.5,
            "free_gb": 51.5,
            "usage_percent": 35.6,
            "backend": "emulated",
            "gpu_name": self.gpu_name
        }


class AutoCalibratingVRAMScheduler:
    """
    Самообучающийся диспетчер VRAM с отслеживанием спайков и EMA-коррекцией весов.
    """

    _instance: Optional["AutoCalibratingVRAMScheduler"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AutoCalibratingVRAMScheduler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, scanner: Optional[VRAMScanner] = None, safety_margin_gb: float = 3.0):
        if getattr(self, "_initialized", False):
            return

        self.scanner = scanner or VRAMScanner()
        self.safety_margin_gb = safety_margin_gb  # Буфер безопасности от OOM

        # Стартовые пессимистичные веса задач (ГБ VRAM)
        self.dynamic_task_cost: Dict[str, float] = {
            "generate_image": 18.0,
            "generate_video": 26.0,
            "generate_post": 3.5,
            "direct_generate": 3.5,
            "generate_strategy": 2.0,
            "plan_content": 1.5,
            "critic_review": 1.5,
            "quick_vision": 3.0,
            "parse_telegram": 3.0,       # С учётом Moondream2 + OCR
            "universal_hub": 3.0,
            "analyze_documents": 1.5,
            # Чистые сетевые I/O задачи (0.0 GB VRAM)
            "parse_website": 0.0,
            "parse_vk": 0.0,
            "parse_geo": 0.0,
            "rag_query": 0.5,
            "rag_ingest": 0.5
        }

        self.active_gpu_tasks: Dict[str, Dict[str, Any]] = {}
        self.active_io_tasks: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._is_warmed_up = False
        self._initialized = True

        logger.info(
            f"[VRAMScheduler] 🧠 Auto-Calibrating VRAM Scheduler инициализирован. "
            f"Буфер безопасности: {self.safety_margin_gb} GB."
        )

    def get_task_estimated_cost(self, task_type: str) -> float:
        """Возвращает текущую откалиброванную стоимость задачи в ГБ VRAM."""
        return self.dynamic_task_cost.get(task_type, 1.5)

    def can_dispatch(self, task_type: str) -> bool:
        """Проверяет, достаточно ли видеопамяти для немедленного запуска задачи."""
        cost = self.get_task_estimated_cost(task_type)
        if cost == 0.0:
            return True  # I/O задачи всегда разрешены

        vram = self.scanner.get_vram_info()
        available_free = vram["free_gb"]
        
        # Учитываем виртуально зарезервированную память уже работающих GPU-задач
        active_reserved = sum(t.get("estimated_cost", 0.0) for t in self.active_gpu_tasks.values())
        effective_free = max(0.0, available_free - active_reserved)

        return effective_free >= (cost + self.safety_margin_gb)

    async def schedule_and_run(
        self,
        task_id: str,
        task_type: str,
        coroutine_func: Callable[..., Coroutine[Any, Any, Any]],
        *args,
        **kwargs
    ) -> Any:
        """
        Главный метод диспетчера:
        1. Если задача I/O (cost == 0) — запускает параллельно без ожидания.
        2. Если задача GPU (cost > 0) — ждёт наличия свободной VRAM, запускает фоновый Spike Tracker и выполняет.
        """
        cost = self.get_task_estimated_cost(task_type)

        # Режим А: Чистый I/O Bound (парсеры)
        if cost == 0.0:
            task_info = {"task_id": task_id, "task_type": task_type, "started_at": time.time()}
            self.active_io_tasks[task_id] = task_info
            try:
                return await coroutine_func(*args, **kwargs)
            finally:
                self.active_io_tasks.pop(task_id, None)

        # Режим Б: GPU Compute Bound (генерации / VLM / OCR)
        # Ожидаем доступности видеопамяти
        wait_start = time.time()
        while not self.can_dispatch(task_type):
            await asyncio.sleep(0.15)
            if time.time() - wait_start > 120.0:
                logger.warning(f"[VRAMScheduler] ⚠️ Таймаут ожидания VRAM для задачи {task_id} ({task_type})")
                break

        # Резервируем задачу в списке активных
        task_info = {
            "task_id": task_id,
            "task_type": task_type,
            "estimated_cost": cost,
            "started_at": time.time()
        }
        self.active_gpu_tasks[task_id] = task_info

        try:
            return await self._run_with_spike_tracking(task_id, task_type, coroutine_func, *args, **kwargs)
        finally:
            self.active_gpu_tasks.pop(task_id, None)

    async def _run_with_spike_tracking(
        self,
        task_id: str,
        task_type: str,
        coroutine_func: Callable[..., Coroutine[Any, Any, Any]],
        *args,
        **kwargs
    ) -> Any:
        """
        Выполняет задачу с фоновым «шпионом» VRAM (тик 100 мс) и калибрует dynamic_task_cost через EMA.
        """
        baseline_vram = self.scanner.get_vram_info()["used_gb"]
        peak_vram = baseline_vram
        is_running = True

        # 1. Фоновый шпион: опрашивает VRAM каждые 100 мс
        async def vram_spy():
            nonlocal peak_vram
            while is_running:
                try:
                    curr = self.scanner.get_vram_info()["used_gb"]
                    if curr > peak_vram:
                        peak_vram = curr
                    await asyncio.sleep(0.1)
                except Exception:
                    break

        spy_task = asyncio.create_task(vram_spy())
        t_start = time.time()
        result = None
        error = None

        try:
            result = await coroutine_func(*args, **kwargs)
            return result
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            is_running = False
            spy_task.cancel()
            try:
                await spy_task
            except asyncio.CancelledError:
                pass

            duration = round(time.time() - t_start, 3)
            actual_cost = max(0.0, round(peak_vram - baseline_vram, 2))

            # 2. Калибровка словаря весов
            old_cost = self.dynamic_task_cost.get(task_type, 2.0)
            if actual_cost > 0.3:  # Игнорируем фоновый шум <300MB
                if actual_cost > old_cost:
                    # Превысили ожидание ➔ немедленно повышаем с запасом 500 МБ
                    new_cost = round(actual_cost + 0.5, 2)
                    logger.info(
                        f"[VRAMScheduler] 📈 Всплеск VRAM в '{task_type}': {actual_cost} GB > {old_cost} GB. "
                        f"Новый лимит: {new_cost} GB"
                    )
                else:
                    # Потратили меньше ➔ плавно смягчаем по формуле EMA (85% старое + 15% новое)
                    new_cost = round((old_cost * 0.85) + (actual_cost * 0.15), 2)

                self.dynamic_task_cost[task_type] = new_cost

            # Записываем в историю
            self.history.append({
                "task_id": task_id,
                "task_type": task_type,
                "duration_sec": duration,
                "baseline_vram_gb": baseline_vram,
                "peak_vram_gb": peak_vram,
                "actual_cost_gb": actual_cost,
                "calibrated_cost_gb": self.dynamic_task_cost.get(task_type, old_cost),
                "timestamp": time.time(),
                "success": error is None
            })
            if len(self.history) > 100:
                self.history.pop(0)

    async def warmup_gpu_pipelines(self, orchestrator: Optional[Any] = None):
        """
        Процедура прогрева (Warmup):
        Выполняет микро-прогон по ключевым моделям при старте сервера,
        чтобы PyTorch аллоцировал CUDA-контекст до прихода реальных пользователей.
        """
        if self._is_warmed_up:
            return

        logger.info("[VRAMScheduler] 🔥 Запуск прогрева GPU-пайплайнов (Warmup Routine)...")
        t0 = time.time()

        try:
            # 1. Прогрев LLM / Orchestrator (легкий пустой прогон)
            if orchestrator:
                try:
                    await orchestrator.execute_task(
                        task_type="critic_review",
                        user_data={"text": "Тест прогрева", "strictness": 0.5},
                        session_id="warmup_llm"
                    )
                    logger.info("[VRAMScheduler]  • LLM / Critic пайплайн прогрет.")
                except Exception as e:
                    logger.debug(f"[VRAMScheduler] Warmup LLM skipped: {e}")

            self._is_warmed_up = True
            logger.info(f"[VRAMScheduler] ✅ Прогрев завершен за {round(time.time() - t0, 2)} сек.")
        except Exception as e:
            logger.warning(f"[VRAMScheduler] ⚠️ Ошибка во время прогрева: {e}")

    def get_diagnostics(self) -> Dict[str, Any]:
        """Возвращает полную телеметрию для дашборда мониторинга."""
        vram = self.scanner.get_vram_info()
        return {
            "status": "healthy",
            "gpu_device": vram.get("gpu_name", self.scanner.gpu_name),
            "backend": vram.get("backend", self.scanner.backend),
            "vram": {
                "total_gb": vram["total_gb"],
                "used_gb": vram["used_gb"],
                "free_gb": vram["free_gb"],
                "usage_percent": vram["usage_percent"],
                "safety_margin_gb": self.safety_margin_gb
            },
            "active_workers": {
                "gpu_tasks_running": len(self.active_gpu_tasks),
                "io_scrapers_running": len(self.active_io_tasks),
                "gpu_active_tasks": list(self.active_gpu_tasks.values()),
                "io_active_tasks": list(self.active_io_tasks.values())
            },
            "learned_task_costs": self.dynamic_task_cost,
            "recent_executions_count": len(self.history),
            "is_warmed_up": self._is_warmed_up
        }
