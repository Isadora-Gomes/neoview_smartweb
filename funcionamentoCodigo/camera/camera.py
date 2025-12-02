import cv2
import time

class Camera:
    def __init__(self, url: str):
        self.url = url
        self.cap = cv2.VideoCapture(url)
        if not self.cap.isOpened():
            raise Exception(f"Não foi possível abrir a câmera no URL: {url}")
        
    def ler_frame(self):
        for _ in range(5):  # descarta frames antigos para exibir a imagem atual
            ret, frame = self.cap.read()
            if ret:
                return frame
            time.sleep(0.1)  # espera um pouco antes de tentar novamente
        raise RuntimeError("Não foi possível capturar o frame da câmera após várias tentativas.")
    
    def liberar(self):
        self.cap.release()