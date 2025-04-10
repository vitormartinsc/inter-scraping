from imapclient import IMAPClient
import pyzmail
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def pegar_codigo_mais_recente(email, senha_email, remetente='gestao.portal@granitopagamentos.com.br', desde=None):
    with IMAPClient('imap.gmail.com', ssl=True) as client:
        client.login(email, senha_email)
        client.select_folder('INBOX', readonly=True)

        if desde is None:
            desde = datetime.now() - timedelta(minutes=10)

        messages = client.search([
            'FROM', remetente,
            'SINCE', desde.strftime('%d-%b-%Y')
        ])
        messages = sorted(messages, reverse=True)

        for uid in messages:
            raw = client.fetch([uid], ['BODY[]', 'INTERNALDATE'])
            msg = pyzmail.PyzMessage.factory(raw[uid][b'BODY[]'])
            data_email = raw[uid][b'INTERNALDATE']

            if data_email < desde:
                continue

            corpo = ""
            if msg.text_part:
                corpo = msg.text_part.get_payload().decode(msg.text_part.charset)
            elif msg.html_part:
                corpo = msg.html_part.get_payload().decode(msg.html_part.charset)

            codigos = re.findall(r'\b\d{6}\b', corpo)
            if codigos:
                return codigos[0]
    return None


def login_granito_com_2fa():
    navegador = webdriver.Chrome()
    wait = WebDriverWait(navegador, 20)

    navegador.get("https://gestao.granitopagamentos.com.br/Login/Index")

    # Preenche login
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("sandro.leao@creditoessencial.com.br")
    navegador.find_element(By.ID, "password").send_keys("1011S@ndr0310")
    wait.until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()

    # Interage com o modal 2FA
    try:
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modalMFA"]/div[2]/div/div[2]/div[2]/label/input')))
        navegador.execute_script("arguments[0].click();", checkbox)

        botao_continuar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="modalMFA"]/div[2]/div/div[3]/button[2]')))
        navegador.execute_script("arguments[0].click();", botao_continuar)

        # Marca o horário para filtrar o email
        hora_requisicao = datetime.now()

        # Aguarda campo de código no modal
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mfa-code"]')))

        # Espera o código chegar
        codigo = None
        for _ in range(6):
            codigo = pegar_codigo_mais_recente(
                email="sandro.leao@creditoessencial.com.br",
                senha_email="11S@ndr010",  # sua senha do email
                desde=hora_requisicao
            )
            if codigo:
                break
            time.sleep(5)

        if not codigo:
            print("❌ Código não encontrado no e-mail.")
            return

        print(f"✅ Código recebido: {codigo}")

        # Preenche e confirma dentro do modal
        campo_codigo = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mfa-code"]')))
        campo_codigo.send_keys(codigo)

        botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="confirm-authorize"]')))
        botao_confirmar.click()

        print("✅ Login finalizado com sucesso.")

    except Exception as e:
        print("❌ Erro no processo de login:", e)

login_granito_com_2fa()