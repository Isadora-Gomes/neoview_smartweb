"""
Biblioteca PisoTatil - Detecção de Pisos Táteis usando Visão Computacional

Esta biblioteca fornece ferramentas para detectar pisos táteis em imagens e vídeos
usando técnicas de processamento de imagem com OpenCV e opcionalmente YOLO.

Módulos principais:
- detection: Detecção usando OpenCV (pronta para uso)
- training: Treinamento de modelos YOLO (para uso futuro)
- utils: Utilitários e funções auxiliares
- config: Gerenciamento de configurações

Exemplo básico de uso:
    from pisotatil import PisoTatil
    
    detector = PisoTatil()
    resultado = detector.detectar_piso_tatil(frame)
    
    if resultado is not None:
        print("Piso tátil detectado!")

Autor: Sistema de Detecção de Pisos Táteis
Versão: 1.0.0
"""

from .detection import PisoTatilDeteccao, ResultadoMapeamento, DeteccaoInfo
from .detection.tipos import PisoTatil
from .training import YOLOTrainer, YOLODetector, YOLOConfig
from .utils import (
    PerformanceMonitor, 
    redimensionar_frame, 
    salvar_deteccao,
    calcular_metricas_deteccao,
    converter_coordenadas_yolo_para_opencv,
    criar_video_deteccoes
)

# Importar configurações se disponível
try:
    from ..config import config_manager
except ImportError:
    # Fallback para quando importado como biblioteca instalada
    try:
        from config import config_manager
    except ImportError:
        config_manager = None

__version__ = "1.0.0"
__author__ = "Sistema de Detecção de Pisos Táteis"

# Exportações principais
__all__ = [
    'PisoTatilDeteccao',
    'DeteccaoInfo',
    'ResultadoMapeamento',
    'PisoTatil',
    'YOLOTrainer', 
    'YOLODetector',
    'YOLOConfig',
    'PerformanceMonitor',
    'redimensionar_frame',
    'salvar_deteccao',
    'calcular_metricas_deteccao',
    'converter_coordenadas_yolo_para_opencv',
    'criar_video_deteccoes',
    'config_manager'
]

# Informações da biblioteca
__description__ = "Biblioteca para detecção de pisos táteis usando visão computacional"
__url__ = "https://github.com/seu-usuario/neoview-piso"
__license__ = "MIT"
