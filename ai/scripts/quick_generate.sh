#!/usr/bin/env bash
# ==================================================================
# UCust AI: Fast Autonomous Post & Photo Generation Runner
# ==================================================================

set -e

AI_DIR="/opt/ucust/ai"
VENV_PYTHON="$AI_DIR/venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON=$(which python3)
fi

cd "$AI_DIR"

TOPIC="${1:-Интерфейс платформы UCust на стильном ноутбуке в современном светлом офисе с панорамными окнами и растениями, малая глубина резкости, 35mm lens}"
NICHE="${2:-Martech}"
COMPANY="${3:-UCust}"
RATIO="${4:-1:1}"
IMAGES="$5"

echo "============================================================"
echo "🚀 UCUST AI: Запуск генерации контента..."
echo "📌 Тема: $TOPIC"
echo "🏢 Компания: $COMPANY | Ниша: $NICHE | Формат: $RATIO"
if [ -n "$IMAGES" ]; then
    echo "📎 Прикрепленные фото: $IMAGES"
fi
echo "============================================================"

if [ -n "$IMAGES" ]; then
    "$VENV_PYTHON" scripts/run_autonomous_campaign.py \
      --prompt "$TOPIC" \
      --niche "$NICHE" \
      --company "$COMPANY" \
      --aspect-ratio "$RATIO" \
      --images "$IMAGES"
else
    "$VENV_PYTHON" scripts/run_autonomous_campaign.py \
      --prompt "$TOPIC" \
      --niche "$NICHE" \
      --company "$COMPANY" \
      --aspect-ratio "$RATIO"
fi
