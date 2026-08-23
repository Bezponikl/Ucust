"""
Unit test for TravitySearchSkill integration with Agent_Analyst.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.agents import AgentContext, Agent_Analyst
from schemas.models import (
    QuestionnaireStep1,
    QuestionnaireStep2,
    QuestionnaireStep3,
    QuestionnaireStep4,
    QuestionnaireStep5,
    UserQuestionnaire,
)
from skills.travity_search import TravitySearchSkill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_travity_search")


async def run_travity_test():
    logger.info("=== Starting TravitySearchSkill & Agent_Analyst Integration Test ===")

    # 1. Test TravitySearchSkill direct search
    skill = TravitySearchSkill()
    md_result = await skill.search("B2B автоматизация SMM")
    assert "Актуальные рыночные тренды" in md_result, "Expected Markdown title in search results"
    logger.info("[OK] TravitySearchSkill.search returned valid Markdown.")

    # 2. Test Agent_Analyst execution with web search
    q = UserQuestionnaire(
        step1=QuestionnaireStep1(
            business_name="TechFlow",
            mission="Автоматизация бизнес-процессов",
            region="Москва",
        ),
        step2=QuestionnaireStep2(
            target_audience="B2B сегмент",
            demographics="Менеджеры 30-50",
            pain_points="Затраты времени",
        ),
        step3=QuestionnaireStep3(
            tone_of_voice="Экспертный",
            content_formats="Посты",
            taboo_topics="Нет",
        ),
        step4=QuestionnaireStep4(
            goals="Лиды",
            kpi="CPL",
            frequency="3/неделю",
        ),
        step5=QuestionnaireStep5(
            competitors="CompA",
            references="RefA",
            additional_notes="Тест",
        ),
    )
    context = AgentContext(questionnaire=q)
    analyst = Agent_Analyst(search_skill=skill)

    context = analyst.process(context)
    assert context.strategy is not None, "Agent_Analyst failed to generate strategy"
    assert any("web search" in log.lower() for log in context.logs), "Log should record web search execution"

    logger.info("[OK] Agent_Analyst successfully integrated Travity web search.")
    logger.info("=== TravitySearchSkill Test SUCCESSFUL ===")


if __name__ == "__main__":
    asyncio.run(run_travity_test())
