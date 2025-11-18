import cv2
import easyocr
import warnings
from gtts import gTTS
import pygame
import io
import time
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)

pygame.mixer.init()

class Voz:
    @staticmethod
    def falar(texto: str) -> None:
        try:
            mp3_fp = io.BytesIO()
            tts = gTTS(texto, lang='pt-br')
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            pygame.mixer.music.load(mp3_fp, 'mp3')
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Erro ao reproduzir áudio: {e}")

class LeitorTexto:
    def __init__(self, lang="pt"):
        self.reader = easyocr.Reader([lang], gpu=False)

    def ler_texto(self, frame: np.ndarray) -> str:
        results = self.reader.readtext(frame)
        textos = [res[1] for res in results]
        return " ".join(textos) if textos else "Nenhum texto encontrado"

class Aplicacao:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.leitor = LeitorTexto()

    def preview(self):
        print("Pressione ESC para sair da pré-visualização")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            cv2.imshow("Pré-visualização (ESC para sair)", frame)
            if cv2.waitKey(1) & 0xFF == 27: 
                break

        cv2.destroyAllWindows()

    def executar(self):
        try:
            while True:
                print("\n--- MENU ---")
                print("1 - Ler texto")
                opcao = input("--> ")

                if opcao == "1":
                    ret, frame = self.cap.read()
                    if ret:
                        texto = self.leitor.ler_texto(frame)
                        print("\nTexto detectado:", texto)
                        if texto != "Nenhum texto encontrado":
                            print("Reproduzindo áudio...")
                            Voz.falar(texto)
                        else:
                            print("Nenhum texto para reproduzir em áudio.")

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            pygame.mixer.quit()


if __name__ == "__main__":
    app = Aplicacao()
    app.executar()


# import cv2
# import torch
# import time
# import threading
# from collections import defaultdict
# from ultralytics import YOLO  # YOLOv8, mais rápido
# from gtts import gTTS
# import pygame
# import io
# import numpy as np
# import warnings

# warnings.filterwarnings("ignore", category=FutureWarning)

# pygame.mixer.init()
# CONFIANCA_MINIMA = 0.55


# class TraducaoEgenero:
#     def __init__(self):
#         self.traducao = {"person": "pessoa", "car": "carro", "dog": "cachorro"}
#         self.genero = {"person": "f", "car": "m", "dog": "m"}

#     def traduzir(self, nome: str) -> str:
#         return self.traducao.get(nome, nome)

#     def genero_objeto(self, nome: str) -> str:
#         return self.genero.get(nome, "m")


# class Voz:
#     @staticmethod
#     def falar(texto: str) -> None:
#         def _executar():
#             mp3_fp = io.BytesIO()
#             tts = gTTS(texto, lang="pt")
#             tts.write_to_fp(mp3_fp)
#             mp3_fp.seek(0)
#             pygame.mixer.music.load(mp3_fp, "mp3")
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)

#         # Fala em thread separada, sem travar o programa
#         threading.Thread(target=_executar, daemon=True).start()


# class DetectorObjetos:
#     def __init__(self, confianca=CONFIANCA_MINIMA):
#         self.model = YOLO("yolov8n.pt")  # modelo leve e rápido
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.model.to(self.device)
#         self.confianca = confianca
#         self.obj_traducao = TraducaoEgenero()

#     def detectar(self, frame: np.ndarray) -> dict:
#         # reduz resolução para acelerar
#         small_frame = cv2.resize(frame, (640, 480))
#         results = self.model.predict(small_frame, verbose=False, conf=self.confianca)
#         contagem = defaultdict(int)
#         for box in results[0].boxes:
#             nome = self.model.names[int(box.cls)]
#             contagem[nome] += 1
#         return contagem

#     def gerar_frase(self, contagem: dict[str, int]) -> str:
#         if not contagem:
#             return "Nenhum objeto encontrado"
#         frases = []
#         for nome, qtd in contagem.items():
#             nome_pt = self.obj_traducao.traduzir(nome)
#             gen = self.obj_traducao.genero_objeto(nome)
#             artigo = "uma" if gen == "f" else "um" if qtd == 1 else str(qtd)
#             verbo = "detectada" if gen == "f" else "detectado"
#             frases.append(f"{artigo} {nome_pt} {verbo}")
#         return ", ".join(frases)


# class Aplicacao:
#     def __init__(self):
#         self.cap = cv2.VideoCapture(0)
#         self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#         self.detector = DetectorObjetos()

#     def executar(self):
#         try:
#             while True:
#                 ret, frame = self.cap.read()
#                 if not ret:
#                     continue

#                 contagem = self.detector.detectar(frame)
#                 frase = self.detector.gerar_frase(contagem)
#                 print("--->", frase)
#                 Voz.falar(frase)

#                 cv2.imshow("Detecção", frame)
#                 if cv2.waitKey(1) & 0xFF == ord("q"):
#                     break

#         finally:
#             self.cap.release()
#             cv2.destroyAllWindows()
#             pygame.mixer.quit()


# if __name__ == "__main__":
#     app = Aplicacao()
#     app.executar()