#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' 

echo -e "${GREEN}Iniciando os containers Docker em segundo plano...${NC}"
docker compose up --build -d

echo ""
echo -e "${GREEN}Aguardando o serviço do Ollama ficar pronto...${NC}"

ATTEMPTS=0
MAX_ATTEMPTS=30
until $(curl --output /dev/null --silent --head --fail http://localhost:11434); do
    if [ ${ATTEMPTS} -eq ${MAX_ATTEMPTS} ]; then
        echo "Erro: O serviço Ollama não iniciou após 1 minuto."
        exit 1
    fi
    printf '.'
    ATTEMPTS=$(($ATTEMPTS+1))
    sleep 2
done


echo -e "${GREEN}Ollama está pronto!${NC}"
echo ""
echo -e "${GREEN}Baixando o modelo de IA 'gemma3:1b'. Isso pode demorar vários minutos...${NC}"
docker compose exec ollama ollama pull gemma3:1b

echo ""
echo -e "${GREEN}Modelo baixado. Executando o script Python principal...${NC}"
docker compose exec app python main.py

echo ""
echo -e "${GREEN}Setup concluído com sucesso!${NC}"
