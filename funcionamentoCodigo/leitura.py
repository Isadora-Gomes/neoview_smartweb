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