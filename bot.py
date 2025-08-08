import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import functools

# Uma paleta de 16 cores em formato RGB
Paletacores = [
    (0, 0, 0),         # Preto
    (255, 255, 255),   # Branco
    (255, 0, 0),       # Vermelho
    (0, 255, 0),       # Verde
    (0, 0, 255),       # Azul
    (255, 255, 0),     # Amarelo
    (0, 255, 255),     # Ciano
    (255, 0, 255),     # Magenta
    (192, 192, 192),   # Cinza Claro
    (128, 128, 128),   # Cinza
    (128, 0, 0),       # Marrom
    (128, 128, 0),     # Oliva
    (0, 128, 0),       # Verde Escuro
    (128, 0, 128),     # Púrpura
    (0, 128, 128),     # Teal
    (0, 0, 128)        # Azul Marinho
]

#encontar a cor pela distancia euclidiana
def encontrarcor(cororiginal,paleta):
    r_orig,g_orig,b_orig = cororiginal
    corproxima = None
    menordistancia = float('inf')

    for r_pal, g_pal, b_pal in paleta:
        distancia = (r_orig - r_pal)**2 + (g_orig - g_pal)**2 + (b_orig - b_pal)**2

        if distancia < menordistancia:
            menordistancia = distancia
            corproxima = (r_pal,g_pal,b_pal)
    return corproxima

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
                cormapeada = encontrarcor((r,g,b),Paletacores)
                #gera o codigo hexa das cores
                r_map , g_map, b_map = cormapeada
                hexacor = f'#{r_map:02x}{g_map:02x}{b_map:02x}'
                linha.append(hexacor)
            matrizpixels.append(linha) # adiciona a linha completa a matriz
        return matrizpixels # retorna a matriz com todos os pixels

    except FileNotFoundError:
        # se o arquivo nao for possivel encontrar
        print("erro ao localizar arquvio")
        return None



#inicia o servidorchrome
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import functools

def iniciar_servidor_temporario():
    # Detecta o caminho base da mesma forma que antes
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Verifica se a pasta 'data' existe e usa-a, se sim
    data_path = os.path.join(base_path, 'data')
    if os.path.exists(data_path):
        server_path = data_path
    else:
        server_path = base_path
    
    # Cria uma classe de handler que serve os arquivos do server_path
    class MyHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=server_path, **kwargs)

    # Inicia o servidor com a nossa classe personalizada
    httpd = HTTPServer(("localhost", 8000), MyHandler)
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
    except Exception as e:
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
