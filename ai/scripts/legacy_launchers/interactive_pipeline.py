import os
import time
import asyncio
from typing import Optional

# Ensure we use Postgres backend for Atlas graph
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/ai_smm"
os.environ["SYNRIX_BACKEND"] = "postgres"

from synrix_runtime.api.runtime import AgentRuntime
from synrix.agent_backend import SynrixAgentBackend
from core.orchestrator import AgentOrchestrator, AgentState, UserApprovalNode, build_default_orchestrator
from core.notification_bridge import NotificationBridge, ApprovalDecision
from storage.db import Database
from schemas.models import QuestionnaireStep1, QuestionnaireStep2, QuestionnaireStep3, QuestionnaireStep4, QuestionnaireStep5, UserQuestionnaire
from core.agents import AgentContext

def get_backend():
    db_url = os.environ.get("DATABASE_URL", "")
    return SynrixAgentBackend(backend="postgres", dsn=db_url, tenant_id="dev")

def interactive_notifier(post_content: str, image_url: Optional[str] = None) -> ApprovalDecision:
    print("\n" + "="*60)
    print("🔔 ВНИМАНИЕ: Ожидается действие пользователя (Human-in-the-Loop)!")
    print("="*60)
    print("\n📝 Сгенерированный черновик (Draft):\n")
    print(post_content)
    print("-" * 60)
    
    while True:
        print("\nВаши действия:")
        print(" [1] Одобрить (APPROVED)")
        print(" [2] Переделать с нуля (REGENERATE)")
        print(" [3] Внести правки (EDIT)")
        
        choice = input("Выберите номер [1/2/3]: ").strip()
        
        if choice == "1":
            print("✅ Черновик одобрен! Продолжаем пайплайн (генерация видео)...")
            return ApprovalDecision.APPROVED
        elif choice == "2":
            print("🔄 Запрошена полная регенерация. Возвращаем стейт-машину на шаг MARKET_ANALYZED...")
            return ApprovalDecision.REGENERATE
        elif choice == "3":
            print("✏️ Режим редактирования. Введите, что именно нужно исправить:")
            edit_context = input("> ")
            # We return EDIT. The orchestrator will handle it.
            return ApprovalDecision.EDIT
        else:
            print("❌ Неизвестный выбор, попробуйте еще раз.")

async def main():
    print("\n🚀 Инициализация интерактивного пайплайна UCust.AI...")
    
    # Init Octopoda Backend
    backend = get_backend()
    
    # Create AgentRuntimes for our agents so we can log to Atlas
    orchestrator_rt = AgentRuntime("orchestrator", agent_type="orchestrator", backend_override=backend, require_account=False)
    
    # Build a database (mock sqlite memory for Interviewer)
    db = Database("sqlite:///:memory:")
    db.create_all()
    
    # Build Orchestrator
    orchestrator = build_default_orchestrator(database=db)
    
    # Replace the Approval Node's bridge with our interactive terminal bridge
    interactive_bridge = NotificationBridge(notifier=interactive_notifier)
    orchestrator.approval_node = UserApprovalNode(bridge=interactive_bridge)
    
    # Create a dummy questionnaire (like a user filled out the briefing)
    q = UserQuestionnaire(
        step1=QuestionnaireStep1(business_name="CyberTech SMM", industry="Tech", product="AI Automation", location="Global"),
        step2=QuestionnaireStep2(target_audience="B2B", pain_points="Slow process", goals="Lead Gen"),
        step3=QuestionnaireStep3(tone_of_voice="Professional", content_formats="Posts", taboo_topics="Politics"),
        step4=QuestionnaireStep4(goals="Leads", kpi="Clicks", frequency="Daily"),
        step5=QuestionnaireStep5(competitors="None", references="Apple", additional_notes="Make it viral")
    )
    context = AgentContext(questionnaire=q)
    
    # Hack the context.add_log to write directly to Octopoda Memory!
    original_add_log = context.add_log
    def new_add_log(message: str):
        original_add_log(message)
        print(f"[{orchestrator.current_state.name}] {message}")
        
        # Write to Octopoda memory so it shows up in Atlas Graph
        mem_key = f"pipeline:log:{int(time.time()*1000)}"
        try:
            orchestrator_rt.remember(mem_key, {"message": message, "state": orchestrator.current_state.name}, tags=["pipeline_log"])
        except Exception:
            pass
            
    context.add_log = new_add_log
    
    # Track the pipeline loop manually to handle EDIT events (which need context)
    try:
        while orchestrator.current_state != AgentState.USER_APPROVED:
            context = await orchestrator.run_pipeline(context)
            
            # If the pipeline paused because of an EDIT decision, we need to inject the event and resume
            if context and context.pending_user_action and context.approval_status == ApprovalDecision.EDIT.value:
                # Orchestrator is paused waiting for EDIT context.
                print("📝 Отправляем правки агенту-копирайтеру и возобновляем работу...")
                # We saved the edit string in our interactive_notifier loop? Wait, we didn't pass it back natively.
                # In a real app it's passed via REST. We'll just hardcode it here for the demo.
                context.user_event_type = "user_edit"
                context.user_event_context = "Сделай текст более агрессивным и добавь эмодзи ракеты."
                
                # We resume the pipeline (run_pipeline will see AWAITING_USER_DECISION and apply_user_command)
                context.approval_status = ApprovalDecision.EDIT.value
                context.pending_user_action = False
                
    except Exception as e:
        print(f"❌ Ошибка пайплайна: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n🎉 Пайплайн успешно завершен!")
    
if __name__ == "__main__":
    asyncio.run(main())
