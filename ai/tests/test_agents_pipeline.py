"""
Integration test script for the UCust.AI agent pipeline.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import traceback

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import pytest
except ImportError:
    pytest = None

# Decorator fallback if pytest / pytest-asyncio is missing
def asyncio_test(func):
    if pytest and hasattr(pytest, "mark") and hasattr(pytest.mark, "asyncio"):
        return pytest.mark.asyncio(func)
    return func

from core.agents import (
    AgentContext,
    Agent_Analyst,
    Agent_Copywriter,
    Agent_FactChecker,
    Agent_Interviewer,
    Agent_Visual_Director,
)
from schemas.models import (
    QuestionnaireStep1,
    QuestionnaireStep2,
    QuestionnaireStep3,
    QuestionnaireStep4,
    QuestionnaireStep5,
    UserQuestionnaire,
)
from storage.db import Database
from storage.vector_store import InMemoryVectorStore

# Reconfigure stdout for UTF-8 on Windows if needed
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("test_agents_pipeline")


def create_dummy_questionnaire() -> UserQuestionnaire:
    """Creates a dummy valid UserQuestionnaire for testing."""
    return UserQuestionnaire(
        step1=QuestionnaireStep1(
            business_name="TechB2B Solutions",
            mission="Автоматизация маркетинга для B2B клиентов и ускорение продаж",
            region="Москва и МО",
        ),
        step2=QuestionnaireStep2(
            target_audience="Маркетологи и владельцы малого и среднего бизнеса",
            demographics="Мужчины и женщины 25-50 лет, B2B/B2C сегмент",
            age_range="25-50 лет",
            geo="Москва и МО",
            core_audience_description="Владельцы бизнеса и SMM специалисты, ищущие автоматизацию",
            pain_points="Высокая стоимость привлечения лидов, нехватка времени на контент",
        ),
        step3=QuestionnaireStep3(
            tone_of_voice="Дружелюбный и экспертный",
            content_formats="Посты-кейсы, гайды, аналитические разборы",
            taboo_topics="Политика, религиозные споры, незаверенные обещания",
        ),
        step4=QuestionnaireStep4(
            goals="Повышение вовлеченности аудитории и конверсий",
            kpi="ER (Engagement Rate), количество заявок",
            frequency="3 раза в неделю",
        ),
        step5=QuestionnaireStep5(
            competitors="CompetitorA, CompetitorB",
            references="Примеры успешных IT-брендов и техно-блогов",
            additional_notes="Тестовый запуск конвейера агентов",
        ),
    )


@asyncio_test
async def run_pipeline_test() -> AgentContext:
    """
    Asynchronously executes the end-to-end agent pipeline test sequence:
    Agent_Interviewer -> Agent_Analyst -> Agent_Copywriter -> Agent_Visual_Director.
    """
    logger.info("=== Starting UCust.AI Agent Pipeline Integration Test ===")

    # 1. Prepare database connection for interviewer persistence test (SQLite in-memory)
    db = Database("sqlite:///:memory:")
    db.create_all()
    logger.info("Initialized SQLite in-memory database.")

    # 2. Build dummy questionnaire and base context
    questionnaire = create_dummy_questionnaire()
    context = AgentContext(questionnaire=questionnaire)
    logger.info(
        "Created initial AgentContext with questionnaire for '%s'.",
        questionnaire.step1.business_name,
    )

    # 3. Pipeline execution with error handling & logging
    current_agent_name = "Agent_Interviewer"
    try:
        # Step 3.1: Agent_Interviewer
        logger.info("[FSM State: IDLE] Executing %s...", current_agent_name)
        interviewer = Agent_Interviewer(database=db)
        context = await interviewer.process(context)

        assert (
            context.user_profile_id is not None
        ), "Agent_Interviewer failed to set user_profile_id"
        logger.info(
            "[OK] %s completed. Profile ID: %s",
            current_agent_name,
            context.user_profile_id,
        )

        # Step 3.2: Agent_Analyst
        current_agent_name = "Agent_Analyst"
        logger.info("[FSM State: DATA_COLLECTED] Executing %s...", current_agent_name)
        analyst = Agent_Analyst()
        context = await analyst.process(context)

        assert context.swot is not None, "Agent_Analyst failed to generate SWOT result"
        assert context.strategy is not None, "Agent_Analyst failed to generate strategy plan"
        logger.info(
            "[OK] %s completed. SWOT Strengths: %d, Weaknesses: %d, Opportunities: %d, Threats: %d",
            current_agent_name,
            len(context.swot.strengths),
            len(context.swot.weaknesses),
            len(context.swot.opportunities),
            len(context.swot.threats),
        )
        logger.info("Generated Strategy: %s", context.strategy.strategy[:100])

        # Step 3.3: Agent_Copywriter
        current_agent_name = "Agent_Copywriter"
        logger.info("[FSM State: MARKET_ANALYZED] Executing %s...", current_agent_name)
        vector_store = InMemoryVectorStore()
        copywriter = Agent_Copywriter(vector_store=vector_store)
        context = await copywriter.process(context)

        assert context.post_draft is not None, "Agent_Copywriter failed to produce post_draft"
        logger.info("[OK] %s completed.", current_agent_name)
        logger.info(
            "Generated Post Draft:\n'%.120s...'\nUniqueness Score: %.2f | Duplicate Flag: %s",
            context.post_draft.text,
            context.post_draft.uniqueness_score,
            context.post_draft.duplicates_found,
        )

        # Test deduplication by re-running copywriter with the same vector store
        logger.info("Testing vector store deduplication (InMemoryVectorStore)...")
        await copywriter.process(context)
        logger.info(
            "Deduplication test score: %.2f | Duplicate Flag: %s",
            context.post_draft.uniqueness_score,
            context.post_draft.duplicates_found,
        )

        # Step 3.4: Agent_FactChecker with Reflection Loop test
        current_agent_name = "Agent_FactChecker"
        logger.info("[FSM State: DRAFT_GENERATED] Testing Agent_FactChecker Reflection Loop...")

        # Simulate hallucinated claim in draft
        context.post_draft.text += " (unverified_claim 100% guarantee)"
        fact_checker = Agent_FactChecker()

        # Iteration 1: FactChecker detects hallucination -> correction_attempts=1
        context = await fact_checker.process(context)
        assert context.post_draft.fact_checked is False, "FactChecker should reject draft with unverified_claims"
        assert context.correction_attempts == 1, f"Expected correction_attempts=1, got {context.correction_attempts}"
        logger.info("[OK] Reflection Loop Attempt #1: FactChecker caught hallucinated claims: %s", context.post_draft.removed_claims)

        # Copywriter re-runs with reflection critique
        context = await copywriter.process(context)
        assert "ПРЕДЫДУЩАЯ ОШИБКА" in context.post_draft.text, "Copywriter should include reflection critique instruction"
        logger.info("[OK] Reflection Loop: Copywriter incorporated critique instruction.")

        # Iteration 2: FactChecker re-checks corrected draft -> passes cleanly
        context = await fact_checker.process(context)
        assert context.post_draft.fact_checked is True, "FactChecker should accept corrected draft"
        logger.info(
            "[OK] %s completed after reflection loop. Fact Checked: %s | Attempts: %d",
            current_agent_name,
            context.post_draft.fact_checked,
            context.correction_attempts,
        )

        # Step 3.5: Agent_Visual_Director
        current_agent_name = "Agent_Visual_Director"
        logger.info("[FSM State: CONTENT_READY] Executing %s...", current_agent_name)
        visual_director = Agent_Visual_Director()
        context = await visual_director.process(context)

        assert context.grid_plan is not None, "Agent_Visual_Director failed to build grid_plan"
        assert len(context.ltx23_prompts) > 0, "Agent_Visual_Director generated no LTX-2.3 prompts"
        logger.info("[OK] %s completed.", current_agent_name)
        logger.info("Grid Tiles count: %d", len(context.grid_plan.tiles))
        for idx, prompt in enumerate(context.ltx23_prompts, 1):
            logger.info(
                "LTX-2.3 Workflow #%d [%s, fps=%d, ckpt=%s]: Video: %s | Audio: %s",
                idx,
                prompt.aspect_ratio,
                prompt.fps,
                prompt.config.checkpoint,
                prompt.video_prompt,
                prompt.audio_prompt,
            )

        logger.info("=== Pipeline Integration Test SUCCESSFUL ===")
        return context

    except Exception as exc:
        logger.error("[FAIL] Pipeline test failed at node '%s': %s", current_agent_name, exc)
        logger.error("Detailed traceback:\n%s", traceback.format_exc())
        raise exc


if __name__ == "__main__":
    asyncio.run(run_pipeline_test())
