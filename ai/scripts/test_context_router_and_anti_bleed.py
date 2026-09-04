# File: scripts/test_context_router_and_anti_bleed.py
"""
Сквозное тестирование ContextRouterSkill, Multi-Tenant RAG и Anti-Bleed фильтров в UCust.AI:
1. Тест B2B SaaS (UCust RAG Pipeline).
2. Тест Crossover / Bridge Mode (Кот в IT-офисе / Утренний кофе разработчиков).
3. Тест B2C Lifestyle (Кофейня / Свежеобжаренный раф).
4. Тест Религия / Культура (Церковь / Уважительный исторический тон без сокращения бюджета на 25%).
5. Тест Multi-Tenant RAG Isolation (0% утечки чужих чанков между тенантами).
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skills.context_router import ContextRouterSkill, QuadrantEnum, IntentModeEnum, FunnelLockEnum
from skills.critic_munger import CriticMungerSkill
from skills.photo_generator import CinematographyDirector
from rag.pipeline import CleanRAGPipeline
from rag.models import Document


def run_tests():
    print("=" * 70)
    print("🧪 ЗАПУСК ТЕСТОВОГО НАБОРА: CONTEXT ROUTER, MULTI-TENANT RAG & ANTI-BLEED")
    print("=" * 70)

    router = ContextRouterSkill()
    critic = CriticMungerSkill(strictness=0.75)

    # -------------------------------------------------------------------------
    # ТЕСТ 1: Чистый B2B SaaS
    # -------------------------------------------------------------------------
    print("\n[ТЕСТ 1] 🏢 Чистый B2B SaaS: 'Релиз RAG-пайплайна v2 с семантическим поиском'")
    d1 = router.route_task("Релиз RAG-пайплайна v2 с семантическим поиском", company_name="UCust", niche="Martech")
    assert d1.quadrant == QuadrantEnum.B2B_TECH, f"Expected B2B_TECH, got {d1.quadrant}"
    assert d1.intent_mode == IntentModeEnum.CORE_BUSINESS, f"Expected CORE_BUSINESS, got {d1.intent_mode}"
    print(f"  ✅ Квадрант: {d1.quadrant.value}, Режим: {d1.intent_mode.value}, FunnelLock: {d1.text_directive.funnel_lock.value}")

    # -------------------------------------------------------------------------
    # ТЕСТ 2: Bridge Mode / Crossover (IT + Кот)
    # -------------------------------------------------------------------------
    print("\n[ТЕСТ 2] 🐱 Crossover / Bridge Mode: 'Рыжий кот спит на клавиатуре программиста'")
    d2 = router.route_task("Рыжий кот спит на клавиатуре программиста перед релизом", company_name="UCust", niche="Martech")
    assert d2.intent_mode == IntentModeEnum.LIFESTYLE_CROSSOVER, f"Expected LIFESTYLE_CROSSOVER, got {d2.intent_mode}"
    assert d2.text_directive.funnel_lock == FunnelLockEnum.TOFU_UNAWARE, f"Expected TOFU_UNAWARE, got {d2.text_directive.funnel_lock}"
    print(f"  ✅ Режим: {d2.intent_mode.value}, FunnelLock: {d2.text_directive.funnel_lock.value}, Visual Anchor: {d2.visual_anchor.environment_preset}")

    # Проверяем, что CriticMunger бракует попытку натянуть B2B ROI на кота
    bad_cat_text = "В Кот разработали решение: армия котиков! Снижение расходов на 20% благодаря оптимизации рационов."
    audit_bad = critic.review_content(bad_cat_text, topic="армия котиков", routing=d2)
    assert not audit_bad["passed"], "CriticMunger should REJECT oxymoronic B2B cat post!"
    print(f"  ✅ CriticMunger успешно забраковал оксюморон: {audit_bad['fatal_flaws']}")

    # -------------------------------------------------------------------------
    # ТЕСТ 3: Чистый B2C Lifestyle (Кофе / Раф)
    # -------------------------------------------------------------------------
    print("\n[ТЕСТ 3] ☕ Чистый B2C Lifestyle: 'Свежеобжаренный лавандовый раф с воздушной пенкой'")
    d3 = router.route_task("Свежеобжаренный лавандовый раф с воздушной пенкой", company_name="Coffee House", niche="Кофейня")
    assert d3.quadrant == QuadrantEnum.B2C_LIFESTYLE, f"Expected B2C_LIFESTYLE, got {d3.quadrant}"
    vis_coffee = CinematographyDirector.compose_cinematic_prompt("Лавандовый раф", "Кофейня", routing=d3)
    assert "coffee" in vis_coffee["prompt"].lower() or "artisan" in vis_coffee["prompt"].lower() or "sunlit" in vis_coffee["prompt"].lower()
    print(f"  ✅ Квадрант: {d3.quadrant.value}, ComfyUI Visual Prompt: {vis_coffee['prompt'][:90]}...")

    # -------------------------------------------------------------------------
    # ТЕСТ 4: Религия / Культура (Церковь)
    # -------------------------------------------------------------------------
    print("\n[ТЕСТ 4] 🏛️ Религия / Культура: 'Праздничное богослужение и история собора'")
    d4 = router.route_task("Праздничное богослужение и история собора", company_name="Церковь", niche="Религия")
    assert d4.quadrant == QuadrantEnum.B2C_LIFESTYLE
    # Проверяем, что CriticMunger бракует "сокращение бюджета церкви на 25%"
    bad_church_text = "Компания Церковь внедрила инновации. Мы сократили время на подготовку документов на 40% и бюджет на 25%."
    audit_church = critic.review_content(bad_church_text, topic="Церковь", routing=d4)
    assert not audit_church["passed"], "CriticMunger should REJECT corporate metrics in church post!"
    print(f"  ✅ CriticMunger успешно забраковал искажение церковной темы: {audit_church['fatal_flaws']}")

    # -------------------------------------------------------------------------
    # ТЕСТ 5: Multi-Tenant RAG Hard Isolation
    # -------------------------------------------------------------------------
    print("\n[ТЕСТ 5] 🔒 Multi-Tenant RAG Hard Partitioning")
    rag = CleanRAGPipeline()
    rag.ingest_documents([
        Document(doc_id="c1", text="Свежеобжаренный кофе Эфиопия с нотками жасмина", metadata={"tenant_id": "coffee_tenant", "company_name": "Coffee House"}),
        Document(doc_id="i1", text="Отладочная плата ESP-32 Type-C для IoT", metadata={"tenant_id": "iot_tenant", "company_name": "IoT Lab"}),
        Document(doc_id="u1", text="Платформа UCust AI снижает стоимость привлечения клиента (CAC) на 40%", metadata={"tenant_id": "ucust_tenant", "company_name": "UCust"})
    ])

    # Запрос кофе тенантом UCust (НЕ должен получить чужие чанки кофейни!)
    res_ucust = rag.query("кофе с жасмином", tenant_id="ucust_tenant")
    # Проверяем, что ни один чанк из чужого тенанта coffee_tenant не попал в выдачу UCust
    assert all("кофе" not in c.text.lower() and "жасмин" not in c.text.lower() for c in res_ucust.chunks), "Cross-Tenant Leakage! Coffee chunk leaked into UCust tenant!"

    # Запрос кофе тенантом Coffee Shop (должен найти свой чанк!)
    res_coffee = rag.query("кофе с жасмином", tenant_id="coffee_tenant")
    assert len(res_coffee.chunks) > 0, "Expected coffee chunk for Coffee tenant"
    assert any("жасмин" in c.text.lower() for c in res_coffee.chunks), "Coffee tenant must find its own coffee chunk"
    print(f"  ✅ Multi-Tenant RAG изоляция: 0 чужих чанков кофейни в UCust (Cross-Tenant Leakage = 0%).")

    print("\n" + "=" * 70)
    print("🎉 ВСЕ 5 ТЕСТОВ УСПЕШНО ПРОЙДЕНЫ! АРХИТЕКТУРА ПОЛНОСТЬЮ СИНХРОНИЗИРОВАНА.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
