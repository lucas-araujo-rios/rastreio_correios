import time
import dotenv
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# traz o .env
dotenv.load_dotenv()

# define o driver e seus argumentos
chrome_options = Options()
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)

# função que somente retorn a atualização mais recente
def extrair_status_atual(codigo_rastreio):
    
    # abre chrome
    url = f"https://m.17track.net/pt/track-details?nums={codigo_rastreio}"
    driver.get(url)
    
    # obtem status atual
    status = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[4]/uni-view/uni-view[1]/uni-view[2]/uni-view[1]/uni-view[2]/uni-text[1]/span'))
        )
    status_text = status.text
    driver.quit()
    
    return status_text

def extrair_historico(codigo_rastreio):
    
    '''
    função para extrair o histórico de uma encomenda pelo 17track. o padrão do XPATH é:
    /html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[4]/uni-view/uni-view[{loc}]/uni-view[2]/uni-view[{pos}]/uni-view[2]/uni-text[{item}]/span

    loc=1 a mais recente
    loc=2 a mais antiga

    pos=1 é o tracks__event mais recente
    pos=2,3,...,N são os eventos seguintes

    tem=1 é o texto
    item=2 é a data
    '''
    
    # cria colunas vazias pra ir preenchendo
    data=[]
    status=[]
    
    # abre chrome
    url = f"https://m.17track.net/pt/track-details?nums={codigo_rastreio}"
    driver.get(url)
    
    # itera os elementos
    for loc in [1,2]:
        pos=1
        while True:
            try:
                status_i = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         f'/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[4]/uni-view/uni-view[{loc}]/uni-view[2]/uni-view[{pos}]/uni-view[2]/uni-text[1]/span'
                         )
                        )
                    )
                data_i = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         f'/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[4]/uni-view/uni-view[{loc}]/uni-view[2]/uni-view[{pos}]/uni-view[2]/uni-text[2]/span'
                         )
                        )
                    )
                status.append(status_i.text)
                data.append(data_i.text)
                # reporta progresso e continua o loop pelos itens
                print(status_i.text+" "+data_i.text)
                pos+=1
            except TimeoutException: # quer dizer que percorreu toda a lista 
                break
    # fecha o navegador e retorna a tabela com o historico
    driver.quit()
    historico = pd.DataFrame({'data':data,'status':status})
    return historico            

#def enviar_email(status_atual,log_status):

# exportar pra bruna
historico_bruna = extrair_historico('LI074746355KR')
historico_bruna.to_excel('historico_bruna.xlsx',index=False)

