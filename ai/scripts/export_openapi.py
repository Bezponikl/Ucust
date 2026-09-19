"""
File: ai/scripts/export_openapi.py
Экспорт OpenAPI спецификации для генерации DTO на стороне Main Backend.
Выполняется локально перед пушем или в рамках CI-пайплайна.
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, AI_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.openapi.utils import get_openapi
from api_gateway import app

EXPORT_DIR = os.path.join(AI_DIR, "contracts")


def export_schema():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    
    filepath = os.path.join(EXPORT_DIR, "openapi.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Спецификация OpenAPI 3.1 успешно сохранена: {filepath}")
    print(f"   Количество эндпоинтов: {len(schema.get('paths', {}))}")
    print("   Команда для Main Backend: openapi-generator-cli generate -i openapi.json -g java/typescript-fetch")


if __name__ == "__main__":
    export_schema()
