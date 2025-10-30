# --- Imports ---
import tempfile, os, uuid, time, json
import sys
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd

# Módulos locais
from utils.driver_seguro import criar_driver_seguro, capturar_estado_driver
import arvoreDriver
import gera_id
import llm

# --- Configuração e Inicialização ---
app = Flask(__name__)
CORS(app)


ids = gera_id.GeraId()
arvore = arvoreDriver.ArvDriver(id=ids.geraId())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados_notas")
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
def login(email: str, senha: str, id: int):
    print('🕓 Aguardando 2s...')
    time.sleep(2)

    driver = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 20)

    try:
        botao = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "uc_flex-r")))
        botao.click()
        print('✅ Botão clicado')

        campo_email = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        campo_email.send_keys(email)
        campo_email.send_keys(Keys.ENTER)

        campo_senha = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        print('⌨️ Digitando senha...')
        campo_senha.send_keys(senha)
        print('Senha enviada')

        print('Clicando no entrar...')
        time.sleep(2)
        botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        botao_entrar.click()
        print('🔒 Login submetido')

        campo_texto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
        campo_texto.click()
        print('🟢 Autenticação em andamento...')

        return json.dumps({'bool': True, 'id': id})

    except Exception as e:
        print('❌ Erro durante o login:', e)
        capturar_estado_driver(driver, prefixo=f"erro_login_{id}")
        return json.dumps({'bool': False, 'erro': str(e), 'id': id})

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
        capturar_estado_driver(driver, prefixo=f"confirmacao_{id}")
        resposta = {'bool': False, 'erro': 'Falha na confirmação do código.'}
    
    return json.dumps(resposta, ensure_ascii=False, indent=4)

def scrapeNotas(id: int):
    print("Fazer_scrape")
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 8)
    # time.sleep(3)
    print("Fazer_scrape Iniciando")
    try:
        # 1 - Clicar em "meu curso"
        curso_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uc_appfooter-button.uc_pointer")))
        for btn in curso_btns:
            try:
                print(btn)
                span = btn.find_elements(By.TAG_NAME, "center")[1]
                if span.text.strip().lower() == "meu curso":
                    btn.click()
                    break
            except Exception:
                continue

        # 2 - Clicar em "Histórico"
        historico_btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uc_appgrid-item.uc_pointer")))
        for btn in historico_btns:
            try:
                span = btn.find_element(By.TAG_NAME, "span")
                if span.text.strip().lower() == "histórico":
                    btn.click()
                    break
            except Exception:
                continue

        # 3 - Extrair cards
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "uc_appcard")))
        cards = driver.find_elements(By.CLASS_NAME, "uc_appcard")

        # Coletar os dados
        
        mates_p = []
        notas_p = []
        status_list_p = []
        mates_h = []
        notas_h = []
        status_list_h = []

        for card in cards:
            try:
                nome_materia = card.find_element(By.CLASS_NAME, "uc_appcard-title").text.strip()
                if nome_materia.startswith('Projeto Integrador'):
                    continue
                linhas_info = card.find_elements(By.CSS_SELECTOR, ".uc_flex-r.uc_flex-jcsb.uc_w100.uc_mb5")
                nota = linhas_info[0].find_element(By.CLASS_NAME, "uc_apptext").text.strip()
                status = linhas_info[4].find_element(By.CLASS_NAME, "uc_apptext").text.strip()

                if status == 'Em Curso':
                    mates_p.append(nome_materia)
                    notas_p.append(nota)
                    status_list_p.append(status)
                else:
                    mates_h.append(nome_materia)
                    notas_h.append(nota)
                    status_list_h.append(status)

            except Exception as e:
                print(f"Erro ao extrair dados de uma matéria: {e}")
                continue
        # Gerar estrutura final
        parcial = [
            {"tipo": "a", "nome": materia, "nota": nota, "abc": rank_nota(nota), "status": status}
            for materia, nota, status in zip(mates_p, notas_p, status_list_p)
        ]
        historico = [
            {"tipo": "h", "nome": materia, "nota": nota, "abc": rank_nota(nota), "status": status}
            for materia, nota, status in zip(mates_h, notas_h, status_list_h)
        ]

        resultado = {
            "parciais": parcial,
            "historicas": historico
        }

        with open(f"resultado_notas_{id}.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        save_to_cache(id, resultado)

        return json.dumps(resultado, ensure_ascii=False, indent=4)
    
    except Exception as e:
        print(f"❌ Erro ao fazer scrape das notas: {e}")
        capturar_estado_driver(driver, prefixo=f"scrape_notas_{id}")
        return json.dumps({'bool': False, 'erro': "Falha ao extrair notas."})

    finally:
        print('Feito o scrape de notas, retornando')
        print(len(resultado['parciais']))
        print(len(resultado['historicas']))
        time.sleep(3)
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
    print('Dados recebidos para login:', dados)

    email = dados['email']
    senha = dados['senha']

    # cria novo driver isolado
    driver, user_data_dir = criar_driver_seguro()
    id = ids.geraId()
    print(f'\n🔑 Gerado ID {id}')

    arvore.insere(id=id, driver=driver, user_data_dir=user_data_dir)
    print('✅ Driver inserido na árvore')

    driver.get('https://siga.cps.sp.gov.br/sigaaluno/applogin.aspx')
    print('Página carregada')

    # chama função que faz o login com o driver certo
    return login(email, senha, id)

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

@app.route('/api/notas/teste', methods=['POST'])
def api_notas_teste():
    """Endpoint para fornecer dados de notas de teste a partir de um arquivo local."""
    dados = request.json
    id = dados['id']
    json_path = f"resultado_notas_{id}.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            dados_teste = json.load(f)
        save_to_cache(id, dados_teste)
        return jsonify(dados_teste), 200
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de teste não encontrado."}), 404
    except Exception as e:
        print(f"[ERRO] Falha ao carregar dados de teste: {e}", file=sys.stderr)
        return jsonify({"erro": "Erro ao carregar dados de teste."}), 500

@app.route('/api/init', methods=['POST'])
def init_user_session():
    data = request.get_json()
    user_id = data.get("id_usuario")
    perfil = data.get("perfil")  # opcional, ex.: quiz inicial

    if not user_id:
        return jsonify({"erro": "É necessário fornecer 'id_usuario'."}), 400

    notas = load_from_cache(str(user_id))
    if not notas:
        return jsonify({"erro": f"Nenhum dado encontrado para o usuário de ID {user_id}."}), 404

    disciplinas_historicas = notas.get('historicas', [])
    disciplinas_parciais  = notas.get('parciais', [])
    if not disciplinas_historicas and not disciplinas_parciais:
        return jsonify({"relatorio_inicial": "Nenhuma disciplina foi fornecida para análise."}), 200

    todas = disciplinas_historicas + disciplinas_parciais

    try:
        relatorio = llm.gerar_relatorio_inicial_ollama(todas, perfil=perfil)
        if not relatorio.strip():
            relatorio = "Desculpe, não foi possível gerar o relatório inicial. Tente novamente."
    except Exception as e:
        print(f"[ERRO] Falha ao gerar relatório inicial: {e}", file=sys.stderr)
        relatorio = "Erro ao processar seus dados. Por favor, tente novamente mais tarde."

    return jsonify({
        "relatorio_inicial": relatorio,
        "user_id": int(user_id),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/api/chatbot", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("chat_id")
    user_message = data.get("text", "")
    perfil = data.get("perfil")  # opcional

    if not user_id or not user_message:
        return jsonify({"erro": "É necessário fornecer 'chat_id' e 'text'."}), 400

    dados_em_cache = load_from_cache(str(user_id))
    if not dados_em_cache:
        return jsonify({
            "chat_id": int(user_id),
            "text": "Seus dados não foram encontrados. Por favor, faça login novamente.",
            "remetente": 'bot'
        }), 200

    disciplinas_historicas = dados_em_cache.get('historicas', [])
    disciplinas_atuais     = dados_em_cache.get('parciais', [])

    historico_formatado = "\n".join([
        f"- {d.get('nome','N/A')}: Nota {d.get('nota','N/A')} (Conceito {d.get('abc','N/A')}) — {d.get('status','N/A')}"
        for d in disciplinas_historicas if d.get('nome')
    ]) or "(sem histórico)"

    atuais_formatado = "\n".join([
        f"- {d.get('nome','N/A')}: Nota Parcial {d.get('nota','N/A')} (Conceito {d.get('abc','N/A')}) — {d.get('status','N/A')}"
        for d in disciplinas_atuais if d.get('nome')
    ]) or "(sem atuais)"

    contexto_completo = f"""HISTÓRICO COMPLETO:
{historico_formatado}

DISCIPLINAS ATUAIS:
{atuais_formatado}
"""

    perfil_txt = ""
    if perfil:
        # exemplo de chaves aceitas no perfil
        horas = perfil.get("horas_estudo_dia", "não informado")
        tipo  = perfil.get("tipo_aprendiz", "não informado")
        fam   = perfil.get("familiaridade_metodos", {})
        foc   = perfil.get("nivel_foco", "não informado")
        mot   = perfil.get("motivacao_estudo", "não informado")
        perfil_txt = (
            "Perfil do aluno:\n"
            f"- Horas de estudo/dia: {horas}\n"
            f"- Tipo de aprendiz: {tipo}\n"
            f"- Familiaridade com métodos: {fam}\n"
            f"- Nível de foco/concentração: {foc}\n"
            f"- Motivação para estudar: {mot}\n"
        )
        print(perfil_txt)

    try:
        bot_response = llm.gerar_resposta_chat_ollama(user_message, contexto_completo, perfil=perfil_txt)
        if not bot_response.strip():
            bot_response = "Desculpe, tive dificuldade em processar sua pergunta. Pode reformular?"
    except Exception as e:
        print(f"[ERRO] Falha ao gerar resposta do chatbot: {e}", file=sys.stderr)
        bot_response = "Desculpe, estou com problemas técnicos no momento. Tente novamente em alguns instantes."
    print('\n\nTeste')
    return jsonify({
        "chat_id": int(user_id),
        "text": bot_response,
        "remetente": 'bot',
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)

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