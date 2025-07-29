from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import time
import pandas as pd
from datetime import datetime, timedelta

def sanitize_filename(s):
    return ''.join(c for c in str(s) if c.isalnum() or c in (' ', '_', '-')).rstrip()

def change_window(driver):
    from selenium.common.exceptions import ElementClickInterceptedException
    link_pesquisa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Pesquisa"))
    )
    time.sleep(0.5)  # Pequeno delay para garantir que o elemento está realmente clicável
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        try:
            link_pesquisa.click()
            break
        except ElementClickInterceptedException:
            print("Elemento não clicável, tentando novamente...")
            time.sleep(1)
            attempts += 1
            continue
    else:
        raise Exception("Não foi possível clicar no elemento 'Pesquisa' após várias tentativas.")

def change_date_and_search(driver, initial_date, end_date):
    initial_date_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "DataInicio"))
    )
    initial_date_input.clear()
    initial_date_input.send_keys(initial_date)
    end_date_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "DataFim"))
    )
    end_date_input.clear()
    end_date_input.send_keys(end_date)
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnPesquisar"))
    )
    search_button.click()
    return True

def download_and_wait(driver, download_dir, timeout=300):
    try:
        botao_exportar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btdlTransacoes"))
        )
    except:
        time.sleep(1)
        return None
    if 'disabled' in botao_exportar.get_attribute('class'):
        return None
    files_before = set(os.listdir(download_dir))
    start_time = time.time()
    botao_exportar.click()
    while time.time() - start_time < timeout:
        time.sleep(1)
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        for file in new_files:
            if not file.endswith('.crdownload'):
                return file
    print("Timeout ao esperar pelo download do arquivo.")
    return None

def search_by_cpf_cnpj(driver, cpf_cnpj):
    cpf_cnpj_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'CPF_CNPJPesquisa'))
    )
    cpf_cnpj_input.clear()
    cpf_cnpj_input.send_keys(cpf_cnpj)
    search_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'btnPesquisarCliente'))
    )
    search_button.click()

def loop_and_save_by_lines(driver, download_dir, initial_date, end_date, database_dir, found_cpfs, max_attempts=10):
    attempts = 0
    while True:
        linhas = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")
        if len(linhas) == 0:
            attempts += 1
            if attempts >= max_attempts:
                print(f"Nenhum usuário encontrado após {max_attempts} tentativas. Pulando cpf/cnpj.")
                return
            time.sleep(1)
            continue
        i = 0
        while i < len(linhas):
            try:
                linha = linhas[i]
                id = linha.find_element(By.XPATH, ".//td[2]").text
                name = linha.find_element(By.XPATH, ".//td[3]").text
                linha.click()
            except:
                time.sleep(1)
                linhas = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")
                attempts += 1
                if attempts >= max_attempts:
                    print(f"Não foi possível processar a linha após {max_attempts} tentativas. Pulando cpf/cnpj.")
                    return
                continue
            change_date_and_search(driver, initial_date, end_date)
            new_file = download_and_wait(driver, download_dir)
            if new_file:
                file_path = os.path.join(download_dir, new_file)
                ref_date = initial_date.replace('/', '-')
                safe_name = sanitize_filename(name)
                safe_id = sanitize_filename(id)
                new_filename = f"{safe_id}_{safe_name}_{ref_date}.csv"
                dest_path = os.path.join(database_dir, new_filename)
                if os.path.exists(dest_path):
                    print(f"Arquivo já existe, pulando: {dest_path}")
                else:
                    os.rename(file_path, dest_path)
                    print(f"Salvo: {dest_path}")
                found_cpfs.add(id)
            change_window(driver)
            time.sleep(1)
            i += 1
        next_button_li = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tabelaClientes_next"))
        )
        if 'disabled' in next_button_li.get_attribute('class'):
            return
        next_button = next_button_li.find_element(By.TAG_NAME, "a")
        next_button.click()

def main():
    # Configurações
    download_dir = os.path.expanduser('~/Downloads')  # Caminho padrão do Linux
    database_dir = os.path.join(os.getcwd(), 'database')
    os.makedirs(database_dir, exist_ok=True)
    start_date = datetime.strptime('01/06/2025', '%d/%m/%Y')
    end_date = datetime.strptime('28/06/2025', '%d/%m/%Y')
    
    # Selenium com ChromeDriver Manager
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Opcional: executar em headless mode (sem interface gráfica)
    # options.add_argument('--headless')
    
    # Configurar diretório de download
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Inicializar o driver com webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    driver.get('https://gestao.granitopagamentos.com.br/Login/Index')
    # --- Faça o login manualmente ou automatize aqui ---
    input("Faça login manualmente e pressione Enter...")
    change_window(driver)
    # Carrega CPFs/CNPJs
    cpf_cnpj_df = pd.read_excel('Credito Essencial Clientes_ Transações.xlsx')
    cpf_cnpj_data = cpf_cnpj_df['cpf_cnpj']
    name_data = cpf_cnpj_df['name'] if 'name' in cpf_cnpj_df.columns else ["user"]*len(cpf_cnpj_df)
    current_date = start_date
    while current_date < end_date:
        initial_date = current_date.strftime('%d/%m/%Y')
        #next_date = current_date + timedelta(days=30)
        #final_date = min(next_date, end_date).strftime('%d/%m/%Y')
        final_date = end_date.strftime('%d/%m/%Y')  # Usa a data final definida
        print(f"Processando intervalo: {initial_date} a {final_date}")
        found_cpfs = set()
        # Segundo: loop por CPFs/CNPJs da planilha que não apareceram
        for cpf_cnpj, name in zip(cpf_cnpj_data, name_data):
            if str(cpf_cnpj) not in found_cpfs:
                print(f"Buscando extra: {cpf_cnpj} - {name}")
                search_by_cpf_cnpj(driver, cpf_cnpj)
                # Agora roda o loop para todos os usuários retornados na busca
                loop_and_save_by_lines(driver, download_dir, initial_date, final_date, database_dir, found_cpfs)
                change_window(driver)
                time.sleep(1)
        current_date = next_date
    driver.quit()

if __name__ == "__main__":
    main()
