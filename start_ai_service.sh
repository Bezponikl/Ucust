#!/usr/bin/env bash
# ====================================================================
# UCust AI Unified Service Gateway Launcher (v2.5.0 Linux/Server)
# ====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/ai"

export PYTHONIOENCODING=utf-8
export AI_SERVICE_HOST="${AI_SERVICE_HOST:-0.0.0.0}"
export AI_SERVICE_PORT="${AI_SERVICE_PORT:-8000}"

echo "===================================================================="
echo "🚀 Запуск UCust AI Unified Service Gateway (v2.5.0)"
echo "Host: http://$AI_SERVICE_HOST:$AI_SERVICE_PORT"
echo "Docs: http://$AI_SERVICE_HOST:$AI_SERVICE_PORT/docs"
echo "Gateway: POST /api/v1/orchestrator/execute"
echo "===================================================================="

python3 api_gateway.py
