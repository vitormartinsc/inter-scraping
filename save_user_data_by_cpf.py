import os
import pandas as pd
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def download_and_wait(driver, download_dir, timeout=300):
    botao_exportar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btdlTransacoes"))
    )

    if 'disabled' in botao_exportar.get_attribute('class'):
        return None

    files_before = set(os.listdir(download_dir))
    botao_exportar.click()

    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(1)
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        for file in new_files:
            if not file.endswith('.crdownload'):
                return file

    print("Timeout ao esperar pelo download do arquivo.")
    return None

def process_user_data(driver, download_dir, cpf_cnpj, start_date, end_date, base_dir):
    current_date = start_date

    while current_date < end_date:
        initial_date = current_date.strftime('%d/%m/%Y')
        next_date = current_date + timedelta(days=30)
        final_date = min(next_date, end_date).strftime('%d/%m/%Y')

        print(f"Processando CPF/CNPJ {cpf_cnpj} no intervalo: {initial_date} a {final_date}")

        change_date_and_search(driver, initial_date, final_date)
        new_file = download_and_wait(driver, download_dir)

        if new_file:
            file_path = os.path.join(download_dir, new_file)
            dest_path = os.path.join(base_dir, f"{cpf_cnpj}_data_{initial_date.replace('/', '-')}_to_{final_date.replace('/', '-')}.csv")
            os.rename(file_path, dest_path)
            print(f"Arquivo salvo em: {dest_path}")

        current_date = next_date

def main():
    download_dir = r'C:\Users\vitor\Downloads'
    base_dir = os.path.join(os.getcwd(), 'database')
    os.makedirs(base_dir, exist_ok=True)

    start_date = datetime.strptime('01/05/2025', '%d/%m/%Y')
    end_date = datetime.strptime('09/05/2025', '%d/%m/%Y')

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    cpf_cnpj_df = pd.read_excel('Credito Essencial Clientes_ Transações.xlsx')
    cpf_cnpj_data = cpf_cnpj_df['cpf/cnpj']

    for cpf_cnpj in cpf_cnpj_data:
        process_user_data(driver, download_dir, cpf_cnpj, start_date, end_date, base_dir)

    driver.quit()

if __name__ == "__main__":
    main()
