"""
Feedback Loop & Audience Response Engine for UCust.AI.
Анализ реакции аудитории, комментариев и вовлеченности (ER) с автоматической
адаптацией контент-стратегии и синхронизацией инсайтов в Clean RAG.
"""

from __future__ import annotations

import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("feedback_loop")


class FeedbackLoopEngine:
    """
    Движок замкнутого цикла обратной связи:
    1. Расчет вовлеченности (ER) и ранжирование постов.
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

    def __init__(self):
        pass

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

        # 2. Документ с лучшими темами и форматами с высоким ER
        if top_performing_topics:
            hooks_lines = [
                f"- «{t.get('topic', '')}» (Формат: {t.get('format', 'Пост')}, ER: {t.get('er', 0.0)}%)"
                for t in top_performing_topics[:5]
            ]
            docs_to_ingest.append(Document(
                doc_id=f"high_performing_hooks_{company_name}",
                text=(
                    f"Самые результативные публикации и форматы {company_name} с максимальным откликом аудитории:\n"
                    + "\n".join(hooks_lines) + "\n"
                    f"Рекомендация: масштабировать подобные структуры постов и хуки в контент-плане."
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
        - Какие форматы усилить
        - Какие темы добавить для закрытия болей
        """
        high_er_posts = sorted(
            [p for p in history_records if p.get("er", 0) > 0],
            key=lambda x: x.get("er", 0),
            reverse=True
        )[:3]

        objections = comments_insights.get("top_objections", [])
        questions = comments_insights.get("top_questions", [])

        actionable_recommendations = []

        if high_er_posts:
            best = high_er_posts[0]
            actionable_recommendations.append(
                f"Увеличить частоту формата '{best.get('format', 'Кейс')}' — он показал максимальную вовлеченность (ER: {best.get('er', 0)}%)."
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
            "top_performing_posts": high_er_posts,
            "identified_objections": objections,
            "identified_questions": questions,
            "recommendations": actionable_recommendations,
            "summary": f"Стратегия адаптирована: выявлено {len(objections)} возражений, {len(questions)} частых вопросов и {len(high_er_posts)} топ-форматов."
        }
