"""
AI Service Gateway (FastAPI)
Единый шлюз подключения ИИ-агентов UCust к Бэкенду и Фронтенду.
Предоставляет REST API и WebSockets для real-time онбординга.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from fastapi.staticfiles import StaticFiles
import os

from storage.db import DatabaseFactory
from core.orchestrator import UnifiedOrchestrator, SecurityGuard
from rag.pipeline import CleanRAGPipeline
from rag.models import Document

# -------------------------------------------------------------------
# 1. Pydantic Модели запросов и ответов (API Contract)
# -------------------------------------------------------------------

class TaskRequest(BaseModel):
    user_id: str = Field("default_user", example="usr_94812", description="Идентификатор пользователя")
    session_id: Optional[str] = Field(None, example="sess_abc123", description="ID сессии диалога")
    task_type: str = Field(..., example="generate_post", description="Тип задачи: generate_post | generate_image | prepare_holiday_greeting | get_trends | rag_query")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Параметры задачи")


class TaskResponse(BaseModel):
    status: str = Field(..., example="success")
    task_id: str = Field(..., example="task_38df92a")
    session_id: str = Field(..., example="sess_abc123")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TrendResponse(BaseModel):
    status: str = "success"
    niche: str
    trends: Any
    cached: bool = True


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., example="Сезонный тыквенный латте с корицей и круассан")
    niche: str = Field("Кофейня", example="Кофейня")
    aspect_ratio: str = Field("1:1", example="1:1")
    style: str = Field("photorealistic", example="photorealistic")
    brand_colors: Optional[List[str]] = None


class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="Сколько стоит тариф Pro?")
    top_k: int = Field(5, ge=1, le=20)


class RAGIngestRequest(BaseModel):
    documents: List[Dict[str, Any]] = Field(..., description="Список документов для базы знаний")


# -------------------------------------------------------------------
# 2. Инициализация FastAPI приложения
# -------------------------------------------------------------------

app = FastAPI(
    title="UCust AI Service Gateway",
    description="Единая точка входа для бэкенда и фронтенда к команде автономных ИИ-агентов UCust.",
    version="2.1.0"
)

# Разрешаем CORS для любых фронтендов (React, Next.js, Vue, Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача сгенерированных фото и медиа файлов
output_static_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "output"))
os.makedirs(os.path.join(output_static_dir, "photos"), exist_ok=True)
app.mount("/output", StaticFiles(directory=output_static_dir), name="output")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storage.models import Base

db_engine = create_engine("sqlite:///./ai_smm_dev.db", echo=False)
Base.metadata.create_all(bind=db_engine)
SessionLocal = sessionmaker(bind=db_engine)
db_session = SessionLocal()
orchestrator = UnifiedOrchestrator(db_session=db_session)
rag_pipeline = CleanRAGPipeline(min_confidence_threshold=0.65)


# -------------------------------------------------------------------
# 3. REST API Эндпоинты
# -------------------------------------------------------------------

@app.get("/api/v1/ai/health", tags=["System"])
async def health_check():
    """Проверка доступности ИИ-шлюза и агентов."""
    return {
        "status": "healthy",
        "service": "UCust AI Gateway",
        "agents": ["Interviewer", "Analyst", "Saiga Copywriter", "Visual Director LTX-2", "ToV Gatekeeper"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ai/task", response_model=TaskResponse, tags=["AI Tasks"])
async def execute_ai_task(request: TaskRequest):
    """
    Универсальный эндпоинт выполнения задач агентами.
    Бэкенд передает task_type и payload, Оркестратор распределяет нагрузку.
    """
    session_id = request.session_id or f"sess_{uuid.uuid4().hex[:8]}"
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # 1. Проверка безопасности входящих данных
    payload_str = json.dumps(request.payload, ensure_ascii=False)
    if not SecurityGuard.check_user_input(payload_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violation: обнаружен запрещенный запрос или попытка инъекции."
        )

    # 2. Передача в UnifiedOrchestrator
    try:
        result = await orchestrator.execute_task(
            task_type=request.task_type,
            user_data=request.payload,
            session_id=session_id
        )
        
        if result.get("status") == "error":
            return TaskResponse(
                status="error",
                task_id=task_id,
                session_id=session_id,
                error=result.get("message", "Ошибка выполнения задачи")
            )
            
        return TaskResponse(
            status="success",
            task_id=task_id,
            session_id=session_id,
            data=result
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка оркестратора: {str(e)}"
        )


@app.get("/api/v1/ai/trends", response_model=TrendResponse, tags=["Trends & Analytics"])
async def get_weekly_trends(niche: str = Query("IT и Автоматизация", description="Ниша бизнеса")):
    """
    Отдача закешированных недельных трендов из Redis за 3-5 миллисекунд.
    """
    session_id = f"trend_req_{uuid.uuid4().hex[:6]}"
    result = await orchestrator.execute_task(
        task_type="get_trends",
        user_data={"niche": niche},
        session_id=session_id
    )
    
    return TrendResponse(
        niche=niche,
        trends=result.get("trends", ""),
        cached=True
    )


@app.get("/api/v1/ai/analytics/graphs", tags=["Trends & Analytics"])
async def get_frontend_graphs():
    """
    Безопасные агрегированные данные для графиков и дашбордов фронтенда (без PII).
    """
    graphs_data = orchestrator.get_frontend_graph_data()
    return {
        "status": "success",
        "data": graphs_data
    }


@app.post("/api/v1/ai/generate-image", tags=["Visual & Media"])
async def generate_smm_image(request: ImageGenerateRequest):
    """
    Генерация качественного SMM-изображения для постов, баннеров и сторис.
    """
    result = await orchestrator.execute_task(
        task_type="generate_image",
        user_data=request.dict(),
        session_id=f"img_{uuid.uuid4().hex[:8]}"
    )
    return result


@app.post("/api/v1/ai/rag/query", tags=["Knowledge Base RAG"])
async def query_knowledge_base(request: RAGQueryRequest):
    """
    Поиск по базе знаний через Clean RAG с защитой от галлюцинаций.
    """
    rag_context = await rag_pipeline.query_async(request.query, top_k_retrieval=request.top_k)
    return {
        "query": rag_context.query,
        "has_sufficient_context": rag_context.has_sufficient_context,
        "top_score": round(rag_context.top_score, 3),
        "context": rag_context.formatted_context if rag_context.has_sufficient_context else None,
        "fallback_message": rag_context.fallback_message
    }


@app.post("/api/v1/ai/rag/ingest", tags=["Knowledge Base RAG"])
async def ingest_knowledge_base(request: RAGIngestRequest):
    """
    Загрузка и индексация документов в локальный Clean RAG.
    """
    docs = []
    for item in request.documents:
        docs.append(
            Document(
                doc_id=item.get("doc_id", str(uuid.uuid4())),
                text=item.get("text", ""),
                source=item.get("source", "api_upload"),
                metadata=item.get("metadata", {})
            )
        )
    indexed_count = await rag_pipeline.ingest_documents_async(docs)
    return {
        "status": "success",
        "indexed_chunks_count": indexed_count
    }


# -------------------------------------------------------------------
# 4. WebSocket: Живой онбординг и Real-time стриминг для Фронтенда
# -------------------------------------------------------------------

class ConnectionManager:
    """Менеджер активных WebSocket подключений."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"[WebSocket] 🔌 Клиент подключен к сессии: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"[WebSocket] 🔌 Клиент отключен: {session_id}")

    async def send_event(self, session_id: str, step: str, payload: Any):
        if session_id in self.active_connections:
            message = {
                "session_id": session_id,
                "step": step,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload
            }
            await self.active_connections[session_id].send_text(json.dumps(message, ensure_ascii=False))

ws_manager = ConnectionManager()


@app.websocket("/ws/ai/session/{session_id}")
async def websocket_onboarding_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket канал для живого интерактивного онбординга.
    Фронтенд отправляет данные формы или сообщения пользователя,
    Оркестратор в реальном времени стримит ответы агентов и статус прогресса.
    """
    await ws_manager.connect(session_id, websocket)
    
    try:
        # Приветственное событие от Интервьюера
        await ws_manager.send_event(
            session_id=session_id,
            step="interviewer_greeting",
            payload={
                "message": "Здравствуйте! Я ИИ-ассистент онбординга UCust. Готов собрать данные о вашем бизнесе и настроить команду агентов.",
                "required_fields": ["company_name", "niche", "raw_social_input", "goals"]
            }
        )
        
        while True:
            # Получаем сообщение от фронтенда
            raw_data = await websocket.receive_text()
            user_msg = json.loads(raw_data)
            
            # 1. Этап интервьюера (проверка ссылок и целей)
            await ws_manager.send_event(
                session_id=session_id,
                step="interviewer_processing",
                payload={"status": "Проверка ссылок и структуры данных..."}
            )
            await asyncio.sleep(0.5)
            
            # Запуск онбординга через Оркестратор
            await ws_manager.send_event(
                session_id=session_id,
                step="analyst_started",
                payload={"progress": 25, "status": "Аналитик собирает посты и отзывы..."}
            )
            
            result = await orchestrator.execute_task(
                task_type="onboarding",
                user_data=user_msg,
                session_id=session_id
            )
            
            await ws_manager.send_event(
                session_id=session_id,
                step="copywriter_started",
                payload={"progress": 65, "status": "Сайга формирует Tone-of-Voice и контент-план..."}
            )
            await asyncio.sleep(0.5)
            
            # Финальное событие завершения
            await ws_manager.send_event(
                session_id=session_id,
                step="pipeline_completed",
                payload={
                    "progress": 100,
                    "status": "Команда агентов успешно настроена!",
                    "result": result
                }
            )
            
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
    except Exception as e:
        await ws_manager.send_event(
            session_id=session_id,
            step="error",
            payload={"error": str(e)}
        )
        ws_manager.disconnect(session_id)


if __name__ == "__main__":
    import uvicorn
    print("[API Gateway] 🚀 Запуск AI Service Gateway на http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
