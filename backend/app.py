
from flask import Flask, request
from flask_cors import CORS # type: ignore

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import arvoreDriver
import gera_id


# Instanciar o gerador de ID
ids = gera_id.GeraId()
# Instanciar o primeiro nó
arvore = arvoreDriver.ArvDriver(id = ids.geraId())

def login(e: str, s: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver() # driver, do tipo webdriver.Chrome, recebe...
    wait = WebDriverWait(driver, 20)
    try:    
        # Espera o botão/formulário e clica
        botao = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "uc_flex-r")))
        botao.click()
        print('Botão clicado')

        # Espera o campo de e-mail
        campo_email = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        campo_email.send_keys(e)
        campo_email.send_keys(Keys.ENTER)

        # Espera o campo de senha
        campo_senha = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        print('Digitando senha...')
        campo_senha.send_keys(s)
        # wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "idSIButton9")))
        try:
            botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        except TimeoutException:
            print(botao_entrar, "não carrregou")
            driver.find_element(By.ID, "idSIButton9").click()
        botao_entrar.click()

        # Espera o botão de confirmação por SMS
        campo_texto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
        campo_texto.click()

        print("Aguardando autenticação por dois fatores (digite o código)...")
     

    except TimeoutException as e:
        print("Erro de tempo ao carregar um elemento da página:", str(e))
        return {'bool': False}
    except Exception as e:
        print("Erro desconhecido ao carregar um elemento da página:", str(e) + ', tentando novamente.')
        try:
            botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            botao_entrar.click()
            # Espera o botão de confirmação por SMS
            campo_texto = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-row")))
            campo_texto.click()
        except Exception as e:
            print("Erro desconhecido ao carregar um elemento da página:", str(e))
            return {'bool': False}
    
    resposta = {'bool': True, 'id': id}
    resposta = json.dumps(resposta, ensure_ascii=False, indent=4)
    print("Login realizado com sucesso!")
    return resposta

def confirmacao(c: str, id: int):
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 8)
    resposta = {'bool': False} # Padrão da resposta


    try:
        campo_codigo = wait.until(EC.presence_of_element_located((By.ID, "idTxtBx_SAOTCC_OTC")))
        print('Digitando código...')
        campo_codigo.clear()
        campo_codigo.send_keys(c)
        campo_codigo.send_keys(Keys.ENTER)

        try:
            span = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "uc_appuser-name")))
            nome = 'vazio'
            nome = str(span.text.strip().lower()).split(' ')[1].capitalize()
            print(nome)
            if nome != 'vazio':
                resposta = {'bool': True, 'nome': nome} # Resposta sucesso
            else:
                print("Não foi encontrado o nome:", nome)
        except Exception as e:
            print(e)
        except TimeoutException:
            print('Timeout no Login, ID:', id)
            time.sleep(3)
            driver.quit()
            resposta = {'bool': False, 'erro': 'Timeout'}
    except Exception as e:
        print("Um problema foi encontrado:", e)
        resposta = {'bool': False, 'erro': 'Algum erro ocorreu.'}

    print('Terminando requisição confirmação. ID:', id)
    resposta = json.dumps(resposta, ensure_ascii=False, indent=4)
    return resposta

def scrapeNotas(id: int):
    print("Fazer_scrape")
    driver: webdriver.Chrome = arvore.encontra(id).obtemDriver()
    wait = WebDriverWait(driver, 8)
    time.sleep(3)
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
            {"tipo": "a", "nome": materia, "nota": nota, "abc": "D", "status": status}
            for materia, nota, status in zip(mates_p, notas_p, status_list_p)
        ]
        historico = [
            {"tipo": "h", "nome": materia, "nota": nota, "abc": "D", "status": status}
            for materia, nota, status in zip(mates_h, notas_h, status_list_h)
        ]

        resultado = {
            "parciais": parcial,
            "historicas": historico
        }

        return json.dumps(resultado, ensure_ascii=False, indent=4)
    
    finally:
        print('Feito o scrape de notas, retornando')
        print(len(resultado['parciais']))
        print(len(resultado['historicas']))
        time.sleep(3)
        driver.quit()


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'API funcionando!'

@app.route('/api/login', methods=['POST'])
def receber_login():
    print('\n\n\n\ndados recebidos para login')
    dados = request.json 
    e = dados['email']
    s = dados['senha']
    # print(dados)  # Adicionar em caso de testes
    chrome_options = Options()
    # chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    id = ids.geraId()
    # Inserir primeira árvore que possui Driver
    arvore.insere(id = id, driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                                options=chrome_options))
    # print('inserido uma nova árvore') # Adicionar em caso de testes
    arvore.encontra(id).obtemDriver().get('https://siga.cps.sp.gov.br/sigaaluno/applogin.aspx')

    # print('Árvore') # Adicionar em caso de testes
    # arvore.mostra_EmOrdem() # Adicionar em caso de testes
    # print('Return') # Adicionar em caso de testes
    return login(e, s, id)

@app.route('/api/login/confirmacao', methods=['POST'])
def confirmacao_login():
    print('\n\n\nConfirmação recebida para login')
    dados = request.json
    c = dados['codigo']
    id = dados['id']

    print('Código de confirmação:', c) # mudar para receber 
    return confirmacao(c, id)

@app.route('/api/notas', methods=['POST'])
def scrape_notas():
    print('\n\n\n\nDados recebidos para pegar notas')
    dados = request.json
    # print(dados)  # Adicionar em caso de testes
    id = dados['id']

    # print(notas) # Adicionar em caso de testes
    return scrapeNotas(id)

if __name__ == '__main__':
    app.run(debug=True)