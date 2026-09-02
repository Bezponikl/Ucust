"""
Feedback Loop & Audience Response Engine for UCust.AI.
Анализ реакции аудитории, комментариев и вовлеченности (ER) с автоматической
адаптацией контент-стратегии и синхронизацией инсайтов в Clean RAG.
"""

from __future__ import annotations

import re
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("feedback_loop")


class FeedbackLoopEngine:
    """
    Движок замкнутого цикла обратной связи и самообучения:
    1. Расчет вовлеченности (ER) и позитивности аудитории (NAI, WPR, Log Score).
    2. Семантический анализ комментариев: извлечение болей, вопросов и возражений.
    3. Синхронизация инсайтов аудитории в RAG и SQL.
    4. Автоматическая адаптация будущих контент-планов.
    """

    POSITIVE_WORDS = {
        "спасибо", "отлично", "супер", "круто", "огонь", "класс", "молодцы", "рекомендую",
        "лучшие", "топ", "красота", "нравится", "полезно", "записался", "купил", "восторг"
    }
    NEGATIVE_WORDS = {
        "ужас", "плохо", "обман", "не работает", "разочарован", "минус", "хамство", "долго",
        "не советую", "брак", "отвратительно", "развод", "отписка", "спам"
    }

    OBJECTION_PATTERNS = [
        (r"(?i)(?:слишком\s*)?дорог[оа-я]*|цен[аы]|переплат[а-я]*|стоимост[а-я]*\s*высок", "Высокая цена / Страх переплаты"),
        (r"(?i)гаранти[яиюе]|возврат|страховк|а\s*если\s*сломается|надежн[оа-я]*", "Сомнения в гарантии и надежности"),
        (r"(?i)срок[иов]|дедлайн|когда\s*будет\s*готов|как\s*долго|опоздан", "Сроки выполнения и пунктуальность"),
        (r"(?i)где\s*находит[а-я]*|адрес|как\s*доехать|локаци[яию]|доставк[а-я]*", "География, адрес и условия доставки"),
        (r"(?i)рассрочк[а-я]*|кредит|оплат[а-я]*\s*частями|безнал", "Условия оплаты и рассрочки")
    ]

    # Справочники реакций и эмодзи по соцсетям
    EMOJI_POSITIVE_SET = {
        '👍', '❤️', '🔥', '🎉', '🤩', '🥰', '👏', '💯', '⚡', '🤝', '🏆',
        '😍', '🚀', '👌', '💪', '✨', '💐', '💎', '🎯', '🙌', '🌟', '💖',
        'like', 'super', 'love', 'fire', 'heart', 'applause', 'celebrate'
    }
    EMOJI_NEGATIVE_SET = {
        '👎', '💩', '🤮', '😡', '🤬', '🥱', '💔', '🤡', '🤦', '🖕', '🤢',
        'dislike', 'hate', 'angry', 'trash', 'frown', 'bad', 'crap'
    }
    EMOJI_AMUSED_NEUTRAL_SET = {
        '🤔', '😱', '🤯', '👀', '🤷', '🤨', '😂', '🤣', '😆', '😄',
        'funny', 'laugh', 'wow', 'sad'
    }

    def __init__(self):
        pass

    @classmethod
    def parse_social_reactions(
        cls,
        platform: str,
        raw_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Универсальный парсер реакций и кастомных эмодзи для любых соцсетей:
        Telegram, VK, Instagram, TikTok, YouTube, MAX.
        
        Принимает:
        - raw_metrics со словарем эмодзи: {"👍": 150, "🔥": 80, "👎": 4, "custom_fire": 12, "💩": 1}
        - Либо стандартные поля: {"likes": 1200, "dislikes": 5, "comments": 45, "shares": 30, "saves": 70}
        - Либо смешанный формат с кастомными эмодзи.
        """
        p_lower = (platform or "telegram").lower()
        
        likes = int(raw_metrics.get("likes", 0) or raw_metrics.get("like", 0))
        dislikes = int(raw_metrics.get("dislikes", 0) or raw_metrics.get("dislike", 0))
        comments = int(raw_metrics.get("comments", 0) or raw_metrics.get("comment", 0))
        shares = int(raw_metrics.get("shares", 0) or raw_metrics.get("reposts", 0) or raw_metrics.get("share", 0))
        saves = int(raw_metrics.get("saves", 0) or raw_metrics.get("bookmarks", 0) or raw_metrics.get("favorites", 0))
        
        custom_positives = 0
        custom_negatives = 0
        custom_neutral = 0

        breakdown = {
            "platform": platform,
            "positive_emojis": {},
            "negative_emojis": {},
            "neutral_emojis": {},
            "custom_emojis": {},
            "high_intent_actions": {"saves": saves, "shares": shares, "comments": comments}
        }

        # 1. Извлечение словаря реакций (если передан словарь эмодзи или поле reactions)
        reactions_dict = {}
        if isinstance(raw_metrics.get("reactions"), dict):
            reactions_dict.update(raw_metrics["reactions"])
        elif isinstance(raw_metrics.get("reactions"), list):
            for item in raw_metrics["reactions"]:
                if isinstance(item, dict) and "emoji" in item:
                    reactions_dict[str(item.get("emoji"))] = int(item.get("count", 1))
                elif isinstance(item, str):
                    reactions_dict[item] = reactions_dict.get(item, 0) + 1

        # Также сканируем ключи первого уровня raw_metrics
        for k, v in raw_metrics.items():
            if k not in {"views", "likes", "like", "dislikes", "dislike", "comments", "comment", "shares", "share", "reposts", "saves", "bookmarks", "favorites", "reactions", "platform", "post_id"}:
                if isinstance(v, (int, float)) and v > 0:
                    reactions_dict[str(k)] = int(v)

        # 2. Классификация эмодзи и кастомных реакций
        for emoji_key, count in reactions_dict.items():
            clean_key = str(emoji_key).strip()
            key_lower = clean_key.lower()

            # Проверка стандартных позитивных эмодзи
            if clean_key in cls.EMOJI_POSITIVE_SET or key_lower in cls.EMOJI_POSITIVE_SET:
                likes += count
                breakdown["positive_emojis"][clean_key] = count

            # Проверка стандартных негативных эмодзи
            elif clean_key in cls.EMOJI_NEGATIVE_SET or key_lower in cls.EMOJI_NEGATIVE_SET:
                dislikes += count
                breakdown["negative_emojis"][clean_key] = count

            # Проверка нейтральных/смех
            elif clean_key in cls.EMOJI_AMUSED_NEUTRAL_SET or key_lower in cls.EMOJI_AMUSED_NEUTRAL_SET:
                custom_neutral += count
                breakdown["neutral_emojis"][clean_key] = count

            # Кастомные эмодзи (Telegram Premium / Brand Emojis)
            else:
                # Если в имени кастомного эмодзи есть маркер негатива
                if any(neg_kw in key_lower for neg_kw in ["neg", "bad", "trash", "poop", "clown", "hate", "angry", "dislike"]):
                    custom_negatives += count
                    dislikes += count
                    breakdown["custom_emojis"][f"{clean_key} (негатив)"] = count
                else:
                    # Все остальные кастомные брендовые эмодзи трактуются как активный позитив
                    custom_positives += count
                    breakdown["custom_emojis"][clean_key] = count

        # 3. Расчет суммарного R (глубокое вовлечение с учетом весов соцсетей)
        # Комментарии (1.5x) + Репосты (1.8x) + Закладки/Сохранения Instagram/TikTok (2.0x) + Кастомные позитивные эмодзи (1.5x) + Смех/Любопытство (1.0x)
        weighted_R = (
            comments * 1.0 +
            shares * 1.2 +
            saves * 1.5 +
            custom_positives * 1.0 +
            custom_neutral * 0.7
        )

        return {
            "effective_likes": likes,
            "effective_dislikes": dislikes,
            "effective_reactions": round(weighted_R, 2),
            "raw_comments": comments,
            "raw_shares": shares,
            "raw_saves": saves,
            "breakdown": breakdown
        }

    @classmethod
    def calculate_positivity_metrics(
        cls,
        views: int,
        likes: int,
        dislikes: int = 0,
        comments: int = 0,
        shares: int = 0,
        other_reactions: int = 0,
        platform: str = "telegram",
        raw_reactions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Математический расчет качества восприятия (позитивности) поста:
        1. NAI (Net Approval Index) — Индекс чистого одобрения [0.0 ... 1.0]:
           NAI = L / (L + D + 1)
        2. WPR (Weighted Positivity Rate) — Взвешенная позитивность на просмотр (%):
           WPR = ((1.0 * L + 1.5 * R - 2.0 * D) / max(V, 1)) * 100
        3. Logarithmic Positivity Score — Логарифмический масштабированный балл:
           Score = log10(V + 1) * ((1.0 * L + 1.5 * R + 1) / (1.0 * D + 1))
        """
        V = max(0, int(views))

        # Если передан словарь кастомных эмодзи / мультиплатформенных реакций
        if raw_reactions:
            parsed = cls.parse_social_reactions(platform, raw_reactions)
            L = parsed["effective_likes"]
            D = parsed["effective_dislikes"]
            R = parsed["effective_reactions"]
            breakdown_info = parsed["breakdown"]
        else:
            L = max(0, int(likes))
            D = max(0, int(dislikes))
            R = max(0, int(comments) + int(shares) + int(other_reactions))
            breakdown_info = None

        # 1. Индекс чистого одобрения (Net Approval Index)
        nai = float(L) / float(L + D + 1)
        nai_rounded = round(nai, 4)

        # 2. Взвешенный расчет с просмотрами (Weighted Positivity Rate в %)
        safe_v = max(V, 1)
        wpr = ((1.0 * L + 1.5 * R - 2.0 * D) / safe_v) * 100.0
        wpr_rounded = round(wpr, 2)

        # 3. Логарифмический масштабированный балл (Logarithmic Positivity Score)
        log_views = math.log10(V + 1)
        positivity_multiplier = (1.0 * L + 1.5 * R + 1.0) / (1.0 * D + 1.0)
        score = log_views * positivity_multiplier
        score_rounded = round(score, 2)

        # 4. Категоризация и грейд успешности поста
        if V < 20:
            grade = "INITIAL_REACH"
            sentiment_summary = "Стартовый охват (мало данных)"
        elif score >= 100.0 and nai >= 0.85:
            grade = "VIRAL_POSITIVE"
            sentiment_summary = "🔥 Вирусный хит с максимальным одобрением"
        elif score >= 20.0 and nai >= 0.70:
            grade = "HIGH_POSITIVE"
            sentiment_summary = "⭐ Высокий устойчивый позитив аудитории"
        elif score >= 5.0 and nai >= 0.50:
            grade = "MODERATE_POSITIVE"
            sentiment_summary = "👍 Умеренно-позитивный отклик"
        elif D > L or nai < 0.40:
            grade = "NEGATIVE_OUTFLOW"
            sentiment_summary = "⚠️ Преобладание негатива / Требуется реакция"
        else:
            grade = "CONTROVERSIAL"
            sentiment_summary = "⚡ Спорный контент (высокий уровень дизлайков)"

        # Взвешенный ER для совместимости
        er = cls.calculate_engagement_rate(views=V, likes=L, comments=int(comments), shares=int(shares))

        result = {
            "views": V,
            "likes": L,
            "dislikes": D,
            "reactions": R,
            "net_approval_index": nai_rounded,
            "weighted_positivity_rate": wpr_rounded,
            "log_positivity_score": score_rounded,
            "engagement_rate": er,
            "grade": grade,
            "summary": sentiment_summary
        }
        if breakdown_info:
            result["reactions_breakdown"] = breakdown_info
        return result

    @classmethod
    def calculate_engagement_rate(cls, views: int, likes: int, comments: int, shares: int) -> float:
        """
        Взвешенный Engagement Rate (ER):
        Лайк: 1x, Комментарий: 2x (высокое вовлечение), Репост: 3x (виральность).
        """
        safe_views = max(int(views), 1)
        weighted_interactions = int(likes) * 1.0 + int(comments) * 2.0 + int(shares) * 3.0
        er = (weighted_interactions / safe_views) * 100.0
        return round(er, 2)

    @classmethod
    def analyze_comments(cls, comments: List[str]) -> Dict[str, Any]:
        """
        Семантический анализ комментариев:
        - Определение тональности (Sentiment)
        - Извлечение частых вопросов покупателей (FAQ)
        - Выявление возражений и барьеров к покупке
        """
        if not comments:
            return {
                "total_comments": 0,
                "sentiment": "neutral",
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "top_questions": [],
                "top_objections": []
            }

        pos_count = 0
        neg_count = 0
        neu_count = 0
        questions: List[str] = []
        objections: List[str] = []

        for comment in comments:
            c_clean = comment.strip()
            if not c_clean:
                continue

            c_lower = c_clean.lower()
            words = set(re.findall(r'[a-zA-Zа-яА-ЯёЁ]+', c_lower))

            has_pos = bool(words & cls.POSITIVE_WORDS)
            has_neg = bool(words & cls.NEGATIVE_WORDS)

            if has_pos and not has_neg:
                pos_count += 1
            elif has_neg and not has_pos:
                neg_count += 1
            else:
                neu_count += 1

            # Поиск вопросов
            if "?" in c_clean or any(q_word in c_lower for q_word in ["как ", "сколько ", "где ", "можно ли", "подскажите"]):
                if len(c_clean) > 8 and c_clean not in questions:
                    questions.append(c_clean)

            # Поиск возражений
            for pattern, obj_label in cls.OBJECTION_PATTERNS:
                if re.search(pattern, c_clean):
                    if obj_label not in objections:
                        objections.append(obj_label)

        total = len(comments)
        if pos_count > neg_count and pos_count > neu_count:
            overall_sentiment = "positive"
        elif neg_count > pos_count:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        return {
            "total_comments": total,
            "sentiment": overall_sentiment,
            "sentiment_breakdown": {
                "positive": pos_count,
                "neutral": neu_count,
                "negative": neg_count
            },
            "top_questions": questions[:5],
            "top_objections": objections[:5]
        }

    async def sync_feedback_to_rag(
        self,
        company_name: str,
        niche: str,
        comments_analysis: Dict[str, Any],
        top_performing_topics: List[Dict[str, Any]],
        rag_pipeline: Any
    ) -> int:
        """
        Векторизует и сохраняет извлеченные инсайты аудитории в Clean RAG.
        """
        from rag.models import Document

        docs_to_ingest = []
        questions = comments_analysis.get("top_questions", [])
        objections = comments_analysis.get("top_objections", [])

        # 1. Документ с вопросами и возражениями аудитории
        if questions or objections:
            q_str = "\n- ".join(questions) if questions else "Вопросов нет"
            obj_str = "\n- ".join(objections) if objections else "Явных барьеров не выявлено"
            docs_to_ingest.append(Document(
                doc_id=f"audience_feedback_{company_name}",
                text=(
                    f"Реальные вопросы и возражения аудитории компании {company_name} (Ниша: {niche}):\n"
                    f"Часто задаваемые вопросы покупателей (FAQ):\n- {q_str}\n"
                    f"Главные возражения и сомнения аудитории:\n- {obj_str}\n"
                    f"Рекомендация: следующие посты должны снимать эти возражения и отвечать на эти вопросы."
                ),
                metadata={"category": "audience_feedback", "company_name": company_name}
            ))

        # 2. Документ с лучшими темами и форматами с высоким Score и одобрением (NAI)
        if top_performing_topics:
            hooks_lines = [
                f"- «{t.get('topic', '')}» (Формат: {t.get('format', 'Пост')}, Positivity Score: {t.get('log_positivity_score', t.get('score', 0.0))}, Одобрение NAI: {t.get('net_approval_index', t.get('nai', 1.0))}, ER: {t.get('er', 0.0)}%)"
                for t in top_performing_topics[:5]
            ]
            docs_to_ingest.append(Document(
                doc_id=f"high_performing_hooks_{company_name}",
                text=(
                    f"Самые результативные и позитивно воспринятые публикации {company_name} с максимальным одобрением:\n"
                    + "\n".join(hooks_lines) + "\n"
                    f"Рекомендация: масштабировать подобные структуры постов, формулы хуков и офферы в контент-плане."
                ),
                metadata={"category": "high_performing_hooks", "company_name": company_name}
            ))

        if docs_to_ingest and rag_pipeline:
            count = await rag_pipeline.ingest_documents_async(docs_to_ingest)
            logger.info(f"[FeedbackLoop] 📚 Засинхронизировано {count} инсайтов обратной связи в RAG для {company_name}.")
            return count
        return 0

    @classmethod
    def generate_strategy_adaptations(
        cls,
        history_records: List[Dict[str, Any]],
        comments_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерирует конкретные рекомендации по адаптации контент-стратегии:
        - Ранжирование по логарифмическому баллу позитивности (Log Positivity Score)
        - Выявление спорных и негативных тем для отработки
        - Какие форматы масштабировать
        - Какие темы добавить для закрытия болей
        """
        # Сортируем по логарифмическому баллу позитивности и вовлеченности
        high_performing_posts = sorted(
            history_records,
            key=lambda x: (x.get("log_positivity_score", 0.0), x.get("er", 0.0)),
            reverse=True
        )[:3]

        controversial_posts = [
            p for p in history_records 
            if (p.get("dislikes_count", 0) > 0 or p.get("net_approval_index", 1.0) < 0.6)
        ]

        objections = comments_insights.get("top_objections", [])
        questions = comments_insights.get("top_questions", [])

        actionable_recommendations = []

        if high_performing_posts:
            best = high_performing_posts[0]
            actionable_recommendations.append(
                f"Масштабировать формат '{best.get('format', 'Пост')}' — он показал рекордный балл позитивности (Score: {best.get('log_positivity_score', 0)}, NAI: {best.get('net_approval_index', 1.0)})."
            )

        if controversial_posts:
            worst = controversial_posts[0]
            actionable_recommendations.append(
                f"Отработать критику к теме «{worst.get('topic', 'Прошлая публикация')}» (NAI: {worst.get('net_approval_index', 0.5)}) через экспертный пост с фактами и гарантиями."
            )

        if objections:
            actionable_recommendations.append(
                f"Внедрить в контент-план посты, напрямую закрывающие барьер «{objections[0]}»."
            )

        if questions:
            actionable_recommendations.append(
                f"Опубликовать пост-разбор с прямым ответом на вопрос аудитории: «{questions[0]}»."
            )

        return {
            "status": "success",
            "top_performing_posts": high_performing_posts,
            "controversial_posts": controversial_posts,
            "identified_objections": objections,
            "identified_questions": questions,
            "recommendations": actionable_recommendations,
            "summary": f"Стратегия адаптирована: выявлено {len(objections)} возражений, {len(questions)} частых вопросов и {len(high_performing_posts)} топ-публикаций."
        }
