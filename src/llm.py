import requests
import sys
import os
from dotenv import load_dotenv

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")


def generate_ollama_report(disciplinas: list) -> tuple[str, int]:
    """
    Esta função contém a lógica pura para contatar o Ollama.
    Ela não sabe nada sobre a web, apenas recebe uma lista e retorna uma tupla.
    """
    if not OLLAMA_URL or not MODEL_NAME:
        error_msg = (
            "[ERRO] Variáveis OLLAMA_URL ou MODEL_NAME não encontradas no arquivo .env"
        )
        print(error_msg, file=sys.stderr)
        return error_msg, 500

    formate_data = "\n".join(
        [
            f"- Disciplina: {d['nome']}, Nota: {d['nota']}, Classificação ABC: {d['abc']}, Status: {d['status']}"
            for d in disciplinas
        ]
    )

    prompt = f"""
    Você é um tutor acadêmico e especialista em análise de dados educacionais (metodologia ABC).
    Sua tarefa é analisar o histórico de um aluno para fornecer um feedback construtivo.

    Abaixo estão os dados das disciplinas cursadas e em curso pelo aluno:
    {formate_data}

    Com base nesses dados, gere um relatório de análise de desempenho que responda às seguintes perguntas:
    1.  Qual é a análise geral do desempenho do aluno com base nas disciplinas já 'Aprovadas'?
    2.  Identifique os pontos fortes e as áreas que precisam de mais atenção.
    3.  Considerando a disciplina 'Em Curso' e seu baixo desempenho inicial (nota 0,0), forneça recomendações e um plano de ação para que o aluno possa melhorar e ser aprovado.

    Instruções para o relatório:
    - Responda em português.
    - Use uma linguagem encorajadora e positiva.
    - Seja claro, resumido e objetivo.
    - Estruture sua resposta em seções claras para cada uma das três perguntas.
    """
    try:
        print(f"\nGerando Relatório Acadêmico com {MODEL_NAME}...")
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=290,
        )
        response.raise_for_status()

        full_response = response.json().get("response", "")
        print("Relatório gerado com sucesso.")
        return full_response, 200

    except requests.exceptions.RequestException as e:
        error_msg = f"[ERRO] Ocorreu um erro na chamada da API: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg, 500
