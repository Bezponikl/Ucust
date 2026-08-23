import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from rag import CleanRAGPipeline, Document, TextSanitizer

async def run_clean_rag_tests():
    print("===================================================================")
    print("🧪 ЗАПУСК ТЕСТОВ CLEAN RAG ПАЙПЛАЙНА UCUST")
    print("===================================================================\n")
    
    # 1. Тест очистки текста и эмодзи
    raw_noisy_text = (
        "Скидка 50% только сегодня! Переходи по ссылке https://spamsite.com/buy "
        "и покупай наш курс по SMM! 🚀🚀🚀🚀🚀\n\n"
        "UCust — это автономная платформа для генерации постов и видео с помощью ИИ-агентов. "
        "Включает парсеры соцсетей, Сайгу и LTX-2 режиссера. Подпишись на канал t.me/spam!"
    )
    cleaned = TextSanitizer.sanitize(raw_noisy_text)
    print("--- 1. ТЕСТ ОЧИСТКИ ТЕКСТА (SANITIZER) ---")
    print("🧹 Исходный текст (со спамом и ссылками):", len(raw_noisy_text), "символов")
    print("✨ Очищенный текст:\n", f"'{cleaned}'\n")
    assert "https://" not in cleaned
    assert "Скидка" not in cleaned
    assert "UCust - это автономная платформа" in cleaned

    # 2. Инициализация CleanRAGPipeline
    rag_pipeline = CleanRAGPipeline(
        target_chunk_tokens=300,
        overlap_tokens=50,
        min_confidence_threshold=0.60
    )
    
    # 3. Индексация документов базы знаний UCust
    sample_documents = [
        Document(
            doc_id="doc_pricing",
            source="kb_pricing.md",
            text=(
                "Тарифные планы UCust на 2026 год:\n"
                "1. Тариф Starter: 4 900 руб/мес, включает 30 сценариев постов и анализ 2 каналов.\n"
                "2. Тариф Pro: 14 900 руб/мес, включает безлимитный парсинг Telegram, VK, Яндекс Карт, генерацию 60 LTX-2 видео и ToV Gatekeeper.\n"
                "3. Тариф Enterprise: по запросу, с выделенным сервером и кастомными весами Сайги."
            ),
            metadata={"category": "pricing", "version": "2.0"}
        ),
        Document(
            doc_id="doc_architecture",
            source="kb_architecture.md",
            text=(
                "Архитектура UCust состоит из 5 автономных агентов:\n"
                "1. Интервьюер: тактичный онбординг клиентов без панибратства.\n"
                "2. Аналитик: парсинг через Telethon и Playwright с компрессией Repowise.\n"
                "3. Сайга: копирайтер со строгим Tone-of-Voice регламентом (без тавтологий и фальши).\n"
                "4. Режиссер: генерация LTX-2 кинематографичных видео с Moondream QA.\n"
                "5. Оркестратор: защита от инъекций, кэширование Redis, pgvector и Tone-of-Voice Gatekeeper."
            ),
            metadata={"category": "tech_spec"}
        )
    ]
    
    print("--- 2. ИНДЕКСАЦИЯ БАЗЫ ЗНАНИЙ ---")
    indexed_count = await rag_pipeline.ingest_documents_async(sample_documents)
    print(f"✅ Успешно проиндексировано {indexed_count} семантических чанков.\n")
    
    # 4. Тест целевого гибридного поиска (Dense + BM25 + Rerank)
    print("--- 3. ТЕСТ ТОЧНОГО ЗАПРОСА (УСПЕШНЫЙ RAG) ---")
    target_query = "Сколько стоит тариф Pro в UCust и что в него входит?"
    print(f"🔍 Запрос: '{target_query}'")
    
    context_result = await rag_pipeline.query_async(target_query)
    print(f"📊 Достаточность контекста (Guard): {context_result.has_sufficient_context}")
    print(f"⭐ Top Score: {context_result.top_score:.2f}")
    print(f"📄 Форматированный контекст:\n{context_result.formatted_context}\n")
    
    assert context_result.has_sufficient_context is True
    assert "14 900 руб/мес" in context_result.formatted_context

    # 5. Тест защиты от галлюцинаций (Anti-Hallucination Guard)
    print("--- 4. ТЕСТ ЗАЩИТЫ ОТ ГАЛЛЮЦИНАЦИЙ (OUT-OF-DOMAIN QUERY) ---")
    hallucination_query = "Как приготовить квантовый суп с антиматерией в космосе?"
    print(f"🔍 Запрос: '{hallucination_query}'")
    
    guarded_result = await rag_pipeline.query_async(hallucination_query)
    print(f"📊 Достаточность контекста (Guard): {guarded_result.has_sufficient_context}")
    print(f"⭐ Top Score: {guarded_result.top_score:.2f}")
    print(f"🛡️ Сообщение защиты от галлюцинаций:\n{guarded_result.fallback_message}\n")
    
    assert guarded_result.has_sufficient_context is False
    assert guarded_result.fallback_message is not None

    print("===================================================================")
    print("🎉 ВСЕ ТЕСТЫ CLEAN RAG ПАЙПЛАЙНА УСПЕШНО ПРОЙДЕНЫ!")
    print("===================================================================")

if __name__ == "__main__":
    asyncio.run(run_clean_rag_tests())
