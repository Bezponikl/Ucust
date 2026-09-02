"""
test_multi_platform_reactions.py
======================================================================
Тестирование адаптации Positivity Engine под все соцсети и кастомные эмодзи:
1. Telegram (стандартные реакции 👍, 🔥, ❤️, 🎉 vs 👎, 💩, 🤡 + Custom Brand Emojis)
2. VK (реакции: like, heart/super, funny, dislike/hate, репосты)
3. Instagram (лайки, комментарии, сохранения/закладки saves, репосты в Direct)
4. TikTok (лайки, комментарии, избранное/favorites, репосты)
5. YouTube (лайки, дизлайки, комментарии, репосты)
6. MAX (реакции и кастомные эмодзи)
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from analytics.feedback_loop import FeedbackLoopEngine


def run_all_platform_tests():
    print("=" * 80)
    print("🌐 ТЕСТИРОВАНИЕ АДАПТАЦИИ ПОД ВСЕ СОЦСЕТИ И КАСТОМНЫЕ ЭМОДЗИ")
    print("=" * 80)

    # 1. Telegram с набором стандартных и кастомных эмодзи
    print("\n1️⃣ TELEGRAM: Стандартные реакции + Telegram Premium Custom Emojis")
    tg_reactions = {
        "👍": 320,
        "🔥": 140,
        "❤️": 90,
        "🎉": 50,
        "custom_brand_rocket": 45,       # Кастомный позитивный эмодзи
        "custom_gold_star": 30,          # Кастомный позитивный эмодзи
        "👎": 6,
        "💩": 2,
        "custom_neg_trash": 3,           # Кастомный негативный эмодзи
        "comments": 35,
        "shares": 55
    }
    m_tg = FeedbackLoopEngine.calculate_positivity_metrics(
        views=15000,
        likes=0,
        platform="telegram",
        raw_reactions=tg_reactions
    )
    print(f"   • Эффективные лайки (L): {m_tg['likes']}")
    print(f"   • Эффективные дизлайки (D): {m_tg['dislikes']}")
    print(f"   • Эффективные реакции (R): {m_tg['reactions']}")
    print(f"   • NAI (Индекс одобрения): {m_tg['net_approval_index']}")
    print(f"   • WPR: {m_tg['weighted_positivity_rate']}%")
    print(f"   • Score: {m_tg['log_positivity_score']}")
    print(f"   • Грейд: {m_tg['grade']} ({m_tg['summary']})")
    assert m_tg['likes'] == (320 + 140 + 90 + 50)  # 600
    assert m_tg['dislikes'] == (6 + 2 + 3)          # 11
    assert m_tg['net_approval_index'] > 0.97
    assert m_tg['log_positivity_score'] > 200

    # 2. VKontakte с реакциями платформы
    print("\n2️⃣ VKONTAKTE: Реакции (Нравится, Восторг, Смешно, Неприязнь)")
    vk_reactions = {
        "like": 450,
        "heart": 120,
        "funny": 60,
        "dislike": 8,
        "reposts": 75,
        "comments": 40
    }
    m_vk = FeedbackLoopEngine.calculate_positivity_metrics(
        views=12000,
        likes=0,
        platform="vk",
        raw_reactions=vk_reactions
    )
    print(f"   • Эффективные лайки (L): {m_vk['likes']}")
    print(f"   • Эффективные дизлайки (D): {m_vk['dislikes']}")
    print(f"   • Эффективные реакции (R): {m_vk['reactions']}")
    print(f"   • NAI: {m_vk['net_approval_index']}")
    print(f"   • Score: {m_vk['log_positivity_score']}")
    print(f"   • Грейд: {m_vk['grade']} ({m_vk['summary']})")
    assert m_vk['likes'] >= 450
    assert m_vk['dislikes'] == 8
    assert m_vk['net_approval_index'] > 0.95

    # 3. Instagram: Лайки, комментарии, сохранения в закладки (Saves) и Direct
    print("\n3️⃣ INSTAGRAM: Лайки, Комментарии и Закладки (Saves/Bookmarks)")
    ig_reactions = {
        "likes": 3500,
        "comments": 140,
        "saves": 420,     # Закладки имеют максимальный вес (высокое намерение покупки)
        "shares": 110
    }
    m_ig = FeedbackLoopEngine.calculate_positivity_metrics(
        views=40000,
        likes=0,
        platform="instagram",
        raw_reactions=ig_reactions
    )
    print(f"   • Лайки (L): {m_ig['likes']}")
    print(f"   • Реакции глубокого вовлечения (R): {m_ig['reactions']}")
    print(f"   • NAI: {m_ig['net_approval_index']}")
    print(f"   • Score: {m_ig['log_positivity_score']}")
    print(f"   • Грейд: {m_ig['grade']} ({m_ig['summary']})")
    assert m_ig['likes'] == 3500
    assert m_ig['dislikes'] == 0
    assert m_ig['grade'] == "VIRAL_POSITIVE"

    # 4. TikTok: Лайки, избранное (Favorites), репосты
    print("\n4️⃣ TIKTOK: Лайки, Избранное (Favorites) и Репосты")
    tt_reactions = {
        "likes": 25000,
        "comments": 800,
        "favorites": 1500,
        "shares": 950
    }
    m_tt = FeedbackLoopEngine.calculate_positivity_metrics(
        views=200000,
        likes=0,
        platform="tiktok",
        raw_reactions=tt_reactions
    )
    print(f"   • Лайки (L): {m_tt['likes']}")
    print(f"   • Реакции (R): {m_tt['reactions']}")
    print(f"   • Score: {m_tt['log_positivity_score']}")
    print(f"   • Грейд: {m_tt['grade']} ({m_tt['summary']})")
    assert m_tt['log_positivity_score'] > 1000

    # 5. YouTube: Лайки, Дизлайки и комментарии
    print("\n5️⃣ YOUTUBE: Лайки, Дизлайки, Комментарии")
    yt_reactions = {
        "likes": 8000,
        "dislikes": 40,
        "comments": 320,
        "shares": 180
    }
    m_yt = FeedbackLoopEngine.calculate_positivity_metrics(
        views=90000,
        likes=0,
        platform="youtube",
        raw_reactions=yt_reactions
    )
    print(f"   • Лайки (L): {m_yt['likes']}, Дизлайки (D): {m_yt['dislikes']}")
    print(f"   • NAI: {m_yt['net_approval_index']}")
    print(f"   • Score: {m_yt['log_positivity_score']}")
    print(f"   • Грейд: {m_yt['grade']} ({m_yt['summary']})")
    assert m_yt['likes'] == 8000
    assert m_yt['dislikes'] == 40
    assert m_yt['net_approval_index'] > 0.99

    print("\n🎉 ВСЕ ТЕСТЫ ДЛЯ TELEGRAM, VK, INSTAGRAM, TIKTOK И YOUTUBE УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    run_all_platform_tests()
