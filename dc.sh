#!/bin/bash

# Caminho da pasta do projeto (onde está o docker-compose.dev.yml)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Rodar docker compose com o arquivo dev
docker compose -f "$PROJECT_DIR/docker-compose.dev.yml" "$@"
