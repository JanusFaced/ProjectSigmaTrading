@echo off
cd /d %~dp0

echo Make image python_app!
docker build -t python_app .

echo Start container python_app!
docker run --rm -v "%cd%/output:/app/output" python_app

pause