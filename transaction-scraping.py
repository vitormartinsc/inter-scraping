from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Caminho para o ChromeDriver
service = Service("C://Users//servi//inter-scraping//chromedriver-win64//chromedriver-win64//chromedriver.exe")
chrome_profile_path = r'C:\Users\servi\AppData\Local\Google\Chrome\User Data\Default'

# Configuração das opções do Chrome
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile_path}")

# Inicializa o Chrome com as opções
driver = webdriver.Chrome(service=service, options=options)

# Acesse a página que contém a tabela
driver.get("URL_DA_PAGINA_COM_A_TABELA")  # Substitua pela URL correta

try:
    # Aguarde até que a tabela esteja presente
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tabelaClientes")))

    # Localiza a tabela
    tabela = driver.find_element(By.ID, "tabelaClientes")

    # Encontra todas as linhas da tabela
    linhas = driver.find_elements(By.XPATH, "//table[@id='tabelaClientes']/tbody/tr")

    # Clica em cada linha
    for linha in linhas:
        try:
            # Clica na primeira célula da linha
            celula = linha.find_element(By.TAG_NAME, "td")
            celula.click()
            # Aguarda um tempo para a ação ser concluída, se necessário
            WebDriverWait(driver, 10).until(EC.staleness_of(celula))  # Espera até que a célula não esteja mais disponível
            # Você pode querer fazer algo aqui após o clique, se necessário
        except Exception as e:
            print(f"Ocorreu um erro ao clicar na linha: {e}")

except Exception as e:
    print(f"Ocorreu um erro ao processar a tabela: {e}")

finally:
    # Fecha o navegador
    driver.quit()
