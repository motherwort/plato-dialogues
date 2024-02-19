ssh root@myremote rm -rf ./plato
ssh root@myremote mkdir ./plato/
ssh root@myremote mkdir ./plato/docker/
ssh root@myremote mkdir ./plato/src/
scp -r ./docker root@myremote:~/plato
scp -r ./src root@myremote:~/plato
scp -r ./poetry.lock root@myremote:~/plato
scp -r ./pyproject.toml root@myremote:~/plato
ssh root@myremote docker compose -f ./plato/docker/docker-compose.yml --project-directory ./plato up -d --build