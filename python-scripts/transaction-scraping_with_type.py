from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
from datetime import datetime, timedelta

# pasta inter scraping
os.chdir('C:\\Users\\vitor\\inter-scraping')

#service = Service("C://Users//servi//inter-scraping//chromedriver-win64//chromedriver-win64//chromedriver.exe")
options = Options()
# Comente a linha abaixo se quiser VER o navegador aberto (para testar)
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Cria o driver globalmente
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
"""
https://gestao.granitopagamentos.com.br/Login/Index
sandro.leao@creditoessencial.com.br
1011S@ndr0310
"""

def change_window():
    
    link_pesquisa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Pesquisa"))
    )
    link_pesquisa.click()

def change_date_and_search(initial_date, end_date):
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
        
def download_and_wait(download_dir, timeout=300):
    try:
        botao_exportar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btdlTransacoes"))
        )
    except:
        time.sleep(1)
    
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
                return file  # Retorna o nome do arquivo quando o download estiver completo

    print("Timeout ao esperar pelo download do arquivo.")
    return None

def search_by_cpf_cnpj(cpf_cnpj):
    cpf_cnpj_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'CPF_CNPJPesquisa'))
    )
    cpf_cnpj_input.clear()
    cpf_cnpj_input.send_keys(cpf_cnpj)

    search_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'btnPesquisarCliente'))
    )
    search_button.click()

download_dir = r'C:\Users\vitor\Downloads'

def loop_in_lines(download_dir, initial_date, end_date):
    data = {
        'cpf/cnpj': [], 'name': [], 'value': [], 'date': [],
        'payment_method': [], 'installments': [], 'brand': []
    }  # Updated dictionary to include additional fields
    
    while True:
        linhas = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")
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
                continue  
            
            change_date_and_search(initial_date=initial_date, end_date=end_date)
            new_file = download_and_wait(download_dir=download_dir)

            transacoes = set()

            if new_file:
                file_path = os.path.join(download_dir, new_file)
                df = pd.read_csv(file_path, sep=';')
                aprovada_df = df[df['Status'] == "Aprovada"].copy()
                aprovada_df['Valor'] = aprovada_df['Valor'].str.replace('.', '').str.replace(',', '.').astype(float)
                aprovada_df['Data e hora'] = pd.to_datetime(aprovada_df['Data e hora'], dayfirst=True)
                aprovada_df['Data'] = aprovada_df['Data e hora'].dt.date
                resultado = aprovada_df.groupby(['Data', 'Tipo', 'Bandeira', 'Numero Parcelas'])['Valor'].sum()

                for (date, payment_method, brand, installments), total_value in resultado.items():
                    # Verifica se há valores nulos em payment_method, brand ou installments
                    if (pd.isnull(payment_method) or pd.isnull(brand) or 
                        pd.isnull(installments) or 
                        brand not in ["MASTERCARD", "VISA", "ELO","AMEX"]):         
                                                  
                        breakpoint()  # Ignora registros com valores nulos

                    data['cpf/cnpj'].append(id)
                    data['name'].append(name)
                    data['value'].append(total_value)
                    data['date'].append(date)
                    data['payment_method'].append(payment_method)
                    data['installments'].append(installments)
                    data['brand'].append(brand)
                    transacoes.add(date)

            change_window()
            time.sleep(1)
            i += 1
        
        next_button_li = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tabelaClientes_next"))
        )
        
        if 'disabled' in next_button_li.get_attribute('class'):
            return data
        
        next_button = next_button_li.find_element(By.TAG_NAME, "a")
        next_button.click()

# Define a pasta para salvar os arquivos CSV
database_dir = os.path.join(os.getcwd(), 'database')
os.makedirs(database_dir, exist_ok=True)

# Define os intervalos de datas
start_date = datetime.strptime('12/05/2025', '%d/%m/%Y')
end_date = datetime.strptime('22/05/2025', '%d/%m/%Y')

# Itera mês a mês
current_date = start_date
while current_date < end_date:
    # Define o intervalo de datas para o loop
    initial_date = current_date.strftime('%d/%m/%Y')
    next_date = current_date + timedelta(days=30)  # Limita o intervalo a 30 dias
    final_date = min(next_date, end_date).strftime('%d/%m/%Y')  # Garante que final_date não ultrapasse end_date

    print(f"Processando intervalo: {initial_date} a {final_date}")

    # Executa o loop para o intervalo de datas
    transaction_data = loop_in_lines(download_dir, initial_date, final_date)

    # Salva o transaction_data em CSV
    transaction_file = os.path.join(database_dir, f'transaction_data_{initial_date.replace("/", "-")}_to_{final_date.replace("/", "-")}.csv')
    pd.DataFrame(transaction_data).to_csv(transaction_file, index=False)
    print(f"Salvo: {transaction_file}")

    # Processa os dados adicionais
    cpf_cnpj_df = pd.read_excel('Credito Essencial Clientes_ Transações.xlsx')
    cpf_cnpj_data = cpf_cnpj_df['cpf/cnpj']

    cpf_cnpj_transaction_data = {'cpf/cnpj': [], 'name': [], 'value': [], 'date': []}

    for cpf_cnpj in cpf_cnpj_data:
        if cpf_cnpj not in transaction_data['cpf/cnpj']:
            search_by_cpf_cnpj(cpf_cnpj)
            user_data = loop_in_lines(download_dir, initial_date, final_date)

            for key in cpf_cnpj_transaction_data:
                cpf_cnpj_transaction_data[key].extend(user_data.get(key, []))

    by_id_df = pd.DataFrame(cpf_cnpj_transaction_data)
    by_loop_df = pd.DataFrame(transaction_data)

    # Combina os dados e salva o all_data
    all_data = pd.concat([by_id_df, by_loop_df], ignore_index=True)
    all_data_file = os.path.join(database_dir, f'all_data_{initial_date.replace("/", "-")}_to_{final_date.replace("/", "-")}.csv')
    all_data.to_csv(all_data_file, index=False)
    print(f"Salvo: {all_data_file}")

    # Avança para o próximo mês
    current_date = next_date

# Fecha o WebDriver
driver.quit()
