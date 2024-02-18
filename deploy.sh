ssh root@myremote rm -rf ./plato
scp -r . root@myremote:~/plato
ssh root@myremote docker compose -f ./plato/docker/docker-compose.yml --project-directory ./plato up -d --build