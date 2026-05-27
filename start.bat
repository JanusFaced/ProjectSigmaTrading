@echo off
cd /d %~dp0

echo Start profile dev build!
docker-compose --profile dev up --build

pause