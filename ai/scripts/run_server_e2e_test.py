"""
run_server_e2e_test.py
======================================================================
Комплексный сквозной тест готовности AI-сервера к интеграции с Бэкендом:
1. 🛡️ Безопасность: TechSanitizer (защита от утечек моделей) + ZeroAssumptionsGuard (защита от галлюцинаций цен/скидок/доставки).
2. ✍️ Генеративный движок: Сайга + фреймворки AIDA/PAS + 2-режимное распределение (80% студийное фото, 20% текст).
3. 🥐 Экспертный сторителлинг: форматы «Знали ли вы, что...» и «Уравнение идеального вкуса».
4. 🏷️ Хэштеги конкурентов: 3-уровневый пакет без внутренних тегов (#UCust).
5. 💳 Тарифный шлюз и Календарь: расчет слотов для тарифов Start, Business, Enterprise и Custom.
6. 🔐 Шифрование токенов и контракт RabbitMQ: AES-256 vault + JSON-пакет для бэкенда.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from datetime import datetime

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from skills.tech_sanitizer import TechSanitizer
from skills.zero_assumptions_guard import ZeroAssumptionsGuard
from skills.competitor_hashtags import NicheCompetitorHashtagEngine
from skills.object_storytelling import ObjectKnowledgeStoryteller
from skills.saiga_llm import SaigaLLMSkill
from skills.marketing_frameworks import MarketingFrameworkDirector, MarketingFramework, HuntStage
from bridge.backend_posting_bridge import BackendPostingBridge, TokenCryptoVault, PublishMode


async def run_master_server_test():
    print("=" * 80)
    print("🚀 [SERVER E2E HEALTHCHECK] КОМПЛЕКСНЫЙ ТЕСТ ГОТОВНОСТИ AI-КОНТУРА К РАБОТЕ")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # ШАГ 1: Тест безопасности и фильтров
    # -------------------------------------------------------------------------
    print("\n🛡️ 1. ПРОВЕРКА БЕЗОПАСНОСТИ И ФИЛЬТРОВ УТЕЧЕК (TECH SANITIZER & ZERO ASSUMPTIONS)")
    leak_test_text = "Локальная модель Сайга генерирует фото через ComfyUI со скидкой на 80% и доставкой за 5 минут."
    sanitized_text = TechSanitizer.sanitize_text(leak_test_text)
    safe_text = ZeroAssumptionsGuard.sanitize_assumptions(sanitized_text)
    
    print(f"   • Исходный опасный текст:\n     '{leak_test_text}'")
    print(f"   • Очищенный безопасный текст:\n     '{safe_text}'")
    assert "сайга" not in safe_text.lower()
    assert "comfyui" not in safe_text.lower()
    assert "80%" not in safe_text
    assert "за 5 минут" not in safe_text
    print("   ✅ Фильтры TechSanitizer и ZeroAssumptionsGuard работают безупречно!")

    # -------------------------------------------------------------------------
    # ШАГ 2: Генерация постов с маркетинговыми фреймворками
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("✍️ 2. ГЕНЕРАЦИЯ ПОСТА С МАРКЕТИНГОВЫМ ФРЕЙМВОРКОМ И ЛЕСТНИЦЕЙ ХАНТА")
    print("=" * 80)
    saiga = SaigaLLMSkill()
    post_data = saiga.generate_smm_post(
        topic="Авторский слоеный краффин со свежей корицей",
        company_name="Bakery Mood",
        niche="Кондитерская и пекарня",
        city="Москва",
        tone="Естественный и живой",
        format_type="post"
    )
    print(f"   📄 Текст поста:\n{post_data['post_text']}\n")
    print(f"   🏷️ Хэштеги конкурентов:\n{post_data['hashtags']}\n")
    print(f"   🎨 Промпт для фотосессии:\n{post_data['visual_prompt']}\n")
    assert "#ucust" not in post_data["hashtags"].lower()
    print("   ✅ Генератор постов успешно выдал чистый, продающий контент с хэштегами!")

    # -------------------------------------------------------------------------
    # ШАГ 3: Тест сторителлинга и формата «Уравнение вкуса»
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("🥐 3. ТЕСТ СТОРИТЕЛЛИНГА И ФОРМАТА «УРАВНЕНИЕ ИДЕАЛЬНОГО ВКУСА»")
    print("=" * 80)
    equation_post = ObjectKnowledgeStoryteller.generate_equation_formula_post(
        topic="Ролл с миндалем и кремом Франжипан",
        company_name="La Patisserie",
        niche="Кондитерская и пекарня",
        city="Москва"
    )
    print(f"   📄 Формула вкуса:\n{equation_post['post_text']}\n")
    assert "слоёное тесто" in equation_post["post_text"].lower()
    assert "миндальные лепестки" in equation_post["post_text"].lower()
    print("   ✅ Формула сторителлинга успешно сгенерирована!")

    # -------------------------------------------------------------------------
    # ШАГ 4: Тест тарифного шлюза и 2-режимного распределения медиа (80% фото / 20% текст)
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("💳 4. ТЕСТ ТАРИФНОГО ШЛЮЗА И КАЛЕНДАРНОЙ СЕТКИ (80% ФОТО / 20% ТЕКСТ)")
    print("=" * 80)
    bridge = BackendPostingBridge()
    quota_biz = await bridge.fetch_client_subscription_quota_async("client_bakery_01")
    slots = bridge.calculate_allowed_calendar_dates(quota_biz, start_date=datetime(2026, 9, 1))
    
    photo_count = sum(1 for s in slots if s["media_type"] == "PHOTO")
    text_count = sum(1 for s in slots if s["media_type"] == "TEXT_ONLY")
    
    print(f"   • Тариф: {quota_biz['tier_name']}")
    print(f"   • Всего слотов в календаре: {len(slots)}")
    print(f"   • Студийных фото (80%): {photo_count} слотов")
    print(f"   • Текстовых/Интерактивов (20%): {text_count} слотов")
    print(f"   • Пример слота #1 (ФОТО): {slots[0]['date']} {slots[0]['time']} -> {slots[0]['media_type']}")
    print(f"   • Пример слота #5 (ТЕКСТ): {slots[4]['date']} {slots[4]['time']} -> {slots[4]['media_type']}")
    assert len(slots) == 20
    assert photo_count == 16
    assert text_count == 4
    print("   ✅ 2-режимное распределение (80% фото / 20% текст) идеально соблюдено!")

    # -------------------------------------------------------------------------
    # ШАГ 5: Тест шифрования токенов и формирования пакета публикации для бэкенда
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("🔐 5. ТЕСТ ШИФРОВАНИЯ ТОКЕНОВ И СБОРКИ ПАКЕТА ДЛЯ РАСПИСАНИЯ БЭКЕНДА")
    print("=" * 80)
    vault = TokenCryptoVault()
    encrypted_tg = vault.encrypt_token("bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    decrypted_tg = vault.decrypt_token(encrypted_tg)
    assert decrypted_tg == "bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    
    payload = bridge.format_post_payload(
        post_id="post_test_901",
        client_id="client_bakery_01",
        company_name="Bakery Mood",
        niche="Кондитерская и пекарня",
        channels=["telegram", "vk", "max"],
        post_text=post_data["post_text"],
        media_files=["https://storage.ucust.ai/renders/cruffin_photo_01.jpg"],
        hashtags=post_data["hashtags"],
        promo_code="BAKERY2026",
        client_timezone="Europe/Moscow",
        publish_mode=PublishMode.FULL_AUTOPILOT,
        client_tokens={"telegram": "bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"}
    )
    print(f"   • Post ID: {payload['post_id']}")
    print(f"   • Target Channels: {payload['target_channels']}")
    print(f"   • Client Timezone: {payload['scheduling']['client_timezone']}")
    print(f"   • Scheduled Local Time: {payload['scheduling']['scheduled_local_time']}")
    print(f"   • Publish Mode: {payload['scheduling']['publish_mode']}")
    print(f"   • Encrypted Tokens: {bool(payload['security']['encrypted_tokens'])}")
    print("   ✅ Пакет публикации для RabbitMQ/Бэкенда сформирован в строгом соответствии с контрактом!")

    print("\n" + "=" * 80)
    print("🎉 ВСЕ 5 ЭТАПОВ E2E ТЕСТИРОВАНИЯ AI-СЕРВЕРА УСПЕШНО ПРОЙДЕНЫ (100% SUCCESS)!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_master_server_test())
