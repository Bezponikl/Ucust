# -*- coding: utf-8 -*-
import sys
import os
import asyncio

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from bridge.api_controller import (
    quick_vision_analyze,
    analyze_documents_direct,
    analyze_brand_multimodal,
    QuickVisionAnalysisRequest,
    DocumentAnalysisRequest,
    UnifiedBrandAnalysisRequest
)

async def test_endpoints():
    print("Testing Multimodal Collectors & Moondream Vision Endpoints...")

    # 1. Тест моментального анализа фото при загрузке на фронте (Moondream + Realism 2.0 Nodes 55, 64, 65)
    print("\n[1] Тест моментального анализа фото (/api/v1/vision/quick-analyze)...")
    req_vision = QuickVisionAnalysisRequest(
        user_id="usr_test_vision",
        prompt="хочу что бы на таких руках у меня сидела такая собачка и мы пили кофе в этой кофейне",
        company_name="Maison Cafe",
        attachments=[
            {"file_name": "hands.png", "description": "slender manicured female hands in cozy knit sweater"},
            {"file_name": "husky.png", "description": "charming expressive husky dog"},
            {"file_name": "cafe.png", "description": "cozy sunlit artisan specialty coffee shop with a cup of cappuccino"}
        ]
    )
    res_vision = await quick_vision_analyze(req_vision)
    print("  -> Status:", res_vision.get("status"))
    print("  -> Execution time:", res_vision.get("execution_time_ms"), "ms")
    print("  -> Slot 1 (Node 55):", res_vision.get("slot_mapping", {}).get("image1_node55", {}).get("label"))
    print("  -> Slot 2 (Node 64):", res_vision.get("slot_mapping", {}).get("image2_node64", {}).get("label"))
    print("  -> Slot 3 (Node 65):", res_vision.get("slot_mapping", {}).get("image3_node65", {}).get("label"))
    assert res_vision.get("status") == "success"
    assert res_vision.get("photos_count") == 3

    # 2. Тест парсинга документов (/api/v1/collectors/analyze-documents)
    print("\n[2] Тест анализа документов (/api/v1/collectors/analyze-documents)...")
    req_doc = DocumentAnalysisRequest(
        user_id="usr_test_docs",
        company_name="Maison Cafe",
        documents=["README.md"]  # Тестовый существующий текстовый документ
    )
    res_doc = await analyze_documents_direct(req_doc)
    print("  -> Status:", res_doc.get("status"))
    print("  -> Documents parsed:", res_doc.get("documents_count"))
    assert res_doc.get("status") == "success"

    # 3. Тест комплексного онбординга (/api/v1/collectors/analyze-brand)
    print("\n[3] Тест комплексного мультимодального онбординга (/api/v1/collectors/analyze-brand)...")
    req_brand = UnifiedBrandAnalysisRequest(
        user_id="usr_test_brand",
        company_name="Maison Cafe",
        city="Москва",
        urls=["https://maisoncafe.ru"],
        documents=["README.md"],
        images=[{"file_name": "cafe.png", "description": "cozy specialty cafe"}]
    )
    res_brand = await analyze_brand_multimodal(req_brand)
    print("  -> Status:", res_brand.get("status"))
    print("  -> Execution time:", res_brand.get("execution_time_ms"), "ms")
    print("  -> Prefilled Profile:", res_brand.get("prefilled_profile", {}).get("business_name"))
    assert res_brand.get("status") == "success"
    assert "prefilled_profile" in res_brand

    print("\n🎉 ВСЕ ТЕСТЫ МУЛЬТИМОДАЛЬНЫХ ЭНДПОИНТОВ УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
