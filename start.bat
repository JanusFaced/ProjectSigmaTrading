@echo off
cd /d %~dp0

echo Start docker compose!
docker-compose up --build

pause