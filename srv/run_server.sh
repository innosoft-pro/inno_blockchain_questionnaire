#!/usr/bin/env bash
docker build --tag "bchquiz_system:latest" -f ./Dockerfile_back .
docker-compose -f "docker-compose.yml" -p "bchquiz_system-latest" up
