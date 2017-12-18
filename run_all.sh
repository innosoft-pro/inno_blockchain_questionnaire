#!/usr/bin/env bash
docker build --tag "bchquiz_web:latest" -f ./srv/Dockerfile_back .
docker build --tag "bchquiz_bot:latest" -f ./bot/Dockerfile_bot .
docker-compose -f "docker-compose.yml" -p "bchquiz_system-latest" up
