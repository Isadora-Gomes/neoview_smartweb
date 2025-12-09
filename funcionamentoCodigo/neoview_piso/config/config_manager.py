"""
Módulo de configuração para o projeto de detecção de pisos táteis.
"""

import configparser
import os
from pathlib import Path
from typing import Dict, Any
import logging


class ConfigManager:
    """Gerenciador de configurações do projeto."""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        if config_path is None:
            # Tentar encontrar o arquivo de configuração
            current_dir = Path(__file__).parent
            config_path = current_dir / "settings.conf"
        
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()
        
        # Carregar configurações
        self._load_config()
        
    def _load_config(self):
        """Carrega configurações do arquivo."""
        try:
            if self.config_path.exists():
                self.config.read(self.config_path, encoding='utf-8')
            else:
                print(f"Arquivo de configuração não encontrado: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Cria configuração padrão."""
        self.config['detection'] = {
            'hough_circles_dp': '1',
            'hough_circles_min_dist': '20',
            'hough_circles_param1': '50',
            'hough_circles_param2': '30',
            'hough_circles_min_radius': '5',
            'hough_circles_max_radius': '25',
            'contrast_threshold': '15'
        }
        
        self.config['yolo'] = {
            'model_name': 'yolov8n.pt',
            'img_size': '640',
            'confidence_threshold': '0.5',
            'device': 'cpu'
        }
    
    def get(self, section: str, key: str, default: Any = None, value_type: type = str):
        """
        Obtém valor de configuração.
        
        Args:
            section: Seção da configuração
            key: Chave da configuração
            default: Valor padrão se não encontrado
            value_type: Tipo de retorno (str, int, float, bool)
            
        Returns:
            Valor da configuração convertido para o tipo especificado
        """
        try:
            if value_type == bool:
                return self.config.getboolean(section, key)
            elif value_type == int:
                return self.config.getint(section, key)
            elif value_type == float:
                return self.config.getfloat(section, key)
            else:
                return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """
        Define valor de configuração.
        
        Args:
            section: Seção da configuração
            key: Chave da configuração
            value: Valor a ser definido
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
    
    def save(self):
        """Salva configurações no arquivo."""
        try:
            os.makedirs(self.config_path.parent, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def get_detection_params(self) -> Dict[str, Any]:
        """Retorna parâmetros de detecção."""
        return {
            'hough_circles_params': {
                'dp': self.get('detection', 'hough_circles_dp', 1, int),
                'min_dist': self.get('detection', 'hough_circles_min_dist', 20, int),
                'param1': self.get('detection', 'hough_circles_param1', 50, int),
                'param2': self.get('detection', 'hough_circles_param2', 30, int),
                'min_radius': self.get('detection', 'hough_circles_min_radius', 5, int),
                'max_radius': self.get('detection', 'hough_circles_max_radius', 25, int),
            },
            'hough_lines_params': {
                'rho': self.get('detection', 'hough_lines_rho', 1, int),
                'theta': self.get('detection', 'hough_lines_theta', 0.017453, float),
                'threshold': self.get('detection', 'hough_lines_threshold', 100, int),
                'min_line_length': self.get('detection', 'hough_lines_min_line_length', 50, int),
                'max_line_gap': self.get('detection', 'hough_lines_max_line_gap', 10, int),
            },
            'contrast_threshold': self.get('detection', 'contrast_threshold', 15, int)
        }
    
    def get_yolo_params(self) -> Dict[str, Any]:
        """Retorna parâmetros do YOLO."""
        return {
            'model_name': self.get('yolo', 'model_name', 'yolov8n.pt'),
            'img_size': self.get('yolo', 'img_size', 640, int),
            'batch_size': self.get('yolo', 'batch_size', 16, int),
            'epochs': self.get('yolo', 'epochs', 100, int),
            'learning_rate': self.get('yolo', 'learning_rate', 0.01, float),
            'confidence_threshold': self.get('yolo', 'confidence_threshold', 0.5, float),
            'iou_threshold': self.get('yolo', 'iou_threshold', 0.45, float),
            'device': self.get('yolo', 'device', 'cpu'),
            'patience': self.get('yolo', 'patience', 100, int)
        }


# Instância global do gerenciador de configuração
config_manager = ConfigManager()
