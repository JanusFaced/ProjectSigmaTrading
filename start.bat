@echo off
cd /d %~dp0

echo Start project!
docker-compose up --build

pause