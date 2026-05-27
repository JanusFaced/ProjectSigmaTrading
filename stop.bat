@echo off
cd /d %~dp0

docker-compose --profile dev down -v
echo Stop docker-compose profile dev!

pause