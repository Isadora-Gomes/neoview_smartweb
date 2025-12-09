"""
Módulo para detecção de pisos táteis usando visão computacional.

Este módulo implementa a classe PisoTatil que utiliza técnicas de processamento
de imagem com OpenCV para identificar pisos táteis em frames de vídeo ou imagens.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import logging
from pathlib import Path
from dataclasses import dataclass
from io import StringIO

# Importações opcionais para YOLO
try:
    from ..training.yolo_trainer import YOLODetector
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLODetector = None

# Importar mapeamento e enum
from .mapeamento import MapaPisoTatil
from .tipos import PisoTatil


@dataclass
class DeteccaoInfo:
    """Informações de uma detecção individual"""
    classe: PisoTatil
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confianca: float
    centro: Tuple[int, int]

@dataclass
class ResultadoMapeamento:
    mapa: np.ndarray
    leitura: str

class ParteLeituraMapa:
    def __init__(self, subpartes: list['ParteLeituraMapa'] = [], principal: bool = False):
        self.subpartes = subpartes
        self.principal = principal

    def ler(self, index: Optional[int]) -> str:
        qnt_ramificacoes = len(self.subpartes)
        texto_ramificacoes: str = None

        if qnt_ramificacoes == 1:
            texto_ramificacoes = f"possui 1 {"" if index is None else "sub-"}ramificação"
        elif qnt_ramificacoes == 0:
            texto_ramificacoes = f"não possui {"" if index is None else "sub-"}ramificações"
        else:
            texto_ramificacoes = f"possui {qnt_ramificacoes} {"" if index is None else "sub-"}ramificações"

        buffer = StringIO()

        if self.principal:
            buffer.write(f"O caminho principal {texto_ramificacoes} ")
        elif index == None:
            buffer.write(f"Este caminho possui {texto_ramificacoes} ")
        else:
            buffer.write(f"A {index + 1}º ramificação {texto_ramificacoes} ")
        

        

        

class PisoTatilDeteccao:
    """
    Classe para detecção de pisos táteis em imagens usando OpenCV e YOLO.
    
    A detecção utiliza:
    1. YOLO (preferencial): Modelo treinado para detecção completa de caminhos
    2. OpenCV (fallback): Técnicas de visão computacional tradicionais
    
    Classes detectadas (5 tipos):
    - piso_tatil: Piso tátil geral/padrão
    - piso_tatil_direcional: Piso direcional (linhas)
    - piso_tatil_alerta: Piso de alerta (pontos)
    - piso_tatil_direcional_vertical: Direcionamento vertical
    - piso_tatil_direcional_horizontal: Direcionamento horizontal
    """
    
    def __init__(self, debug: bool = False, yolo_model_path: Optional[str] = None):
        """
        Inicializa o detector de pisos táteis.
        
        Args:
            debug: Se True, ativa modo debug com visualizações intermediárias
            yolo_model_path: Caminho para modelo YOLO treinado (opcional)
        """
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        
        # Configurar detector YOLO se disponível
        self.yolo_detector = None
        self.use_yolo = False
        
        # Mapeamento de classes: corrige ordem incorreta do LabelImg
        # O modelo foi treinado com ordem incorreta, precisamos mapear
        self.class_mapping = {
            # Ordem atual do modelo → Ordem correta desejada
            0: 4,  # Modelo detecta como 0 → Na verdade é classe 4 (piso_tatil)
            1: 0,  # Modelo detecta como 1 → Na verdade é classe 0 (piso_tatil_direcional)
            2: 1,  # Modelo detecta como 2 → Na verdade é classe 1 (piso_tatil_alerta)
            3: 2,  # Modelo detecta como 3 → Na verdade é classe 2 (piso_tatil_direcional_vertical)
            4: 3   # Modelo detecta como 4 → Na verdade é classe 3 (piso_tatil_direcional_horizontal)
        }
        
        # Nomes das classes na ordem correta
        self.class_names = {
            0: 'piso_tatil_direcional',
            1: 'piso_tatil_alerta', 
            2: 'piso_tatil_direcional_vertical',
            3: 'piso_tatil_direcional_horizontal',
            4: 'piso_tatil'
        }
        
        # Inicializar gerador de mapas
        self.mapa_generator = MapaPisoTatil(resolucao_mapa=(20, 20))
        
        if yolo_model_path and YOLO_AVAILABLE:
            self._inicializar_yolo(yolo_model_path)
        elif yolo_model_path and not YOLO_AVAILABLE:
            self.logger.warning("YOLO solicitado mas ultralytics não está instalado")
        
        # Se não há modelo YOLO, tentar buscar modelo treinado
        if not self.use_yolo:
            self._buscar_modelo_treinado()
        
        # Parâmetros para detecção de círculos (pontos táteis) - mais restritivos
        self.hough_circles_params = {
            'dp': 1,
            'min_dist': 15,  # Reduzido para detectar pontos próximos
            'param1': 100,   # Aumentado para reduzir falsos positivos
            'param2': 15,    # Reduzido para ser mais sensível
            'min_radius': 3,
            'max_radius': 20
        }
        
        # Parâmetros para detecção de linhas (piso direcional) - mais restritivos
        self.hough_lines_params = {
            'rho': 1,
            'theta': np.pi/180,
            'threshold': 80,     # Aumentado para reduzir falsas detecções
            'min_line_length': 30,  # Reduzido para capturar linhas menores
            'max_line_gap': 5    # Reduzido para ser mais restritivo
        }
        
        # Parâmetros de validação mais rigorosos
        self.validation_params = {
            'min_density_circles': 4,     # Mínimo de círculos em região
            'min_density_lines': 3,      # Mínimo de linhas paralelas
            'region_size': 100,          # Tamanho da região para análise
            'texture_threshold': 0.3,    # Limiar para análise de textura
            'edge_density_threshold': 0.2 # Limiar para densidade de bordas
        }

        self.mapeamento_classes = {
            0: None,  # piso_tatil_direcional -> não mapeado (depende do ângulo)
            1: PisoTatil.alerta,  # piso_tatil_alerta
            2: PisoTatil.vertical,  # piso_tatil_direcional_vertical  
            3: PisoTatil.horizontal,  # piso_tatil_direcional_horizontal
            4: None   # piso_tatil -> não mapeado (genérico)
        }
    
    def _inicializar_yolo(self, model_path: str):
        """Inicializa o detector YOLO."""
        try:
            if Path(model_path).exists():
                self.yolo_detector = YOLODetector(model_path, confidence_threshold=0.5)
                if self.yolo_detector.model is not None:
                    self.use_yolo = True
                    self.logger.info(f"Detector YOLO inicializado: {model_path}")
                else:
                    self.logger.warning("Falha ao carregar modelo YOLO")
            else:
                self.logger.warning(f"Modelo YOLO não encontrado: {model_path}")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar YOLO: {e}")
    
    def _buscar_modelo_treinado(self):
        """Busca automaticamente por modelo YOLO treinado no projeto."""
        possible_paths = [
            "models/piso_tatil_detector8/weights/best.pt",
            # "models/piso_tatil_detector7/weights/best.pt",
            # "models/piso_tatil_detector6/weights/best.pt",
            "models/piso_tatil_detector5/weights/best.pt",
            "models/piso_tatil_detector4/weights/best.pt",
            "models/piso_tatil_detector3/weights/best.pt", 
            "models/piso_tatil_detector2/weights/best.pt",
            "models/piso_tatil_detector/weights/best.pt",
            "runs/detect/train/weights/best.pt", 
            "runs/detect/piso_tatil_detector/weights/best.pt",
            "models/best.pt"
        ]
        
        # Tentar encontrar o modelo mais recente
        modelo_encontrado = None
        for path in possible_paths:
            if Path(path).exists():
                self.logger.info(f"Modelo YOLO encontrado automaticamente: {path}")
                modelo_encontrado = path
                break
        
        # Se encontrou modelo, inicializar
        if modelo_encontrado:
            try:
                self._inicializar_yolo(modelo_encontrado)
                self.logger.info(f"YOLO inicializado automaticamente com: {modelo_encontrado}")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar YOLO automaticamente: {e}")
        else:
            self.logger.warning("Nenhum modelo YOLO encontrado automaticamente")
        
    def detectar_piso_tatil(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta pisos táteis no frame usando APENAS YOLO (OpenCV desabilitado).
        
        Args:
            frame: Frame de entrada (imagem BGR)
            
        Returns:
            Frame com pisos táteis detectados ou None se não encontrado
        """
        if frame is None or frame.size == 0:
            self.logger.warning("Frame vazio ou inválido fornecido")
            return None

        # USAR APENAS YOLO - SEM FALLBACK PARA OPENCV
        if self.use_yolo and self.yolo_detector is not None:
            try:
                resultado_yolo = self._detectar_com_yolo(frame)
                if resultado_yolo is not None:
                    self.logger.info("Piso tátil detectado com YOLO")
                    return resultado_yolo
                else:
                    self.logger.info("YOLO não detectou piso tátil")
                    return None
            except Exception as e:
                self.logger.error(f"Erro no YOLO: {e}")
                return None
        else:
            self.logger.warning("Modelo YOLO não disponível")
            return None
    
    def _detectar_com_yolo(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta pisos táteis usando modelo YOLO treinado.
        
        Args:
            frame: Frame de entrada
            
        Returns:
            Frame com detecções YOLO ou None
        """
        if self.yolo_detector is None:
            return None
        
        try:
            # Usar detector YOLO
            resultado = self.yolo_detector.detectar_piso_tatil(frame)
            
            if resultado is not None:
                # Adicionar informações específicas no frame
                h, w = frame.shape[:2]
                cv2.putText(resultado, "DETECTADO COM YOLO", (10, h-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if self.debug:
                    cv2.putText(resultado, "Modelo: YOLOv8 Treinado", (10, h-50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                return resultado
                
        except Exception as e:
            self.logger.error(f"Erro na detecção YOLO: {e}")
            
        return None
    
    def _extrair_frames(self, results) -> List[DeteccaoInfo]:
        deteccoes = []
        
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confianca = box.conf[0].cpu().numpy()
                classe_id = int(box.cls[0].cpu().numpy())
                
                x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                centro = (int(x + w/2), int(y + h/2))
                
                classe_mapeada = self.mapeamento_classes.get(classe_id)
                if classe_mapeada is not None:
                    deteccao = DeteccaoInfo(
                        classe=classe_mapeada,
                        bbox=(x, y, w, h),
                        confianca=float(confianca),
                        centro=centro
                    )
                    deteccoes.append(deteccao)
        
        return deteccoes
    
    def _detectar_frames(self, frame: np.ndarray) -> List[DeteccaoInfo]:
        """
        Detecta pisos táteis no frame e retorna informações detalhadas.
        
        Args:
            frame: Frame de entrada (imagem BGR)
            
        Returns:
            Lista de informações de detecção
        """
        deteccoes_info: List[DeteccaoInfo] = []
        
        if frame is None or frame.size == 0:
            self.logger.warning("Frame vazio ou inválido fornecido")
            return deteccoes_info

        # USAR APENAS YOLO - SEM FALLBACK PARA OPENCV
        if self.use_yolo and self.yolo_detector is not None:
            try:
                results = self.yolo_detector.model(frame)
                deteccoes_info = self._extrair_frames(results)
                
                if deteccoes_info:
                    self.logger.info(f"{len(deteccoes_info)} pisos táteis detectados com YOLO")
                else:
                    self.logger.info("YOLO não detectou pisos táteis")
                    
            except Exception as e:
                self.logger.error(f"Erro no YOLO: {e}")
        
        else:
            self.logger.warning("Modelo YOLO não disponível")
        
        return deteccoes_info

    def _mapear_frames(self, base_frames: List[DeteccaoInfo]) -> np.ndarray:
        sum_heights = 0
        sum_widths = 0

        for frame in base_frames:
            height = frame.bbox[3]
            width = frame.bbox[2]

            sum_heights += height
            sum_widths += width

        # medias
        avg_height = sum_heights / len(base_frames) if base_frames else 1
        avg_width = sum_widths / len(base_frames) if base_frames else 1

        heights_allowed = (avg_height * 0.65, avg_height * 1.35)
        widths_allowed = (avg_width * 0.65, avg_width * 1.35)

        # nova lista de frames
        new_frames: List[DeteccaoInfo] = []

        # quantidade de frames quebrados
        framesplits: List[int] = []

        for index, frame in enumerate(base_frames):
            height = frame.bbox[3]
            width = frame.bbox[2]
            
            if (height < heights_allowed[0] or width < widths_allowed[0]):
                new_frames.append(frame)    
            else:
                return_rows = 1
                return_columns = 1
                # enquanto for maior, divide o frame em 2 nesse eixo
                while (height > heights_allowed[1]):
                    height /= 2
                    return_rows *= 2
                while (width > widths_allowed[1]):
                    width /= 2
                    return_columns *= 2
                
                if (return_rows == 1 and return_columns == 1):
                    new_frames.append(frame)
                else:
                    # contabiliza quantos frames foram criados
                    framesplits.append(return_rows * return_columns)

                    # define o tamanho de columa e linha de cada um dos novos frames
                    column_size = frame.bbox[2] / return_columns
                    row_size = frame.bbox[3] / return_rows

                    for row in range(return_rows):
                        # posição y (original + index * subtamanho)
                        y = frame.bbox[1] + row * row_size
                        for column in range(return_columns):
                            # posição x (original + index * subtamanho)
                            x = frame.bbox[0] + column * column_size
                            # novo sub-frame do original
                            sub_frame = DeteccaoInfo(
                                classe=frame.classe,
                                bbox=(int(x), int(y), int(column_size), int(row_size)),
                                confianca=frame.confianca,
                                centro=(int(x + column_size/2), int(y + row_size/2))
                            )
                            new_frames.append(sub_frame)

        for split in framesplits:
            print(f" - Frame quebrado em {split} partes")

        # ordenamento baseado em x e y
        x_ordered: list[DeteccaoInfo] = []
        y_ordered: list[DeteccaoInfo] = []

        # tamanhos máximos e mínimos permitidos baseados na média
        # previamente determinada
        x_translation_max_diff = avg_width * 0.35
        y_translation_max_diff = avg_height * 0.35

        # determina o index a ser inserido em cada lista-eixo
        for frame in new_frames:
            x_index = 0
            y_index = 0

            for in_x in x_ordered:
                if frame.centro[0] >= in_x.centro[0]:
                    x_index += 1
            for in_y in y_ordered:
                if frame.centro[1] >= in_y.centro[1]:
                    y_index += 1
            
            x_ordered.insert(x_index, frame)
            y_ordered.insert(y_index, frame)

        # salva os indices baseados no id() do DeteccaoInfo
        x_indexes: dict[int, int] = {}
        y_indexes: dict[int, int] = {}

        # salva os maiores index para determinar tamanho da matrix
        x_bigger_index = 0
        y_bigger_index = 0

        for index, frame in enumerate(x_ordered):
            frame_id = id(frame)
            if (index == 0):
                x_indexes[frame_id] = 0
            else:
                prev_frame = x_ordered[index - 1]
                prev_frame_id = id(prev_frame)
                # calcula diferença de tamanho entre atual e anterior
                if (abs(frame.centro[0] - prev_frame.centro[0]) > x_translation_max_diff):
                    # se passar o limite, salta para novo index
                    x_bigger_index = x_indexes[frame_id] = x_indexes[prev_frame_id] + 1
                else:
                    # caso contrário, mantém na mesma linha
                    x_indexes[frame_id] = x_indexes[prev_frame_id]
        
        # repete processo para eixo y
        for index, frame in enumerate(y_ordered):
            frame_id = id(frame)
            if (index == 0):
                y_indexes[frame_id] = 0
            else:
                prev_frame = y_ordered[index - 1]
                prev_frame_id = id(prev_frame)
                if (abs(frame.centro[1] - prev_frame.centro[1]) > y_translation_max_diff):
                    y_bigger_index = y_indexes[frame_id] = y_indexes[prev_frame_id] + 1
                else:
                    y_indexes[frame_id] = y_indexes[prev_frame_id]

        # cria matrix full nula para preencher com os index
        matrix = np.full(( y_bigger_index + 1, x_bigger_index + 1 ), dtype=object, fill_value=None)

        # recupera os index baseado no id
        for frame in new_frames:
            frame_id = id(frame)
            x_index = x_indexes[frame_id]
            y_index = y_indexes[frame_id]
            matrix[y_index, x_index] = frame

        return matrix

    def _ler_mapa(self, mapa: np.ndarray) -> str:
        """
        Gera descrição sequencial do caminho seguindo a lógica de navegação.
        SEM contagem de alertas - apenas segue o caminho até bifurcações.
        """
        if mapa is None or mapa.size == 0:
            return "Nenhum caminho detectado no ambiente."
        
        # Seguir o caminho sequencialmente desde a base
        descricao = self._seguir_caminho_sequencial_simples(mapa)
        
        return descricao

    def _seguir_caminho_sequencial_simples(self, mapa: np.ndarray) -> str:
        """Segue o caminho sequencialmente identificando apenas bifurcações - SEM contar alertas."""
        altura, largura = mapa.shape
        
        # Encontrar linha de início (base do mapa)
        linha_inicio = None
        for y in range(altura - 1, -1, -1):
            if any(mapa[y, x] is not None and 
                   mapa[y, x].classe in [PisoTatil.vertical, PisoTatil.horizontal] 
                   for x in range(largura)):
                linha_inicio = y
                break
        
        if linha_inicio is None:
            return "Nenhum caminho detectado."
        
        # Encontrar coluna principal (mais comum entre elementos de caminho)
        colunas_caminho = []
        for y in range(linha_inicio, -1, -1):
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe == PisoTatil.vertical):  # Apenas verticais para caminho principal
                    colunas_caminho.append(x)
        
        if colunas_caminho:
            from collections import Counter
            counter = Counter(colunas_caminho)
            coluna_principal = counter.most_common(1)[0][0]
        else:
            coluna_principal = largura // 2
        
        # Analisar cada linha de baixo para cima procurando bifurcações
        bifurcacoes = []
        
        for y in range(linha_inicio, -1, -1):
            # Verificar se há caminhos nesta linha
            elementos_caminho = []
            elementos_horizontais = []
            for x in range(largura):
                if mapa[y, x] is not None:
                    if mapa[y, x].classe in [PisoTatil.horizontal, PisoTatil.vertical]:
                        elementos_caminho.append(x)
                        if mapa[y, x].classe == PisoTatil.horizontal:
                            elementos_horizontais.append(x)
            
            # Detectar bifurcações por elementos horizontais OU verticais fora da coluna principal
            if elementos_horizontais:
                # Bifurcação por elementos horizontais (mudança de direção horizontal)
                # Elementos horizontais à esquerda da coluna principal = bifurcação para esquerda
                if any(x < coluna_principal - 1 for x in elementos_horizontais):
                    if any(x > coluna_principal + 1 for x in elementos_horizontais):
                        direcao = "bilateral"
                    else:
                        direcao = "para a esquerda"  # Horizontais à esquerda = bifurcação para esquerda
                elif any(x > coluna_principal + 1 for x in elementos_horizontais):
                    direcao = "para a direita"     # Horizontais à direita = bifurcação para direita
                else:
                    continue  # Elementos horizontais estão na coluna principal
                
                if not bifurcacoes or abs(bifurcacoes[-1]["linha"] - y) > 1:
                    bifurcacoes.append({"linha": y, "direcao": direcao})
            
            # Detectar bifurcações por verticais fora da coluna principal
            elif len(elementos_caminho) > 0:
                elementos_verticais = []
                for x in elementos_caminho:
                    if (mapa[y, x] is not None and 
                        mapa[y, x].classe == PisoTatil.vertical and
                        abs(x - coluna_principal) > 1):
                        elementos_verticais.append(x)
                
                if elementos_verticais:
                    # Para verticais, analisar se é continuação de bifurcação anterior
                    if bifurcacoes and y < bifurcacoes[-1]["linha"]:
                        # É uma segunda bifurcação - continuação da primeira que foi para esquerda
                        # Vertical na coluna 0 (esquerda) representa bifurcação para direita desse ponto
                        if any(x < coluna_principal for x in elementos_verticais):
                            direcao = "para a direita"  # Segunda bifurcação: da esquerda vai para direita
                        else:
                            direcao = "para a esquerda"  # Segunda bifurcação: da direita vai para esquerda
                    else:
                        # Primeira bifurcação por vertical - usar lógica normal
                        if any(x < coluna_principal for x in elementos_verticais):
                            direcao = "para a esquerda"
                        else:
                            direcao = "para a direita"
                    
                    if not bifurcacoes or abs(bifurcacoes[-1]["linha"] - y) > 1:
                        bifurcacoes.append({"linha": y, "direcao": direcao})
        
        # Construir descrição sequencial
        descricao = ["O caminho principal"]
        
        if not bifurcacoes:
            descricao.append(" segue diretamente para frente")
        else:
            # Ordenar bifurcações por linha (de baixo para cima)
            bifurcacoes_ordenadas = sorted(bifurcacoes, key=lambda x: x['linha'], reverse=True)
            
            for i, bif in enumerate(bifurcacoes_ordenadas):
                if i == 0:
                    descricao.append(f" segue até uma bifurcação {bif['direcao']}")
                else:
                    descricao.append(f", que segue até uma bifurcação {bif['direcao']}")
            
            # Sempre termina indo para fora do campo de visão (sem mencionar alertas)
            descricao.append(" e segue para fora do campo de visão")
        
        descricao.append(".")
        
        return "".join(descricao)

    def _termina_em_alerta(self, mapa: np.ndarray) -> bool:
        """Verifica se o caminho termina em um ponto de alerta."""
        altura, largura = mapa.shape
        
        # Verificar as primeiras linhas (topo do mapa) em busca de alertas
        for y in range(min(3, altura)):
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe == PisoTatil.alerta):
                    # Verificar se há caminho conectado
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y + dy, x + dx
                            if (0 <= ny < altura and 0 <= nx < largura and 
                                mapa[ny, nx] is not None and
                                mapa[ny, nx].classe in [PisoTatil.vertical, PisoTatil.horizontal]):
                                return True
        
        return False

    def _agrupar_alertas_em_clusters(self, mapa: np.ndarray) -> list:
        """Agrupa alertas próximos em clusters."""
        altura, largura = mapa.shape
        alertas = []
        
        # Encontrar todos os alertas
        for y in range(altura):
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe == PisoTatil.alerta):
                    alertas.append((y, x))
        
        if not alertas:
            return []
        
        # Agrupar alertas próximos (distância ≤ 2)
        clusters = []
        alertas_usados = set()
        
        for y, x in alertas:
            if (y, x) in alertas_usados:
                continue
                
            cluster = [(y, x)]
            alertas_usados.add((y, x))
            
            # Procurar alertas próximos
            for ay, ax in alertas:
                if (ay, ax) in alertas_usados:
                    continue
                    
                # Verificar se está próximo de algum alerta do cluster
                for cy, cx in cluster:
                    if abs(ay - cy) <= 2 and abs(ax - cx) <= 2:
                        cluster.append((ay, ax))
                        alertas_usados.add((ay, ax))
                        break
            
            clusters.append(cluster)
        
        return clusters

    def _seguir_caminho_sequencial(self, mapa: np.ndarray, clusters_alertas: list) -> str:
        """Segue o caminho sequencialmente desde a base identificando bifurcações."""
        altura, largura = mapa.shape
        
        # Encontrar linha de início (base do mapa)
        linha_inicio = None
        for y in range(altura - 1, -1, -1):
            if any(mapa[y, x] is not None for x in range(largura)):
                linha_inicio = y
                break
        
        if linha_inicio is None:
            return "Nenhum caminho detectado."
        
        descricao = ["O caminho principal"]
        
        # Encontrar caminho principal (coluna mais comum)
        colunas_caminho = []
        for y in range(linha_inicio, -1, -1):
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe in [PisoTatil.vertical, PisoTatil.horizontal]):
                    colunas_caminho.append(x)
        
        # Determinar coluna principal (mais frequente)
        if colunas_caminho:
            from collections import Counter
            counter = Counter(colunas_caminho)
            coluna_principal = counter.most_common(1)[0][0]
        else:
            coluna_principal = largura // 2
        
        # Analisar cada linha de baixo para cima procurando bifurcações
        bifurcacoes_encontradas = []
        
        for y in range(linha_inicio, -1, -1):
            # Verificar se há caminhos nesta linha
            elementos_linha = []
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe in [PisoTatil.horizontal, PisoTatil.vertical]):
                    elementos_linha.append(x)
            
            # Se há mais elementos que apenas o caminho principal, é uma bifurcação
            if len(elementos_linha) > 1:
                # Verificar se não é apenas o caminho principal continuando
                elementos_bifurcacao = [x for x in elementos_linha if abs(x - coluna_principal) > 1]
                
                if elementos_bifurcacao:
                    bifurcacao = self._analisar_bifurcacao_sequencial(
                        mapa, y, elementos_linha, coluna_principal, bifurcacoes_encontradas
                    )
                    if bifurcacao and bifurcacao not in bifurcacoes_encontradas:
                        bifurcacoes_encontradas.append(bifurcacao)
        
        # Construir descrição sequencial
        if not bifurcacoes_encontradas:
            descricao.append(" segue diretamente para frente")
        else:
            # Ordenar bifurcações por linha (de baixo para cima)
            bifurcacoes_ordenadas = sorted(bifurcacoes_encontradas, 
                                         key=lambda x: x['linha'], reverse=True)
            
            for i, bif in enumerate(bifurcacoes_ordenadas):
                if i == 0:
                    descricao.append(f" segue até uma bifurcação {bif['direcao']}")
                else:
                    descricao.append(f", que segue até uma bifurcação {bif['direcao']}")
            
            descricao.append(" e segue para fora do campo de visão")
        
        # Adicionar informação sobre clusters de alerta se existirem
        if clusters_alertas:
            desc_clusters = self._descrever_clusters_alertas(clusters_alertas)
            if desc_clusters:
                descricao.append(f", {desc_clusters}")
        
        descricao.append(".")
        
        return "".join(descricao)

    def _analisar_bifurcacao_sequencial(self, mapa: np.ndarray, linha: int, elementos: list, coluna_principal: int, bifurcacoes_anteriores: list) -> dict:
        """Analisa uma bifurcação no contexto sequencial do caminho."""
        altura, largura = mapa.shape
        
        # Verificar se é uma bifurcação real (não apenas alertas agrupados)
        tem_caminho = any(mapa[linha, x] is not None and 
                         mapa[linha, x].classe in [PisoTatil.horizontal, PisoTatil.vertical] 
                         for x in elementos)
        
        if not tem_caminho:
            return None
        
        # Separar elementos por relação ao caminho principal
        elementos_esquerda = [x for x in elementos if x < coluna_principal - 1]
        elementos_direita = [x for x in elementos if x > coluna_principal + 1]
        
        # Determinar direção da bifurcação
        if elementos_esquerda and elementos_direita:
            return {"direcao": "bilateral", "linha": linha, "posicoes": elementos}
        elif elementos_esquerda:
            return {"direcao": "para a esquerda", "linha": linha, "posicoes": elementos}
        elif elementos_direita:
            return {"direcao": "para a direita", "linha": linha, "posicoes": elementos}
        
        # Se não há bifurcação clara, verificar se há mudança horizontal
        if len(elementos) > 1:
            # Verificar se há elementos horizontais (indicando bifurcação)
            for x in elementos:
                if (mapa[linha, x] is not None and 
                    mapa[linha, x].classe == PisoTatil.horizontal):
                    if x < coluna_principal:
                        return {"direcao": "para a esquerda", "linha": linha, "posicoes": elementos}
                    elif x > coluna_principal:
                        return {"direcao": "para a direita", "linha": linha, "posicoes": elementos}
        
        return None

    def _descrever_clusters_alertas(self, clusters: list) -> str:
        """Descreve os clusters de alerta identificados."""
        if not clusters:
            return ""
        
        num_clusters = len(clusters)
        
        if num_clusters == 1:
            return "possui um ponto de alerta"
        elif num_clusters == 2:
            return "possui dois pontos de alerta"
        else:
            return f"possui {num_clusters} pontos de alerta distribuídos"

    def _encontrar_inicio(self, mapa: np.ndarray) -> tuple:
        """Encontra o ponto de início do caminho (linha mais baixa)."""
        altura, largura = mapa.shape
        for y in range(altura - 1, -1, -1):
            for x in range(largura):
                if mapa[y, x] is not None:
                    return (y, x)
        return None

    def _analisar_caminho_principal(self, mapa: np.ndarray, inicio: tuple) -> str:
        """Analisa e descreve o caminho principal."""
        linha, coluna = inicio
        altura, largura = mapa.shape
        
        # Contar elementos verticais no caminho principal
        elementos_verticais = 0
        for y in range(altura):
            if (coluna < largura and mapa[y, coluna] is not None and 
                mapa[y, coluna].classe == PisoTatil.vertical):
                elementos_verticais += 1
        
        if elementos_verticais > altura * 0.7:
            return "segue diretamente para frente"
        elif elementos_verticais > altura * 0.4:
            return "segue predominantemente para frente com algumas curvas"
        else:
            return "apresenta múltiplas direções"

    def _detectar_ramificacoes(self, mapa: np.ndarray) -> list:
        """Detecta pontos de ramificação no mapa."""
        altura, largura = mapa.shape
        ramificacoes = []
        
        for y in range(altura):
            elementos_linha = [x for x in range(largura) if mapa[y, x] is not None]
            if len(elementos_linha) > 1:
                # Verificar se são caminhos distintos (não alertas agrupados)
                tipos = [mapa[y, x].classe for x in elementos_linha if mapa[y, x] is not None]
                if any(t in [PisoTatil.horizontal, PisoTatil.vertical] for t in tipos):
                    ramificacoes.append((y, elementos_linha))
        
        return ramificacoes

    def _descrever_ramificacoes(self, mapa: np.ndarray, ramificacoes: list) -> str:
        """Descreve as ramificações encontradas com suas direções."""
        if not ramificacoes:
            return ""
        
        num_ramificacoes = len(ramificacoes)
        
        if num_ramificacoes == 1:
            linha, colunas = ramificacoes[0]
            direcao = self._analisar_direcao_ramificacao(mapa, linha, colunas)
            return f"uma ramificação {direcao}"
        elif num_ramificacoes == 2:
            # Analisar cada ramificação
            desc_ramif = []
            for i, (linha, colunas) in enumerate(ramificacoes):
                direcao = self._analisar_direcao_ramificacao(mapa, linha, colunas)
                resultado = self._analisar_destino_ramificacao(mapa, linha, colunas)
                if i == 0:
                    desc_ramif.append(f"duas ramificações, a primeira {direcao} que {resultado}")
                else:
                    desc_ramif.append(f" e a segunda {direcao} que {resultado}")
            return "".join(desc_ramif)
        else:
            return f"múltiplas ramificações ({num_ramificacoes} pontos)"

    def _analisar_direcao_ramificacao(self, mapa: np.ndarray, linha: int, colunas: list) -> str:
        """Analisa a direção de uma ramificação."""
        altura, largura = mapa.shape
        
        # Determinar posição central do caminho principal
        centro_mapa = largura // 2
        
        # Analisar posições dos elementos da ramificação
        posicoes_elementos = []
        for col in colunas:
            if col < largura and mapa[linha, col] is not None:
                posicoes_elementos.append(col)
        
        if not posicoes_elementos:
            return "indefinida"
        
        # Determinar direção baseada na posição relativa
        pos_media = sum(posicoes_elementos) / len(posicoes_elementos)
        
        if len(posicoes_elementos) > 1:
            # Múltiplos elementos - verificar se estão à esquerda, direita ou ambos
            min_pos = min(posicoes_elementos)
            max_pos = max(posicoes_elementos)
            
            if min_pos < centro_mapa and max_pos > centro_mapa:
                return "bilateral"
            elif pos_media < centro_mapa:
                return "à esquerda"
            else:
                return "à direita"
        else:
            # Elemento único
            if pos_media < centro_mapa:
                return "à esquerda"
            elif pos_media > centro_mapa:
                return "à direita"
            else:
                return "central"

    def _analisar_destino_ramificacao(self, mapa: np.ndarray, linha_inicial: int, colunas: list) -> str:
        """Analisa para onde uma ramificação leva."""
        altura, largura = mapa.shape
        
        # Verificar continuidade da ramificação
        continua_acima = False
        for y in range(linha_inicial - 1, -1, -1):
            elementos_acima = any(mapa[y, col] is not None for col in colunas if col < largura)
            if elementos_acima:
                continua_acima = True
                break
        
        if continua_acima:
            # Verificar se ramifica novamente
            sub_ramificacoes = 0
            for y in range(linha_inicial - 1, -1, -1):
                elementos_linha = [x for x in range(largura) if mapa[y, x] is not None]
                if len(elementos_linha) > 2:
                    sub_ramificacoes += 1
            
            if sub_ramificacoes > 0:
                return "se ramifica novamente e segue fora do campo de visão"
            else:
                return "segue fora do campo de visão"
        else:
            return "leva a uma saída do caminho"

    def _detectar_alertas(self, mapa: np.ndarray) -> list:
        """Detecta pontos de alerta no mapa."""
        altura, largura = mapa.shape
        alertas = []
        
        for y in range(altura):
            for x in range(largura):
                if (mapa[y, x] is not None and 
                    mapa[y, x].classe == PisoTatil.alerta):
                    alertas.append((y, x))
        
        return alertas

    def _descrever_alertas(self, alertas: list) -> str:
        """Descreve os pontos de alerta identificando fins de caminho vs continuidades."""
        if not alertas:
            return ""
        
        # Analisar contexto de cada alerta
        fins_de_caminho = 0
        continuidades = 0
        
        for y, x in alertas:
            # Verificar se há caminhos conectados ao alerta
            conexoes = self._verificar_conexoes_alerta(y, x)
            
            if conexoes <= 1:
                fins_de_caminho += 1
            else:
                continuidades += 1
        
        # Gerar descrição baseada no contexto
        descricoes = []
        
        if fins_de_caminho > 0:
            if fins_de_caminho == 1:
                descricoes.append("apresenta um fim de caminho sinalizado")
            else:
                descricoes.append(f"apresenta {fins_de_caminho} fins de caminho sinalizados")
        
        if continuidades > 0:
            if continuidades == 1:
                descricoes.append("possui um ponto de atenção no percurso")
            else:
                descricoes.append(f"possui {continuidades} pontos de atenção no percurso")
        
        if len(descricoes) == 2:
            return f"{descricoes[0]} e {descricoes[1]}"
        elif len(descricoes) == 1:
            return descricoes[0]
        else:
            return "apresenta sinalizações de alerta"

    def _verificar_conexoes_alerta(self, y: int, x: int) -> int:
        """Verifica quantas conexões um ponto de alerta possui."""
        if not hasattr(self, 'mapa_temp'):
            return 0
        
        altura, largura = self.mapa_temp.shape
        conexoes = 0
        
        # Verificar 8 direções ao redor do alerta
        direcoes = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for dy, dx in direcoes:
            ny, nx = y + dy, x + dx
            if (0 <= ny < altura and 0 <= nx < largura and 
                self.mapa_temp[ny, nx] is not None):
                # Verificar se é um caminho (horizontal ou vertical)
                if (self.mapa_temp[ny, nx].classe in [PisoTatil.horizontal, PisoTatil.vertical]):
                    conexoes += 1
        
        return conexoes

    def mapear(self, imagem: np.ndarray) -> ResultadoMapeamento:
        frames = self._detectar_frames(imagem)
        mapa = self._mapear_frames(frames)
        leitura = self._ler_mapa(mapa)

        return ResultadoMapeamento(
            mapa=mapa,
            leitura=leitura,
        )

    def _detectar_com_opencv(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta pisos táteis usando algoritmos OpenCV (fallback).
        Classifica em uma das 5 categorias quando possível.
        
        Args:
            frame: Frame de entrada
            
        Returns:
            Frame com detecções OpenCV ou None
        """
        try:
            # Pré-processamento avançado da imagem
            gray = self._preprocessar_imagem(frame)
            
            # Detectar diferentes tipos de padrões táteis
            pontos_detectados = self._detectar_pontos_tateis(gray)  # piso_tatil_alerta
            linhas_detectadas = self._detectar_linhas_tateis(gray)  # piso_tatil_direcional
            
            # Classificar tipo baseado nos padrões encontrados
            tipo_detectado = self._classificar_tipo_piso_tatil(pontos_detectados, linhas_detectadas)
            
            # Lógica para detectar presença de piso tátil
            confianca_pontos = len(pontos_detectados)
            confianca_linhas = len(linhas_detectadas)
            
            piso_detectado = False
            tipo_detectado = ""
            
            # DETECTAR CAMINHOS COMPLETOS - critérios mais flexíveis
            if confianca_pontos >= 8:  # Muitos pontos = caminho de pontos
                piso_detectado = True
                tipo_detectado = "caminho_pontos"
                
            elif confianca_linhas >= 6:  # Muitas linhas = caminho direcional
                piso_detectado = True
                tipo_detectado = "caminho_direcional"
                
            elif confianca_pontos >= 4 and confianca_linhas >= 3:  # Caminho misto
                piso_detectado = True
                tipo_detectado = "caminho_misto"
                
            elif confianca_pontos >= 3:  # Poucos pontos = bloco pequeno
                piso_detectado = True
                tipo_detectado = "bloco_pontos"
                
            elif confianca_linhas >= 3:  # Poucas linhas = bloco direcional
                piso_detectado = True
                tipo_detectado = "bloco_direcional"
            
            if piso_detectado:
                resultado = self._criar_frame_resultado(
                    frame, pontos_detectados, linhas_detectadas, tipo_detectado
                )
                
                # Adicionar indicação de método de detecção e tipo
                h, w = frame.shape[:2]
                cv2.putText(resultado, "DETECTADO COM OPENCV", (10, h-20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(resultado, f"Tipo: {tipo_detectado}", (10, h-50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
                self.logger.info(
                    f"Piso tátil detectado (OpenCV): {tipo_detectado} - "
                    f"Pontos: {len(pontos_detectados)}, "
                    f"Linhas: {len(linhas_detectadas)}"
                )
                return resultado
            
            self.logger.debug("Nenhum piso tátil detectado no frame (OpenCV)")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de piso tátil (OpenCV): {str(e)}")
            return None
    
    def _classificar_tipo_piso_tatil(self, pontos_detectados, linhas_detectadas) -> str:
        """
        Classifica o tipo de piso tátil baseado nos padrões detectados.
        
        Args:
            pontos_detectados: Lista de pontos circulares detectados
            linhas_detectadas: Lista de linhas direcionais detectadas
            
        Returns:
            Tipo classificado: 'piso_tatil', 'piso_tatil_direcional', 'piso_tatil_alerta', 
            'piso_tatil_direcional_vertical', 'piso_tatil_direcional_horizontal'
        """
        num_pontos = len(pontos_detectados)
        num_linhas = len(linhas_detectadas)
        
        # Classificação baseada na predominância de padrões
        if num_pontos > num_linhas * 2:
            # Predominância de pontos = piso de alerta
            return 'piso_tatil_alerta'
        elif num_linhas > num_pontos * 2:
            # Predominância de linhas = piso direcional
            if self._eh_predominantemente_vertical(linhas_detectadas):
                return 'piso_tatil_direcional_vertical'
            elif self._eh_predominantemente_horizontal(linhas_detectadas):
                return 'piso_tatil_direcional_horizontal'
            else:
                return 'piso_tatil_direcional'
        else:
            # Padrão misto ou geral
            return 'piso_tatil'
    
    def _eh_predominantemente_vertical(self, linhas) -> bool:
        """Verifica se as linhas são predominantemente verticais."""
        if not linhas:
            return False
        # Análise simplificada - pode ser aprimorada
        return True  # Placeholder para implementação futura
    
    def _eh_predominantemente_horizontal(self, linhas) -> bool:
        """Verifica se as linhas são predominantemente horizontais."""
        if not linhas:
            return False
        # Análise simplificada - pode ser aprimorada  
        return False  # Placeholder para implementação futura
    
    def _preprocessar_imagem(self, frame: np.ndarray) -> np.ndarray:
        """
        Aplica pré-processamento avançado na imagem para melhorar a detecção.
        
        Args:
            frame: Frame original
            
        Returns:
            Imagem em escala de cinza processada
        """
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Redimensionar se muito grande para melhor performance
        h, w = gray.shape
        if w > 800:
            scale = 800 / w
            new_h = int(h * scale)
            gray = cv2.resize(gray, (800, new_h))
        
        # Aplicar filtro mediano para reduzir ruído preservando bordas
        gray = cv2.medianBlur(gray, 3)
        
        # Melhorar contraste usando CLAHE com parâmetros otimizados
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Aplicar filtro morfológico para realçar estruturas circulares
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        # Suavização seletiva para preservar detalhes importantes
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        if self.debug:
            cv2.imshow('Preprocessed', gray)
            cv2.waitKey(1)
            
        return gray
    
    def _detectar_pontos_tateis(self, gray: np.ndarray) -> List[Tuple[int, int, int]]:
        """
        Detecta pontos circulares característicos dos pisos táteis com foco na precisão.
        
        Args:
            gray: Imagem em escala de cinza
            
        Returns:
            Lista de círculos detectados (x, y, raio)
        """
        # Pré-processamento específico para pontos
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Filtro bilateral para preservar bordas dos pontos
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Operação morfológica para realçar pontos circulares
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        tophat = cv2.morphologyEx(bilateral, cv2.MORPH_TOPHAT, kernel)
        
        # Combinar imagens
        processed = cv2.addWeighted(bilateral, 0.7, tophat, 0.3, 0)
        
        pontos_validos = []
        
        # Detecção multi-escala para CAMINHOS COMPLETOS
        estrategias = [
            # Círculos pequenos (detalhes)
            {'param1': 70, 'param2': 20, 'min_r': 2, 'max_r': 15, 'min_dist': 6},
            # Círculos médios (padrão)  
            {'param1': 60, 'param2': 25, 'min_r': 8, 'max_r': 30, 'min_dist': 10},
            # Círculos grandes (para capturar mais)
            {'param1': 50, 'param2': 30, 'min_r': 15, 'max_r': 50, 'min_dist': 15}
        ]
        
        todos_circulos = []
        
        for estrategia in estrategias:
            circles = cv2.HoughCircles(
                processed,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=estrategia['min_dist'],
                param1=estrategia['param1'],
                param2=estrategia['param2'],
                minRadius=estrategia['min_r'],
                maxRadius=estrategia['max_r']
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                todos_circulos.extend(circles)
        
        if not todos_circulos:
            return []
        
        # Remover duplicatas
        circulos_unicos = []
        for (x, y, r) in todos_circulos:
            is_duplicate = False
            for (ux, uy, ur) in circulos_unicos:
                dist = np.sqrt((x - ux)**2 + (y - uy)**2)
                if dist < max(r, ur) * 1.2:
                    is_duplicate = True
                    break
            if not is_duplicate:
                circulos_unicos.append((x, y, r))
        
        # Validação rigorosa de cada ponto
        h, w = gray.shape
        for (x, y, r) in circulos_unicos:
            if self._validar_ponto_circular_rigoroso(gray, x, y, r, h, w):
                pontos_validos.append((x, y, r))
        
        self._log_debug(f"Padrões de alerta detectados: {len(pontos_validos)} de {len(circulos_unicos)} candidatos")
        return pontos_validos
    
    def _log_debug(self, message: str):
        """Log de debug interno."""
        if self.debug:
            print(f"DEBUG: {message}")
        self.logger.debug(message)
    
    def _validar_ponto_circular_rigoroso(self, gray: np.ndarray, x: int, y: int, r: int, h: int, w: int) -> bool:
        """Validação rigorosa de ponto circular."""
        # Verificar se está dentro da imagem
        if x-r < 0 or y-r < 0 or x+r >= w or y+r >= h:
            return False
            
        # Extrair região do ponto
        roi = gray[y-r:y+r+1, x-r:x+r+1]
        if roi.size == 0:
            return False
            
        # 1. Verificar contraste suficiente
        roi_std = np.std(roi)
        if roi_std < 10:
            return False
            
        # 2. Verificar formato circular básico
        center_val = gray[y, x]
        edge_vals = []
        for angle in range(0, 360, 45):
            px = int(x + r * np.cos(np.radians(angle)))
            py = int(y + r * np.sin(np.radians(angle)))
            if 0 <= py < h and 0 <= px < w:
                edge_vals.append(gray[py, px])
        
        if edge_vals and len(edge_vals) >= 4:
            edge_mean = np.mean(edge_vals)
            # Ponto tátil deve ter centro diferente da borda
            return abs(center_val - edge_mean) > 15
            
        return False
    
    def _remove_duplicate_circles(self, circles: List) -> List:
        """Remove círculos duplicados ou muito próximos."""
        if len(circles) <= 1:
            return circles
        
        unique_circles = []
        for (x, y, r) in circles:
            is_duplicate = False
            for (ux, uy, ur) in unique_circles:
                distance = np.sqrt((x - ux)**2 + (y - uy)**2)
                if distance < min(r, ur) * 1.5:  # Se muito próximos
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_circles.append((x, y, r))
        
        return unique_circles
    
    def _validar_densidade_pontos(self, pontos: List) -> List:
        """Valida se os pontos formam um padrão de densidade típico de piso tátil."""
        if len(pontos) < 3:
            return []
        
        # Verificar se há pelo menos um cluster com densidade adequada
        region_size = self.validation_params['region_size']
        min_density = self.validation_params['min_density_circles']
        
        valid_clusters = []
        
        for i, (x, y, r) in enumerate(pontos):
            # Contar pontos na região ao redor
            nearby_count = 0
            for j, (x2, y2, r2) in enumerate(pontos):
                if i != j:
                    distance = np.sqrt((x - x2)**2 + (y - y2)**2)
                    if distance <= region_size:
                        nearby_count += 1
            
            # Se há densidade suficiente, este ponto é válido
            if nearby_count >= min_density - 1:
                valid_clusters.append((x, y, r))
        
        return valid_clusters
    
    def _detectar_linhas_tateis(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta linhas direcionais com abordagem MUITO conservadora para evitar falsos positivos.
        
        Args:
            gray: Imagem em escala de cinza
            
        Returns:
            Lista de linhas detectadas (x1, y1, x2, y2)
        """
        # Só detectar linhas se necessário (poucos pontos detectados)
        # Esta função agora é muito mais conservadora
        
        linhas_validas = []
        
        # Pré-processamento suave
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Filtro bilateral para suavizar mantendo bordas
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Detecção de bordas mais conservadora
        edges = cv2.Canny(bilateral, 40, 120)
        
        # Detectar linhas para CAMINHOS COMPLETOS
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,        # Threshold mais baixo para detectar mais
            minLineLength=20,    # Linhas menores para capturar segmentos
            maxLineGap=15        # Gap maior para conectar linhas quebradas
        )
        
        if lines is not None:
            # Filtrar apenas linhas bem definidas (horizontais/verticais)
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calcular comprimento e ângulo
                dx = x2 - x1
                dy = y2 - y1
                length = np.sqrt(dx*dx + dy*dy)
                
                if length < 15:  # Linha muito curta
                    continue
                    
                angle = np.abs(np.arctan2(dy, dx) * 180 / np.pi)
                
                # Aceitar linhas horizontais, verticais E diagonais
                is_horizontal = (angle < 20 or angle > 160)
                is_vertical = (70 < angle < 110)
                is_diagonal = (35 < angle < 55) or (125 < angle < 145)
                
                if is_horizontal or is_vertical or is_diagonal:
                    linhas_validas.append((x1, y1, x2, y2))
                    
                    # Aumentar limite para caminhos completos
                    if len(linhas_validas) >= 30:
                        break
        
        self._log_debug(f"Padrões direcionais detectados: {len(linhas_validas)} (modo conservador)")
        return linhas_validas
        
        # Configuração 1: Linhas longas
        lines1 = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=self.hough_lines_params['threshold'],
            minLineLength=self.hough_lines_params['min_line_length'],
            maxLineGap=self.hough_lines_params['max_line_gap']
        )
        
        # Configuração 2: Linhas mais curtas mas com maior threshold
        lines2 = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=int(self.hough_lines_params['threshold'] * 1.5),
            minLineLength=int(self.hough_lines_params['min_line_length'] * 0.7),
            maxLineGap=3
        )
        
        # Combinar resultados
        if lines1 is not None:
            all_lines.extend([tuple(line[0]) for line in lines1])
        if lines2 is not None:
            all_lines.extend([tuple(line[0]) for line in lines2])
        
        if not all_lines:
            return []
        
        # Filtrar linhas válidas e agrupar paralelas
        linhas_validadas = self._filtrar_e_validar_linhas(all_lines, gray)
        
        return linhas_validadas
    
    def _filtrar_e_validar_linhas(self, lines: List, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Filtra e valida linhas para encontrar padrões de piso tátil direcional.
        """
        if len(lines) < 2:
            return []
        
        # Remover linhas muito curtas ou com ângulos extremos
        filtered_lines = []
        for (x1, y1, x2, y2) in lines:
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if length < 15:  # Muito curta
                continue
                
            # Calcular ângulo
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Filtrar linhas muito horizontais ou muito verticais (geralmente ruído)
            if 10 < angle < 80 or 100 < angle < 170:  # Manter apenas linhas com ângulos razoáveis
                # Validar se a linha passa por região com textura adequada
                if self._validar_linha_textura(x1, y1, x2, y2, gray):
                    filtered_lines.append((x1, y1, x2, y2))
        
        if len(filtered_lines) < 2:
            return []
        
        # Agrupar linhas paralelas
        parallel_groups = self._agrupar_linhas_paralelas(filtered_lines)
        
        # Retornar apenas grupos com densidade suficiente
        valid_lines = []
        min_parallel = self.validation_params['min_density_lines']
        
        for group in parallel_groups:
            if len(group) >= min_parallel:
                valid_lines.extend(group)
        
        return valid_lines
    
    def _validar_linha_textura(self, x1: int, y1: int, x2: int, y2: int, gray: np.ndarray) -> bool:
        """Valida se uma linha passa por região com textura de piso tátil."""
        # Criar máscara da linha
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.line(mask, (x1, y1), (x2, y2), 255, 3)  # Linha ligeiramente mais espessa
        
        # Extrair região da linha
        line_region = cv2.bitwise_and(gray, mask)
        
        # Calcular estatísticas da região
        pixels = line_region[line_region > 0]
        if len(pixels) < 10:
            return False
        
        # Verificar variação de intensidade (textura)
        std_dev = np.std(pixels)
        mean_intensity = np.mean(pixels)
        
        # Linhas de piso tátil têm textura específica
        if std_dev > 15 and 50 < mean_intensity < 200:
            return True
        
        return False
    
    def _agrupar_linhas_paralelas(self, lines: List) -> List[List]:
        """Agrupa linhas em conjuntos paralelos."""
        if len(lines) < 2:
            return [lines] if lines else []
        
        groups = []
        used = set()
        
        angle_tolerance = 15  # graus
        
        for i, line1 in enumerate(lines):
            if i in used:
                continue
                
            x1, y1, x2, y2 = line1
            angle1 = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            group = [line1]
            used.add(i)
            
            # Procurar linhas paralelas
            for j, line2 in enumerate(lines):
                if j <= i or j in used:
                    continue
                    
                x3, y3, x4, y4 = line2
                angle2 = np.arctan2(y4 - y3, x4 - x3) * 180 / np.pi
                
                # Verificar se são paralelas
                angle_diff = abs(angle1 - angle2)
                if angle_diff < angle_tolerance or angle_diff > (180 - angle_tolerance):
                    # Verificar se estão próximas (não muito distantes)
                    mid1_x, mid1_y = (x1 + x2) / 2, (y1 + y2) / 2
                    mid2_x, mid2_y = (x3 + x4) / 2, (y3 + y4) / 2
                    distance = np.sqrt((mid1_x - mid2_x)**2 + (mid1_y - mid2_y)**2)
                    
                    if distance < 100:  # Próximas o suficiente
                        group.append(line2)
                        used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _validar_ponto_tatil_avancado(self, gray: np.ndarray, x: int, y: int, r: int) -> bool:
        """
        Validação avançada se um círculo detectado é realmente um ponto tátil.
        
        Args:
            gray: Imagem em escala de cinza
            x, y: Centro do círculo
            r: Raio do círculo
            
        Returns:
            True se o ponto é válido como tátil
        """
        h, w = gray.shape
        margin = r + 5
        
        # Verificar se está dentro das margens da imagem
        if x - margin < 0 or x + margin >= w or y - margin < 0 or y + margin >= h:
            return False
        
        # Extrair região do círculo e região ao redor
        mask_circle = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask_circle, (x, y), r, 255, -1)
        
        mask_ring = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask_ring, (x, y), r + 5, 255, -1)
        cv2.circle(mask_ring, (x, y), r, 0, -1)
        
        # Calcular estatísticas
        circle_mean = cv2.mean(gray, mask=mask_circle)[0]
        ring_mean = cv2.mean(gray, mask=mask_ring)[0]
        
        # 1. Verificar contraste (pontos táteis têm contraste com o entorno)
        contrast = abs(circle_mean - ring_mean)
        if contrast < 20:  # Contraste mínimo
            return False
        
        # 2. Verificar se não é muito escuro ou muito claro (ruído)
        if circle_mean < 30 or circle_mean > 220:
            return False
        
        # 3. Verificar circularidade usando contornos
        roi = gray[y-r:y+r, x-r:x+r]
        if roi.size == 0:
            return False
        
        # Detectar bordas na ROI
        edges = cv2.Canny(roi, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Verificar se há contorno circular
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 10:  # Área mínima
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.6:  # Relativamente circular
                            return True
        
        return False
    
    def _filtrar_linhas_paralelas(self, lines: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Método mantido para compatibilidade - use _filtrar_e_validar_linhas.
        """
        return self._filtrar_e_validar_linhas([tuple(line[0]) for line in lines], None)
    
    def _criar_frame_resultado(self, frame: np.ndarray, pontos: List[Tuple[int, int, int]], 
                              linhas: List[Tuple[int, int, int, int]], tipo: str = "") -> np.ndarray:
        """
        Cria frame resultado com as detecções marcadas.
        
        Args:
            frame: Frame original
            pontos: Lista de pontos detectados
            linhas: Lista de linhas detectadas
            tipo: Tipo de piso detectado
            
        Returns:
            Frame com detecções marcadas
        """
        resultado = frame.copy()
        
        # Desenhar pontos detectados com diferentes cores por qualidade
        for i, (x, y, r) in enumerate(pontos):
            # Cor baseada na confiança (verde para alta confiança)
            cor_ponto = (0, 255, 0) if i < len(pontos)//2 else (0, 255, 255)
            cv2.circle(resultado, (x, y), r, cor_ponto, 2)
            cv2.circle(resultado, (x, y), 2, cor_ponto, 3)
            
            # Numerar pontos se em debug
            if self.debug:
                cv2.putText(resultado, str(i+1), (x-10, y-r-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor_ponto, 1)
        
        # Desenhar linhas detectadas
        for i, (x1, y1, x2, y2) in enumerate(linhas):
            cv2.line(resultado, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Marcar extremidades se em debug
            if self.debug:
                cv2.circle(resultado, (x1, y1), 3, (255, 0, 0), -1)
                cv2.circle(resultado, (x2, y2), 3, (255, 0, 0), -1)
        
        # Adicionar informações detalhadas
        h, w = frame.shape[:2]
        texto_principal = f"PISO TATIL {tipo.upper()}: {len(pontos)} pontos, {len(linhas)} linhas"
        cv2.putText(resultado, texto_principal, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Adicionar confiança
        if len(pontos) >= 4:
            confianca = "ALTA"
            cor_conf = (0, 255, 0)
        elif len(pontos) >= 2 or len(linhas) >= 3:
            confianca = "MEDIA"
            cor_conf = (0, 255, 255)
        else:
            confianca = "BAIXA"
            cor_conf = (0, 0, 255)
            
        cv2.putText(resultado, f"Confianca: {confianca}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_conf, 2)
        
        # Adicionar área de detecção se houver pontos
        if len(pontos) >= 2:
            # Calcular região que contém os pontos
            xs = [x for x, y, r in pontos]
            ys = [y for x, y, r in pontos]
            
            min_x, max_x = min(xs) - 20, max(xs) + 20
            min_y, max_y = min(ys) - 20, max(ys) + 20
            
            cv2.rectangle(resultado, (min_x, min_y), (max_x, max_y), (255, 255, 0), 2)
            cv2.putText(resultado, "AREA PISO TATIL", (min_x, min_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return resultado
    
    def configurar_parametros(self, **kwargs):
        """
        Permite configurar parâmetros de detecção dinamicamente.
        
        Args:
            **kwargs: Parâmetros a serem alterados
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"Parâmetro {key} atualizado para {value}")
    
    def ajustar_sensibilidade(self, nivel: str = "medio"):
        """
        Ajusta a sensibilidade da detecção.
        
        Args:
            nivel: "baixo" (mais restritivo), "medio", "alto" (mais sensível)
        """
        if nivel == "alto":
            # Mais sensível - detecta mais facilmente
            self.hough_circles_params['param2'] = 20
            self.validation_params['min_density_circles'] = 2
            self.validation_params['min_density_lines'] = 2
            self.hough_lines_params['threshold'] = 60
            
        elif nivel == "baixo":
            # Mais restritivo - só detecta com alta confiança
            self.hough_circles_params['param2'] = 10
            self.validation_params['min_density_circles'] = 5
            self.validation_params['min_density_lines'] = 4
            self.hough_lines_params['threshold'] = 120
            
        else:  # medio
            # Configuração balanceada
            self.hough_circles_params['param2'] = 15
            self.validation_params['min_density_circles'] = 3
            self.validation_params['min_density_lines'] = 3
            self.hough_lines_params['threshold'] = 80
        
        self.logger.info(f"Sensibilidade ajustada para: {nivel}")
    
    def carregar_modelo_yolo(self, model_path: str) -> bool:
        """
        Carrega um modelo YOLO treinado para detecção.
        
        Args:
            model_path: Caminho para o arquivo .pt do modelo
            
        Returns:
            True se carregado com sucesso
        """
        if not YOLO_AVAILABLE:
            self.logger.error("ultralytics não está instalado. Execute: pip install ultralytics")
            return False
        
        try:
            self._inicializar_yolo(model_path)
            return self.use_yolo
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo YOLO: {e}")
            return False
    
    def desabilitar_yolo(self):
        """Desabilita o uso do YOLO e força uso do OpenCV."""
        self.use_yolo = False
        self.yolo_detector = None
        self.logger.info("YOLO desabilitado - usando apenas OpenCV")
    
    def habilitar_yolo(self) -> bool:
        """
        Tenta habilitar YOLO procurando por modelo treinado.
        
        Returns:
            True se YOLO foi habilitado com sucesso
        """
        if not self.use_yolo:
            self._buscar_modelo_treinado()
        
        return self.use_yolo
    
    def status_detectores(self) -> dict:
        """
        Retorna status dos detectores disponíveis.
        
        Returns:
            Dict com informações sobre detectores
        """
        return {
            "yolo_disponivel": YOLO_AVAILABLE,
            "yolo_ativo": self.use_yolo,
            "modelo_yolo": str(self.yolo_detector.model_path) if self.yolo_detector else None,
            "opencv_ativo": True,
            "modo_debug": self.debug
        }
    
    def detectar_com_metodo(self, frame: np.ndarray, metodo: str = "auto") -> Optional[np.ndarray]:
        """
        Detecta usando método específico.
        
        Args:
            frame: Frame de entrada
            metodo: "auto", "yolo", "opencv"
            
        Returns:
            Frame com detecções ou None
        """
        if metodo == "yolo":
            return self._detectar_com_yolo(frame)
        elif metodo == "opencv":
            return self._detectar_com_opencv(frame)
        else:  # auto
            return self.detectar_piso_tatil(frame)
    
    def gerar_mapa_ambiente(self, frame: np.ndarray, 
                           resolucao: Tuple[int, int] = (20, 20),
                           salvar_csv: bool = True,
                           arquivo_csv: str = "resultados/mapa_piso_tatil.csv",
                           refinar_caminhos: bool = True,
                           normalizar_tamanhos: bool = True) -> Optional[np.ndarray]:
        """
        Detecta pisos táteis e gera mapa 2D do ambiente.
        
        Args:
            frame: Frame de entrada
            resolucao: Resolução do mapa 2D (largura, altura)
            salvar_csv: Se deve salvar arquivo CSV
            arquivo_csv: Caminho do arquivo CSV
            refinar_caminhos: Se deve criar caminhos contínuos
            normalizar_tamanhos: Se deve normalizar tamanhos dos segmentos
            
        Returns:
            Array 2D do mapa ou None se erro
        """
        if not self.use_yolo or self.yolo_detector is None:
            self.logger.error("Geração de mapa requer detector YOLO ativo")
            return None
        
        try:
            # Configurar resolução do mapa
            self.mapa_generator.resolucao_mapa = resolucao
            
            # Fazer detecção YOLO para obter resultados brutos
            results = self.yolo_detector.model(frame, conf=self.yolo_detector.confidence_threshold, 
                                             iou=0.3, max_det=1000, verbose=False)
            
            # Processar e gerar mapa
            mapa = self.mapa_generator.processar_imagem_completa(
                frame, results, salvar_csv, arquivo_csv, refinar_caminhos, normalizar_tamanhos
            )
            
            return mapa
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar mapa: {e}")
            return None
