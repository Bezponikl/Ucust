#!/usr/bin/env bash
# ==============================================================================
# UCust ComfyUI & AI Full Environment Setup Script
# ==============================================================================

set -e

REPO_DIR="${REPO_DIR:-/opt/ucust}"
COMFYUI_DIR="${COMFYUI_DIR:-/opt/ucust/ComfyUI}"
VENV_DIR="${VENV_DIR:-/opt/ucust/ai/venv}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================================================"
echo "🚀 УСТАНОВКА ДРАЙВЕРОВ, ОКРУЖЕНИЯ И COMFYUI ДЛЯ UCUST.AI"
echo "📁 Рабочая папка: $REPO_DIR"
echo "======================================================================"

# 1. Системные пакеты и кодеки
echo "📦 Установка системных библиотек (FFmpeg, OpenGL, C++)..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
    build-essential \
    pkg-config \
    git \
    curl \
    wget \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-pip \
    python3-venv \
    python3-dev \
    redis-server \
    jq

# 2. Настройка виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Создание виртуального окружения Python: $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel

# 3. PyTorch с CUDA поддержкой
echo "⚙️ Установка PyTorch (CUDA)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || pip install torch torchvision torchaudio

# 4. Установка ComfyUI
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "⏳ Клонирование ComfyUI..."
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
fi

cd "$COMFYUI_DIR"
pip install -r requirements.txt

# 5. Автоматическая загрузка кастомных нод (LTX, VHS, GGUF, Essentials)
python3 "$SCRIPT_DIR/setup_comfyui_nodes.py" "$COMFYUI_DIR"

# 6. Зависимости AI-агентов (FastAPI, Saiga, Moondream, Photo)
if [ -f "$REPO_DIR/ai/requirements.txt" ]; then
    pip install -r "$REPO_DIR/ai/requirements.txt" || true
fi
pip install llama-cpp-python pillow timm einops sentence-transformers redis psutil || true

# 7. Папки моделей
mkdir -p "$COMFYUI_DIR/models/checkpoints/ltx"
mkdir -p "$COMFYUI_DIR/models/clip/ltx"
mkdir -p "$COMFYUI_DIR/models/loras/ltx"
mkdir -p "$COMFYUI_DIR/models/latent_upscale_models/ltx"
mkdir -p "$REPO_DIR/ai/output/photos"

echo "======================================================================"
echo "✅ Все драйверы, окружение и ComfyUI ноды успешно установлены!"
echo "======================================================================"

if [ "$1" == "--start" ]; then
    echo "🚀 Запуск ComfyUI (0.0.0.0:8188)..."
    python3 main.py --listen 0.0.0.0 --port 8188 --highvram
fi
