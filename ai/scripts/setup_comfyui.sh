#!/usr/bin/env bash
# ==============================================================================
# UCust ComfyUI & LTX-2 Automated Setup & Launch Script (Ubuntu / Debian)
# ==============================================================================

set -e

COMFYUI_DIR="${COMFYUI_DIR:-/opt/ucust/ComfyUI}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================================"
echo "🚀 ИНИЦИАЛИЗАЦИЯ COMFYUI И КАСТОМНЫХ НОД ДЛЯ LTX-2.3 (UCust.AI)"
echo "📁 Директория ComfyUI: $COMFYUI_DIR"
echo "======================================================================"

# 1. Клонирование репозитория ComfyUI (если еще не склонирован)
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "⏳ Клонирование основного репозитория ComfyUI..."
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
fi

cd "$COMFYUI_DIR"

# 2. Установка базовых зависимостей ComfyUI
echo "⚙️ Проверка и установка зависимостей ComfyUI (PyTorch / Torchvision)..."
pip install -r requirements.txt

# 3. Автоматическая загрузка всех необходимых кастомных нод
python3 "$SCRIPT_DIR/setup_comfyui_nodes.py" "$COMFYUI_DIR"

# 4. Создание необходимых подпапок для моделей
mkdir -p models/checkpoints/ltx
mkdir -p models/clip/ltx
mkdir -p models/loras/ltx
mkdir -p models/latent_upscale_models/ltx
mkdir -p output

echo "======================================================================"
echo "🎉 ComfyUI готов к запуску в фоновом режиме на порту 8188!"
echo "======================================================================"

# Если передан флаг --start, запускаем сервер
if [ "$1" == "--start" ]; then
    echo "🚀 Запуск ComfyUI (0.0.0.0:8188)..."
    python3 main.py --listen 0.0.0.0 --port 8188 --highvram
fi
