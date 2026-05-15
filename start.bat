@echo off
cd /d %~dp0

echo Start python!
docker build -t js_image .
docker run -p 3000:3000 --rm js_image

pause