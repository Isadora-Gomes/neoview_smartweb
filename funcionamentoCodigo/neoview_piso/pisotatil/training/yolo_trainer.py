"""
Módulo para treinamento de modelo YOLO para detecção de pisos táteis.

Este módulo fornece ferramentas para treinar um modelo YOLO personalizado
para detectar pisos táteis em imagens. Inclui funcionalidades para:
- Preparação de dados
- Configuração do modelo
- Treinamento
- Validação
- Inferência

Nota: Este módulo requer dataset de imagens anotadas para funcionar.
"""

import os
try:
    import yaml  # O pacote PyYAML é importado como 'yaml'
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass


@dataclass
class YOLOConfig:
    """Configurações para o treinamento YOLO."""
    model_name: str = "yolov8n.pt"  # Modelo base
    img_size: int = 640
    batch_size: int = 16
    epochs: int = 200  # MUITO mais épocas para blocos individuais
    learning_rate: float = 0.01
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    device: str = "cpu"  # ou "cuda" se GPU disponível
    patience: int = 100  # Early stopping patience
    
    
class YOLOTrainer:
    """
    Classe para treinamento de modelo YOLO para detecção de pisos táteis.
    
    Esta classe gerencia todo o processo de treinamento, desde a preparação
    dos dados até a validação do modelo treinado.
    """
    
    def __init__(self, config: YOLOConfig, project_root: str):
        """
        Inicializa o trainer YOLO.
        
        Args:
            config: Configurações de treinamento
            project_root: Caminho raiz do projeto
        """
        self.config = config
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
        # Caminhos importantes
        self.dataset_path = self.project_root / "dataset_piso_tatil"
        self.models_path = self.project_root / "models"
        self.config_path = self.project_root / "config"
        
        # Criar pastas se não existirem
        self._criar_estrutura_pastas()
        
    def _criar_estrutura_pastas(self):
        """Cria estrutura de pastas necessária para o treinamento."""
        pastas = [
            self.dataset_path / "images" / "train",
            self.dataset_path / "images" / "val",
            self.dataset_path / "images" / "test",
            self.dataset_path / "labels" / "train",
            self.dataset_path / "labels" / "val",
            self.dataset_path / "labels" / "test",
            self.models_path,
            self.config_path
        ]
        
        for pasta in pastas:
            pasta.mkdir(parents=True, exist_ok=True)
            
        self.logger.info("Estrutura de pastas criada com sucesso")
    
    def preparar_dataset(self, imagens_path: str, anotacoes_path: str, split_ratio: Tuple[float, float, float] = (0.7, 0.2, 0.1)):
        """
        Prepara o dataset dividindo em treino, validação e teste.
        
        Args:
            imagens_path: Caminho para pasta com imagens originais
            anotacoes_path: Caminho para pasta com anotações (formato YOLO)
            split_ratio: Proporção (treino, validação, teste)
        """
        try:
            import shutil
            from sklearn.model_selection import train_test_split
            
            # Listar todas as imagens
            imagens = list(Path(imagens_path).glob("*.jpg")) + list(Path(imagens_path).glob("*.png"))
            
            if not imagens:
                raise ValueError(f"Nenhuma imagem encontrada em {imagens_path}")
            
            # Dividir dataset
            train_ratio, val_ratio, test_ratio = split_ratio
            
            # Primeiro split: treino vs (val + test)
            train_imgs, temp_imgs = train_test_split(imagens, test_size=(val_ratio + test_ratio), random_state=42)
            
            # Segundo split: val vs test
            val_imgs, test_imgs = train_test_split(temp_imgs, test_size=test_ratio/(val_ratio + test_ratio), random_state=42)
            
            # Copiar arquivos para as pastas apropriadas
            for split_name, img_list in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
                for img_path in img_list:
                    # Copiar imagem
                    dest_img = self.dataset_path / "images" / split_name / img_path.name
                    shutil.copy2(img_path, dest_img)
                    
                    # Copiar anotação correspondente
                    annotation_file = Path(anotacoes_path) / f"{img_path.stem}.txt"
                    if annotation_file.exists():
                        dest_ann = self.dataset_path / "labels" / split_name / annotation_file.name
                        shutil.copy2(annotation_file, dest_ann)
            
            self.logger.info(f"Dataset preparado: {len(train_imgs)} treino, {len(val_imgs)} val, {len(test_imgs)} teste")
            
        except ImportError:
            self.logger.error("scikit-learn é necessário para divisão do dataset. Execute: pip install scikit-learn")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao preparar dataset: {str(e)}")
            raise
    
    def criar_config_yaml(self):
        """Cria arquivo de configuração YAML para YOLO."""
        if not YAML_AVAILABLE:
            self.logger.warning("PyYAML não disponível. Instale com: pip install pyyaml")
            return None
            
        # Usar caminho absoluto para o dataset
        dataset_abs_path = os.path.abspath(str(self.dataset_path))
            
        config = {
            'path': dataset_abs_path,
            'train': 'images/train',
            'val': 'images/train',  # Usar mesmo treino para validação (dataset pequeno)
            'test': 'images/test',
            'nc': 5,  # Número de classes atualizadas
            'names': {
                0: 'piso_tatil_direcional',
                1: 'piso_tatil_alerta',
                2: 'piso_tatil_direcional_vertical',
                3: 'piso_tatil_direcional_horizontal',
                4: 'piso_tatil'
            }
        }
        
        config_file = self.config_path / "piso_tatil_dataset.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"Arquivo de configuração criado: {config_file}")
        return config_file
    
    def treinar_modelo(self):
        """
        Inicia o treinamento do modelo YOLO.
        
        Nota: Requer ultralytics instalado e dataset preparado.
        """
        try:
            from ultralytics import YOLO
            
            # Criar arquivo de configuração
            config_file = self.criar_config_yaml()
            
            # Carregar modelo base
            model = YOLO(self.config.model_name)
            
            # Configurar parâmetros de treinamento
            train_args = {
                'data': str(config_file),
                'epochs': self.config.epochs,
                'imgsz': self.config.img_size,
                'batch': self.config.batch_size,
                'lr0': self.config.learning_rate,
                'device': self.config.device,
                'project': str(self.models_path),
                'name': 'piso_tatil_detector',
                'save_period': 10,  # Salvar a cada 10 épocas
                'patience': self.config.patience,     # Early stopping do config
                'cache': True,      # Cache para acelerar treinamento
                'workers': 4,       # Número de workers
                'verbose': True
            }
            
            # Iniciar treinamento
            self.logger.info("Iniciando treinamento do modelo YOLO...")
            results = model.train(**train_args)
            
            self.logger.info(f"Treinamento concluído. Resultados salvos em: {self.models_path}")
            return results
            
        except ImportError:
            self.logger.error("ultralytics não instalado. Execute: pip install ultralytics")
            raise
        except Exception as e:
            self.logger.error(f"Erro durante treinamento: {str(e)}")
            raise
    
    def validar_modelo(self, model_path: str):
        """
        Valida o modelo treinado no conjunto de teste.
        
        Args:
            model_path: Caminho para o modelo treinado (.pt)
        """
        try:
            from ultralytics import YOLO
            
            model = YOLO(model_path)
            
            # Validar no conjunto de teste
            config_file = self.config_path / "piso_tatil_dataset.yaml"
            results = model.val(
                data=str(config_file),
                split='test',
                imgsz=self.config.img_size,
                conf=self.config.confidence_threshold,
                iou=self.config.iou_threshold
            )
            
            self.logger.info("Validação concluída")
            return results
            
        except ImportError:
            self.logger.error("ultralytics não instalado para validação")
            raise
        except Exception as e:
            self.logger.error(f"Erro durante validação: {str(e)}")
            raise


class YOLODetector:
    """
    Classe para detecção usando modelo YOLO treinado.
    
    Esta classe pode ser usada como alternativa à detecção baseada em OpenCV
    quando um modelo YOLO estiver disponível.
    """
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.01):
        """
        Inicializa o detector YOLO.
        
        Args:
            model_path: Caminho para o modelo treinado
            confidence_threshold: Threshold baixo para blocos individuais (0.01)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.logger.info(f"Modelo YOLO carregado: {model_path}")
        except ImportError:
            self.logger.error("ultralytics não instalado")
            self.model = None
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {str(e)}")
            self.model = None
    
    def detectar_piso_tatil(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta pisos táteis usando modelo YOLO.
        
        Args:
            frame: Frame de entrada (imagem BGR)
            
        Returns:
            Frame com detecções ou None se não encontrado
        """
        if self.model is None:
            self.logger.warning("Modelo não carregado")
            return None
        
        try:
            # Fazer predição com configurações mais permissivas
            results = self.model(frame, conf=self.confidence_threshold, 
                               iou=0.3, max_det=1000, verbose=False)
            
            # Verificar se há detecções
            if len(results[0].boxes) > 0:
                # Desenhar detecções no frame
                annotated_frame = results[0].plot(conf=True, labels=True, boxes=True)
                return annotated_frame
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção YOLO: {str(e)}")
            return None


def criar_exemplo_anotacao(image_path: str, output_path: str):
    """
    Função utilitária para criar exemplo de anotação YOLO.
    
    Args:
        image_path: Caminho da imagem
        output_path: Caminho para salvar anotação
    """
    # Exemplo de anotação YOLO (class x_center y_center width height)
    # Valores normalizados entre 0 e 1
    exemplo_anotacao = """0 0.5 0.3 0.2 0.1
1 0.7 0.6 0.15 0.05"""
    
    with open(output_path, 'w') as f:
        f.write(exemplo_anotacao)
    
    print("Exemplo de anotação criado em: {output_path}")
    print("Formato: class x_center y_center width height (valores normalizados)")
    print("Classes das 5 novas categorias de piso tátil:")
    print("  0 = piso_tatil_direcional (linhas direcionais)")
    print("  1 = piso_tatil_alerta (pontos de alerta)")
    print("  2 = piso_tatil_direcional_vertical (direcionamento vertical)")
    print("  3 = piso_tatil_direcional_horizontal (direcionamento horizontal)")
    print("  4 = piso_tatil (geral/padrão)")


if __name__ == "__main__":
    # Exemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Configuração
    config = YOLOConfig(
        epochs=50,
        batch_size=8,
        img_size=640
    )
    
    # Criar trainer
    trainer = YOLOTrainer(config, ".")
    
    print("Módulo de treinamento YOLO criado com sucesso!")
    print("Para usar:")
    print("1. Coloque suas imagens e anotações nas pastas apropriadas")
    print("2. Execute trainer.preparar_dataset()")
    print("3. Execute trainer.treinar_modelo()")
