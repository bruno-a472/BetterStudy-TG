# BetterStudy_Bot
Um bot que utiliza a metodologia ABC nas notas dos alunos.

## Pré-requisitos

Antes de começar, certifique-se de que você atende aos seguintes requisitos:

    Docker e Docker Compose: A plataforma de contêineres deve estar instalada e em execução na sua máquina.

    Conexão com a Internet: Necessária para baixar a imagem do Ollama e o modelo de IA.

    ⚠️ Atenção: Espaço em Disco Necessário
    O download do modelo de IA tem um tamanho aproximado de **1.3 GB**. Por favor, garanta que você tenha espaço de armazenamento suficiente em seu disco antes de continuar.

## Como Rodar o Projeto com Docker

 Navegue até a Pasta do Projeto

    Execute os comandos de setup:
     chmod +x setup.sh  # Dá permissão de execução (só precisa na 1ª vez)
     ./setup.sh

## Parar a aplicação
 
 Para parar e remover todos os containers e redes criados pelo projeto, utilize o comando:
    docker compose down

```bash
./setup.sh
