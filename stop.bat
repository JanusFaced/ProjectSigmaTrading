@echo off
cd /d %~dp0

docker-compose down
echo Stop docker compose!

pause