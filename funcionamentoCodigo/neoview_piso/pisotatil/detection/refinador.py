"""
Módulo para refinamento e criação de caminhos contínuos no mapa de piso tátil.

Implementa algoritmos para:
1. Conectar blocos isolados em caminhos contínuos
2. Suavizar trajetórias 
3. Preencher lacunas entre detecções
4. Criar rotas navegáveis
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional
from scipy.ndimage import binary_dilation, binary_erosion
from sklearn.cluster import DBSCAN
from .tipos import PisoTatil

class RefinadorCaminhos:
    """
    Classe para refinar mapas de piso tátil criando caminhos contínuos.
    """
    
    def __init__(self):
        self.kernel_conectar = np.ones((3, 3), np.uint8)
        self.kernel_suavizar = np.ones((5, 5), np.uint8)
        
    def refinar_mapa(self, mapa: np.ndarray, 
                    conectar_gaps: bool = True,
                    suavizar_caminhos: bool = True,
                    min_tamanho_segmento: int = 3) -> np.ndarray:
        """
        Refina o mapa criando caminhos contínuos.
        
        Args:
            mapa: Mapa original com detecções esparsas
            conectar_gaps: Se deve conectar lacunas entre blocos
            suavizar_caminhos: Se deve suavizar os caminhos
            min_tamanho_segmento: Tamanho mínimo para manter um segmento
            
        Returns:
            Mapa refinado com caminhos contínuos
        """
        mapa_refinado = mapa.copy()
        
        # 1. Separar por tipos de piso
        mapa_horizontal = (mapa == 1).astype(np.uint8)
        mapa_vertical = (mapa == 2).astype(np.uint8)
        mapa_alerta = (mapa == 3).astype(np.uint8)
        
        print("🔧 REFINANDO CAMINHOS...")
        
        # 2. Refinar cada tipo separadamente
        if conectar_gaps:
            print("   🔗 Conectando lacunas...")
            mapa_horizontal = self._conectar_lacunas_horizontais(mapa_horizontal)
            mapa_vertical = self._conectar_lacunas_verticais(mapa_vertical)
            # Conectar alertas próximos para formar clusters contínuos
            mapa_alerta = self._conectar_alertas_proximos(mapa_alerta)
        
        if suavizar_caminhos:
            print("   🪄 Suavizando caminhos...")
            mapa_horizontal = self._suavizar_caminho(mapa_horizontal, direcao='horizontal')
            mapa_vertical = self._suavizar_caminho(mapa_vertical, direcao='vertical')
        
        # 3. Remover segmentos muito pequenos
        print("   🧹 Removendo segmentos pequenos...")
        mapa_horizontal = self._remover_segmentos_pequenos(mapa_horizontal, min_tamanho_segmento)
        mapa_vertical = self._remover_segmentos_pequenos(mapa_vertical, min_tamanho_segmento)
        # Alertas mantêm tamanho mínimo de 1 para preservar blocos individuais
        mapa_alerta = self._remover_segmentos_pequenos(mapa_alerta, 1)
        
        # 4. Recompor mapa final
        mapa_refinado = np.zeros_like(mapa)
        mapa_refinado[mapa_horizontal == 1] = 1  # horizontal
        mapa_refinado[mapa_vertical == 1] = 2    # vertical
        mapa_refinado[mapa_alerta == 1] = 3      # alerta
        
        return mapa_refinado
    
    def _conectar_lacunas_horizontais(self, mapa_binario: np.ndarray) -> np.ndarray:
        """Conecta lacunas em caminhos horizontais."""
        resultado = mapa_binario.copy()
        
        for row in range(mapa_binario.shape[0]):
            linha = mapa_binario[row, :]
            posicoes = np.where(linha == 1)[0]
            
            if len(posicoes) >= 2:
                # Conectar pontos próximos (distância <= 3 células)
                for i in range(len(posicoes) - 1):
                    inicio = posicoes[i]
                    fim = posicoes[i + 1]
                    
                    if fim - inicio <= 4:  # Gap de no máximo 3 células
                        resultado[row, inicio:fim+1] = 1
        
        return resultado
    
    def _conectar_lacunas_verticais(self, mapa_binario: np.ndarray) -> np.ndarray:
        """Conecta lacunas em caminhos verticais."""
        resultado = mapa_binario.copy()
        
        for col in range(mapa_binario.shape[1]):
            coluna = mapa_binario[:, col]
            posicoes = np.where(coluna == 1)[0]
            
            if len(posicoes) >= 2:
                # Conectar pontos próximos (distância <= 3 células)
                for i in range(len(posicoes) - 1):
                    inicio = posicoes[i]
                    fim = posicoes[i + 1]
                    
                    if fim - inicio <= 4:  # Gap de no máximo 3 células
                        resultado[inicio:fim+1, col] = 1
        
        return resultado
    
    def _conectar_alertas_proximos(self, mapa_binario: np.ndarray) -> np.ndarray:
        """Conecta pontos de alerta muito próximos para formar clusters contínuos."""
        resultado = mapa_binario.copy()
        
        # Usar kernel menor para conectar apenas adjacentes ou muito próximos
        kernel = np.array([[1, 1, 1],
                          [1, 1, 1], 
                          [1, 1, 1]], dtype=np.uint8)
        
        # Aplicar dilatação mínima para conectar apenas gaps de 1 célula
        dilatado = cv2.dilate(resultado, kernel, iterations=1)
        
        return dilatado
    
    def _suavizar_caminho(self, mapa_binario: np.ndarray, direcao: str) -> np.ndarray:
        """Suaviza caminhos usando operações morfológicas."""
        if direcao == 'horizontal':
            # Kernel horizontal para suavização
            kernel = np.array([[0, 0, 0, 0, 0],
                              [1, 1, 1, 1, 1],
                              [0, 0, 0, 0, 0]], dtype=np.uint8)
        else:  # vertical
            # Kernel vertical para suavização  
            kernel = np.array([[0, 1, 0],
                              [0, 1, 0],
                              [0, 1, 0],
                              [0, 1, 0],
                              [0, 1, 0]], dtype=np.uint8)
        
        # Aplicar fechamento morfológico para suavizar
        suavizado = cv2.morphologyEx(mapa_binario, cv2.MORPH_CLOSE, kernel)
        
        return suavizado
    
    def _remover_segmentos_pequenos(self, mapa_binario: np.ndarray, 
                                   min_tamanho: int) -> np.ndarray:
        """Remove segmentos menores que o tamanho mínimo."""
        # Encontrar componentes conectados
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mapa_binario)
        
        resultado = np.zeros_like(mapa_binario)
        
        for i in range(1, num_labels):  # Pular background (0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_tamanho:
                resultado[labels == i] = 1
        
        return resultado
    
    def criar_caminhos_navegaveis(self, mapa: np.ndarray) -> List[List[Tuple[int, int]]]:
        """
        Cria lista de caminhos navegáveis a partir do mapa refinado.
        
        Args:
            mapa: Mapa refinado com caminhos contínuos
            
        Returns:
            Lista de caminhos, cada um sendo uma lista de coordenadas (x, y)
        """
        caminhos = []
        
        # Processar cada tipo de piso separadamente
        for tipo_piso in [1, 2, 3]:  # horizontal, vertical, alerta
            mapa_tipo = (mapa == tipo_piso).astype(np.uint8)
            
            # Encontrar componentes conectados
            num_labels, labels = cv2.connectedComponents(mapa_tipo)
            
            for i in range(1, num_labels):  # Pular background (0)
                # Extrair coordenadas do caminho
                coordenadas = np.where(labels == i)
                caminho = list(zip(coordenadas[1], coordenadas[0]))  # (x, y)
                
                if len(caminho) >= 2:  # Só manter caminhos com pelo menos 2 pontos
                    # Ordenar coordenadas para formar sequência lógica
                    if tipo_piso == 1:  # horizontal
                        caminho.sort(key=lambda p: p[0])  # Ordenar por x
                    elif tipo_piso == 2:  # vertical  
                        caminho.sort(key=lambda p: p[1])  # Ordenar por y
                    
                    caminhos.append(caminho)
        
        return caminhos
    
    def imprimir_estatisticas_refinamento(self, mapa_original: np.ndarray, 
                                         mapa_refinado: np.ndarray):
        """Imprime estatísticas do refinamento."""
        print("\n📊 ESTATÍSTICAS DO REFINAMENTO:")
        print("=" * 40)
        
        # Contar células por tipo - original
        orig_horizontal = np.sum(mapa_original == 1)
        orig_vertical = np.sum(mapa_original == 2) 
        orig_alerta = np.sum(mapa_original == 3)
        orig_total = orig_horizontal + orig_vertical + orig_alerta
        
        # Contar células por tipo - refinado
        ref_horizontal = np.sum(mapa_refinado == 1)
        ref_vertical = np.sum(mapa_refinado == 2)
        ref_alerta = np.sum(mapa_refinado == 3)
        ref_total = ref_horizontal + ref_vertical + ref_alerta
        
        print("ORIGINAL:")
        print(f"   Horizontal: {orig_horizontal} células")
        print(f"   Vertical: {orig_vertical} células") 
        print(f"   Alerta: {orig_alerta} células")
        print(f"   Total: {orig_total} células")
        
        print("\nREFINADO:")
        print(f"   Horizontal: {ref_horizontal} células (+{ref_horizontal - orig_horizontal})")
        print(f"   Vertical: {ref_vertical} células (+{ref_vertical - orig_vertical})")
        print(f"   Alerta: {ref_alerta} células (+{ref_alerta - orig_alerta})")
        print(f"   Total: {ref_total} células (+{ref_total - orig_total})")
        
        print(f"\nCONECTIVIDADE:")
        print(f"   Aumento total: {((ref_total / max(orig_total, 1)) - 1) * 100:.1f}%")
        print(f"   Taxa de preenchimento: {(ref_total / mapa_refinado.size) * 100:.1f}%")
