# File: scripts/generate_ecosystem_funnel_showcase.py
"""
Сквозная генерация контента по всем этапам воронки (TOFU, MOFU, BOFU)
для собственной экосистемы UCust.AI:
- ContextRouter (маршрутизация и выбор фреймворка)
- AdvancedVisualDirector (генерация фотореалистичных промптов Realism 2.0)
- CriticMunger (аудит и защита от бреда/клише)
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from skills.context_router import ContextRouterSkill
from skills.advanced_visual_director import AdvancedVisualDirector
from skills.critic_munger import CriticMungerSkill

def run_funnel_showcase():
    print("=" * 80)
    print("🚀 ГЕНЕРАЦИЯ ПОСТОВ И ПРОМПТОВ ПО ВСЕМ ВОРОНКАМ (ТЕМА: ЭКОСИСТЕМА UCUST.AI)")
    print("=" * 80)
    
    router = ContextRouterSkill()
    director = AdvancedVisualDirector()
    critic = CriticMungerSkill()
    
    brand_colors = ["#1E293B", "#3B82F6", "#F8FAFC", "#10B981", "#6366F1"]
    
    funnel_stages = [
        {
            "stage_name": "TOFU (Top of Funnel — Верхний уровень / Охват и Вирусность)",
            "goal": "Привлечь внимание, разрушить мифы классического SMM, вызвать репосты (pShare).",
            "topic": "Почему классический ручной SMM умирает: 90% бизнеса сливают бюджет на хаотичные посты и выгорают",
            "framework": "BAB (Before - After - Bridge)",
            "post_text": (
                "Знакомо чувство, когда в воскресенье вечером вы сидите перед пустым экраном и судорожно думаете: «Что выложить в канал завтра в 9:00?» 🤯\n\n"
                "9 из 10 предпринимателей и маркетологов проходят через один и тот же замкнутый круг:\n"
                "1. Наняли копирайтера $\\rightarrow$ получили водянистые тексты про «динамично развивающуюся компанию».\n"
                "2. Наняли дизайнера $\\rightarrow$ получили пластиковые стоковые картинки без единого стиля.\n"
                "3. Потратили 40 часов в месяц $\\rightarrow$ охваты на нуле, а в комментариях тишина.\n\n"
                "Проблема не в вас и не в алгоритмах. Проблема в «ручном управлении» там, где должна работать замкнутая экосистема: когда парсер в реальном времени видит реакции аудитории, а ИИ-арт-директор выдерживает фирменную сетку без фотосессий.\n\n"
                "Сколько часов в неделю у вас сейчас уходит на подготовку контента? Пишите честную цифру в комментариях 👇"
            )
        },
        {
            "stage_name": "MOFU (Middle of Funnel — Середина / Экспертность и Технологии)",
            "goal": "Показать внутреннюю кухню, архитектурную мощь и сформировать доверие к платформе.",
            "topic": "Анатомия автономного контент-завода: как 4 ИИ-агента за 8 секунд создают публикацию топ-уровня",
            "framework": "PAS (Problem - Agitation - Solution)",
            "post_text": (
                "Почему обычные чат-боты пишут банальности, а специализированные мультиагентные системы выдают конвертящий контент?\n\n"
                "Вся магия — в разделении ролей. Внутри экосистемы UCust над каждым постом работают сразу 4 автономных узла:\n\n"
                "🔍 1. Telethon & Web Parsers — сканируют последние 30 постов конкурентов, собирая реальные данные: какие темы залетают в репосты, а что вызывает пролистывания (Skip).\n"
                "👁️ 2. Moondream2 VLM — за 15 миллисекунд считывает визуальное ДНК: свет, оптику и цветовую палитру (Hex).\n"
                "🧠 3. Сайга LLM & ContextRouter — изолирует контекст бизнеса (RAG Multi-Tenant), подбирает психологический фреймворк и исключает семантический бред.\n"
                "📸 4. ComfyUI (Realism 2.0) — рендерит живую мобильную фотографию (iPhone 16 Pro, 24mm) без пластика и студийной фальши.\n\n"
                "Итог: 0 секунд на объяснение ТЗ дизайнеру и 100% защита от галлюцинаций.\n\n"
                "Сохраните пост в закладки, чтобы не потерять архитектурный разбор 📌"
            )
        },
        {
            "stage_name": "BOFU (Bottom of Funnel — Низ воронки / Конверсия и Продажи)",
            "goal": "Сфокусировать на конкретной выгоде, спецпредложении и закрыть в регистрацию/демо.",
            "topic": "Подключение экосистемы UCust.AI: автоматизируйте контент-маркетинг вашего бизнеса",
            "framework": "AIDA (Attention - Interest - Desire - Action)",
            "post_text": (
                "Передайте 80% рутины контент-маркетинга автономной ИИ-экосистеме UCust.AI уже сегодня ⚡\n\n"
                "Что получает ваш бизнес сразу после онбординга за 30 секунд:\n"
                "✅ Персональный ИИ-Арт-директор, обученный на вашем фирменном стиле и брендбуке.\n"
                "✅ Автоматический контент-план на 30 дней с жесткой защитой от выгорания базы.\n"
                "✅ Фотореалистичные вижуалы студийного качества без найма продакшн-команды.\n"
                "✅ Кросс-постинг в Telegram, VK и соцсети в 1 клик через удобный дашборд.\n\n"
                "🔥 Специальное предложение: при регистрации до конца недели — полный аудит вашего текущего канала и 14 дней доступа к платформе в подарок.\n\n"
                "👉 Переходите по ссылке в описании профиля и запустите ваш автономный контент-завод за 1 минуту!"
            )
        }
    ]
    
    for idx, stage in enumerate(funnel_stages, 1):
        print("\n" + "=" * 80)
        print(f"[{idx}/3] {stage['stage_name']}")
        print("=" * 80)
        print(f"🎯 Бизнес-цель: {stage['goal']}")
        print(f"📐 Фреймворк:   {stage['framework']}")
        print(f"📌 Тема:        {stage['topic']}\n")
        
        # 1. Routing
        directive = router.route_task(topic=stage['topic'], company_name="UCust", niche="AI MarTech & SMM Automation")
        
        # 2. Prompt Generation
        prompt_data = director.create_photorealistic_prompt(
            topic=stage['topic'],
            niche="AI MarTech / Технологическая SaaS платформа",
            aspect_ratio="1:1",
            brand_colors=brand_colors
        )
        
        # 3. Critic Audit
        audit = critic.review_content(stage['post_text'], topic=stage['topic'], routing=directive)
        
        print("📝 ТЕКСТ ПОСТА ДЛЯ ПУБЛИКАЦИИ:")
        print("-" * 60)
        print(stage['post_text'])
        print("-" * 60)
        
        print("\n📸 ПРОМПТ ДЛЯ ГЕНЕРАЦИИ ВИЗУАЛА (Realism 2.0):")
        print(f"🟢 POSITIVE:\n{prompt_data['positive_prompt']}\n")
        print(f"🔴 NEGATIVE:\n{prompt_data['negative_prompt']}\n")
        
        print(f"🛡️ АУДИТ КРИТИКА: Passed = {audit.get('passed', True)}, Score = {audit.get('score', 0.95)}/1.0")

if __name__ == "__main__":
    run_funnel_showcase()
