// PM2 Unified Process Manager Configuration for UCust Ecosystem
module.exports = {
  apps: [
    {
      name: "ucust-ai-gateway",
      script: "/opt/ucust/ai/venv/bin/uvicorn",
      args: "api_gateway:app --host 0.0.0.0 --port 8000",
      cwd: "/opt/ucust/ai",
      interpreter: "none",
      env: {
        PYTHONPATH: "/opt/ucust/ai",
        COMFYUI_URL: "http://127.0.0.1:8188",
        SERVER_MODE: "true"
      },
      restart_delay: 3000,
      max_restarts: 10,
      autorestart: true
    },
    {
      name: "ucust-comfyui",
      script: "/opt/ucust/ai/venv/bin/python3",
      args: "main.py --listen 0.0.0.0 --port 8188 --highvram",
      cwd: "/opt/ucust/ComfyUI",
      interpreter: "none",
      restart_delay: 5000,
      max_restarts: 10,
      autorestart: true
    },
    {
      name: "ucust-frontend",
      script: "npm",
      args: "start",
      cwd: "/opt/ucust/Frontend",
      env: {
        PORT: 3000,
        NODE_ENV: "production",
        NEXT_PUBLIC_AI_GATEWAY_URL: "/api/v1"
      },
      restart_delay: 3000,
      max_restarts: 10,
      autorestart: true
    }
  ]
};
