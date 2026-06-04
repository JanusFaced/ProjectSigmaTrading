echo "Start profile dev build!"
docker compose -f docker-compose.dev.yml --profile dev up --build

read -p "Press any key to continue..."