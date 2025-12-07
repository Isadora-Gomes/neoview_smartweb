import cv2
from collections import defaultdict
from gtts import gTTS
import pygame
import io
import warnings
import time
import numpy as np
from funcionamentoCodigo.camera.camera import Camera
from ultralytics import YOLO

warnings.simplefilter(action='ignore', category=FutureWarning)
pygame.mixer.init()

CONFIANCA_MINIMA = 0.44


class TraducaoEgenero:
    def __init__(self):
        self.traducao = {
            'person': 'pessoa', 'bicycle': 'bicicleta', 'car': 'carro', 'motorcycle': 'moto',
            'airplane': 'avião', 'bus': 'ônibus', 'train': 'trem', 'truck': 'caminhão', 'boat': 'barco',
            'traffic light': 'semáforo', 'fire hydrant': 'hidrante', 'stop sign': 'placa de pare',
            'parking meter': 'parquímetro', 'bench': 'banco', 'bird': 'pássaro', 'cat': 'gato',
            'dog': 'cachorro', 'horse': 'cavalo', 'sheep': 'ovelha', 'cow': 'vaca', 'bed': 'cama'
        }
        self.genero = {
            'person': 'f', 'bicycle': 'f', 'car': 'm', 'motorcycle': 'f',
            'airplane': 'm', 'bus': 'm', 'train': 'm', 'truck': 'm', 'boat': 'm',
            'traffic light': 'm', 'fire hydrant': 'm', 'stop sign': 'f',
            'parking meter': 'm', 'bench': 'm', 'bird': 'm', 'cat': 'm',
            'dog': 'm', 'horse': 'm', 'sheep': 'f', 'cow': 'f'
        }

    def traduzir(self, nome):
        return self.traducao.get(nome, nome)

    def genero_objeto(self, nome):
        return self.genero.get(nome, 'm')


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


class DetectorObjetos:
    def __init__(self, confianca=CONFIANCA_MINIMA):
        self.model = YOLO("yolov8n.pt")
        self.confianca = confianca
        self.obj_traducao = TraducaoEgenero()

    def detectar(self, frame):
        results = self.model.predict(source=frame, conf=self.confianca, verbose=False)
        detections = results[0].boxes
        contagem = defaultdict(int)
        for box in detections:
            nome = self.model.names[int(box.cls)]
            contagem[nome] += 1
        annotated_frame = results[0].plot()
        return contagem, annotated_frame

    def gerar_frase(self, contagem):
        if not contagem:
            return "Nenhum objeto encontrado"
        frases = []
        for nome, qtd in contagem.items():
            nome_pt = self.obj_traducao.traduzir(nome)
            gen = self.obj_traducao.genero_objeto(nome)
            if qtd == 1:
                artigo = 'uma' if gen == 'f' else 'um'
                verbo = 'detectada' if gen == 'f' else 'detectado'
            else:
                artigo = str(qtd)
                verbo = 'detectadas' if gen == 'f' else 'detectados'
            frases.append(f"{artigo} {nome_pt} {verbo}")
        return ", ".join(frases)


class Aplicacao:
    def __init__(self):
        self.url = "http://192.168.1.100:81/stream"
        self.detector = DetectorObjetos()

    def executar(self):
        time.sleep(2)
        camera = Camera(self.url)
        try:
            print("Executando detecção de objetos...")
            frame = camera.ler_frame()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (640, 480))
            contagem, annotated = self.detector.detectar(frame_rgb)
            frase = self.detector.gerar_frase(contagem)
            print("---> " + frase)
            Voz.falar(frase)
            cv2.imshow("ESP32-CAM - Detecção", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
            cv2.waitKey(2000)
        finally:
            camera.liberar()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    app = Aplicacao()
    app.executar()