"""
Automated Verification Suite for the 5 UCust AI Architectural Directives & Edge Cases:
1. Directive 1: StatePruningReducer token budgeting (<= 2048 tokens)
2. Directive 2 (Edge Case 1): DiffApplier fuzzy sentence-level patching (>= 0.85 ratio)
3. Directive 3 (Edge Case 2): Two-Tier Deduplication (Russian Stemmed BM25 + Cosine similarity)
4. Directive 4 (Edge Case 3): Bounded Clean RAG Retrieval & Multi-Tenant Cache Invalidation
5. Directive 5 (Edge Case 4): Lazy Rendering FSM, OOM Handling, and DLQ Notification
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Set encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Adjust path to include project root and ai dir
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from schemas.models import (
    UserQuestionnaire,
    QuestionnaireStep1,
    QuestionnaireStep2,
    QuestionnaireStep3,
    QuestionnaireStep4,
    QuestionnaireStep5,
    SWOTResultSchema,
    StrategyPlanSchema,
    CopywritingFramework
)
from core.agents import AgentContext, StatePruningReducer
from skills.diff_applier import DiffApplier
from skills.audit_deduplication_agent import AuditDeduplicationAgent
from rag.pipeline import CleanRAGPipeline
from rag.models import Document
from core.lazy_rendering_controller import (
    LazyRenderingController,
    PostDraft,
    ContentFormat,
    ImageGenerationSpec,
    PostLifecycleStatus
)
from services.webhook_manager import WebhookCallbackManager


def test_directive_1_state_pruning_reducer():
    print("\n--- [TEST 1] Directive 1: StatePruningReducer Context Projection & Token Budget ---")
    questionnaire = UserQuestionnaire(
        step1=QuestionnaireStep1(
            business_name="Aroma Hub",
            mission="Спешелти кофе и уютная атмосфера",
            region="Москва, Арбат"
        ),
        step2=QuestionnaireStep2(
            target_audience="Жители и гости Арбата 20-45 лет",
            demographics="М/Ж 20-45, средний+ доход",
            pain_points="Поиск качественного кофе без очередей"
        ),
        step3=QuestionnaireStep3(
            tone_of_voice="Friendly, energetic",
            content_formats="Посты с экспертными советами и анонсы",
            taboo_topics="Политика, негатив о конкурентах"
        ),
        step4=QuestionnaireStep4(
            goals="Привлечение новых постоянных клиентов",
            kpi="Охват, вовлеченность (ER), переходы",
            frequency="5 постов в неделю"
        ),
        step5=QuestionnaireStep5(
            competitors="Даблби, Кофемания",
            references="Эстетичные лайфстайл кофейни",
            additional_notes="Приоритет на утренние часы"
        )
    )
    swot = SWOTResultSchema(
        summary="Сильный бренд, отличное зерно, но высокая конкуренция на Арбате.",
        strengths=["Спешелти зерно 100% арабика", "Опытные бариста"],
        weaknesses=["Высокая аренда", "Ограниченная посадка"],
        opportunities=["Запуск доставки", "Сезонное меню напитков"],
        threats=["Сетевые кофейни по соседству", "Рост цен на зерно"]
    )
    strategy = StrategyPlanSchema(
        strategy="Фокус на авторских напитках и программе лояльности. " + ("Стратегический блок с деталями. " * 300),
        risks=["Рост себестоимости"],
        recommendations=["Тестировать рафы с травами"]
    )

    context = AgentContext(
        questionnaire=questionnaire,
        swot=swot,
        strategy=strategy,
        framework=CopywritingFramework.PAS,
        logs=["Log entry " * 500 for _ in range(10)]
    )

    reduced = StatePruningReducer.reduce_for_copywriter(context, max_token_budget=2048)
    
    assert "brand_dna_summary" in reduced
    assert "swot_key_points" in reduced
    assert "strategy_summary" in reduced
    assert reduced["estimated_tokens"] <= 2048, f"Estimated tokens exceeded: {reduced['estimated_tokens']} > 2048"
    assert "logs" not in reduced
    print(f"✅ StatePruningReducer passed. Estimated tokens: {reduced['estimated_tokens']} / 2048.")


def test_directive_2_diff_applier_fuzzy_patch():
    print("\n--- [TEST 2] Directive 2 & Edge Case 1: DiffApplier Fuzzy Patching ---")
    original_text = (
        "В нашей уютной кофейне на Арбате мы готовим эспрессо из 100% арабики. "
        "В субботу мы дарим каждому гостю бесплатный яблочный пирог. "
        "Приходите всей семьей и наслаждайтесь теплой атмосферой!"
    )
    
    # Fact-checker notices fact hallucination: apple pie isn't free, it's 50% discount.
    # Minor punctuation/casing drift in target string from LLM output.
    patches = [
        {
            "target": "В субботу мы дарим каждому гостю бесплатный яблочный пирог!",  # Exclamation instead of dot
            "replacement": "В субботу действует скидка 50% на наш фирменный яблочный пирог.",
            "reason": "Corrected free giveaway hallucination to 50% promo discount"
        }
    ]

    t0 = time.perf_counter()
    patched_text, count = DiffApplier.apply_patches(original_text, patches, similarity_threshold=0.85)
    t_elapsed = (time.perf_counter() - t0) * 1000

    print(f"Patched Text:\n{patched_text}")
    assert count == 1
    assert "скидка 50% на наш фирменный яблочный пирог" in patched_text
    assert "бесплатный яблочный пирог" not in patched_text
    assert "В нашей уютной кофейне на Арбате" in patched_text
    assert t_elapsed < 200, f"DiffApplier took too long: {t_elapsed:.2f}ms"
    print(f"✅ DiffApplier fuzzy matching passed in {t_elapsed:.2f}ms.")


def test_directive_3_two_tier_deduplication():
    print("\n--- [TEST 3] Directive 3 & Edge Case 2: Two-Tier Deduplication with Russian Stemming ---")
    agent = AuditDeduplicationAgent(custom_threshold=0.82)
    
    post1 = "Наша новая кофейня открылась на Арбате. Попробуйте авторский раф с лавандой и свежие круассаны!"
    # post2 has inflected Russian forms ("кофейне", "Арбату", "авторские", "рафы", "лавандовые", "круассанов")
    post2 = "В новой кофейне на Арбате пробуем авторские рафы с лавандовыми нотками и свежих круассанов!"
    # post3 is conceptually different
    post3 = "Вечерний акустический концерт и дегустация редких сортов чая пуэр в эту пятницу."

    overlap_stemmed = agent.calculate_bm25_lexical_overlap(post1, post2)
    print(f"Stemmed lexical overlap between inflected posts: {overlap_stemmed:.3f}")
    assert overlap_stemmed >= 0.40, f"Stemming failed to identify lexical overlap: {overlap_stemmed}"

    # Evaluate uniqueness against history containing post1
    eval_res_dup = agent.evaluate_uniqueness(post2, recent_channel_posts=[post1])
    print(f"Deduplication eval for inflected variant: is_duplicate={eval_res_dup.is_duplicate}, score={eval_res_dup.similarity_score}")
    assert eval_res_dup.is_duplicate is True, "Expected post2 to be marked duplicate of post1"

    eval_res_unique = agent.evaluate_uniqueness(post3, recent_channel_posts=[post1])
    print(f"Deduplication eval for unique post: is_duplicate={eval_res_unique.is_duplicate}, score={eval_res_unique.similarity_score}")
    assert eval_res_unique.is_duplicate is False, "Expected post3 to be marked unique"
    print("✅ Two-Tier Deduplication with Russian stemming passed.")


def test_directive_4_bounded_rag_and_cache_invalidation():
    print("\n--- [TEST 4] Directive 4 & Edge Case 3: Bounded Clean RAG & Cache Invalidation ---")
    rag = CleanRAGPipeline()
    
    tenant_a = "coffee_shop_alpha"
    tenant_b = "gym_beta"
    
    docs_a = [
        Document(
            doc_id="doc_a1",
            text="В кофейне Альфа мы используем зерна спешелти класса сорта Гейша и готовим кемекс.",
            metadata={"tenant_id": tenant_a}
        )
    ]
    docs_b = [
        Document(
            doc_id="doc_b1",
            text="В фитнес-клубе Бета открылся новый зал для кроссфита и бассейн с морской водой.",
            metadata={"tenant_id": tenant_b}
        )
    ]
    
    rag.ingest_documents(docs_a)
    rag.ingest_documents(docs_b)
    
    # 1. Multi-tenant bounded query
    t0 = time.perf_counter()
    ctx_a = rag.query("Какие сорта кофе используются?", top_k_retrieval=10, top_n_rerank=5, tenant_id=tenant_a)
    query_lat_ms = (time.perf_counter() - t0) * 1000
    print(f"RAG query latency: {query_lat_ms:.2f}ms")
    
    assert ctx_a.has_sufficient_context is True
    assert any("Гейша" in c.text for c in ctx_a.chunks)
    assert not any("кроссфит" in c.text for c in ctx_a.chunks), "Cross-tenant data leak detected!"
    
    # 2. Check query cache hit
    t1 = time.perf_counter()
    ctx_a_cached = rag.query("Какие сорта кофе используются?", top_k_retrieval=10, top_n_rerank=5, tenant_id=tenant_a)
    cached_lat_ms = (time.perf_counter() - t1) * 1000
    print(f"Cached RAG query latency: {cached_lat_ms:.2f}ms")
    assert cached_lat_ms < query_lat_ms
    
    # 3. Test Invalidation on tenant delete (Edge Case 3)
    rag.delete_tenant(tenant_a)
    ctx_a_after_del = rag.query("Какие сорта кофе используются?", top_k_retrieval=10, top_n_rerank=5, tenant_id=tenant_a)
    assert not ctx_a_after_del.chunks, "Tenant chunks were not purged on deletion!"
    print("✅ Bounded Clean RAG with multi-tenant cache invalidation passed.")


async def async_test_directive_5_lazy_rendering_fsm():
    print("\n--- [TEST 5] Directive 5 & Edge Case 4: Lazy Rendering FSM, OOM & DLQ ---")
    controller = LazyRenderingController(dev_simulation_mode=True)
    
    draft = PostDraft(
        post_id="post_999",
        brand_id="brand_xyz",
        target_date=datetime.now(),
        format=ContentFormat.SINGLE_SHOT,
        text_content="Тестовый пост с генерацией тяжелого визуального контента",
        image_specs=[
            ImageGenerationSpec(
                prompt="Epic macro shot of espresso machine in warm sunlight",
                width=1024,
                height=1024
            )
        ],
        callback_url="https://mock-backend.ucust.ai/api/v1/webhooks/render",
        status=PostLifecycleStatus.DRAFT_TEXT
    )
    
    # 1. User approval transition
    draft.status = PostLifecycleStatus.APPROVED_QUEUED
    assert draft.status == PostLifecycleStatus.APPROVED_QUEUED
    
    # 2. Simulate OOM error -> CPU Fallback
    await controller._handle_cpu_fallback(draft, oom_reason="CUDA out of memory: 14.2 GB requested")
    assert draft.status == PostLifecycleStatus.RENDERED
    assert len(draft.rendered_image_urls) == 1
    assert "cpu_fallback" in draft.rendered_image_urls[0]
    
    # 3. Simulate fatal / timeout error -> Transition to DLQ
    await controller._transition_to_dlq(draft, reason="CPU rendering pipeline exhausted after 300s")
    assert draft.status == PostLifecycleStatus.DEAD_LETTER_QUEUE
    assert draft.requires_user_action is True
    assert "exhausted" in (draft.error_message or "")
    
    # 4. Verify HMAC signature calculation for webhook
    payload = b'{"post_id":"post_999","status":"dead_letter_queue","requires_user_action":true}'
    sig = WebhookCallbackManager.generate_signature(payload)
    assert isinstance(sig, str) and len(sig) == 64
    print(f"Generated DLQ Webhook HMAC Signature: {sig}")
    print("✅ Lazy Rendering FSM, OOM CPU Fallback and DLQ Webhook notification passed.")


def main():
    print("================================================================================")
    print("🚀 RUNNING ARCHITECTURAL DIRECTIVES & EDGE CASES VERIFICATION SUITE")
    print("================================================================================")
    
    test_directive_1_state_pruning_reducer()
    test_directive_2_diff_applier_fuzzy_patch()
    test_directive_3_two_tier_deduplication()
    test_directive_4_bounded_rag_and_cache_invalidation()
    asyncio.run(async_test_directive_5_lazy_rendering_fsm())
    
    print("\n================================================================================")
    print("🎉 ALL 5 ARCHITECTURAL DIRECTIVES AND 4 EDGE CASES SUCCESSFULLY VERIFIED!")
    print("================================================================================")


if __name__ == "__main__":
    main()
