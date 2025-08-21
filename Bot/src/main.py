import sqlite3
import requests
import json
import sys

DB_FILE = "escola.db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b" 

def inicializar_banco(db_path: str):

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY,
            aluno TEXT,
            atividade TEXT,
            custo REAL, -- Pode representar tempo, esforço ou complexidade
            nota REAL
        )
        ''')

        cursor.execute("SELECT COUNT(*) FROM notas")
        if cursor.fetchone()[0] == 0:
            print("Banco de dados vazio. Inserindo dados de exemplo...")
            dados_exemplo = [
                ("Ana", "Prova Matemática", 50, 8.5),
                ("Ana", "Trabalho História", 30, 9.0),
                ("João", "Prova Matemática", 50, 7.0),
                ("João", "Trabalho História", 30, 8.0),
                ("Maria", "Prova Matemática", 50, 6.5),
                ("Maria", "Trabalho História", 30, 7.5),
            ]
            cursor.executemany("INSERT INTO notas (aluno, atividade, custo, nota) VALUES (?, ?, ?, ?)", dados_exemplo)
            print("Dados inseridos com sucesso.")

def buscar_dados_notas(db_path: str) -> list:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT aluno, atividade, custo, nota FROM notas")
        return cursor.fetchall()

def gerar_relatorio_abc(dados_notas: list):
    dados_formatados = "\n".join([
        f"- Aluno: {aluno}, Atividade: {atividade}, Custo/Esforço: {custo}, Nota: {nota}"
        for aluno, atividade, custo, nota in dados_notas
    ])

    prompt = f"""
    Você é um especialista em análise de dados educacionais e Custeio Baseado em Atividades (ABC).
    Analise os seguintes dados de notas de alunos, onde 'Custo/Esforço' representa o peso ou a dificuldade da atividade.

    Dados:
    {dados_formatados}

    Com base nos dados, gere um relatório final respondendo à seguinte pergunta:
    1. Como o método de Custeio Baseado em Atividades (ABC) pode ser aplicado a este cenário para analisar o desempenho dos alunos?

    Instruções para o relatório:
    - Seja claro, resumido e objetivo.
    - Estruture sua resposta usando tópicos ou uma lista numerada.
    - Não repita a lista de dados brutos na sua resposta. Comece diretamente com a análise.
    """
    try:
        print("\nGerando Relatório ABC com Llama 3.2:1b...\n")
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True 
            },
            timeout=60 
        )
        response.raise_for_status() 

        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    print(data["response"], end="", flush=True)
                    full_response += data["response"]
        print("\n\nRelatório gerado com sucesso.")

    except requests.exceptions.ConnectionError:
        print("\n[ERRO] Não foi possível conectar ao servidor do Ollama.", file=sys.stderr)
        print("Verifique se o Ollama está em execução no endereço:", OLLAMA_URL, file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO] Ocorreu um erro na chamada da API: {e}", file=sys.stderr)

def main():
    """
    Função principal que orquestra a execução do script.
    """
    inicializar_banco(DB_FILE)
    notas = buscar_dados_notas(DB_FILE)
    if notas:
        gerar_relatorio_abc(notas)
    else:
        print("Nenhum dado encontrado no banco de dados para análise.")

if __name__ == "__main__":
    main()