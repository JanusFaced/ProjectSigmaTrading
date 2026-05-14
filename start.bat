@echo off
cd /d %~dp0

echo Start python!
docker build -t python_image .

pause