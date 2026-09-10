#!/usr/bin/env bash
# UCust AI Mock Server Launcher
echo "=================================================================="
echo " 🚀 Запуск Мок-Сервера UCust AI Gateway (CPU Mock Server)"
echo "=================================================================="
PORT="${AI_MOCK_PORT:-8000}"
HOST="${AI_MOCK_HOST:-0.0.0.0}"

python3 start_mock.py --host "$HOST" --port "$PORT"
