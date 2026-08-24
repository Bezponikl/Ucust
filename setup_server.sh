#!/usr/bin/env bash
# ==============================================================================
# UCust Master Server Provisioning & Deployment Script (Ubuntu / Debian)
# Устанавливает все системные пакеты, драйверы, Node.js, Python CUDA venv,
# ComfyUI с кастомными нодами, собирает Frontend и запускает всё через PM2.
# ==============================================================================

set -e

REPO_DIR="/opt/ucust"
VENV_DIR="$REPO_DIR/ai/venv"
COMFYUI_DIR="$REPO_DIR/ComfyUI"

echo "======================================================================"
echo "🚀 UCUST MASTER SERVER SETUP & DEPLOYMENT"
echo "📁 Рабочая папка: $REPO_DIR"
echo "======================================================================"

# 1. Обновление репозиториев и установка системных утилит и драйверов
echo "📦 1. Установка системных зависимостей (FFmpeg, OpenGL, C++, Redis, JDK)..."
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
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    redis-server \
    openjdk-17-jdk \
    htop \
    jq

# Запуск и автозагрузка Redis
systemctl enable redis-server || true
systemctl start redis-server || true
echo "✅ Redis запущен и настроен."

# 2. Установка Node.js 20.x LTS и PM2
echo "📦 2. Проверка и установка Node.js 20.x и PM2..."
if ! command -v node &> /dev/null || [[ $(node -v | cut -d'.' -f1 | tr -d 'v') -lt 20 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi
npm install -g pm2
echo "✅ Node.js $(node -v) и PM2 $(pm2 -v) установлены."

# 3. Настройка изолированного Python Virtualenv для ИИ и ComfyUI
echo "📦 3. Создание и настройка Python Virtualenv ($VENV_DIR)..."
mkdir -p "$REPO_DIR/ai"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

pip install --upgrade pip setuptools wheel

# Установка PyTorch с поддержкой CUDA
echo "⚙️ Установка PyTorch (CUDA 12.1)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 || pip install torch torchvision torchaudio

# Установка зависимостей AI Gateway и навыков
echo "⚙️ Установка зависимостей AI агентов (FastAPI, Saiga, Moondream, RAG)..."
pip install -r "$REPO_DIR/ai/requirements.txt" || true
pip install llama-cpp-python pillow timm einops sentence-transformers redis psutil || true

# 4. Настройка ComfyUI и кастомных нод (LTX-2.3, VHS, Manager, GGUF)
echo "📦 4. Инициализация ComfyUI и кастомных нод..."
if [ ! -d "$COMFYUI_DIR" ]; then
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
fi

pip install -r "$COMFYUI_DIR/requirements.txt"

# Запуск авто-установщика нод
python3 "$REPO_DIR/ai/scripts/setup_comfyui_nodes.py" "$COMFYUI_DIR"

# Создание каталогов для моделей
mkdir -p "$COMFYUI_DIR/models/checkpoints/ltx"
mkdir -p "$COMFYUI_DIR/models/clip/ltx"
mkdir -p "$COMFYUI_DIR/models/loras/ltx"
mkdir -p "$COMFYUI_DIR/models/latent_upscale_models/ltx"
mkdir -p "$REPO_DIR/ai/output/photos"

# 5. Сборка Frontend (Next.js)
echo "📦 5. Установка зависимостей и сборка Frontend..."
cd "$REPO_DIR/Frontend"
npm install --legacy-peer-deps
npm run build
echo "✅ Frontend успешно скомпилирован."

# 6. Запуск всех сервисов через PM2
echo "📦 6. Запуск сервисов экосистемы UCust через PM2..."
cd "$REPO_DIR"
pm2 delete all || true
pm2 start ecosystem.config.js
pm2 save

echo ""
echo "======================================================================"
echo "🎉 ВСЕ СЕРВИСЫ UCUST УСПЕШНО УСТАНОВЛЕНЫ И ЗАПУЩЕНЫ В ФОНЕ!"
echo "======================================================================"
echo "  • 🌐 Frontend (Next.js):     http://localhost:3000"
echo "  • ⚡ AI Service Gateway:     http://localhost:8000 (Swagger: /docs)"
echo "  • 🎬 ComfyUI (LTX-2):        http://localhost:8188"
echo "  • 💾 Redis Cache:            localhost:6379"
echo "======================================================================"
echo "Полезные команды управления:"
echo "  pm2 status        - проверить статус процессов"
echo "  pm2 logs          - посмотреть логи в реальном времени"
echo "  pm2 restart all   - перезапустить все сервисы"
echo "======================================================================"
