@echo off
echo Starting UCust.AI (Docker + App)...
docker-compose up -d
python start.py
pause