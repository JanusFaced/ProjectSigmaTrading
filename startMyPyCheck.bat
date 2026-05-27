@echo off
cd /d %~dp0

echo Start profile lint [mypyMLPipeline]!
docker-compose --profile lint run --rm mypybackend

echo Start profile dev build!
docker-compose --profile lint run --rm mypyMLPipeline

docker-compose --profile lint down -v
echo Stop docker-compose profile lint!

pause