"""
Utilitários para o projeto de detecção de pisos táteis.
"""

import cv2
import numpy as np
from typing import Tuple, List
import os
import json
from pathlib import Path


def redimensionar_frame(frame: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    """
    Redimensiona frame mantendo proporção.
    
    Args:
        frame: Frame original
        width: Largura desejada
        height: Altura desejada
        
    Returns:
        Frame redimensionado
    """
    h, w = frame.shape[:2]
    
    if width is None and height is None:
        return frame
    
    if width is None:
        aspect = height / h
        width = int(w * aspect)
    elif height is None:
        aspect = width / w
        height = int(h * aspect)
    
    return cv2.resize(frame, (width, height))


def salvar_deteccao(frame: np.ndarray, deteccoes: List, output_path: str):
    """
    Salva frame com detecções em arquivo.
    
    Args:
        frame: Frame com detecções
        deteccoes: Lista de detecções encontradas
        output_path: Caminho para salvar
    """
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar imagem
    cv2.imwrite(output_path, frame)
    
    # Salvar metadados das detecções
    metadata = {
        'num_deteccoes': len(deteccoes),
        'deteccoes': deteccoes,
        'timestamp': str(cv2.getTickCount())
    }
    
    metadata_path = output_path.replace('.jpg', '_metadata.json').replace('.png', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def calcular_metricas_deteccao(deteccoes_verdadeiras: List, deteccoes_preditas: List) -> dict:
    """
    Calcula métricas de avaliação para detecções.
    
    Args:
        deteccoes_verdadeiras: Lista de detecções ground truth
        deteccoes_preditas: Lista de detecções do modelo
        
    Returns:
        Dicionário com métricas
    """
    tp = len(set(deteccoes_verdadeiras) & set(deteccoes_preditas))  # True Positives
    fp = len(deteccoes_preditas) - tp  # False Positives
    fn = len(deteccoes_verdadeiras) - tp  # False Negatives
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'true_positives': tp,
        'false_positives': fp,
        'false_negatives': fn
    }


def converter_coordenadas_yolo_para_opencv(yolo_coords: List[float], img_width: int, img_height: int) -> Tuple[int, int, int, int]:
    """
    Converte coordenadas YOLO (normalizadas) para OpenCV (pixels).
    
    Args:
        yolo_coords: [x_center, y_center, width, height] normalizados
        img_width: Largura da imagem em pixels
        img_height: Altura da imagem em pixels
        
    Returns:
        (x, y, w, h) em pixels
    """
    x_center, y_center, width, height = yolo_coords
    
    # Converter para pixels
    x_center *= img_width
    y_center *= img_height
    width *= img_width
    height *= img_height
    
    # Calcular coordenadas do canto superior esquerdo
    x = int(x_center - width / 2)
    y = int(y_center - height / 2)
    
    return (x, y, int(width), int(height))


def criar_video_deteccoes(frames_path: str, output_video: str, fps: int = 30):
    """
    Cria vídeo a partir de frames com detecções.
    
    Args:
        frames_path: Pasta com frames
        output_video: Caminho do vídeo de saída
        fps: Frames por segundo
    """
    frames = sorted(list(Path(frames_path).glob("*.jpg")) + list(Path(frames_path).glob("*.png")))
    
    if not frames:
        print(f"Nenhum frame encontrado em {frames_path}")
        return
    
    # Ler primeiro frame para obter dimensões
    primeiro_frame = cv2.imread(str(frames[0]))
    h, w, c = primeiro_frame.shape
    
    # Configurar codec e writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
    
    try:
        for frame_path in frames:
            frame = cv2.imread(str(frame_path))
            if frame is not None:
                writer.write(frame)
        
        print(f"Vídeo criado com sucesso: {output_video}")
        
    finally:
        writer.release()


class PerformanceMonitor:
    """Monitor de performance para detecção em tempo real."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.tempos_processamento = []
        self.fps_atual = 0
        
    def atualizar(self, tempo_processamento: float):
        """Atualiza estatísticas de performance."""
        self.tempos_processamento.append(tempo_processamento)
        
        if len(self.tempos_processamento) > self.window_size:
            self.tempos_processamento.pop(0)
        
        # Calcular FPS médio
        tempo_medio = sum(self.tempos_processamento) / len(self.tempos_processamento)
        self.fps_atual = 1.0 / tempo_medio if tempo_medio > 0 else 0
    
    def get_stats(self) -> dict:
        """Retorna estatísticas atuais."""
        if not self.tempos_processamento:
            return {'fps': 0, 'tempo_medio': 0, 'tempo_min': 0, 'tempo_max': 0}
        
        return {
            'fps': self.fps_atual,
            'tempo_medio': sum(self.tempos_processamento) / len(self.tempos_processamento),
            'tempo_min': min(self.tempos_processamento),
            'tempo_max': max(self.tempos_processamento)
        }
