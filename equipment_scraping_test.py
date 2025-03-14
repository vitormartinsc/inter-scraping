from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
import os
import time
import pandas as pd

service = Service("C://Users//servi//inter-scraping//chromedriver-win64//chromedriver-win64//chromedriver.exe")

# Inicializa o Chrome com as opções
driver = webdriver.Chrome(service=service)
"""
https://gestao.granitopagamentos.com.br/Login/Index
sandro.leao@creditoessencial.com.br
11S@ndr01003
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
    equipment_data = {
    'name': [], 'cpf_cnpj': [],
    'equipment_id': [], 'pdv': [], 'phone': [], 'email': [],
    'fantasy_name': [], 'branch_of_activity': [], 'cep': [],
    'street_name': [], 'address_number': [], 'address_complement': [], 'neighborhood_name': [],
    'city_name': [], 'state_name': [], 'status': []
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
                
                change_window('Equipamentos')
    
                # Espera até que os elementos estejam disponíveis
                max_retries = 5
                retries = 0
                while retries < max_retries:
                    try:
                        equipment_rows = driver.find_elements(By.XPATH, "//table[@id='tabelaPDV']/tbody/tr")
                        
                        if not equipment_rows:
                            break  # Nenhum equipamento encontrado, segue para o próximo cliente
    
                        for equipment_row in equipment_rows:
                            equipment_id = equipment_row.find_element(By.XPATH, ".//td[2]").text
                            pdv = equipment_row.find_element(By.XPATH, ".//td[1]").text
                            equipment_data['name'].append(name)
                            equipment_data['cpf_cnpj'].append(cpf_cnpj)
                            equipment_data['equipment_id'].append(equipment_id)
                            equipment_data['pdv'].append(pdv)
                            equipment_data['phone'].append(phone)
                            equipment_data['email'].append(email)
                            equipment_data['fantasy_name'].append(fantasy_name)
                            equipment_data['cep'].append(cep)
                            equipment_data['street_name'].append(street_name)
                            equipment_data['address_number'].append(address_number)
                            equipment_data['address_complement'].append(address_complement)
                            equipment_data['branch_of_activity'].append(branch_of_activity)
                            equipment_data['neighborhood_name'].append(neighborhood_name)
                            equipment_data['city_name'].append(city_name)
                            equipment_data['state_name'].append(state_name)
                            equipment_data['status'].append(status)

    
                        print(f'current_data: {equipment_data}')
    
                        break  # Sai do `while` se tudo der certo
    
                    except StaleElementReferenceException:
                        retries += 1
                        time.sleep(1)  # Tenta novamente após um pequeno delay
                
                i += 1
                change_window('Pesquisa')
                        
            except: 
                time.sleep(1)
                client_rows = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")
    
    
        # Verifica se o botão "Próximo" está desativado
        try:
            next_button_li = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "tabelaClientes_next"))
            )
            
            if 'disabled' in next_button_li.get_attribute('class'):
                print("Fim da paginação. Encerrando.")
                return equipment_data
                
            next_button = next_button_li.find_element(By.TAG_NAME, "a")
            page += 1
            next_button.click()
            time.sleep(1)
    
        except Exception as e:
            print(f"Erro ao clicar em 'Próximo': {e}")
            return equipment_data  # Sai do loop se houver erro na paginação

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
        


equipment_data_general = pd.read_csv('equipment_data_general.csv')

cpf_cnpj_df = pd.read_excel('Credito Essencial Clientes_ Transações.xlsx')
cpf_cnpj_data = cpf_cnpj_df['cpf/cnpj']

cpf_cnpj_equipment_data = []
for cpf_cnpj in cpf_cnpj_data:
    if cpf_cnpj not in equipment_data_general['cpf_cnpj'].values:
        search_by_cpf_cnpj(cpf_cnpj)
        user_data = loop_in_lines()  

        cpf_cnpj_equipment_data.append(user_data)
        
print(cpf_cnpj_equipment_data)
        
    
