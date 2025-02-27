from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import os
import time
import pandas as pd

service = Service("C://Users//servi//inter-scraping//chromedriver-win64//chromedriver-win64//chromedriver.exe")
chrome_profile_path = r'C:\Users\servi\AppData\Local\Google\Chrome\User Data\Default'

# Set up Chrome options
# Configuração das opções do Chrome
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")
options.add_experimental_option("detach", True)  # Isso permite que o Chrome permaneça aberto após o script terminar

# Inicializa o Chrome com as opções
driver = webdriver.Chrome(service=service)
"""
https://gestao.granitopagamentos.com.br/Login/Index
sandro.leao@creditoessencial.com.br
11S@ndr01003
"""

def change_window():
    link_pesquisa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Pesquisa"))
    )
    
    link_pesquisa.click()
    
def change_date_and_search(initial_date, end_date):
    # Espera o input de data estar visível e interagível
    data_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "DataInicio"))
    )
    data_input.clear()
    data_input.send_keys(initial_date)

    # Espera o botão de pesquisar estar visível e clicável
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnPesquisar"))
    )
    search_button.click()

    return True
        
        
def download_and_wait(download_dir, timeout=300):
    
    botao_exportar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btdlTransacoes"))
        )
    
    if 'disabled' in botao_exportar.get_attribute('class'): 
        return None
    
    files_before = set(os.listdir(download_dir))
    start_time = time.time()
    
    botao_exportar.click()
    
    while time.time() - start_time < timeout:
        time.sleep(1)  # Aguarda 1 segundo entre cada verificação para não sobrecarregar o sistema
        files_after = set(os.listdir(download_dir))
        new_files = files_after - files_before
        for file in new_files:
            # Verifica se o arquivo é o esperado e se não tem extensão temporária
            if not (file.endswith('.crdownload')):
                return file  # Retorna o nome do arquivo quando o download estiver completo

    print("Timeout ao esperar pelo download do arquivo.")
    return None

data = {'cpf/cnpj': [], 'name': [], 'value': []}
download_dir = r'C:\Users\servi\Downloads'

while True:
    linhas = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")

    for linha in linhas:
        linha.click()
        change_date_and_search(initial_date='25/02/2025', end_date='26/02/2025')
        new_file = download_and_wait(download_dir=download_dir)
        id = linha.find_element(By.XPATH, ".//td[2]").text
        name = linha.find_element(By.XPATH, ".//td[3]").text
        if new_file:
            file_path= os.path.join(download_dir, new_file)
            df = pd.read_csv(file_path, sep=';')
            aprovada_df = df[df['Status'] == "Aprovada"]
            aprovada_df['Valor'] = aprovada_df['Valor'].str.replace(',', '.').astype(float)
            total_value = aprovada_df['Valor'].sum()
            if total_value != 2 and total_value > 0:
                data['cpf/cnpj'].append(id)
                data['value'].append(total_value)
                data['name'].append(name)

        change_window()
        time.sleep(1)
    
    next_button_li = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "tabelaClientes_next"))
    )
    if 'disabled' in next_button_li.get_attribute('class'):
        break
    
    next_button = next_button_li.find_element(By.TAG_NAME, "a")
    next_button.click()

        

