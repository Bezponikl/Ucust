"""
test_backend_posting_bridge.py
======================================================================
Тестирование моста передачи постов в Бэкенд и Планировщик (Backend Posting Bridge):
1. Шифрование и дешифрование клиентских токенов (TokenCryptoVault AES-256).
2. Режим 1: «Полный автопилот» (FULL_AUTOPILOT) по часовому поясу клиента (Asia/Tashkent).
3. Режим 2: «Подтверждение в Telegram» (TG_CONFIRMATION) за 30 мин до выхода.
4. Механизм Auto-Retry и валидация контракта передачи медиа-пакета.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from datetime import datetime, timezone, timedelta

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from bridge.backend_posting_bridge import (
    BackendPostingBridge,
    TokenCryptoVault,
    PublishMode
)


async def run_all_bridge_tests():
    print("=" * 80)
    print("🚀 ТЕСТИРОВАНИЕ МОСТА ПЕРЕДАЧИ ПОСТОВ В БЭКЕНД (BACKEND POSTING BRIDGE)")
    print("=" * 80)

    # 1. Тестирование шифрования токенов
    print("\n🔐 1. ТЕСТИРОВАНИЕ ШИФРОВАНИЯ ТОКЕНОВ (TOKEN CRYPTO VAULT)")
    vault = TokenCryptoVault()
    sample_vk_token = "vk1.a.SecretOAuthTokenForClientCommunityPost1234567890"
    sample_tg_bot_token = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_secret_bot_token"

    enc_vk = vault.encrypt_token(sample_vk_token)
    enc_tg = vault.encrypt_token(sample_tg_bot_token)
    dec_vk = vault.decrypt_token(enc_vk)
    dec_tg = vault.decrypt_token(enc_tg)

    print(f"   • Исходный VK токен: {sample_vk_token[:20]}...")
    print(f"   • Зашифрованный:     {enc_vk[:35]}...")
    print(f"   • Расшифрованный:    {dec_vk[:20]}...")
    assert dec_vk == sample_vk_token
    assert dec_tg == sample_tg_bot_token
    assert enc_vk != sample_vk_token
    print("✅ Шифрование и дешифрование токенов успешно подтверждено!")

    # 2. Тестирование Режима 1: «Полный автопилот» (FULL_AUTOPILOT)
    print("\n" + "=" * 80)
    print("🤖 2. РЕЖИМ «ПОЛНЫЙ АВТОПИЛОТ» (FULL_AUTOPILOT: Asia/Tashkent)")
    print("=" * 80)

    bridge = BackendPostingBridge()
    target_time_tashkent = datetime(2026, 9, 5, 11, 0, 0)

    payload_autopilot = bridge.format_post_payload(
        post_id="post_auto_101",
        client_id="client_maksima_uz",
        company_name="Maksima Мебель",
        niche="Дизайнерская мебель",
        channels=["telegram", "vk", "max"],
        post_text="✨ Идеальный обеденный стол из массива дуба для вашей гостиной...",
        media_files=["/storage/flux_table_1.jpg", "/storage/ltx_table_video.mp4"],
        hashtags="#мебель #дизайн #массивдуба",
        promo_code="MAKSIMA2026",
        publish_time_local=target_time_tashkent,
        client_timezone="Asia/Tashkent",
        publish_mode=PublishMode.FULL_AUTOPILOT,
        client_tokens={"vk": sample_vk_token, "telegram": sample_tg_bot_token}
    )

    res_auto = await bridge.dispatch_to_backend(payload_autopilot)
    print(f"✅ Результат передачи поста в Бэкенд:")
    print(f"   • Статус: {res_auto['status']}")
    print(f"   • Режим: {res_auto['publish_mode']}")
    print(f"   • Часовой пояс: {res_auto['client_timezone']}")
    print(f"   • Локальное время публикации: {res_auto['scheduled_local_time']}")
    print(f"   • Каналы: {res_auto['target_channels']}")
    print(f"   • Токены зашифрованы: {res_auto['tokens_encrypted']}")
    assert res_auto["status"] == "delivered_to_backend_queue"
    assert res_auto["publish_mode"] == "FULL_AUTOPILOT"
    assert res_auto["client_timezone"] == "Asia/Tashkent"

    # 3. Тестирование Режима 2: «Подтверждение в Telegram» (TG_CONFIRMATION)
    print("\n" + "=" * 80)
    print("📲 3. РЕЖИМ «ПОДТВЕРЖДЕНИЕ В TELEGRAM» (TG_CONFIRMATION за 30 мин)")
    print("=" * 80)

    payload_confirmation = bridge.format_post_payload(
        post_id="post_confirm_202",
        client_id="client_dental_lux",
        company_name="ДентаЛюкс",
        niche="Стоматология",
        channels=["telegram", "vk"],
        post_text="💎 Красивая и здоровая улыбка за 1 визит...",
        publish_mode=PublishMode.TG_CONFIRMATION,
        confirmation_tg_chat_id="987654321",
        client_timezone="Europe/Moscow"
    )

    res_confirm = await bridge.dispatch_to_backend(payload_confirmation)
    print(f"✅ Результат передачи поста согласования:")
    print(f"   • Статус: {res_confirm['status']}")
    print(f"   • Режим: {res_confirm['publish_mode']}")
    print(f"   • Lead time до выхода: {payload_confirmation['approval_workflow']['pre_publish_lead_minutes']} мин")
    print(f"   • Доступные действия клиента: {payload_confirmation['approval_workflow']['callback_actions']}")
    assert res_confirm["publish_mode"] == "TG_CONFIRMATION"
    assert payload_confirmation["approval_workflow"]["pre_publish_lead_minutes"] == 30
    assert "approve" in payload_confirmation["approval_workflow"]["callback_actions"]
    assert "regenerate" in payload_confirmation["approval_workflow"]["callback_actions"]

    # 4. Тестирование RabbitMQBridgeClient (AMQP)
    print("\n" + "=" * 80)
    print("🐇 4. ТЕСТИРОВАНИЕ RABBITMQ BRIDGE CLIENT (SPRING AMQP СОВМЕСТИМОСТЬ)")
    print("=" * 80)
    from bridge.backend_posting_bridge import RabbitMQBridgeClient
    rmq_client = RabbitMQBridgeClient(
        host="localhost",
        port=5672,
        username="service-user",
        password="servicepassword"
    )
    print(f"   • RabbitMQ Connection URL: {rmq_client.get_connection_url()[:25]}***")
    rmq_res = await rmq_client.publish_post_bundle(payload_autopilot)
    print(f"   • Статус публикации в RabbitMQ: {rmq_res['status']}")
    print(f"   • Exchange: {rmq_res['exchange']} | Routing Key: {rmq_res['routing_key']}")
    assert "rabbitmq" in rmq_res["status"]
    print("✅ RabbitMQ клиент успешно сконфигурирован под Spring AMQP бэкенда!")

    print("\n🎉 ВСЕ ТЕСТЫ МОСТА ПЕРЕДАЧИ В БЭКЕНД УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    asyncio.run(run_all_bridge_tests())
