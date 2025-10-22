import os
import sys
import logging
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

# --- Configuração ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    stream=sys.stdout,
)

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma2:2b") 
REQUEST_TIMEOUT = 300

# --- Funções Auxiliares ---

def _chamar_api_ollama(prompt: str, erro_padrao: str) -> str:
    """Função auxiliar para fazer requisições à API do Ollama."""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        logging.info(f"Enviando requisição para Ollama (modelo: {MODEL_NAME})...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        resultado = response.json()
        resposta = resultado.get("response", "").strip()
        
        if not resposta:
            logging.warning("Resposta vazia recebida da API")
            return erro_padrao
            
        logging.info("Resposta recebida com sucesso")
        return resposta
        
    except requests.exceptions.Timeout:
        logging.error(f"Timeout após {REQUEST_TIMEOUT}s")
        return erro_padrao
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição: {e}")
        return erro_padrao
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return erro_padrao

# --- Lógica Principal ---

def gerar_relatorio_inicial_ollama(disciplinas: List[Dict[str, Any]]) -> str:
    """Gera relatório completo analisando histórico e disciplinas atuais."""


    # Separar disciplinas históricas e em curso
    disciplinas_historicas = [d for d in disciplinas if d.get('tipo') == 'h']
    disciplinas_em_curso = [d for d in disciplinas if d.get('tipo') == 'a']
    
    # Formatar dados históricos
    historico = "\n".join([
        f"- {d.get('nome', 'N/A')}: Nota {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')})"
        for d in disciplinas_historicas if d.get('nome')
    ])
    
    # Formatar disciplinas atuais
    atuais = "\n".join([
        f"- {d.get('nome', 'N/A')}: Nota Parcial {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')})"
        for d in disciplinas_em_curso
    ])


    prompt = f"""
Você é um especialista em estratégias de aprendizagem e técnicas de estudo comprovadas cientificamente.

## HISTÓRICO COMPLETO DO ALUNO
### Disciplinas Concluídas:
{historico}

### Disciplinas em Curso (Semestre Atual):
{atuais}

## SUA TAREFA
Analise o desempenho e crie um plano de estudo PRÁTICO e PERSONALIZADO:E

### 📊 ANÁLISE DE PADRÕES

**1. Perfil de Desempenho:**
- Em quais ÁREAS o aluno vai melhor? (Ex: programação, matemática, teoria, áreas práticas)
- Em quais ÁREAS o aluno tem mais dificuldade?
- Identifique o padrão: o aluno é melhor em disciplinas práticas ou teóricas?

**2. Evolução Histórica:**
- As notas estão MELHORANDO, ESTÁVEIS ou PIORANDO ao longo do curso?
- Compare: início do curso vs semestre atual
- Existe alguma "virada de chave" no desempenho?

**3. Tendências Identificadas:**
- O aluno mantém consistência nas notas ou varia muito?
- Baseado no histórico, quais disciplinas atuais têm MAIOR RISCO?


**IMPORTANTE**: Seja ESPECÍFICO e PRÁTICO. Evite conselhos genéricos. Baseie-se nas notas e status das disciplinas.
"""
    erro_padrao = "Desculpe, não foi possível gerar a análise no momento. Tente novamente."
    return _chamar_api_ollama(prompt, erro_padrao)


def gerar_resposta_chat_ollama(pergunta_usuario: str, contexto_disciplinas: str) -> str:
    """Gera resposta conversacional focada em métodos de estudo."""
    prompt = f"""
Você é um tutor especializado em técnicas de aprendizagem. Responda de forma PRÁTICA e DIRETA.

## CONTEXTO DO ALUNO
{contexto_disciplinas}

## PERGUNTA
"{pergunta_usuario}"

## DIRETRIZES PARA SUA RESPOSTA
1. Se for sobre COMO estudar: sugira técnicas específicas (Pomodoro, Feynman, Active Recall, etc.)
2. Se for sobre dificuldade em disciplina: identifique o tipo de problema e ofereça solução direcionada

**Formato da resposta:**
- Seja conciso e direto ao ponto
- Use bullet points quando relevante

**Evite:**
- Conselhos genéricos como "estude mais"
- Respostas muito longas
- Fugir do contexto das disciplinas dele
"""
    erro_padrao = "Desculpe, estou com dificuldades para processar sua pergunta. Reformule e tente novamente."
    return _chamar_api_ollama(prompt, erro_padrao)