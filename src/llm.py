import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")


def create_report_abc(dados_notas: list):
    if not OLLAMA_URL or not MODEL_NAME:
        print(
            "[ERRO] Variáveis OLLAMA_URL ou MODEL_NAME não encontradas no arquivo .env",
            file=sys.stderr,
        )
        return

    formate_data = "\n".join(
        [
            f"- Aluno: {aluno}, Atividade: {atividade}, Custo/Esforço: {custo}, Nota: {nota}"
            for aluno, atividade, custo, nota in dados_notas
        ]
    )

    prompt = f"""
    Você é um especialista em análise de dados educacionais e Custeio Baseado em Atividades (ABC).
    Analise os seguintes dados de notas de alunos, onde 'Custo/Esforço' representa o peso ou a dificuldade da atividade.

    Dados:
    {formate_data}

    Com base nos dados, gere um relatório final respondendo à seguinte pergunta:
    1. Como o método de Custeio Baseado em Atividades (ABC) pode ser aplicado a este cenário para analisar o desempenho dos alunos?

    Instruções para o relatório:
    - Seja claro, resumido e objetivo.
    - Estruture sua resposta usando tópicos ou uma lista numerada.
    - Não repita a lista de dados brutos na sua resposta. Comece diretamente com a análise.
    """
    try:
        print(f"\nGerando Relatório ABC com {MODEL_NAME}...\n")
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
            timeout=60,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    print(data["response"], end="", flush=True)
        print("\n\nRelatório gerado com sucesso.")

    except requests.exceptions.ConnectionError:
        print(
            f"\n[ERRO] Não foi possível conectar ao servidor do Ollama em: {OLLAMA_URL}",
            file=sys.stderr,
        )
        print(
            "Verifique se o Ollama está em execução e se a URL no seu arquivo .env está correta.",
            file=sys.stderr,
        )
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na chamada da API: {e}", file=sys.stderr)
