import cv2
import time

class Camera:
    def __init__(self, url: str):
        self.url = url
        self.cap = cv2.VideoCapture(url)
        time.sleep(2)
        if not self.cap.isOpened():
            raise Exception(f"Não foi possível abrir a câmera no URL: {url}")
        
    def ler_frame(self):
        # Descarta vários frames antigos do buffer para garantir que pega o mais recente
        for _ in range(10):
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Não foi possível capturar o frame da câmera.")
        return frame
    
    def liberar(self):
        self.cap.release()