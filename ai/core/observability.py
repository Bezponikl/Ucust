"""
File: ai/core/observability.py
Сквозной модуль телеметрии, метрик Prometheus и трейсинга ошибок Sentry для UCust AI.
"""

from __future__ import annotations

import os
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("Observability")

# ------------------------------------------------------------------------------
# 1. Sentry Integration & Breadcrumb Tracking
# ------------------------------------------------------------------------------

def init_sentry():
    """
    Инициализация Sentry SDK для FastAPI и Celery с фильтрацией PII и трейсингом.
    """
    sentry_dsn = os.getenv("SENTRY_DSN", "").strip()
    if not sentry_dsn:
        logger.info("ℹ️ Sentry DSN не задан. Автоматический перехват ошибок Sentry отключен.")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        def before_send_filter(event, hint):
            # Фильтрация PII и чувствительных заголовков
            if "request" in event and "headers" in event["request"]:
                headers = event["request"]["headers"]
                if "authorization" in headers:
                    headers["authorization"] = "[REDACTED_JWT]"
                if "x-internal-secret" in headers:
                    headers["x-internal-secret"] = "[REDACTED_SECRET]"
            return event

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            release=f"ucust-ai@{os.getenv('APP_VERSION', '2.5.0')}",
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                CeleryIntegration(monitor_beat_tasks=True)
            ],
            before_send=before_send_filter,
            send_default_pii=False,
            attach_stacktrace=True
        )
        logger.info("🛡️ Sentry SDK успешно подключен (FastAPI + Celery).")
    except ImportError:
        logger.warning("⚠️ Пакет 'sentry-sdk' не установлен (pip install sentry-sdk).")
    except Exception as exc:
        logger.error(f"❌ Ошибка инициализации Sentry: {exc}")


def add_sentry_breadcrumb(category: str, message: str, data: Optional[Dict[str, Any]] = None, level: str = "info"):
    """Добавляет контекстную хлебную крошку в трейс Sentry."""
    try:
        import sentry_sdk
        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            data=data or {},
            level=level
        )
    except Exception:
        pass


def capture_sentry_exception(exc: Exception, tags: Optional[Dict[str, str]] = None, extra: Optional[Dict[str, Any]] = None):
    """Явный перехват и отправка критического исключения в Sentry с тегами."""
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if tags:
                for k, v in tags.items():
                    scope.set_tag(k, v)
            if extra:
                for k, v in extra.items():
                    scope.set_extra(k, v)
            sentry_sdk.capture_exception(exc)
    except Exception:
        pass


# ------------------------------------------------------------------------------
# 2. Prometheus Metrics & Custom Gauges
# ------------------------------------------------------------------------------

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST,
        CollectorRegistry, REGISTRY
    )
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


if HAS_PROMETHEUS:
    # 1. HTTP Метрики
    HTTP_REQUESTS_TOTAL = Counter(
        "ucust_http_requests_total",
        "Общее количество HTTP-запросов к шлюзу FastAPI",
        ["method", "endpoint", "status_code"]
    )
    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        "ucust_http_request_duration_seconds",
        "Латентность обработки HTTP-запросов (секунды)",
        ["method", "endpoint"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
    )

    # 2. Celery Очереди и Задачи
    CELERY_QUEUE_DEPTH = Gauge(
        "ucust_celery_queue_depth",
        "Текущая глубина очередей задач Celery",
        ["queue"]
    )
    TASK_EXECUTION_SECONDS = Histogram(
        "ucust_task_execution_seconds",
        "Длительность выполнения задач воркерами",
        ["task_type"],
        buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0)
    )
    TASK_COMPLETION_TOTAL = Counter(
        "ucust_task_completion_total",
        "Количество завершенных задач воркеров",
        ["task_type", "status"]
    )

    # 3. VRAM & Аппаратные метрики
    ACTIVE_VRAM_ALLOCATION_MB = Gauge(
        "ucust_active_vram_allocation_mb",
        "Текущая оценка аллокации VRAM графического ускорителя (MB)",
        ["device_id"]
    )
    RAG_QUERY_LATENCY_SECONDS = Histogram(
        "ucust_rag_query_latency_seconds",
        "Скорость семантического поиска в PostgreSQL pgvector / SQLite",
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
    )
else:
    HTTP_REQUESTS_TOTAL = None
    HTTP_REQUEST_DURATION_SECONDS = None
    CELERY_QUEUE_DEPTH = None
    TASK_EXECUTION_SECONDS = None
    TASK_COMPLETION_TOTAL = None
    ACTIVE_VRAM_ALLOCATION_MB = None
    RAG_QUERY_LATENCY_SECONDS = None


# In-memory fallback metrics store
_IN_MEMORY_METRICS: Dict[str, Any] = {
    "http_requests": {},
    "queue_depths": {},
    "vram_allocations": {},
    "tasks": {}
}


class ObservabilityManager:
    """Унифицированный интерфейс управления метриками и телеметрией."""

    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration_sec: float):
        if HAS_PROMETHEUS and HTTP_REQUESTS_TOTAL:
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(duration_sec)
        else:
            key = f'{method}_{endpoint}_{status_code}'
            _IN_MEMORY_METRICS["http_requests"][key] = _IN_MEMORY_METRICS["http_requests"].get(key, 0) + 1

    @staticmethod
    def set_queue_depth(queue_name: str, count: int):
        if HAS_PROMETHEUS and CELERY_QUEUE_DEPTH:
            CELERY_QUEUE_DEPTH.labels(queue=queue_name).set(count)
        else:
            _IN_MEMORY_METRICS["queue_depths"][queue_name] = count

    @staticmethod
    def record_task_duration(task_type: str, duration_sec: float, status: str = "success"):
        if HAS_PROMETHEUS and TASK_EXECUTION_SECONDS:
            TASK_EXECUTION_SECONDS.labels(task_type=task_type).observe(duration_sec)
            TASK_COMPLETION_TOTAL.labels(task_type=task_type, status=status).inc()
        else:
            key = f'{task_type}_{status}'
            _IN_MEMORY_METRICS["tasks"][key] = _IN_MEMORY_METRICS["tasks"].get(key, 0) + 1

    @staticmethod
    def set_vram_allocation(vram_mb: int, device_id: str = "cuda:0"):
        if HAS_PROMETHEUS and ACTIVE_VRAM_ALLOCATION_MB:
            ACTIVE_VRAM_ALLOCATION_MB.labels(device_id=device_id).set(vram_mb)
        else:
            _IN_MEMORY_METRICS["vram_allocations"][device_id] = vram_mb

    @staticmethod
    def record_rag_latency(duration_sec: float):
        if HAS_PROMETHEUS and RAG_QUERY_LATENCY_SECONDS:
            RAG_QUERY_LATENCY_SECONDS.observe(duration_sec)

    @staticmethod
    def export_metrics() -> tuple[bytes, str]:
        """Возвращает сырые метрики в формате Prometheus."""
        if HAS_PROMETHEUS:
            return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
        
        # Fallback генератор Prometheus-формата
        lines = [
            "# HELP ucust_http_requests_total Total HTTP requests",
            "# TYPE ucust_http_requests_total counter"
        ]
        for k, v in _IN_MEMORY_METRICS["http_requests"].items():
            parts = k.split("_", 2)
            if len(parts) == 3:
                lines.append(f'ucust_http_requests_total{{method="{parts[0]}",endpoint="{parts[1]}",status_code="{parts[2]}"}} {v}')
            else:
                lines.append(f'ucust_http_requests_total {v}')
        
        lines.extend([
            "# HELP ucust_celery_queue_depth Celery queue depth",
            "# TYPE ucust_celery_queue_depth gauge"
        ])
        for q, d in _IN_MEMORY_METRICS["queue_depths"].items():
            lines.append(f'ucust_celery_queue_depth{{queue="{q}"}} {d}')
            
        lines.extend([
            "# HELP ucust_active_vram_allocation_mb Active VRAM MB",
            "# TYPE ucust_active_vram_allocation_mb gauge"
        ])
        for dev, vram in _IN_MEMORY_METRICS["vram_allocations"].items():
            lines.append(f'ucust_active_vram_allocation_mb{{device_id="{dev}"}} {vram}')
            
        output = "\n".join(lines) + "\n"
        return output.encode("utf-8"), "text/plain; version=0.0.4; charset=utf-8"
