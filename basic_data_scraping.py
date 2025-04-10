from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import os
import time
import pandas as pd

os.chdir('C:\\Users\\servi\\inter-scraping')

# Inicializa o Chrome com as opções
driver = webdriver.Chrome()
"""
https://gestao.granitopagamentos.com.br/Login/Index
sandro.leao@creditoessencial.com.br
1011S@ndr0310
"""

def change_window(window_name):
    link_pesquisa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, window_name))
    )
    try:
        link_pesquisa.click()
    except ElementClickInterceptedException:
        time.sleep(0.5)
    wait_for_processing_to_disappear(driver)

def wait_for_processing_to_disappear(driver, timeout=10):
    """ Aguarda a aba 'Processando...' desaparecer antes de continuar """
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Processando')]"))
        )
        print("Aba 'Processando...' desapareceu. Continuando...")
    except Exception as e:
        print(f"Erro ou tempo esgotado ao esperar a aba 'Processando...': {e}")

def get_element_text_by_xpath(xpath, option = 'value'):
    element_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

    # Capturar o valor do input
    element_text = element_input.get_attribute(option)
    return element_text

def loop_in_lines():
    basic_data = {
        'name': [], 'cpf_cnpj': [], 'phone': [], 'email': [], 'fantasy_name': [],
        'branch_of_activity': [], 'cep': [], 'street_name': [], 'address_number': [],
        'address_complement': [], 'neighborhood_name': [], 'city_name': [],
        'state_name': [], 'status': [], 'bank_name': [], 'agency': [],
        'account_number': [], 'account_dv': [], 'account_type': []
    }
    page = 1
    while True:
        client_rows = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")
        i = 0

        while i < len(client_rows):
            client_row = client_rows[i]

            try:
                cpf_cnpj = client_row.find_element(By.XPATH, ".//td[3]").text
                name = client_row.find_element(By.XPATH, ".//td[4]").text
                status = client_row.find_element(By.XPATH, ".//td[10]").text

                if 'Crédito' in name: 
                    i += 1
                    continue

                print(f'{i+1}/{len(client_rows)} da pag. {page}')
                client_row.click()
                time.sleep(0.5)

                phone = get_element_text_by_xpath('//*[@id="tabelaTelefones"]/tbody/tr/td[2]/input')
                email = get_element_text_by_xpath('//*[@id="tabelaEmails"]/tbody/tr/td[2]/input')
                fantasy_name = get_element_text_by_xpath('//*[@id="Fantasia"]')
                branch_of_activity = get_element_text_by_xpath('//*[@id="RamoAtividadePF"]/option', 'text')
                cep = get_element_text_by_xpath('//*[@id="CEP"]')
                street_name = get_element_text_by_xpath('//*[@id="Endereco"]')
                address_number = get_element_text_by_xpath('//*[@id="Numero"]')
                address_complement = get_element_text_by_xpath('//*[@id="Complemento"]')
                neighborhood_name = get_element_text_by_xpath('//*[@id="Bairro"]')
                city_name = get_element_text_by_xpath('//*[@id="Cidade"]/option', 'text')
                state_name = get_element_text_by_xpath('//*[@id="UF"]/option', 'text')
                bank_name = get_element_text_by_xpath('//*[@id="Banco"]/option', 'text')
                agency = get_element_text_by_xpath('//*[@id="Agencia"]')
                account_number = get_element_text_by_xpath('//*[@id="Conta"]')
                account_dv = get_element_text_by_xpath('//*[@id="ContaDV"]')
                account_type = get_element_text_by_xpath('//*[@id="TipoConta"]/option', 'text')

                basic_data['name'].append(name)
                basic_data['cpf_cnpj'].append(cpf_cnpj)
                basic_data['phone'].append(phone)
                basic_data['email'].append(email)
                basic_data['fantasy_name'].append(fantasy_name)
                basic_data['branch_of_activity'].append(branch_of_activity)
                basic_data['cep'].append(cep)
                basic_data['street_name'].append(street_name)
                basic_data['address_number'].append(address_number)
                basic_data['address_complement'].append(address_complement)
                basic_data['neighborhood_name'].append(neighborhood_name)
                basic_data['city_name'].append(city_name)
                basic_data['state_name'].append(state_name)
                basic_data['status'].append(status)
                basic_data['bank_name'].append(bank_name)
                basic_data['agency'].append(agency)
                basic_data['account_number'].append(account_number)
                basic_data['account_dv'].append(account_dv)
                basic_data['account_type'].append(account_type)

                i += 1
                change_window('Pesquisa')

            except:
                time.sleep(1)
                client_rows = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")

        try:
            next_button_li = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "tabelaClientes_next"))
            )

            if 'disabled' in next_button_li.get_attribute('class'):
                print("Fim da paginação. Encerrando.")
                return basic_data

            next_button = next_button_li.find_element(By.TAG_NAME, "a")
            page += 1
            next_button.click()
            time.sleep(1)

        except Exception as e:
            print(f"Erro ao clicar em 'Próximo': {e}")
            return basic_data


def search_by_cpf_cnpj(cpf_cnpj):
    cpf_cnpj_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'CPF_CNPJPesquisa'))
    )
    cpf_cnpj_input.clear()
    cpf_cnpj_input.send_keys(cpf_cnpj)

    search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "btnPesquisarCliente"))
    )
    
    while True:
        try:
            search_button.click()
            break
        except:
            time.sleep(1)
        
equipment_data_general = loop_in_lines()
df = pd.DataFrame(equipment_data_general)
df.to_csv('equipment_data.csv')

equipment_data_general = pd.read_csv('equipment_data.csv')

cpf_cnpj_df = pd.read_excel('Credito Essencial Clientes_ Transações.xlsx')
cpf_cnpj_data = cpf_cnpj_df['cpf/cnpj']

cpf_cnpj_equipment_data = []
for cpf_cnpj in cpf_cnpj_data:
    if cpf_cnpj not in equipment_data_general['cpf_cnpj'].values:
        search_by_cpf_cnpj(cpf_cnpj)
        user_data = loop_in_lines()  

        cpf_cnpj_equipment_data.append(user_data)
        
resultado = {}

for data in cpf_cnpj_equipment_data:
    for chave, lista_valores in data.items():
        if chave not in resultado:
            resultado[chave] = []
        resultado[chave].extend(lista_valores)

cpf_cnpj_equipment_dataframe = pd.DataFrame(resultado)
pd.concat([equipment_data_general, cpf_cnpj_equipment_dataframe])
