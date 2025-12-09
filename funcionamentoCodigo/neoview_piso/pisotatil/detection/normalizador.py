"""
Módulo para normalização e subdivisão de segmentos grandes no mapa de piso tátil.

Implementa algoritmos para:
1. Detectar segmentos muito grandes comparados à média
2. Subdividir segmentos grandes em partes uniformes  
3. Manter consistência no tamanho dos blocos
4. Preservar a forma e orientação dos caminhos
"""

import numpy as np
import cv2
from typing import List, Tuple, Dict, Optional
from scipy.ndimage import label, center_of_mass
from sklearn.cluster import KMeans

class NormalizadorSegmentos:
    """
    Classe para normalizar tamanhos de segmentos no mapa de piso tátil.
    """
    
    def __init__(self, fator_subdivisao: float = 1.3, tamanho_minimo: int = 1):
        """
        Inicializa o normalizador.
        
        Args:
            fator_subdivisao: Fator que determina quando subdividir (segmento > menor * fator)
            tamanho_minimo: Tamanho mínimo para considerar um segmento válido
        """
        self.fator_subdivisao = fator_subdivisao
        self.tamanho_minimo = tamanho_minimo
        self.tamanho_ideal_bloco = 1  # Cada bloco deveria ser 1 célula
        
    def normalizar_mapa(self, mapa: np.ndarray) -> np.ndarray:
        """
        Normaliza o mapa subdividindo segmentos grandes.
        
        Args:
            mapa: Mapa com segmentos de tamanhos variados
            
        Returns:
            Mapa com segmentos de tamanhos mais uniformes
        """
        mapa_normalizado = mapa.copy()
        
        print("🔧 NORMALIZANDO TAMANHOS DOS SEGMENTOS...")
        
        # Processar cada tipo de piso separadamente
        for tipo_piso in [1, 2, 3]:  # horizontal, vertical, alerta
            if np.sum(mapa == tipo_piso) == 0:
                continue
                
            print(f"   📏 Processando tipo {tipo_piso}...")
            
            # Extrair segmentos do tipo atual
            mapa_tipo = (mapa == tipo_piso).astype(np.uint8)
            segmentos = self._extrair_segmentos(mapa_tipo)
            
            if len(segmentos) == 0:
                continue
                
            # Calcular estatísticas dos tamanhos
            tamanhos = [seg['tamanho'] for seg in segmentos]
            tamanho_medio = np.mean(tamanhos)
            tamanho_mediano = np.median(tamanhos)
            tamanho_minimo_encontrado = min(tamanhos)
            
            # Estratégia: usar o menor segmento como referência ideal
            # Segmentos maiores devem ser subdivididos para esse tamanho
            tamanho_ref = max(tamanho_minimo_encontrado, self.tamanho_ideal_bloco)
            
            print(f"      Segmentos encontrados: {len(segmentos)}")
            print(f"      Tamanhos individuais: {tamanhos}")
            print(f"      Menor tamanho: {tamanho_minimo_encontrado}")
            print(f"      Tamanho médio: {tamanho_medio:.1f}")
            print(f"      Tamanho ideal (referência): {tamanho_ref:.1f}")
            
            # Identificar e subdividir segmentos grandes
            threshold = tamanho_ref * self.fator_subdivisao
            segmentos_grandes = [s for s in segmentos if s['tamanho'] > threshold]
            
            if segmentos_grandes:
                print(f"      Segmentos grandes para subdividir: {len(segmentos_grandes)}")
                
                for segmento in segmentos_grandes:
                    # Remover segmento original do mapa
                    mapa_normalizado[segmento['mask']] = 0
                    
                    # Subdividir e adicionar partes
                    partes = self._subdividir_segmento(segmento, tamanho_ref, tipo_piso)
                    
                    for parte in partes:
                        mapa_normalizado[parte['y'], parte['x']] = tipo_piso
        
        return mapa_normalizado
    
    def _extrair_segmentos(self, mapa_binario: np.ndarray) -> List[Dict]:
        """Extrai informações de todos os segmentos conectados."""
        # Encontrar componentes conectados
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mapa_binario)
        
        segmentos = []
        
        for i in range(1, num_labels):  # Pular background (0)
            # Máscara do segmento
            mask = (labels == i)
            
            # Extrair informações
            area = stats[i, cv2.CC_STAT_AREA]
            bbox = (stats[i, cv2.CC_STAT_LEFT], 
                   stats[i, cv2.CC_STAT_TOP],
                   stats[i, cv2.CC_STAT_WIDTH], 
                   stats[i, cv2.CC_STAT_HEIGHT])
            centroid = (centroids[i, 0], centroids[i, 1])
            
            # Extrair coordenadas do segmento
            coords = np.where(mask)
            pontos = list(zip(coords[1], coords[0]))  # (x, y)
            
            segmento = {
                'id': i,
                'tamanho': area,
                'bbox': bbox,
                'centroid': centroid,
                'mask': mask,
                'pontos': pontos,
                'largura': bbox[2],
                'altura': bbox[3]
            }
            
            if area >= self.tamanho_minimo:
                segmentos.append(segmento)
        
        return segmentos
    
    def _subdividir_segmento(self, segmento: Dict, tamanho_ref: float, tipo_piso: int) -> List[Dict]:
        """Subdivide um segmento grande em partes menores."""
        pontos = segmento['pontos']
        tamanho_atual = segmento['tamanho']
        
        # Calcular número ideal de subdivisões
        num_divisoes = max(2, int(np.round(tamanho_atual / tamanho_ref)))
        
        # Determinar estratégia de subdivisão baseada no tipo e forma
        if tipo_piso == 1:  # horizontal
            return self._subdividir_horizontal(pontos, num_divisoes)
        elif tipo_piso == 2:  # vertical  
            return self._subdividir_vertical(pontos, num_divisoes)
        else:  # alerta (clusters)
            return self._subdividir_cluster(pontos, num_divisoes)
    
    def _subdividir_horizontal(self, pontos: List[Tuple[int, int]], num_divisoes: int) -> List[Dict]:
        """Subdivide segmento horizontal em partes."""
        if not pontos:
            return []
            
        # Ordenar por coordenada X (horizontal)
        pontos_ordenados = sorted(pontos, key=lambda p: p[0])
        
        # Dividir em grupos
        tamanho_grupo = len(pontos_ordenados) // num_divisoes
        partes = []
        
        for i in range(num_divisoes):
            inicio = i * tamanho_grupo
            if i == num_divisoes - 1:  # Última divisão pega o resto
                fim = len(pontos_ordenados)
            else:
                fim = (i + 1) * tamanho_grupo
            
            grupo = pontos_ordenados[inicio:fim]
            
            if grupo:
                # Calcular ponto representativo (centro do grupo)
                x_medio = int(np.mean([p[0] for p in grupo]))
                y_medio = int(np.mean([p[1] for p in grupo]))
                
                partes.append({
                    'x': x_medio,
                    'y': y_medio,
                    'pontos_originais': grupo
                })
        
        return partes
    
    def _subdividir_vertical(self, pontos: List[Tuple[int, int]], num_divisoes: int) -> List[Dict]:
        """Subdivide segmento vertical em partes."""
        if not pontos:
            return []
            
        # Ordenar por coordenada Y (vertical)
        pontos_ordenados = sorted(pontos, key=lambda p: p[1])
        
        # Dividir em grupos
        tamanho_grupo = len(pontos_ordenados) // num_divisoes
        partes = []
        
        for i in range(num_divisoes):
            inicio = i * tamanho_grupo
            if i == num_divisoes - 1:  # Última divisão pega o resto
                fim = len(pontos_ordenados)
            else:
                fim = (i + 1) * tamanho_grupo
            
            grupo = pontos_ordenados[inicio:fim]
            
            if grupo:
                # Calcular ponto representativo (centro do grupo)
                x_medio = int(np.mean([p[0] for p in grupo]))
                y_medio = int(np.mean([p[1] for p in grupo]))
                
                partes.append({
                    'x': x_medio,
                    'y': y_medio,
                    'pontos_originais': grupo
                })
        
        return partes
    
    def _subdividir_cluster(self, pontos: List[Tuple[int, int]], num_divisoes: int) -> List[Dict]:
        """Subdivide cluster de alerta usando K-means."""
        if not pontos or len(pontos) < num_divisoes:
            return [{'x': p[0], 'y': p[1], 'pontos_originais': [p]} for p in pontos]
        
        # Converter para array numpy
        pontos_array = np.array(pontos)
        
        # Aplicar K-means para agrupar
        kmeans = KMeans(n_clusters=num_divisoes, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(pontos_array)
        
        partes = []
        
        for i in range(num_divisoes):
            # Pontos do cluster atual
            mask_cluster = (clusters == i)
            pontos_cluster = pontos_array[mask_cluster]
            
            if len(pontos_cluster) > 0:
                # Centro do cluster
                x_medio = int(np.mean(pontos_cluster[:, 0]))
                y_medio = int(np.mean(pontos_cluster[:, 1]))
                
                partes.append({
                    'x': x_medio,
                    'y': y_medio,
                    'pontos_originais': [tuple(p) for p in pontos_cluster]
                })
        
        return partes
    
    def imprimir_estatisticas_normalizacao(self, mapa_original: np.ndarray, 
                                          mapa_normalizado: np.ndarray):
        """Imprime estatísticas da normalização."""
        print("\n📊 ESTATÍSTICAS DA NORMALIZAÇÃO:")
        print("=" * 45)
        
        for tipo_piso, nome in [(1, "Horizontal"), (2, "Vertical"), (3, "Alerta")]:
            # Contar segmentos originais
            mapa_orig_tipo = (mapa_original == tipo_piso).astype(np.uint8)
            num_labels_orig, _, stats_orig, _ = cv2.connectedComponentsWithStats(mapa_orig_tipo)
            segmentos_orig = num_labels_orig - 1  # Excluir background
            
            # Contar segmentos normalizados
            mapa_norm_tipo = (mapa_normalizado == tipo_piso).astype(np.uint8)
            num_labels_norm, _, stats_norm, _ = cv2.connectedComponentsWithStats(mapa_norm_tipo)
            segmentos_norm = num_labels_norm - 1  # Excluir background
            
            if segmentos_orig > 0 or segmentos_norm > 0:
                print(f"\n{nome.upper()}:")
                print(f"   Segmentos originais: {segmentos_orig}")
                print(f"   Segmentos normalizados: {segmentos_norm}")
                
                if segmentos_orig > 0:
                    # Tamanhos médios
                    tamanhos_orig = stats_orig[1:, cv2.CC_STAT_AREA]  # Excluir background
                    tamanho_medio_orig = np.mean(tamanhos_orig) if len(tamanhos_orig) > 0 else 0
                    
                    tamanhos_norm = stats_norm[1:, cv2.CC_STAT_AREA]  # Excluir background  
                    tamanho_medio_norm = np.mean(tamanhos_norm) if len(tamanhos_norm) > 0 else 0
                    
                    print(f"   Tamanho médio original: {tamanho_medio_orig:.1f}")
                    print(f"   Tamanho médio normalizado: {tamanho_medio_norm:.1f}")
                    
                    # Variação nos tamanhos
                    if len(tamanhos_orig) > 1:
                        cv_orig = np.std(tamanhos_orig) / tamanho_medio_orig if tamanho_medio_orig > 0 else 0
                        cv_norm = np.std(tamanhos_norm) / tamanho_medio_norm if tamanho_medio_norm > 0 else 0
                        
                        print(f"   Coef. variação original: {cv_orig:.2f}")
                        print(f"   Coef. variação normalizado: {cv_norm:.2f}")
                        
                        if cv_norm < cv_orig:
                            print(f"   ✅ Uniformidade melhorada em {((cv_orig - cv_norm) / cv_orig * 100):.1f}%")
