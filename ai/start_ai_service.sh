#!/usr/bin/env bash
# ====================================================================
# UCust AI Unified Service Gateway Launcher (v2.5.0 Linux/Server)
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Определение рабочей директории ai
if [ -d "$SCRIPT_DIR/ai" ]; then
    AI_DIR="$SCRIPT_DIR/ai"
    ROOT_DIR="$SCRIPT_DIR"
else
    AI_DIR="$SCRIPT_DIR"
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Поиск и активация виртуального окружения (venv)
VENV_FOUND=""
for candidate in \
    "$ROOT_DIR/venv" \
    "$ROOT_DIR/.venv" \
    "$AI_DIR/venv" \
    "$AI_DIR/.venv" \
    "/opt/ucust/venv" \
    "/opt/ucust/ai/venv" \
    "$HOME/venv" \
    "$HOME/.venv"; do
    if [ -f "$candidate/bin/activate" ]; then
        VENV_FOUND="$candidate"
        break
    fi
done

if [ -n "$VENV_FOUND" ]; then
    echo "🔍 Найдено виртуальное окружение: $VENV_FOUND"
    # shellcheck disable=SC1090
    source "$VENV_FOUND/bin/activate"
    PYTHON_CMD="python3"
else
    echo "⚠️ Виртуальное окружение не найдено в стандартных путях, используем системный python3."
    PYTHON_CMD="python3"
fi

# Проверяем наличие FastAPI
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo "❌ Ошибка: модуль 'fastapi' не установлен в текущем Python ($($PYTHON_CMD --version 2>&1))."
    echo "💡 Решение:"
    echo "   1) Активируйте ваше venv: source /opt/ucust/venv/bin/activate"
    echo "   2) Либо установите зависимости: pip install -r $AI_DIR/requirements.txt (или pip install fastapi uvicorn httpx)"
    exit 1
fi

cd "$AI_DIR"

export PYTHONIOENCODING=utf-8
export AI_SERVICE_HOST="${AI_SERVICE_HOST:-0.0.0.0}"
export AI_SERVICE_PORT="${AI_SERVICE_PORT:-8000}"

echo "===================================================================="
echo "🚀 Запуск UCust AI Unified Service Gateway (v2.5.0)"
echo "Python:   $($PYTHON_CMD -c 'import sys; print(sys.executable)')"
echo "Host:     http://$AI_SERVICE_HOST:$AI_SERVICE_PORT"
echo "Docs:     http://$AI_SERVICE_HOST:$AI_SERVICE_PORT/docs"
echo "Gateway:  POST /api/v1/orchestrator/execute"
echo "Health:   GET /api/v1/ai/health"
echo "===================================================================="

exec $PYTHON_CMD api_gateway.py

