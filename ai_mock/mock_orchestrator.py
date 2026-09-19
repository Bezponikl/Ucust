"""
Unified Mock Orchestrator for UCust AI Service.
Handles all task types, security validation, and task routing.
"""

import time
import uuid
import random
from typing import Any, Dict, Optional

from ai_mock.mock_responses import (
    get_mock_post_result,
    get_mock_collector_result,
    get_mock_strategy_result,
    get_mock_content_plan_result,
    get_mock_critic_result,
)


class MockSecurityGuard:
    @staticmethod
    def check_user_input(text: str) -> bool:
        if not text:
            return True
        suspicious_patterns = [
            "<script>", "javascript:", "DROP TABLE", "--", "rm -rf", "exec("
        ]
        text_lower = text.lower()
        for p in suspicious_patterns:
            if p.lower() in text_lower:
                return False
        return True


class MockUnifiedOrchestrator:
    """
    Mock replica of UnifiedOrchestrator.
    Dispatches all 14 task types identically to the production orchestrator.
    """

    def __init__(self, host: str = "http://localhost:8000"):
        self.host = host

    async def execute_task(
        self,
        task_type: str,
        user_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        t_start = time.time()
        sid = session_id or f"sess_{uuid.uuid4().hex[:8]}"

        # 1. Post Generation
        if task_type in ["generate_post", "direct_generate", "multi_variations", "trends_post"]:
            result = get_mock_post_result(user_data, host=self.host)
            result["session_id"] = sid
            result["timings"]["orchestrator_seconds"] = round(time.time() - t_start, 3)
            return result

        # 2. Image Generation
        elif task_type == "generate_image":
            img_seed = random.randint(100000, 999999)
            img_url = f"{self.host}/output/photos/gen_image_{img_seed}.png"
            return {
                "status": "success",
                "image_url": img_url,
                "prompt": user_data.get("prompt", "Marketing banner"),
                "aspect_ratio": user_data.get("aspect_ratio", "1:1"),
                "seed": img_seed,
                "timings": {"image_gen_seconds": 0.12, "total_seconds": round(time.time() - t_start, 3)}
            }

        # 3. Strategy Planning
        elif task_type == "generate_strategy":
            res = get_mock_strategy_result(user_data)
            res["session_id"] = sid
            return res

        # 4. Content Planning
        elif task_type == "plan_content":
            res = get_mock_content_plan_result(user_data)
            res["session_id"] = sid
            return res

        # 5. Critic Review
        elif task_type == "critic_review":
            text = user_data.get("text", "")
            strictness = float(user_data.get("strictness", 0.85))
            res = get_mock_critic_result(text, strictness)
            res["session_id"] = sid
            return res

        # 6. Holiday Greeting
        elif task_type == "prepare_holiday_greeting":
            company = user_data.get("company_name", "UCust")
            holiday = user_data.get("holiday_name", "День предпринимателя")
            return {
                "status": "success",
                "holiday_name": holiday,
                "post_text": f"🎉 Поздравляем с праздником: {holiday}!\n\nКоманда {company} желает вам вдохновения, энергии и покорения новых вершин! В честь праздника дарим специальный бонус.\n\n#праздник #{company.lower()}",
                "image_url": f"{self.host}/output/photos/holiday_{random.randint(100, 999)}.png",
                "timings": {"total_seconds": round(time.time() - t_start, 3)}
            }

        # 7. Collectors & Parsers
        elif task_type in ["parse_telegram", "parse_vk", "parse_geo", "parse_website", "analyze_documents", "quick_scan", "universal_hub"]:
            target = user_data.get("target") or user_data.get("url") or user_data.get("channel") or user_data.get("group_id") or "@UcustAi"
            st = task_type.replace("parse_", "")
            res = get_mock_collector_result(st, target=target, limit=int(user_data.get("limit", 10)))
            res["session_id"] = sid
            return res

        # 8. Brand Onboarding & 5-Screen Project Flow
        elif task_type in ["onboard_user", "analyze_brand", "project_analyze"]:
            from ai_mock.mock_responses import get_mock_project_profile_draft
            profile_draft = get_mock_project_profile_draft(
                company_name=user_data.get("company_name"),
                niche=user_data.get("niche"),
                website_url=user_data.get("website_url"),
                telegram_channel=user_data.get("telegram_channel"),
                raw_notes=user_data.get("raw_notes")
            )
            return {
                "status": "success",
                "profile_draft": profile_draft,
                "timings": {"onboard_seconds": 0.22, "total_seconds": round(time.time() - t_start, 3)}
            }

        elif task_type in ["project_commit", "rag_commit"]:
            project_id = user_data.get("project_id", "project_default")
            return {
                "status": "success",
                "project_id": project_id,
                "message": f"База знаний проекта '{project_id}' успешно обновлена и проиндексирована в Clean RAG",
                "indexed_chunks": 5,
                "timings": {"commit_seconds": 0.08, "total_seconds": round(time.time() - t_start, 3)}
            }

        elif task_type in ["render_post", "lazy_render"]:
            post_id = user_data.get("post_id", f"post_{uuid.uuid4().hex[:8]}")
            img_url = f"{self.host}/output/photos/gen_render_{random.randint(1000, 9999)}.png"
            return {
                "status": "success",
                "post_id": post_id,
                "rendered_image_urls": [img_url],
                "vram_cost_mb": 6500,
                "timings": {"render_seconds": 0.15, "total_seconds": round(time.time() - t_start, 3)}
            }

        # 9. RAG Query
        elif task_type == "rag_query":
            q = user_data.get("query", "Вопрос по базе знаний")
            return {
                "status": "success",
                "query": q,
                "answer": f"На основании корпоративной базы знаний UCust: {q} регулируется регламентом обслуживания с гарантией 99.9% uptime и поддержкой 24/7.",
                "confidence": 0.94,
                "sources": [
                    {"doc_id": "doc_kb_101", "title": "Регламент обслуживания 2026", "score": 0.96},
                    {"doc_id": "doc_kb_102", "title": "Тарифы и SLA", "score": 0.91}
                ],
                "timings": {"rag_seconds": 0.05, "total_seconds": round(time.time() - t_start, 3)}
            }

        # 10. RAG Ingest
        elif task_type == "rag_ingest":
            docs = user_data.get("documents", [])
            return {
                "status": "success",
                "ingested_count": len(docs) if docs else 1,
                "message": "Документы успешно проиндексированы в векторное хранилище Clean RAG.",
                "timings": {"ingest_seconds": 0.04, "total_seconds": round(time.time() - t_start, 3)}
            }

        # Default fallback
        else:
            return {
                "status": "success",
                "task_type": task_type,
                "session_id": sid,
                "data": user_data,
                "message": f"Задача '{task_type}' успешно обработана мок-оркестратором.",
                "timings": {"total_seconds": round(time.time() - t_start, 3)}
            }
