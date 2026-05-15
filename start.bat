@echo off
cd /d %~dp0

echo Start python!
docker build -t js_image .
docker run --rm js_image

pause