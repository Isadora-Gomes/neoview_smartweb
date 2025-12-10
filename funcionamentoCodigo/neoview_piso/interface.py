#!/usr/bin/env python3
"""
Interface Gráfica para Detecção e Mapeamento de Piso Tátil
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import cv2
import numpy as np
from pathlib import Path
import threading
from pisotatil.detection.piso_tatil import PisoTatilDeteccao
from pisotatil.detection.tipos import PisoTatil


class PisoTatilInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoView Piso - Detecção de Pisos Táteis")
        self.root.geometry("1200x800")
        
        # Variáveis
        self.imagem_original = None
        self.imagem_resultado = None
        self.detector = None
        self.caminho_imagem = None
        
        # Configurar detector
        self.configurar_detector()
        
        # Criar interface
        self.criar_interface()
        
    def configurar_detector(self):
        """Configura o detector de piso tátil"""
        try:
            self.detector = PisoTatilDeteccao(debug=True)
            if self.detector.use_yolo and self.detector.yolo_detector:
                self.status_detector = "YOLO Carregado"
            else:
                self.status_detector = "YOLO não disponível - Verifique modelo em models/"
        except Exception as e:
            self.status_detector = f"Erro: {str(e)}"
            
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Detecção e Mapeamento de Piso Tátil", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status do detector
        self.label_status = ttk.Label(main_frame, text=self.status_detector)
        self.label_status.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controles_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        controles_frame.columnconfigure(0, weight=1)
        
        # Botão para carregar imagem
        self.btn_carregar = ttk.Button(controles_frame, text="Carregar Imagem", 
                                      command=self.carregar_imagem)
        self.btn_carregar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Label da imagem selecionada
        self.label_imagem = ttk.Label(controles_frame, text="Nenhuma imagem selecionada", 
                                     foreground="gray")
        self.label_imagem.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Separador
        ttk.Separator(controles_frame, orient='horizontal').grid(row=2, column=0, 
                                                               sticky=(tk.W, tk.E), pady=10)
        
        # Botões de ação
        self.btn_detectar = ttk.Button(controles_frame, text="Detectar Piso Tátil", 
                                      command=self.detectar_piso, state="disabled")
        self.btn_detectar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.btn_mapear = ttk.Button(controles_frame, text="Mapear Ambiente", 
                                    command=self.mapear_ambiente, state="disabled")
        self.btn_mapear.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(controles_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Frame de resultados (área scrollável)
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        resultados_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        resultados_frame.columnconfigure(0, weight=1)
        resultados_frame.rowconfigure(1, weight=1)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(resultados_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba 1: Imagens
        self.frame_imagens = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_imagens, text="Imagens")
        self.criar_aba_imagens()
        
        # Aba 2: Mapa
        self.frame_mapa = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_mapa, text="Mapa")
        self.criar_aba_mapa()
        
        # Aba 3: Log
        self.frame_log = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_log, text="Log")
        self.criar_aba_log()
        
    def criar_aba_imagens(self):
        """Cria a aba de visualização de imagens"""
        self.frame_imagens.columnconfigure(0, weight=1)
        self.frame_imagens.columnconfigure(1, weight=1)
        self.frame_imagens.rowconfigure(1, weight=1)
        
        # Labels das imagens
        ttk.Label(self.frame_imagens, text="Imagem Original", font=("Arial", 10, "bold")).grid(
            row=0, column=0, pady=5)
        ttk.Label(self.frame_imagens, text="Resultado da Detecção", font=("Arial", 10, "bold")).grid(
            row=0, column=1, pady=5)
        
        # Canvas para imagens
        self.canvas_original = tk.Canvas(self.frame_imagens, bg="lightgray", width=300, height=300)
        self.canvas_original.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas_resultado = tk.Canvas(self.frame_imagens, bg="lightgray", width=300, height=300)
        self.canvas_resultado.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def criar_aba_mapa(self):
        """Cria a aba de visualização do mapa"""
        self.frame_mapa.columnconfigure(0, weight=1)
        self.frame_mapa.rowconfigure(0, weight=1)
        self.frame_mapa.rowconfigure(1, weight=1)
        
        # Área do mapa (matriz visual)
        mapa_label_frame = ttk.LabelFrame(self.frame_mapa, text="Mapa 2D", padding="10")
        mapa_label_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        mapa_label_frame.columnconfigure(0, weight=1)
        mapa_label_frame.rowconfigure(0, weight=1)
        
        self.texto_mapa = scrolledtext.ScrolledText(mapa_label_frame, height=15, 
                                                   font=("Courier New", 10))
        self.texto_mapa.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Área da descrição
        desc_label_frame = ttk.LabelFrame(self.frame_mapa, text="Descrição do Caminho", padding="10")
        desc_label_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        desc_label_frame.columnconfigure(0, weight=1)
        desc_label_frame.rowconfigure(0, weight=1)
        
        self.texto_descricao = scrolledtext.ScrolledText(desc_label_frame, height=8, 
                                                        font=("Arial", 10), wrap=tk.WORD)
        self.texto_descricao.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def criar_aba_log(self):
        """Cria a aba de log"""
        self.frame_log.columnconfigure(0, weight=1)
        self.frame_log.rowconfigure(0, weight=1)
        
        self.texto_log = scrolledtext.ScrolledText(self.frame_log, font=("Courier New", 9))
        self.texto_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.texto_log.insert(tk.END, f"{mensagem}\n")
        self.texto_log.see(tk.END)
        self.root.update_idletasks()
        
    def carregar_imagem(self):
        """Carrega uma imagem do sistema"""
        filetypes = (
            ('Imagens', '*.jpg *.jpeg *.png *.bmp *.tiff'),
            ('Todos os arquivos', '*.*')
        )
        
        caminho = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=filetypes
        )
        
        if caminho:
            try:
                self.caminho_imagem = Path(caminho)
                self.imagem_original = cv2.imread(str(caminho))
                
                if self.imagem_original is None:
                    raise ValueError("Não foi possível carregar a imagem")
                
                # Atualizar interface
                self.label_imagem.config(text=f"{self.caminho_imagem.name}", foreground="black")
                self.btn_detectar.config(state="normal")
                self.btn_mapear.config(state="normal")
                
                # Mostrar imagem original
                self.mostrar_imagem(self.canvas_original, self.imagem_original)
                
                # Limpar resultados anteriores
                self.limpar_resultados()
                
                self.log(f"   Imagem carregada: {self.caminho_imagem.name}")
                self.log(f"   Dimensões: {self.imagem_original.shape[1]}x{self.imagem_original.shape[0]} pixels")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar imagem:\n{str(e)}")
                self.log(f" Erro ao carregar imagem: {str(e)}")
                
    def mostrar_imagem(self, canvas, imagem_cv):
        """Mostra uma imagem OpenCV no canvas"""
        if imagem_cv is None:
            return
            
        # Converter BGR para RGB
        imagem_rgb = cv2.cvtColor(imagem_cv, cv2.COLOR_BGR2RGB)
        
        # Redimensionar para caber no canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas.update()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
        if canvas_width <= 1:
            canvas_width = 300
        if canvas_height <= 1:
            canvas_height = 300
            
        h, w = imagem_rgb.shape[:2]
        aspect_ratio = w / h
        
        if w > h:
            new_width = min(canvas_width - 20, w)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(canvas_height - 20, h)
            new_width = int(new_height * aspect_ratio)
            
        imagem_redim = cv2.resize(imagem_rgb, (new_width, new_height))
        
        # Converter para PIL e depois para PhotoImage
        imagem_pil = Image.fromarray(imagem_redim)
        imagem_tk = ImageTk.PhotoImage(imagem_pil)
        
        # Mostrar no canvas
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, image=imagem_tk, anchor="center")
        
        # Manter referência para evitar garbage collection
        canvas.image = imagem_tk
        
    def limpar_resultados(self):
        """Limpa os resultados anteriores"""
        self.canvas_resultado.delete("all")
        self.texto_mapa.delete(1.0, tk.END)
        self.texto_descricao.delete(1.0, tk.END)
        
    def detectar_piso(self):
        """Executa detecção de piso tátil"""
        if not self.detector or not self.imagem_original is not None:
            return
            
        def executar_deteccao():
            try:
                self.progress.start()
                self.btn_detectar.config(state="disabled")
                self.btn_mapear.config(state="disabled")
                
                self.log("🔍 Iniciando detecção de piso tátil...")
                
                if not self.detector.use_yolo or not self.detector.yolo_detector:
                    self.log(" YOLO não disponível - Verifique se o modelo está instalado")
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Aviso", "Detector YOLO não disponível.\nVerifique se existe modelo em models/"))
                    return
                
                # Executar detecção
                resultado_frame = self.detector.detectar_piso_tatil(self.imagem_original)
                
                if resultado_frame is not None:
                    self.imagem_resultado = resultado_frame
                    self.log(" Piso tátil detectado!")
                    
                    # Mostrar resultado na interface
                    self.root.after(0, lambda: self.mostrar_imagem(self.canvas_resultado, resultado_frame))
                    self.root.after(0, lambda: self.notebook.select(0))  # Ir para aba de imagens
                    
                else:
                    self.log(" Nenhum piso tátil detectado")
                    self.root.after(0, lambda: messagebox.showinfo("Resultado", "Nenhum piso tátil detectado na imagem"))
                    
            except Exception as e:
                self.log(f" Erro na detecção: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na detecção:\n{str(e)}"))
            finally:
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.btn_detectar.config(state="normal"))
                self.root.after(0, lambda: self.btn_mapear.config(state="normal"))
                
        # Executar em thread separada
        thread = threading.Thread(target=executar_deteccao, daemon=True)
        thread.start()
        
    def mapear_ambiente(self):
        """Executa mapeamento do ambiente"""
        if not self.detector or not self.imagem_original is not None:
            return
            
        def executar_mapeamento():
            try:
                self.progress.start()
                self.btn_detectar.config(state="disabled")
                self.btn_mapear.config(state="disabled")
                
                self.log(" Iniciando mapeamento do ambiente...")
                
                if not self.detector.use_yolo or not self.detector.yolo_detector:
                    self.log(" YOLO não disponível - Mapeamento requer detector YOLO")
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Aviso", "Mapeamento requer detector YOLO.\nVerifique se existe modelo em models/"))
                    return
                
                # Executar mapeamento
                resultado = self.detector.mapear(self.imagem_original)
                mapeamento = resultado.mapa
                descricao = resultado.leitura
                
                self.log(" Mapeamento concluído!")
                
                # Mostrar mapa na interface
                def atualizar_mapa():
                    # Limpar áreas
                    self.texto_mapa.delete(1.0, tk.END)
                    self.texto_descricao.delete(1.0, tk.END)
                    
                    if mapeamento is not None:
                        # Criar matriz visual
                        show_matrix = np.full(mapeamento.shape, fill_value=" ", dtype=str)
                        
                        def icone_para_piso(tipo_piso):
                            if tipo_piso == PisoTatil.horizontal:
                                return "—"
                            elif tipo_piso == PisoTatil.vertical:
                                return "|"
                            elif tipo_piso == PisoTatil.alerta:
                                return "•"
                            else:
                                return "?"
                        
                        for i in range(mapeamento.shape[0]):
                            for j in range(mapeamento.shape[1]):
                                cell = mapeamento[i, j]
                                if cell is not None:
                                    show_matrix[i, j] = icone_para_piso(cell.classe)
                        
                        # Mostrar legenda
                        legenda = (
                            "LEGENDA:\n"
                            "  —  = Piso horizontal\n"
                            "  |  = Piso vertical\n"
                            "  •  = Piso de alerta\n"
                            "     = Vazio\n\n"
                            "MAPA:\n"
                        )
                        self.texto_mapa.insert(tk.END, legenda)
                        
                        # Mostrar matriz
                        for row in show_matrix:
                            self.texto_mapa.insert(tk.END, " ".join(row) + "\n")
                            
                        # Mostrar descrição
                        self.texto_descricao.insert(tk.END, descricao)
                        
                        # Ir para aba do mapa
                        self.notebook.select(1)
                        
                    else:
                        self.texto_mapa.insert(tk.END, "Nenhum mapa gerado.")
                        self.texto_descricao.insert(tk.END, "Nenhum piso tátil identificado.")
                
                self.root.after(0, atualizar_mapa)
                
            except Exception as e:
                self.log(f" Erro no mapeamento: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro no mapeamento:\n{str(e)}"))
            finally:
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.btn_detectar.config(state="normal"))
                self.root.after(0, lambda: self.btn_mapear.config(state="normal"))
                
        # Executar em thread separada
        thread = threading.Thread(target=executar_mapeamento, daemon=True)
        thread.start()


def main():
    """Função principal"""
    root = tk.Tk()
    app = PisoTatilInterface(root)
    root.mainloop()


if __name__ == "__main__":
    main()