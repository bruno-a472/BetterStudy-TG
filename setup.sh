#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' 

echo -e "${GREEN}Iniciando os containers Docker em segundo plano...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}Aguardando o serviço do Ollama ficar pronto (5 segundos)...${NC}"
sleep 5

echo ""
echo -e "${GREEN}Baixando o modelo de IA 'llama3.2:1b'. Isso pode demorar vários minutos...${NC}"
docker compose exec ollama ollama pull llama3.2:1b

echo ""
echo -e "${GREEN}Modelo baixado. Executando o script Python principal...${NC}"
docker compose exec app python main.py

echo ""
echo -e "${GREEN}Setup concluído com sucesso!${NC}"
