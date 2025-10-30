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
REQUEST_TIMEOUT = 600

# =========================
# Chunks estáveis (reuso)
# =========================

CHUNK_PERSONA = """
Você é o BetterStudy, um assistente educacional que aplica Autorregulação da Aprendizagem (AA) como estrutura principal,
com base no modelo cíclico de Zimmerman (Antecipação → Desempenho → Autorreflexão). 
Seu objetivo é ajudar o estudante a planejar, executar e revisar os estudos com autonomia, endereçando respostas diretamente a ele.

Você domina e recomenda técnicas conforme o contexto:
- Pomodoro (gestão de tempo/foco);
- Repetição espaçada (retenção de longo prazo);
- Flashcards (active recall);
- Mapas mentais (organização/síntese);
- Aprendizagem ativa vs. passiva;
- Adapta recomendações a perfis (visual, auditivo, cinestésico, leitura/escrita).
"""

CHUNK_POLICY = """
Política de resposta:
- Seja específico e prático, fundamentando recomendações nas notas/dados do aluno.
- Use um tom encorajador, empático e pessoal. Ao invés de "O aluno demonstra", diga "Você demonstra".
- Prefira bullets e passos claros; evite conselhos genéricos.
- Se faltar dado, explicite o que falta e proponha próxima ação (ex.: “posso rodar um quiz de perfil?”).
- Integre as técnicas à AA (o que vai na fase de Antecipação, na de Desempenho e na de Autorreflexão).
- Respostas curtas e acionáveis: 8–14 linhas, quando possível.
"""

CHUNK_OUTPUT_SCHEMA_RELATORIO = """
Formato da resposta, responda em **Markdown estruturado** (## títulos, **negrito**, *itálico* e listas)(use estes cabeçalhos):
## Diagnóstico (resumo)
- ...

## Prioridades
- Estudo geral (histórico)
- Estudo do semestre (atuais)

## Estratégias por fase da AA
- Antecipação: ...
- Desempenho: ...
- Autorreflexão: ...

## Próximo passo guiado
- (convite curto para continuar; ex.: “Quer ver como montar sua semana com Pomodoro + revisão espaçada?”)
"""

CHUNK_OUTPUT_SCHEMA_CHAT = """
Formato da resposta, responda em **Markdown estruturado** (## títulos, **negrito**, *itálico* e listas):
- Resposta direta (2–4 bullets)
- Técnica(s) sugerida(s) com passo a passo
- Como monitorar (AA) e quando revisar
- Próxima ação (1 linha)
"""

# =========================
# Utilidades de formatação
# =========================

def _linhas_disciplinas(disciplinas: List[Dict[str, Any]], rotulo: str) -> str:
    if not disciplinas:
        return f"{rotulo}: (nenhuma)\n"
    linhas = []
    for d in disciplinas:
        nome = d.get('nome', 'N/A')
        nota = d.get('nota', 'N/A')
        abc  = d.get('abc', 'N/A')
        status = d.get('status', 'N/A')
        linhas.append(f"- {nome}: Nota {nota} (Conceito {abc}) — {status}")
    return f"{rotulo}:\n" + "\n".join(linhas) + "\n"

def _chunk_data(disciplinas: List[Dict[str, Any]], perfil: Dict[str, Any] | None = None) -> str:
    hist = [d for d in disciplinas if d.get('tipo') in ('h','H','historica','historico')]
    atu  = [d for d in disciplinas if d.get('tipo') in ('a','A','atual','atuais','em_curso')]

    parte_hist = _linhas_disciplinas(hist, "Disciplinas concluídas (histórico)")
    parte_atu  = _linhas_disciplinas(atu,  "Disciplinas em curso (semestre atual)")

    perfil_txt = ""
    if perfil:
        # exemplo de chaves aceitas no perfil
        horas = perfil.get("horas_estudo_dia", "não informado")
        tipo  = perfil.get("tipo_aprendiz", "não informado")
        fam   = perfil.get("familiaridade_metodos", {})
        foc   = fam.get("nivel_foco", "não informado")
        mot   = perfil.get("motivacao_estudo", "não informado")
        perfil_txt = (
            "Perfil do aluno:\n"
            f"- Horas de estudo/dia: {horas}\n"
            f"- Tipo de aprendiz: {tipo}\n"
            f"- Familiaridade com métodos: {fam}\n"
            f"- Nível de foco/concentração: {foc}\n"
            f"- Motivação para estudar: {mot}\n"
        )

    return f"### DADOS DO ALUNO\n{parte_hist}\n{parte_atu}\n{perfil_txt}".strip()

def _call_ollama(prompt: str, erro_padrao: str) -> str:
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 1800
        }
        logging.info(f"Ollama request -> model={MODEL_NAME}, len(prompt)={len(prompt)}")
        r = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        resp = r.json().get("response", "").strip()
        return resp or erro_padrao
    except requests.exceptions.Timeout:
        logging.error(f"Timeout após {REQUEST_TIMEOUT}s")
        return erro_padrao
    except Exception as e:
        logging.error(f"Erro Ollama: {e}")
        return erro_padrao

# =========================
# Prompts builders
# =========================

def _build_prompt_relatorio(disciplinas: List[Dict[str, Any]], perfil: Dict[str, Any] | None = None) -> str:
    data_chunk = _chunk_data(disciplinas, perfil)

    task = """
### TAREFA
Analise o desempenho do aluno, identifique áreas fortes/fracas (exatas, humanas, biológicas, prática/teoria),
aponte tendências e riscos atuais, e gere um plano prático personalizando técnicas às fases da AA.
"""
    prompt = "\n".join([
        "### PERSONA", CHUNK_PERSONA,
        "### POLICY", CHUNK_POLICY,
        task,
        data_chunk,
        "### SAÍDA ESPERADA", CHUNK_OUTPUT_SCHEMA_RELATORIO,
    ])
    return prompt

def _build_prompt_chat(pergunta_usuario: str, disciplinas_fmt: str | None, perfil: str | None = None) -> str:
    # disciplinas_fmt é opcional; se vier preformatado do endpoint, usa; senão, pode pular
    data = f"### DADOS DO ALUNO (texto)\n{disciplinas_fmt}\n{perfil}" if disciplinas_fmt else ""
    task = f"""
### TAREFA
Responda à pergunta do aluno de forma prática e direta, integrando a AA e, quando fizer sentido,
Pomodoro, repetição espaçada, flashcards, mapas mentais, aprendizagem ativa e estilos de aprendizagem.

### PERGUNTA
\"\"\"{pergunta_usuario}\"\"\"
"""
    prompt = "\n".join([
        "### PERSONA", CHUNK_PERSONA,
        "### POLICY", CHUNK_POLICY,
        task,
        data,
        "### SAÍDA ESPERADA", CHUNK_OUTPUT_SCHEMA_CHAT
    ])
    return prompt

# =========================
# API pública do módulo
# =========================

def gerar_relatorio_inicial_ollama(disciplinas: List[Dict[str, Any]], perfil: Dict[str, Any] | None = None) -> str:
    """
    Recebe TODAS as disciplinas (históricas e atuais) e (opcionalmente) um perfil do aluno.
    Monta prompt por chunks e chama a LLM.
    """
    prompt = _build_prompt_relatorio(disciplinas, perfil)
    erro = "Desculpe, não foi possível gerar a análise no momento. Tente novamente."
    print('\n\nTeste')
    print('Terminou de rodar relatório inicial')
    return _call_ollama(prompt, erro)

def gerar_resposta_chat_ollama(pergunta_usuario: str, contexto_disciplinas: str | None = None, perfil: Dict[str, Any] | None = None) -> str:
    """
    Gera resposta pontual para uma dúvida, usando os chunks e (opcional) contexto em texto e perfil.
    """
    prompt = _build_prompt_chat(pergunta_usuario, contexto_disciplinas, perfil)
    erro = "Desculpe, estou com dificuldades para processar sua pergunta. Reformule e tente novamente."
    print('\n\nTeste')
    print('Terminou de rodar resposta chat')
    return _call_ollama(prompt, erro)
