import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para configurar o Chrome WebDriver
def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Função para realizar o scraping e gerar os comandos SQL
def fazer_scraping(url):
    driver = configurar_driver()
    driver.get(url)

    # Espera o carregamento da página
    driver.implicitly_wait(10)

    # Clica no botão para abrir a tabela completa
    try:
        button = driver.find_element(By.XPATH, "//button[contains(text(),'Ver tabela completa')]")
        button.click()
        time.sleep(5)
    except Exception as e:
        logging.error(f"Erro ao clicar no botão: {e}")
        return

    # Agora capturamos a tabela de dados
    try:
        tabela = driver.find_element(By.XPATH, "//table")
        rows = tabela.find_elements(By.TAG_NAME, "tr")

        comandos_sql = []
        dados = []

        for row in rows[1:]:  # Ignorando o cabeçalho
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) > 1:
                ano_mes = cols[0].text.strip()
                indice = cols[1].text.strip()
                valor = cols[2].text.strip()

                # Gerar o comando SQL
                comando_sql = f"""
                    INSERT INTO indices_financeiros (id, indice, valor, data)
                    VALUES ('{ano_mes}', '{indice}', '{valor}', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
                    ON DUPLICATE KEY UPDATE
                    indice = '{indice}', valor = '{valor}', data = '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}';
                """
                comandos_sql.append(comando_sql)
                dados.append({"ano_mes": ano_mes, "indice": indice, "valor": valor})

                logging.info(f"Comando SQL gerado: {comando_sql}")

        # Retornar os dados em formato JSON e os comandos SQL
        driver.quit()
        return {
            "data": dados,
            "sql_commands": comandos_sql
        }
    except Exception as e:
        logging.error(f"Erro ao capturar a tabela: {e}")
        driver.quit()
        return

# URLs para scraping
urls = [
    "https://www.debit.com.br/tabelas/igpm-fgv-indice-geral-de-precos-mercado",
    "https://www.debit.com.br/tabelas/ipca-indice-nacional-de-precos-ao-consumidor-amplo",
    "https://www.debit.com.br/tabelas/ipcae-indice-de-precos-ao-consumidor-amplo-especial",
    "https://www.debit.com.br/tabelas/ipc-indice-de-precos-ao-consumidor-fgv",
    "https://www.debit.com.br/tabelas/inpc-indice-nacional-de-precos-ao-consumidor",
    "https://www.debit.com.br/tabelas/igp-fgv-indice-geral-de-precos"
]

# Realizando o scraping e gerando os comandos para cada URL
for url in urls:
    logging.info(f"Iniciando o scraping para a URL: {url}")
    resultado = fazer_scraping(url)

    if resultado:
        # Exibindo os resultados
        print(f"Resultado do Scraping e Comandos SQL Gerados para {url}:")
        print(resultado["data"])  # Dados em formato JSON
        print("\nComandos SQL Gerados:")
        for comando in resultado["sql_commands"]:
            print(comando)
