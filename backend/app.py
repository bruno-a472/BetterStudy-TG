# --- Imports ---
import os
import json
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Módulos locais
import arvoreDriver
import gera_id
import llm

# --- Configuração e Inicialização ---
app = Flask(__name__)
CORS(app)

ids = gera_id.GeraId()
arvore = arvoreDriver.ArvDriver(id=ids.geraId())

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Funções Auxiliares de Cache ---
def save_to_cache(user_id: str, data: dict):
    """Salva os dados de um usuário em um arquivo JSON no cache."""
    cache_path = os.path.join(CACHE_DIR, f"{user_id}_materias.json")
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Cache salvo para o usuário {user_id}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao salvar cache para o usuário {user_id}: {e}", file=sys.stderr)
        return False

def load_from_cache(user_id: str) -> dict | None:
    """Carrega os dados de um usuário a partir do arquivo de cache."""
    cache_path = os.path.join(CACHE_DIR, f"{user_id}_materias.json")
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            print(f"Cache carregado para o usuário {user_id}")
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao ler cache para o usuário {user_id}: {e}", file=sys.stderr)
        return None

# --- Funções de Web Scraping (Selenium) ---
def login(e: str, s: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 20)
    try:
        botao = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "uc_flex-r")))
        botao.click()
        print('Botão clicado')

        campo_email = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        campo_email.send_keys(e)
        campo_email.send_keys(Keys.ENTER)

        campo_senha = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        print('Digitando senha...')
        campo_senha.send_keys(s)

        botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        botao_entrar.click()

        campo_texto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
        campo_texto.click()
        print("Aguardando autenticação por dois fatores...")
        
        resposta = {'bool': True, 'id': id}
        return json.dumps(resposta, ensure_ascii=False, indent=4)
        
    except Exception as e:
        print("Erro durante o login:", str(e))
        return json.dumps({'bool': False})

def confirmacao(c: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 8)
    try:
        campo_codigo = wait.until(EC.presence_of_element_located((By.ID, "idTxtBx_SAOTCC_OTC")))
        print('Digitando código...')
        campo_codigo.clear()
        campo_codigo.send_keys(c)
        campo_codigo.send_keys(Keys.ENTER)

        span = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "uc_appuser-name")))
        nome = str(span.text.strip().lower()).split(' ')[1].capitalize()
        if nome:
            resposta = {'bool': True, 'nome': nome}
        else:
            raise ValueError("Nome não encontrado.")

    except Exception as e:
        print(f"Um problema foi encontrado na confirmação: {e}")
        resposta = {'bool': False, 'erro': 'Falha na confirmação do código.'}
    
    return json.dumps(resposta, ensure_ascii=False, indent=4)

def scrapeNotas(id: int):
    print("Iniciando scrape de notas para o ID:", id)
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 20)
    try:
        # 1 - Clicar em "meu curso"
        curso_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uc_appfooter-button.uc_pointer")))
        for btn in curso_btns:
            try:
                if btn.find_elements(By.TAG_NAME, "center")[1].text.strip().lower() == "meu curso":
                    btn.click()
                    break
            except Exception:
                continue

        # 2 - Clicar em "Histórico"
        historico_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uc_appgrid-item.uc_pointer")))
        for btn in historico_btns:
            try:
                if btn.find_element(By.TAG_NAME, "span").text.strip().lower() == "histórico":
                    btn.click()
                    break
            except Exception:
                continue

        # 3 - Extrair cards
        cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "uc_appcard")))
        parcial = []
        historico = []

        for card in cards:
            try:
                nome_materia = card.find_element(By.CLASS_NAME, "uc_appcard-title").text.strip()
                if nome_materia.startswith('Projeto Integrador'):
                    continue
                
                linhas_info = card.find_elements(By.CSS_SELECTOR, ".uc_flex-r.uc_flex-jcsb.uc_w100.uc_mb5")
                nota = linhas_info[0].find_element(By.CLASS_NAME, "uc_apptext").text.strip()
                status = linhas_info[4].find_element(By.CLASS_NAME, "uc_apptext").text.strip()

                materia = {"nome": nome_materia, "nota": nota, "abc": rank_nota(nota), "status": status}
                if status == 'Em Curso':
                    materia["tipo"] = "a"
                    parcial.append(materia)
                else:
                    materia["tipo"] = "h"
                    historico.append(materia)
            except Exception as e:
                print(f"Erro ao extrair dados de uma matéria: {e}")
                continue
        
        resultado = {"parciais": parcial, "historicas": historico}
        return json.dumps(resultado, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Erro geral no scrape: {e}")
        return json.dumps({"parciais": [], "historicas": []})
    finally:
        print('Finalizando scrape. Fechando driver.')
        if driver:
            driver.quit()

def rank_nota(nota_str: str) -> str:
    try:
        nota = float(nota_str.replace(',', '.'))
        if 8 <= nota <= 10:
            return "A"
        elif 4 <= nota < 8:
            return "B"
    except (ValueError, TypeError):
        return "C"
    return "C"

# --- Endpoints da API ---
@app.route('/api/login', methods=['POST'])
def receber_login():
    dados = request.json
    e = dados['email']
    s = dados['senha']
    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    id = ids.geraId()
    arvore.insere(id=id, driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options))
    arvore.encontra(id).obtemDriver().get('https://siga.cps.sp.gov.br/sigaaluno/applogin.aspx')
    return login(e, s, id)

@app.route('/api/login/confirmacao', methods=['POST'])
def confirmacao_login():
    dados = request.json
    c = dados['codigo']
    id = dados['id']
    return confirmacao(c, id)

@app.route('/api/notas', methods=['POST'])
def api_scrape_notas():
    dados = request.json
    id = dados['id']
    return scrapeNotas(id)

@app.route('/api/init', methods=['POST'])
def init_user_session():
    """Inicializa sessão do usuário e gera relatório inicial completo."""
    data = request.get_json()
    user_id = data.get("id_usuario")
    notas = data.get("notas")

    # Validação
    if not user_id or not notas:
        return jsonify({"erro": "É necessário fornecer 'id_usuario' e 'notas'."}), 400

    # Salvar no cache
    save_to_cache(str(user_id), notas)
    
    # Passar o JSON completo (com separação de históricas e parciais)
    # A função gerar_relatorio_inicial_ollama já faz a separação internamente
    disciplinas_historicas = notas.get('historicas', [])
    disciplinas_parciais = notas.get('parciais', [])
    
    # Validar se há dados
    if not disciplinas_historicas and not disciplinas_parciais:
        return jsonify({"relatorio_inicial": "Nenhuma disciplina foi fornecida para análise."}), 200
    
    # Combinar TODAS as disciplinas em uma lista única
    # A função LLM vai separar internamente pelo campo 'tipo'
    todas_disciplinas = disciplinas_historicas + disciplinas_parciais
    
    try:
        # Gerar relatório inicial (análise de padrões + estado atual)
        relatorio = llm.gerar_relatorio_inicial_ollama(todas_disciplinas)
        
        if not relatorio or relatorio.strip() == "":
            relatorio = "Desculpe, não foi possível gerar o relatório inicial. Tente novamente."
            
    except Exception as e:
        print(f"[ERRO] Falha ao gerar relatório inicial: {e}", file=sys.stderr)
        relatorio = "Erro ao processar seus dados. Por favor, tente novamente mais tarde."
    
    return jsonify({
        "relatorio_inicial": relatorio,
        "user_id": int(user_id),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

# @app.route("/api/chatbot", methods=["POST"])
# def chat():
#     """Endpoint inteligente que gera relatório inicial na primeira mensagem."""
#     data = request.get_json()
#     user_id = data.get("chat_id")
#     user_message = data.get("text", "")

#     if not user_id or not user_message:
#         return jsonify({"erro": "É necessário fornecer 'chat_id' e 'text'."}), 400

#     dados_em_cache = load_from_cache(str(user_id))
    
#     # 🆕 DETECTAR SE É A PRIMEIRA MENSAGEM
#     primeira_mensagem = False
    
#     if not dados_em_cache:
#         print(f"\n⚠️ Cache não encontrado para user_id={user_id}")
#         print("🧪 Criando dados de teste...")
        
#         # Carregar JSON de teste
#         json_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'assets', 'resultado_notas_12.json')
        
#         try:
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 dados_em_cache = json.load(f)
#             save_to_cache(str(user_id), dados_em_cache)
#             primeira_mensagem = True  # Marca como primeira mensagem
#             print(f"✅ Cache criado para user_id={user_id}")
#         except FileNotFoundError:
#             return jsonify({
#                 "chat_id": int(user_id),
#                 "text": "Erro: Não foi possível carregar dados de teste. Verifique se o arquivo resultado_notas_12.json existe.",
#                 "remetente": 'bot'
#             }), 200

#     # 🆕 SE FOR PRIMEIRA MENSAGEM, GERAR RELATÓRIO INICIAL
#     if primeira_mensagem or user_message.lower() in ["oi", "olá", "iniciar", "começar", "start"]:
#         print("🤖 Gerando RELATÓRIO INICIAL...")
        
#         disciplinas_historicas = dados_em_cache.get('historicas', [])
#         disciplinas_parciais = dados_em_cache.get('parciais', [])
#         todas_disciplinas = disciplinas_historicas + disciplinas_parciais
        
#         try:
#             relatorio_inicial = llm.gerar_relatorio_inicial_ollama(todas_disciplinas)
            
#             return jsonify({
#                 "chat_id": int(user_id),
#                 "text": relatorio_inicial,
#                 "remetente": 'bot',
#                 "tipo": "relatorio_inicial",  # Identifica como relatório inicial
#                 "timestamp": datetime.utcnow().isoformat() + "Z"
#             }), 200
            
#         except Exception as e:
#             print(f"❌ ERRO ao gerar relatório: {e}")
#             return jsonify({
#                 "chat_id": int(user_id),
#                 "text": "Desculpe, ocorreu um erro ao gerar o relatório inicial.",
#                 "remetente": 'bot'
#             }), 200

#     # 💬 CONVERSAS NORMAIS (respostas pontuais)
#     disciplinas_historicas = dados_em_cache.get('historicas', [])
#     disciplinas_atuais = dados_em_cache.get('parciais', [])
    
#     historico_formatado = "\n".join([
#         f"- {d.get('nome', 'N/A')}: Nota {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')}) - {d.get('status', 'N/A')}"
#         for d in disciplinas_historicas if d.get('nome')
#     ])
    
#     atuais_formatado = "\n".join([
#         f"- {d.get('nome', 'N/A')}: Nota Parcial {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')}) - {d.get('status', 'N/A')}"
#         for d in disciplinas_atuais if d.get('nome')
#     ])
    
#     contexto_completo = f"""
# HISTÓRICO COMPLETO:
# {historico_formatado if historico_formatado else 'Nenhuma disciplina histórica registrada'}

# DISCIPLINAS ATUAIS:
# {atuais_formatado if atuais_formatado else 'Nenhuma disciplina em curso'}
# """

#     try:
#         bot_response = llm.gerar_resposta_chat_ollama(user_message, contexto_completo)
        
#         if not bot_response or bot_response.strip() == "":
#             bot_response = "Desculpe, tive dificuldade em processar sua pergunta. Pode reformular?"
            
#     except Exception as e:
#         print(f"[ERRO] Falha ao gerar resposta do chatbot: {e}", file=sys.stderr)
#         bot_response = "Desculpe, estou com problemas técnicos no momento. Tente novamente em alguns instantes."

#     return jsonify({
#         "chat_id": int(user_id),
#         "text": bot_response,
#         "remetente": 'bot',
#         "tipo": "resposta_chat",  # Identifica como resposta normal
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     }), 200

@app.route("/api/chatbot", methods=["POST"])
def chat():
    """Endpoint para conversas com o chatbot (apenas respostas pontuais)."""
    data = request.get_json()
    user_id = data.get("chat_id")
    user_message = data.get("text", "")

    # Validação
    if not user_id or not user_message:
        return jsonify({"erro": "É necessário fornecer 'chat_id' e 'text'."}), 400

    # Carregar dados do cache
    dados_em_cache = load_from_cache(str(user_id))
    
    # Se não houver cache, criar dados de teste
    if not dados_em_cache:
        print(f"\n⚠️ Cache não encontrado para user_id={user_id}")
        print("🧪 Carregando dados de teste...")
        
        json_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'assets', 'resultado_notas_12.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                dados_em_cache = json.load(f)
            save_to_cache(str(user_id), dados_em_cache)
            print(f"✅ Cache criado para user_id={user_id}")
        except FileNotFoundError:
            print("❌ JSON de teste não encontrado")
            return jsonify({
                "chat_id": int(user_id),
                "text": "Erro: Seus dados não foram encontrados. Por favor, faça login novamente.",
                "remetente": 'bot'
            }), 200

    # Formatar contexto separado (histórico + atual)
    disciplinas_historicas = dados_em_cache.get('historicas', [])
    disciplinas_atuais = dados_em_cache.get('parciais', [])
    
    historico_formatado = "\n".join([
        f"- {d.get('nome', 'N/A')}: Nota {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')}) - {d.get('status', 'N/A')}"
        for d in disciplinas_historicas if d.get('nome')
    ])
    
    atuais_formatado = "\n".join([
        f"- {d.get('nome', 'N/A')}: Nota Parcial {d.get('nota', 'N/A')} (Conceito {d.get('abc', 'N/A')}) - {d.get('status', 'N/A')}"
        for d in disciplinas_atuais if d.get('nome')
    ])
    
    contexto_completo = f"""
HISTÓRICO COMPLETO:
{historico_formatado if historico_formatado else 'Nenhuma disciplina histórica registrada'}

DISCIPLINAS ATUAIS:
{atuais_formatado if atuais_formatado else 'Nenhuma disciplina em curso'}
"""

    # Gerar resposta pontual
    try:
        bot_response = llm.gerar_resposta_chat_ollama(user_message, contexto_completo)
        
        if not bot_response or bot_response.strip() == "":
            bot_response = "Desculpe, tive dificuldade em processar sua pergunta. Pode reformular?"
            
    except Exception as e:
        print(f"[ERRO] Falha ao gerar resposta do chatbot: {e}", file=sys.stderr)
        bot_response = "Desculpe, estou com problemas técnicos no momento. Tente novamente em alguns instantes."

    return jsonify({
        "chat_id": int(user_id),
        "text": bot_response,
        "remetente": 'bot',
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)
