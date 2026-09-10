#!/usr/bin/env python3
"""
Entry point to start the UCust AI Mock Server.
Usage:
    python start_mock.py [--port 8000] [--host 0.0.0.0]
"""

import argparse
import os
import sys
import uvicorn

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def main():
    parser = argparse.ArgumentParser(description="Start UCust AI Mock Server")
    parser.add_argument("--host", type=str, default=os.getenv("AI_MOCK_HOST", "0.0.0.0"), help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("AI_MOCK_PORT", "8000")), help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    print(f"==================================================================")
    print(f"🚀 UCust AI Service Gateway (MOCK REPLICA v2.5.0) Starting...")
    print(f"📡 Base URL:        http://{args.host}:{args.port}")
    print(f"📖 Swagger Docs:    http://localhost:{args.port}/docs")
    print(f"📋 OpenAPI Schema:  http://localhost:{args.port}/openapi.json")
    print(f"🔒 Internal Secret: ucust-super-secret-service-token-2026")
    print(f"⚡ Mode:            Ultra-Fast CPU Mock (Zero GPU dependencies)")
    print(f"==================================================================")

    uvicorn.run(
        "ai_mock.mock_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
