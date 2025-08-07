import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

#transforma a imagem em matriz
def processarimagem(url):
    try:
        # carrega a imagem apartir do caminho dela
        img = Image.open(url)
        
        # redimensiona a imagem para 64px
        img = img.resize((64,64),Image.Resampling.LANCZOS)
        
        # converte para o modo rgb
        img = img.convert("RGB")

        #salvar os pixels para facilitar
        pixels = img.load()

        #defini a matriz dos pixels
        matrizpixels = []

        #atribuiçao dos pixels na matriz
        # y representa a altura e o x a largura
        for y in range(64):
            linha = [] # serve para guardar os dados da linha atual
            for x in range(64):
                #vai obter o valor do codigo rgb dos pixels
                r,g,b = pixels[x,y]
                #converte os valores para uma cor hexadecimal
                hexcor = f'#{r:02x}{g:02x}{b:02x}'
                linha.append(hexcor)
            matrizpixels.append(linha) # adiciona a linha completa a matriz
        return matrizpixels # retorna a matriz com todos os pixels

    except FileNotFoundError:
        # se o arquivo nao for possivel encontrar
        print("erro ao localizar arquvio")
        return None



#inicia o servidorchrome
def iniciar_servidor_temporario():
    """Inicia um servidor web temporário na porta 8000."""
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("localhost", 8000), handler)
    print("Servidor web iniciado em http://localhost:8000")
    threading.Thread(target=httpd.serve_forever).start()
    return httpd

# essa funçao controla o bot de desenho
def desenharimagem(matrizpronta,velocidade):
    
    httpd = iniciar_servidor_temporario()

    #verifica se a matriz tem algo
    if not matrizpronta:
        print("matriz vazia")
        # CORREÇÃO AQUI: Desliga o servidor se a matriz estiver vazia
        httpd.shutdown()
        print("Servidor web parado.")
        return

    try:
        #inicia o serviço do Chromedrive
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exeception as e:
        print("erro ao iniciar ChromeDRIVER")
        httpd.shutdown()
        print("servidor web parado")
        return
    

    # abre o arquivo html no navegador
    driver.get("http://localhost:8000/index.html")


    try:

        #espera ate 10 segundos para carrehar o primeiro pixel
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pixel[data-x='0'][data-y='0']")))

        
        #vai percorrer a matriz do desenho
        # y (linha) altura, x (coluna) largura
        for y in range(64):
            for x in range(64):
                #pega o valor de cada cor de pixel da matriz
                corpixel = matrizpronta[y][x]
                #bot vai executar o codigo javascript
                driver.execute_script(f"pintarPixel({x}, {y}, '{corpixel}')")

                #pausa para controlar a velocidade
                if velocidade >0:
                    time.sleep(velocidade)
                    
        print("desenho concluido")
        #mantem o navegador aberto por 5s
        time.sleep(5)

    except Exception as e:
        print("ocorreu um erro")
    finally:
        #fecha o navegador
        driver.quit()
        httpd.shutdown()
        print("Servidor web parado.")
