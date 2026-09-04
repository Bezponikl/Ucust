#!/usr/bin/env bash
# ==================================================================
# UCust AI: Launch ComfyUI Server in Virtual Environment
# ==================================================================

set -e

AI_DIR="/opt/ucust/ai"
COMFY_DIR="/opt/ucust/ComfyUI"
VENV_PYTHON="$AI_DIR/venv/bin/python"
PORT=8188
LOG_FILE="$COMFY_DIR/comfy.log"

echo "============================================================"
echo "🚀 UCUST AI: ЗАПУСК COMFYUI СЕРВЕРА (Realism 2.0 Engine)"
echo "============================================================"

if [ ! -d "$COMFY_DIR" ]; then
    echo "❌ Ошибка: Директория ComfyUI не найдена по пути $COMFY_DIR"
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "⚠️ Виртуальное окружение не найдено в $VENV_PYTHON. Поиск системного python3..."
    VENV_PYTHON=$(which python3)
fi

echo "🐍 Используется Python: $VENV_PYTHON"

# Освобождение порта 8188 если занят
RUNNING_PID=$(lsof -ti :$PORT 2>/dev/null || true)
if [ -n "$RUNNING_PID" ]; then
    echo "⚠️ Порт $PORT уже занят процессом PID: $RUNNING_PID. Перезапуск..."
    kill -9 $RUNNING_PID 2>/dev/null || true
    sleep 2
fi

cd "$COMFY_DIR"
echo "⚡ Запуск ComfyUI на 0.0.0.0:$PORT в фоновом режиме..."
nohup "$VENV_PYTHON" main.py --listen 0.0.0.0 --port "$PORT" > "$LOG_FILE" 2>&1 &
COMFY_PID=$!
echo "🟢 ComfyUI запущен с PID: $COMFY_PID"
sleep 5

if curl -s "http://127.0.0.1:$PORT/system_stats" > /dev/null 2>&1; then
    echo "✅ ComfyUI онлайн и готов к генерации: http://127.0.0.1:$PORT"
else
    echo "ℹ️ ComfyUI инициализирует ноды. Последние строки лога:"
fi

echo "------------------------------------------------------------"
tail -n 15 "$LOG_FILE"
echo "------------------------------------------------------------"
echo "💡 Для просмотра логов в реальном времени: tail -f $LOG_FILE"
echo "============================================================"
