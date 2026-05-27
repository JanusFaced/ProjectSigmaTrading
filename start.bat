@echo off
cd /d %~dp0

echo Start profile lint [mypyMLPipeline]!
docker-compose --profile lint run --rm mypyMLPipeline

echo Start profile dev build!
docker-compose --profile dev up --build

pause