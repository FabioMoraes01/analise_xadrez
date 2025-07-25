from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd
import sys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# === PREENCHA SEU USUÁRIO E SENHA AQUI ===
usuario = "seu usuario aqui"
senha = "sua senha aqui"


# === CONFIGURAÇÃO DO NAVEGADOR ===
options = Options()
options.add_argument("--start-maximized")  # Abre o navegador maximizado
driver = webdriver.Chrome(options=options)

# === ACESSA A PÁGINA DE LOGIN ===
url_login = "https://en.chessbase.com/login/true"
driver.get(url_login)

# Aguarda carregamento da página
time.sleep(5)

try:

    wait = WebDriverWait(driver, 15)
    # === LOCALIZA E PREENCHA OS CAMPOS DE LOGIN ===
    campo_usuario = driver.find_element(By.ID, "UID")
    campo_usuario.clear()
    campo_usuario.send_keys(usuario)

    campo_senha = driver.find_element(By.ID, "PWD")
    campo_senha.clear()
    campo_senha.send_keys(senha)

    # === CLICA NO BOTÃO DE LOGIN ===
    # botao_login = driver.find_element(By.CSS_SELECTOR, "input[type='submit'].cb-btn")
    # botao_login.click()
    botao_login = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[4]/div[1]/div/form/fieldset/div[2]/input")))
    botao_login.click()

    print("Login realizado com sucesso!")

except Exception as e:
    print("Erro ao tentar fazer login automaticamente.")
    print(f"Detalhes: {e}")

# Aguarda o redirecionamento após login
time.sleep(5)

    # === 4. ACESSA PÁGINA PRINCIPAL ===
# wait.until(EC.url_contains("account.chessbase.com/en/account"))  # espera redirecionamento
driver.get("https://en.chessbase.com/")
print("Acessando página principal...")

 # === 5. CLICA NO BOTÃO PARA ACESSAR BASE DE DADOS ===
link_bd = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cb-app-block-first"]/div[1]/a[2]/div/span')))
link_bd.click()
print("Redirecionando para ChessBase Database...")

# Aguarda a página da base carregar
time.sleep(5)

def buscar_partidas(driver, nome_jogador, ano_min, ano_max):
    print("Aguardando carregamento da página de busca...")
    wait = WebDriverWait(driver, 10)

   
      # Clica na caixa de pesquisa para ativar os filtros
    input_jogador = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//*[@id="search"]/form/div[1]/div[1]/input'
    )))
    input_jogador.click()

    # Aguarda o checkbox "Ignore color" estar presente
    checkbox_div = wait.until(EC.presence_of_element_located((
        By.XPATH, '//*[@id="search"]/form/div[2]/div[4]/div/div'
    )))

    # Marca o checkbox se ainda não estiver marcado
    class_name = checkbox_div.get_attribute("class")
    if "CBCheckBox_checked__23bO5" not in class_name:
        checkbox_div.click()
        print("Checkbox 'Ignore color' marcado.")
    else:
        print("Checkbox 'Ignore color' já estava marcado.")

    # Preenche o nome do jogador
    input_jogador = wait.until(EC.presence_of_element_located((
        By.XPATH, '//*[@id="search"]/form/div[1]/div[1]/input'
    )))
    input_jogador.clear()
    input_jogador.send_keys(nome_jogador)
    print(f"Nome do jogador preenchido: {nome_jogador}")

    # Preenche o ano mínimo
    input_ano_min = driver.find_element(By.XPATH, '//*[@id="yearmin"]')
    input_ano_min.clear()
    input_ano_min.send_keys(str(ano_min))
    print(f"Ano mínimo preenchido: {ano_min}")

    # Preenche o ano máximo
    input_ano_max = driver.find_element(By.XPATH, '//*[@id="yearmax"]')
    input_ano_max.clear()
    input_ano_max.send_keys(str(ano_max))
    print(f"Ano máximo preenchido: {ano_max}")

    # Clica no botão de busca
    botao_buscar = driver.find_element(By.XPATH, '//*[@id="SearchIcon"]')
    botao_buscar.click()
    print("Busca iniciada.")


def extrair_partidas_como_dataframe(driver):
    print("Iniciando extração com scroll manual...")

   
    body = driver.find_element(By.XPATH, '//*[@id="search"]/div[2]')
    dados = []
    linhas_vistas = set()
    max_tentativas = 20
    tentativas = 0
    last_count = -1

    while tentativas < max_tentativas:
        linhas = driver.find_elements(By.XPATH, '//*[@id="search"]/div[2]/div[contains(@class,"CBTable_bodyRow__1rd1f")]')

        # Clica em cada nova linha que ainda não foi clicada
        for idx, linha in enumerate(linhas):
            if idx not in linhas_vistas:
                try:
                    linha.click()
                    linhas_vistas.add(idx)
                    time.sleep(0.1)
                except:
                    pass  # Caso a linha esteja fora da tela ou não clicável ainda

        if len(linhas) == last_count:
            tentativas += 1
        else:
            tentativas = 0

        last_count = len(linhas)
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1.2)

    print(f"Scroll finalizado. Total de linhas carregadas: {len(linhas)}")
    
    # Coleta os dados após scroll completo
    linhas = driver.find_elements(By.XPATH, '//*[@id="search"]/div[2]/div[contains(@class,"CBTable_bodyRow__1rd1f")]')
    for linha in linhas:
        colunas = linha.find_elements(By.CLASS_NAME, "CBTable_cellInner__1Kv5J")
        dados.append([col.text for col in colunas])

    colunas_nomes = ["year", "white", "white_elo", "black", "black_elo", "result", "eco", "moves"]
    df = pd.DataFrame(dados, columns=colunas_nomes[:len(dados[0])])
    

    df = pd.DataFrame(dados, columns=colunas_nomes[:len(dados[0])])
    print(df)

    # Salva em CSV
    df.to_csv(r"D:\Projetos\analise_xadrez\Data\Gukesh.csv", index=False, encoding='utf-8-sig')
    print("Arquivo CSV salvo com sucesso!")

    return df

# === CHAMADA DA FUNÇÃO COM PARÂMETROS DESEJADOS ===
buscar_partidas(driver, nome_jogador="Gukesh", ano_min=2024, ano_max=2024)
time.sleep(10)
extrair_partidas_como_dataframe(driver)

driver.quit()
sys.exit()

