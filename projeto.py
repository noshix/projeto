import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from bot import processarimagem,desenharimagem

#classe que gerencia a interface do bot
class App:
    def __init__(self,root):
        self.root = root
        self.root.title("Bot de Desenho")
        self.root.geometry("400x200")

        #variavel q armazena o caminho do arquivo de imagem selecionada
        self.caminho_imagem = ""

        #cria o rotulo para mostrar o caminho do arquivo selecionado
        self.label_caminho = tk.Label(root, text="Nenhuma imagem selecionada", wraplength=350)
        self.label_caminho.pack(pady=(10,0))
        

        self.label_velocidade = tk.Label(root, text="Velocidade (segundos por pixel): 0.0")
        self.label_velocidade.pack(pady=(5, 0))

        self.scale_velocidade = tk.Scale(
            root,
            from_=0.0,
            to=0.5,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.atualizar_label_velocidade
        )
        self.scale_velocidade.set(0.0)
        self.scale_velocidade.pack(pady=5)

        #cria um frama para agrupar os botoes
        frame = tk.Frame(root)
        frame.pack()

        #cria o botao de selecionar imagem
        self.btn_selecionar= tk.Button(frame , text="Selecionar Imagem", command=self.selecionarimagem)
        self.btn_selecionar.pack(side=tk.LEFT,padx=5)

        #cria o botao iniciar desenho que começa desativado
        self.btn_iniciar = tk.Button(frame, text="Iniciar Desenho", command=self.iniciardesenho,state=tk.DISABLED)
        self.btn_iniciar.pack(side=tk.LEFT,padx=5)


    def selecionarimagem(self):
        #abre um janela de dialogo para o user selecionar a imagem
        self.caminho_imagem = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=(("Arquivos de Imagem", "*.png;*.jpg;*.jpeg"),("Todo os arquivos","*.*"))
            )
        #se um arquivo foi selecionado
        if self.caminho_imagem:
            self.label_caminho.config(text=f"Imagem selecionada: {self.caminho_imagem}")
            self.btn_iniciar.config(state=tk.NORMAL) #ativa o botao de iniciar
        else:
            #se a seleçao foi cancelada reseta o estado
            self.label_caminho.config(text="Nenhuma imagem selecionada")
            self.btn_iniciar.config(state=tk.DISABLED)
    
    def iniciardesenho(self):
        #funçao chamada ao clicar em iniciar desenho
        if not self.caminho_imagem:
            messagebox.showwarning("Aviso","selecione a imagem primeiro")
            return

        self.label_caminho.config(text="Iniciando desenho...")
        self.btn_iniciar.config(state=tk.DISABLED)
        
        #obtem o valor da velocidade do controle deslizante
        velocidade= self.scale_velocidade.get()
        
        #inicia o bot em outra thread
        threading.Thread(target=self.executarbot,args=(velocidade,)).start()

    def executarbot(self,velocidade):
        #executa a logico do bot
        try:
            velocidade = 0.5 - velocidade
            #chama a funcao de processar a imagem
            matrizpronta = processarimagem(self.caminho_imagem)
            #testa se a matriz feita é valida
            if matrizpronta:
                desenharimagem(matrizpronta,velocidade)
                self.label_caminho.config(text="Desenho concluido, selecione outra imagem")
            else:
                self.label_caminho.config(text="falha ao processar a imagem. tente novamente")
        except Exception as e:
            messagebox.showerror("Erro", f"ocorreu um erro:{e}")
        finally:
            #reativa o botao de iniciar
            self.btn_iniciar.config(state=tk.NORMAL)

    #funçao que controla a velocidade
    def atualizar_label_velocidade(self,valor):
        self.label_velocidade.config(text=f"Velocidade (segundos por pixel): {float(valor):.2f}")

if __name__ =="__main__":
    #cria a janela principal do Tkinter e inicia o loop
    root = tk.Tk()
    app = App(root)
    root.mainloop()
            
        
        
        
