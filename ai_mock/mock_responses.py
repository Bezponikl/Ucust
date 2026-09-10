"""
Mock Response Generator for UCust AI Service.
Provides high-fidelity, realistic response structures matching the real Saiga NeMo, Moondream2, ComfyUI, and Clean RAG outputs.
"""

import time
import random
import uuid
from typing import Any, Dict, List, Optional


def generate_mock_post_text(
    topic: Optional[str] = None,
    company_name: Optional[str] = None,
    niche: Optional[str] = None,
    rubric: Optional[str] = None,
    promo_code: Optional[str] = None,
    primary_cta: Optional[str] = None,
    tone: Optional[str] = None,
    language: str = "ru"
) -> str:
    topic_clean = topic or "Специальное предложение и новинки сезона"
    brand = company_name or "UCust"
    rubric_clean = (rubric or "PRODUCT").upper()
    code = promo_code or "UCUST2026"
    cta = (primary_cta or "BUY").upper()
    
    cta_texts = {
        "BUY": f"👉 Оформляйте заказ прямо сейчас по ссылке в профиле и используйте промокод {code} для приятной выгоды!",
        "BOOK": f"📅 Забронируйте удобное время онлайн или напишите нам в директ прямо сейчас!",
        "COMMENT": "💬 А какой вариант выбираете вы? Поделитесь своим мнением в комментариях ниже 👇",
        "CHAT": "📩 Напишите нам в личные сообщения слово «СТАРТ», чтобы получить персональную консультацию!",
        "PROMO": f"🎁 Назовите промокод {code} при покупке и получите скидку 15% до конца недели!"
    }
    cta_phrase = cta_texts.get(cta, cta_texts["BUY"])

    if language.lower().startswith("en"):
        return (
            f"✨ Elevate your experience with {brand}!\n\n"
            f"Looking for the perfect balance of quality and innovation in {niche or 'our industry'}? "
            f"We are excited to present our latest update: {topic_clean}.\n\n"
            f"🔹 Crafted with attention to every single detail\n"
            f"🔹 Transparent service and unmatched reliability\n"
            f"🔹 Designed specifically to save your valuable time\n\n"
            f"{cta_phrase}\n\n"
            f"#brand #innovation #quality #{brand.lower().replace(' ', '')}"
        )

    # Russian templates by rubric
    if rubric_clean == "EXPERT":
        return (
            f"💡 3 критические ошибки в нише «{niche or 'бизнес'}», которые съедают ваш бюджет\n\n"
            f"Многие считают, что в теме «{topic_clean}» главное — просто делать больше действий. "
            f"Но опыт команды {brand} показывает обратное:\n\n"
            f"1️⃣ Отсутствие системности и четкого позиционирования.\n"
            f"2️⃣ Игнорирование запросов реальной аудитории.\n"
            f"3️⃣ Экономия на инструментах автоматизации.\n\n"
            f"Когда вы внедряете прозрачные процессы, результат вырастает в 2–3 раза без лишних затрат.\n\n"
            f"{cta_phrase}\n\n"
            f"#экспертиза #бизнес #{brand.lower().replace(' ', '')} #развитие"
        )
    elif rubric_clean == "CASE":
        return (
            f"📈 Кейс: Как тема «{topic_clean}» принесла +40% к ключевым метрикам\n\n"
            f"К нам в {brand} часто обращаются с вопросом: как быстро перестроить процессы и масштабировать результат в сфере {niche or 'услуг'}?\n\n"
            f"Что мы сделали:\n"
            f"✔️ Провели полный аудит узких мест\n"
            f"✔️ Внедрили персональный сценарий взаимодействия\n"
            f"✔️ Устранили рутину за счет автоматизации\n\n"
            f"Итог: рост конверсии на 42% и стабильный поток лояльных клиентов.\n\n"
            f"{cta_phrase}\n\n"
            f"#кейс #результаты #{brand.lower().replace(' ', '')} #маркетинг"
        )
    elif rubric_clean == "PROMO":
        return (
            f"🔥 Специальное предложение от {brand}!\n\n"
            f"Только на этой неделе — {topic_clean} с максимальной выгодой.\n\n"
            f"🎁 Используйте промокод «{code}» и получите эксклюзивные условия обслуживания.\n\n"
            f"⏳ Предложение действует ограниченное время. Не откладывайте!\n\n"
            f"{cta_phrase}\n\n"
            f"#скидки #акция #промокод #{brand.lower().replace(' ', '')}"
        )
    else:  # PRODUCT / DEFAULT
        return (
            f"Невесомый баланс эстетики и безупречного качества от {brand} ✨\n\n"
            f"Представляем: {topic_clean}.\n\n"
            f"Мы продумали каждую деталь, чтобы вы получали истинное удовольствие от каждого момента:\n"
            f"🌿 Только премиальные ингредиенты и проверенные материалы\n"
            f"💎 Авторский подход и внимание к вашим пожеланиям\n"
            f"⚡️ Быстрая подача и заботливый сервис\n\n"
            f"{cta_phrase}\n\n"
            f"#новинка #качество #стиль #{brand.lower().replace(' ', '')} #рекомендация"
        )


def get_mock_post_result(payload: Dict[str, Any], host: str = "http://localhost:8000") -> Dict[str, Any]:
    company_name = payload.get("company_name") or payload.get("companyName") or "UCust"
    niche = payload.get("niche") or "Бизнес и Услуги"
    topic = payload.get("topic") or payload.get("prompt") or "Презентация флагманского продукта"
    rubric = payload.get("rubric") or "PRODUCT"
    promo_code = payload.get("promo_code") or payload.get("promoCode")
    primary_cta = payload.get("primaryCta") or payload.get("primary_cta") or "BUY"
    tone = payload.get("tone") or payload.get("toneOfVoice") or "FRIENDLY"
    aspect_ratio = payload.get("aspect_ratio") or "1:1"
    language = payload.get("language") or "ru"

    post_text = generate_mock_post_text(
        topic=topic,
        company_name=company_name,
        niche=niche,
        rubric=rubric,
        promo_code=promo_code,
        primary_cta=primary_cta,
        tone=tone,
        language=language
    )

    img_seed = random.randint(100000, 999999)
    image_url = f"{host}/output/photos/mock_gen_{img_seed}.png"

    return {
        "status": "success",
        "post_text": post_text,
        "image_url": image_url,
        "photo_url": image_url,
        "media_url": image_url,
        "hashtags": f"#{company_name.lower().replace(' ', '')} #{rubric.lower()} #тренды #маркетинг",
        "critic_score": round(random.uniform(9.2, 9.8), 1),
        "uniqueness_score": 0.98,
        "fact_checked": True,
        "metadata": {
            "framework": payload.get("framework", "PAS"),
            "rubric": rubric,
            "primary_cta": primary_cta,
            "tone": tone,
            "language": language,
            "aspect_ratio": aspect_ratio,
            "estimated_reach": random.randint(1800, 4500),
            "engagement_rate": "4.8%"
        },
        "timings": {
            "vlm_seconds": 0.05,
            "llm_seconds": 0.12,
            "image_gen_seconds": 0.08,
            "total_seconds": 0.25
        }
    }


def get_mock_collector_result(source_type: str, target: str, limit: int = 10) -> Dict[str, Any]:
    st = source_type.lower()
    
    if "telegram" in st or (st == "auto" and ("t.me" in target or target.startswith("@"))):
        channel_name = target.replace("https://t.me/", "").replace("@", "")
        return {
            "status": "success",
            "source_type": "telegram",
            "target": target,
            "channel_title": f"{channel_name.capitalize()} Official",
            "subscribers": 14250,
            "avg_views_per_post": 3800,
            "posts_analyzed": min(limit, 10),
            "extracted_posts": [
                {
                    "post_id": i + 100,
                    "date": "2026-03-08T12:00:00Z",
                    "text": f"Свежее обновление в {channel_name}! Мы улучшили процессы и рады представить наши новые возможности.",
                    "views": 4120 - (i * 150),
                    "reactions": 85 - (i * 3),
                    "has_media": True,
                    "vlm_vision_description": "Профессиональная фотография интерьера и продукта с мягким теплым освещением.",
                    "ocr_detected_text": "UCUST 2026 PREMIUM"
                }
                for i in range(min(limit, 5))
            ],
            "brand_identity": {
                "inferred_tov": "FRIENDLY / EXPERT",
                "dominant_colors": ["#1E3A8A", "#F3F4F6", "#D97706"],
                "frequent_topics": ["новинки", "кейсы", "отзывы клиентов", "акции"]
            },
            "timings": {"parse_seconds": 0.08, "vision_ocr_seconds": 0.12, "total_seconds": 0.20}
        }
    
    elif "vk" in st or (st == "auto" and "vk.com" in target):
        return {
            "status": "success",
            "source_type": "vk",
            "target": target,
            "group_name": "Сообщество клиентов и экспертов",
            "members_count": 8900,
            "posts_analyzed": min(limit, 10),
            "top_posts": [
                {
                    "id": 101,
                    "likes": 142,
                    "reposts": 28,
                    "comments": 19,
                    "text": "Как выбрать идеальное решение для вашего бизнеса: 5 практических советов."
                }
            ],
            "audience_engagement": {"er": 3.4, "sentiment": "POSITIVE"},
            "timings": {"parse_seconds": 0.06, "total_seconds": 0.06}
        }

    elif "geo" in st or "2gis" in st or "yandex" in st or (st == "auto" and ("2gis" in target or "yandex.ru/maps" in target)):
        provider = "2gis" if "2gis" in target else "yandex"
        return {
            "status": "success",
            "source_type": f"geo_{provider}",
            "target": target,
            "company_name": "Флагманский филиал в Москве",
            "rating": 4.9,
            "reviews_total": 348,
            "reviews_analyzed": min(limit, 10),
            "key_strengths": ["Быстрое и вежливое обслуживание", "Уютная атмосфера", "Высокое качество продукции"],
            "key_weaknesses": ["Иногда сложно припарковаться в часы пик"],
            "client_pains_summary": "Клиенты ценят стабильное качество и заботу персонала, ключевая ценность — скорость обслуживания.",
            "sample_reviews": [
                {"author": "Алексей С.", "rating": 5, "text": "Великолепный сервис! Все быстро, четко и на высшем уровне."},
                {"author": "Елена М.", "rating": 5, "text": "Постоянно обращаюсь, всегда неизменно высокое качество."}
            ],
            "timings": {"parse_seconds": 0.09, "total_seconds": 0.09}
        }

    elif "website" in st or (st == "auto" and ("http://" in target or "https://" in target)):
        return {
            "status": "success",
            "source_type": "website",
            "target": target,
            "title": "Инновационные решения и продукты нового поколения",
            "meta_description": "Официальный сайт. Профессиональный сервис, индивидуальный подход и гарантированное качество.",
            "usp": "Увеличение эффективности и автоматизация ключевых процессов за 1 день",
            "extracted_services": [
                {"title": "Базовый аудит и настройка", "price": "от 15 000 ₽"},
                {"title": "Комплексное внедрение под ключ", "price": "от 65 000 ₽"}
            ],
            "detected_palette": ["#0F172A", "#3B82F6", "#F8FAFC"],
            "contacts": {"phone": "+7 (495) 123-45-67", "email": "info@ucust.ai", "city": "Москва"},
            "timings": {"parse_seconds": 0.11, "total_seconds": 0.11}
        }

    elif "doc" in st or "pdf" in target.lower() or "docx" in target.lower():
        return {
            "status": "success",
            "source_type": "documents",
            "target": target,
            "pages_analyzed": 12,
            "extracted_text_snippet": "Прайс-лист и регламент оказания услуг компании на 2026 год...",
            "extracted_tables_count": 3,
            "key_facts": [
                "Тариф 'Стандарт' включает 30 публикаций в месяц",
                "Тариф 'Премиум' включает генерацию видео и круглосуточную поддержку",
                "Срок первого запуска составляет 24 часа"
            ],
            "timings": {"parse_seconds": 0.07, "total_seconds": 0.07}
        }

    else:
        return {
            "status": "success",
            "source_type": "universal_hub",
            "target": target,
            "summary": "Автоматический анализ ресурса успешно завершен. Извлечено ключевое позиционирование и параметры бренда.",
            "timings": {"parse_seconds": 0.05, "total_seconds": 0.05}
        }


def get_mock_strategy_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    company = payload.get("company_name", "UCust")
    niche = payload.get("niche", "Бизнес")
    
    return {
        "status": "success",
        "company_name": company,
        "niche": niche,
        "funnel": {
            "TOFU_Awareness": [
                "Вирусные рилсы и посты-боли ниши",
                "Разбор топ-5 заблуждений клиентов",
                "Юмористические тренды и жизненные ситуации"
            ],
            "MOFU_Consideration": [
                "Сравнение методов работы и демонстрация процессов",
                "Интервью с экспертами и ответы на частые вопросы",
                "Разбор реальных кейсов 'До / После'"
            ],
            "BOFU_Conversion": [
                "Специальные промокоды и лимитированные офферы",
                "Прямая демонстрация ценности продукта с призывом к покупке",
                "Отзывы довольных клиентов и социальные доказательства"
            ]
        },
        "target_avatars": [
            {
                "avatar": "Занятой предприниматель 30-45 лет",
                "pain": "Нехватка времени на ведение контента и контроль подрядчиков",
                "solution": "Полная автоматизация и предсказуемый поток заявок"
            }
        ],
        "viral_hooks": [
            "Почему 90% предпринимателей теряют клиентов на ровном месте?",
            "1 секрет, который удвоил нашу конверсию без увеличения бюджета",
            "Если бы я начинал в 2026 году с нуля, вот 3 вещи, которые я бы сделал"
        ],
        "timings": {"strategy_seconds": 0.14, "total_seconds": 0.14}
    }


def get_mock_content_plan_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    days = int(payload.get("days_count", 7))
    company = payload.get("company_name", "UCust")
    niche = payload.get("niche", "Бизнес")
    
    rubrics = ["EXPERT", "PRODUCT", "CASE", "PROMO", "LIFE", "MEME"]
    plan = []
    for d in range(1, days + 1):
        rub = rubrics[(d - 1) % len(rubrics)]
        plan.append({
            "day": d,
            "rubric": rub,
            "title": f"День {d}: {rub.capitalize()} публикация для {company}",
            "topic": f"Практический разбор в нише {niche}: шаг {d}",
            "format": "Пост + Карусель / Фото",
            "goal": "Охват и вовлечение" if rub in ["MEME", "EXPERT"] else "Продажи и лидогенерация"
        })
    
    return {
        "status": "success",
        "company_name": company,
        "niche": niche,
        "days_count": days,
        "schedule": plan,
        "timings": {"plan_seconds": 0.08, "total_seconds": 0.08}
    }


def get_mock_critic_result(text: str, strictness: float = 0.85) -> Dict[str, Any]:
    return {
        "status": "success",
        "score": round(random.uniform(9.3, 9.7), 1),
        "verdict": "Текст соответствует высоким стандартам маркетинговой конверсии и правилам инверсии Чарли Мангера.",
        "analysis": {
            "hook_strength": 9.5,
            "cliche_count": 0,
            "cta_clarity": 9.8,
            "tone_consistency": 9.6
        },
        "suggestions": [
            "Структура выдержана идеально",
            "Призыв к действию четкий и не перегружен"
        ],
        "improved_text": text,
        "timings": {"critic_seconds": 0.04, "total_seconds": 0.04}
    }
