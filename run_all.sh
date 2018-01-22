#!/usr/bin/env bash
#docker build --tag "bchquiz_web:latest" -f ./srv/Dockerfile .
#docker build --tag "bchquiz_bot:latest" -f ./bot/Dockerfile .
#docker-compose -f "docker-compose.yml" -p "innoquiz" up
docker-compose -p innoquiz up
