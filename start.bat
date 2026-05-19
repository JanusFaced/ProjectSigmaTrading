@echo off
cd /d %~dp0

echo Start project!
docker build -t js_image .
docker run -p 3000:3000 --rm js_image

pause