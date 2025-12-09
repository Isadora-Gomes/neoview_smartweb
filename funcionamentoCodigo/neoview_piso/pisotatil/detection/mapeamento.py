"""
Módulo para geração de mapas 2D a partir das detecções de piso tátil.

Converte detecções YOLO em arrays 2D estruturados representando o ambiente.
"""

import cv2
import numpy as np
import csv
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

# Importar o enum, refinador e normalizador
from .tipos import PisoTatil
from .refinador import RefinadorCaminhos
from .normalizador import NormalizadorSegmentos

@dataclass
class DeteccaoInfo:
    """Informações de uma detecção individual"""
    classe: PisoTatil
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confianca: float
    centro: Tuple[int, int]

class MapaPisoTatil:
    """
    Gerador de mapas 2D a partir de detecções de piso tátil.
    
    Converte detecções YOLO em uma representação estruturada do ambiente,
    criando um mapa 2D onde cada célula representa uma área e contém
    informações sobre o tipo de piso tátil presente.
    """
    
    def __init__(self, resolucao_mapa: Tuple[int, int] = (20, 20)):
        """
        Inicializa o gerador de mapas.
        
        Args:
            resolucao_mapa: Tamanho do mapa 2D em células (largura, altura)
        """
        self.resolucao_mapa = resolucao_mapa
        self.refinador = RefinadorCaminhos()
        self.normalizador = NormalizadorSegmentos(fator_subdivisao=1.8, tamanho_minimo=2)
        self.mapeamento_classes = {
            0: None,  # piso_tatil_direcional -> não mapeado (depende do ângulo)
            1: PisoTatil.alerta,  # piso_tatil_alerta
            2: PisoTatil.vertical,  # piso_tatil_direcional_vertical  
            3: PisoTatil.horizontal,  # piso_tatil_direcional_horizontal
            4: None   # piso_tatil -> não mapeado (genérico)
        }
        
    def extrair_deteccoes_yolo(self, results) -> List[DeteccaoInfo]:
        """
        Extrai informações das detecções YOLO.
        
        Args:
            results: Resultados do modelo YOLO
            
        Returns:
            Lista de DeteccaoInfo com informações estruturadas
        """
        deteccoes = []
        
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for box in boxes:
                # Extrair informações da bbox
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confianca = box.conf[0].cpu().numpy()
                classe_id = int(box.cls[0].cpu().numpy())
                
                # Converter para formato x, y, w, h
                x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                centro = (int(x + w/2), int(y + h/2))
                
                # Mapear classe para enum (se aplicável)
                classe_mapeada = self.mapeamento_classes.get(classe_id)
                if classe_mapeada is not None:
                    deteccao = DeteccaoInfo(
                        classe=classe_mapeada,
                        bbox=(x, y, w, h),
                        confianca=float(confianca),
                        centro=centro
                    )
                    deteccoes.append(deteccao)
        
        # Subdividir detecções grandes de alerta baseado no tamanho
        deteccoes = self._subdividir_deteccoes_grandes(deteccoes)
        
        return deteccoes
    
    def _subdividir_deteccoes_grandes(self, deteccoes: List[DeteccaoInfo]) -> List[DeteccaoInfo]:
        """
        Subdivide detecções de alerta grandes em múltiplos blocos menores.
        
        Args:
            deteccoes: Lista original de detecções
            
        Returns:
            Lista com detecções grandes subdivididas
        """
        # Separar detecções de alerta das outras
        alertas = [d for d in deteccoes if d.classe == PisoTatil.alerta]
        outras = [d for d in deteccoes if d.classe != PisoTatil.alerta]
        
        if len(alertas) < 2:
            return deteccoes  # Precisa de pelo menos 2 para comparar tamanhos
        
        # Calcular área de cada detecção de alerta
        areas = []
        for deteccao in alertas:
            x, y, w, h = deteccao.bbox
            area = w * h
            areas.append(area)
        
        # Encontrar tamanho de referência (menor área)
        area_min = min(areas)
        area_media = np.mean(areas)
        
        print(f"   📐 Analisando detecções de alerta:")
        print(f"      Quantidade: {len(alertas)}")
        print(f"      Áreas individuais: {areas}")
        print(f"      Área mínima: {area_min}")
        print(f"      Área média: {area_media:.1f}")
        
        deteccoes_finais = outras.copy()
        
        for i, deteccao in enumerate(alertas):
            area_atual = areas[i]
            
            # Se a área é muito maior que a mínima, subdividir
            ratio = area_atual / area_min
            if ratio > 1.6:  # Se é mais que 1.6x maior (mais agressivo)
                # Calcular quantos blocos deveria ser
                num_blocos = int(round(ratio))
                num_blocos = min(num_blocos, 6)  # Máximo 6 blocos por detecção
                print(f"      Subdividindo detecção {i+1} (área {area_atual}) em {num_blocos} blocos")
                
                # Gerar múltiplos centros dentro da bbox original
                x, y, w, h = deteccao.bbox
                blocos_subdivididos = self._gerar_blocos_subdividos(deteccao, num_blocos)
                deteccoes_finais.extend(blocos_subdivididos)
            else:
                # Manter como está
                deteccoes_finais.append(deteccao)
        
        return deteccoes_finais
    
    def _gerar_blocos_subdividos(self, deteccao_original: DeteccaoInfo, num_blocos: int) -> List[DeteccaoInfo]:
        """
        Gera múltiplos blocos a partir de uma detecção grande.
        Cria blocos adjacentes para formar um cluster contínuo sem buracos.
        
        Args:
            deteccao_original: Detecção original grande
            num_blocos: Número de blocos para gerar
            
        Returns:
            Lista de blocos subdivididos adjacentes
        """
        centro_original = deteccao_original.centro
        blocos = []
        
        # Tamanho padrão pequeno para cada bloco individual
        tamanho_bloco = 25  # Tamanho fixo para uniformidade
        
        # Estratégia: criar blocos adjacentes em formato de cluster compacto
        if num_blocos == 2:
            # 2 blocos: lado a lado horizontalmente (adjacentes)
            centros = [
                (centro_original[0] - tamanho_bloco//2, centro_original[1]),
                (centro_original[0] + tamanho_bloco//2, centro_original[1])
            ]
        elif num_blocos == 3:
            # 3 blocos: linha horizontal contínua
            centros = [
                (centro_original[0] - tamanho_bloco, centro_original[1]),
                (centro_original[0], centro_original[1]),
                (centro_original[0] + tamanho_bloco, centro_original[1])
            ]
        elif num_blocos == 4:
            # 4 blocos: quadrado 2x2 compacto
            offset = tamanho_bloco // 2
            centros = [
                (centro_original[0] - offset, centro_original[1] - offset),
                (centro_original[0] + offset, centro_original[1] - offset),
                (centro_original[0] - offset, centro_original[1] + offset),
                (centro_original[0] + offset, centro_original[1] + offset)
            ]
        elif num_blocos == 6:
            # 6 blocos: retângulo 2x3 compacto
            offset_x = tamanho_bloco // 2
            offset_y = tamanho_bloco
            centros = [
                (centro_original[0] - offset_x, centro_original[1] - offset_y),
                (centro_original[0] + offset_x, centro_original[1] - offset_y),
                (centro_original[0] - offset_x, centro_original[1]),
                (centro_original[0] + offset_x, centro_original[1]),
                (centro_original[0] - offset_x, centro_original[1] + offset_y),
                (centro_original[0] + offset_x, centro_original[1] + offset_y)
            ]
        else:
            # Para outros números: grade compacta
            if num_blocos <= 9:
                cols = 3
                rows = int(np.ceil(num_blocos / cols))
            else:
                cols = int(np.ceil(np.sqrt(num_blocos)))
                rows = int(np.ceil(num_blocos / cols))
            
            centros = []
            bloco_num = 0
            
            # Calcular offset inicial para centralizar a grade
            inicio_x = centro_original[0] - (cols - 1) * tamanho_bloco // 2
            inicio_y = centro_original[1] - (rows - 1) * tamanho_bloco // 2
            
            for row in range(rows):
                for col in range(cols):
                    if bloco_num >= num_blocos:
                        break
                    
                    centro_x = inicio_x + col * tamanho_bloco
                    centro_y = inicio_y + row * tamanho_bloco
                    centros.append((centro_x, centro_y))
                    bloco_num += 1
        
        # Criar detecções para cada centro com tamanho uniforme
        for i, (centro_x, centro_y) in enumerate(centros):
            novo_bloco = DeteccaoInfo(
                classe=PisoTatil.alerta,
                bbox=(centro_x - tamanho_bloco//2, centro_y - tamanho_bloco//2, 
                      tamanho_bloco, tamanho_bloco),
                confianca=deteccao_original.confianca * 0.9,
                centro=(centro_x, centro_y)
            )
            blocos.append(novo_bloco)
        
        return blocos
    
    def gerar_mapa_2d(self, deteccoes: List[DeteccaoInfo], 
                     dimensoes_imagem: Tuple[int, int]) -> np.ndarray:
        """
        Gera mapa 2D a partir das detecções.
        
        Args:
            deteccoes: Lista de detecções estruturadas
            dimensoes_imagem: (largura, altura) da imagem original
            
        Returns:
            Array 2D representando o mapa do ambiente
        """
        largura_img, altura_img = dimensoes_imagem
        largura_mapa, altura_mapa = self.resolucao_mapa
        
        # Criar mapa vazio (0 = sem piso tátil)
        mapa = np.zeros((altura_mapa, largura_mapa), dtype=int)
        
        # Calcular escala de conversão
        escala_x = largura_mapa / largura_img
        escala_y = altura_mapa / altura_img
        
        for deteccao in deteccoes:
            # Converter coordenadas da imagem para coordenadas do mapa
            centro_x, centro_y = deteccao.centro
            mapa_x = int(centro_x * escala_x)
            mapa_y = int(centro_y * escala_y)
            
            # Garantir que está dentro dos limites
            mapa_x = max(0, min(mapa_x, largura_mapa - 1))
            mapa_y = max(0, min(mapa_y, altura_mapa - 1))
            
            # Mapear enum para valor numérico
            if deteccao.classe == PisoTatil.horizontal:
                valor = 1
            elif deteccao.classe == PisoTatil.vertical:
                valor = 2
            elif deteccao.classe == PisoTatil.alerta:
                valor = 3
            else:
                valor = 0
            
            # Marcar no mapa (sobrescrever se necessário)
            mapa[mapa_y, mapa_x] = valor
        
        return mapa
    
    def salvar_mapa_csv(self, mapa: np.ndarray, caminho: str):
        """
        Salva o mapa em formato CSV.
        
        Args:
            mapa: Array 2D do mapa
            caminho: Caminho para salvar o arquivo CSV
        """
        with open(caminho, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Cabeçalho com informações
            writer.writerow(['# Mapa de Piso Tátil'])
            writer.writerow(['# 0=vazio', '1=horizontal', '2=vertical', '3=alerta'])
            writer.writerow(['# Resolução:', f'{self.resolucao_mapa[0]}x{self.resolucao_mapa[1]}'])
            writer.writerow([])  # Linha vazia
            
            # Dados do mapa
            for linha in mapa:
                writer.writerow(linha.tolist())
    
    def imprimir_mapa_console(self, mapa: np.ndarray):
        """
        Imprime o mapa no console de forma visual.
        
        Args:
            mapa: Array 2D do mapa
        """
        simbolos = {
            0: '·',  # vazio
            1: '─',  # horizontal  
            2: '│',  # vertical
            3: '●'   # alerta
        }
        
        print("🗺️  MAPA DE PISO TÁTIL")
        print("=" * 50)
        print("Legenda: · = vazio, ─ = horizontal, │ = vertical, ● = alerta")
        print()
        
        for i, linha in enumerate(mapa):
            linha_str = ""
            for j, valor in enumerate(linha):
                linha_str += simbolos.get(valor, '?') + " "
            print(f"{i:2d} │ {linha_str}")
        
        print()
        print("Estatísticas:")
        unique, counts = np.unique(mapa, return_counts=True)
        for valor, qtd in zip(unique, counts):
            if valor == 0:
                tipo = "vazio"
            elif valor == 1:
                tipo = "horizontal"
            elif valor == 2:
                tipo = "vertical"
            elif valor == 3:
                tipo = "alerta"
            else:
                tipo = "desconhecido"
            print(f"  {tipo}: {qtd} células")
    
    def processar_imagem_completa(self, frame: np.ndarray, results, 
                                 salvar_csv: bool = True, 
                                 arquivo_csv: str = "resultados/mapa_piso_tatil.csv",
                                 refinar_caminhos: bool = True,
                                 normalizar_tamanhos: bool = True) -> np.ndarray:
        """
        Processa uma imagem completa e gera o mapa 2D.
        
        Args:
            frame: Imagem original
            results: Resultados do YOLO
            salvar_csv: Se deve salvar o arquivo CSV
            arquivo_csv: Caminho para o arquivo CSV
            refinar_caminhos: Se deve refinar os caminhos para serem contínuos
            normalizar_tamanhos: Se deve normalizar tamanhos dos segmentos
            
        Returns:
            Array 2D do mapa gerado
        """
        # Extrair detecções
        deteccoes = self.extrair_deteccoes_yolo(results)
        print(f"📊 Detecções extraídas: {len(deteccoes)}")
        
        for i, det in enumerate(deteccoes):
            print(f"  {i+1}. {det.classe.value} (confiança: {det.confianca:.2f})")
        
        # Gerar mapa 2D básico
        altura, largura = frame.shape[:2]
        mapa_original = self.gerar_mapa_2d(deteccoes, (largura, altura))
        
        mapa_atual = mapa_original.copy()
        
        # Refinar caminhos se solicitado
        if refinar_caminhos:
            print(f"\n🔧 REFINANDO CAMINHOS PARA CONTINUIDADE...")
            mapa_atual = self.refinador.refinar_mapa(
                mapa_atual,
                conectar_gaps=True,
                suavizar_caminhos=True,
                min_tamanho_segmento=2
            )
            
            # Mostrar estatísticas do refinamento
            self.refinador.imprimir_estatisticas_refinamento(mapa_original, mapa_atual)
        
        # Normalizar tamanhos se solicitado
        if normalizar_tamanhos:
            print(f"\n📏 NORMALIZANDO TAMANHOS DOS SEGMENTOS...")
            mapa_pre_normalizacao = mapa_atual.copy()
            mapa_atual = self.normalizador.normalizar_mapa(mapa_atual)
            
            # Mostrar estatísticas da normalização
            self.normalizador.imprimir_estatisticas_normalizacao(mapa_pre_normalizacao, mapa_atual)
        
        # Imprimir no console
        self.imprimir_mapa_console(mapa_atual)
        
        # Salvar CSV se solicitado
        if salvar_csv:
            # Criar diretório se não existir
            Path(arquivo_csv).parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar mapas para comparação
            if refinar_caminhos or normalizar_tamanhos:
                # Salvar mapa final
                self.salvar_mapa_csv(mapa_atual, arquivo_csv)
                
                # Salvar mapa original para comparação
                arquivo_original = arquivo_csv.replace('.csv', '_original.csv')
                self.salvar_mapa_csv(mapa_original, arquivo_original)
                print(f"💾 Mapa original salvo em: {arquivo_original}")
                
                # Se houve normalização, salvar também o mapa só refinado
                if normalizar_tamanhos and refinar_caminhos:
                    arquivo_refinado = arquivo_csv.replace('.csv', '_refinado.csv')
                    self.salvar_mapa_csv(mapa_pre_normalizacao, arquivo_refinado)
                    print(f"💾 Mapa refinado salvo em: {arquivo_refinado}")
            else:
                self.salvar_mapa_csv(mapa_atual, arquivo_csv)
                
            print(f"💾 Mapa final salvo em: {arquivo_csv}")
        
        return mapa_atual
