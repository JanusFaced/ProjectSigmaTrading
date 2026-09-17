docker compose down
docker rm grafana promtail loki node-exporter prometheus
echo "Stop docker-compose!"

read -p "Press any key to continue..."