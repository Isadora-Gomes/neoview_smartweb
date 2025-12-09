from pisotatil import *
import time
from funcionamentoCodigo.camera.camera import Camera
import cv2
import pygame
from gtts import gTTS
import io
import numpy as np

class Voz:
    @staticmethod
    def falar(texto):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

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

class Aplicacao:
    def __init__(self):
        self.url = "http://192.168.1.100:81/stream"
        self.mapeador = PisoTatilDeteccao()

    def executar(self):
        time.sleep(2)
        camera = Camera(self.url)
        try:
            print("Executando leitura de texto...")
            frame = camera.ler_frame()
            resultado = self.mapeador.mapear(frame)
            mapeamento = resultado.mapa
            print("\nMapa da imagem:")
            show_matrix = np.full(mapeamento.shape, fill_value=" ", dtype=str)
            
            for i in range(mapeamento.shape[0]):
                for j in range(mapeamento.shape[1]):
                    cell = mapeamento[i,j]
                    
                    if cell is not None:
                        show_matrix[i,j] = icone_para_piso( cell.classe )
            
            print("\nMapa do piso tátil:")
            for row in show_matrix:
                print(" ".join(row))

            print("\nDescrição do mapa:")
            print(f" - {resultado.leitura}")

            Voz.falar(resultado.leitura)
            cv2.imshow("ESP32-CAM - Leitura", frame)
            cv2.waitKey(2000)
        finally:
            camera.liberar()
            cv2.destroyAllWindows()


def icone_para_piso(tipo_piso: PisoTatil):
    if tipo_piso == PisoTatil.horizontal:
        return "—"
    elif tipo_piso == PisoTatil.vertical:
        return "|"
    elif tipo_piso == PisoTatil.alerta:
        return "•"
    else:
        return "?"