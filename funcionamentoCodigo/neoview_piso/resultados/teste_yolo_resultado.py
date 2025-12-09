#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico do modelo YOLO treinado com as 5 classes.
Resultados salvos em resultados/
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from pisotatil.detection.piso_tatil import PisoTatil

def testar_yolo_treinado():
    """Testa o modelo YOLO treinado."""
    
    print("🤖 TESTE DO MODELO YOLO TREINADO")
    print("=" * 40)
    
    # Caminho do modelo treinado
    modelo_path = "../models/piso_tatil_detector4/weights/best.pt"
    imagem_teste = "../teste_piso_tatil.jpg"
    
    # Verificar arquivos
    if not os.path.exists(modelo_path):
        print(f"❌ Modelo não encontrado: {modelo_path}")
        return
    
    if not os.path.exists(imagem_teste):
        print(f"❌ Imagem não encontrada: {imagem_teste}")
        return
    
    print(f"✅ Modelo: {modelo_path}")
    print(f"✅ Imagem: {imagem_teste}")
    
    # Carregar imagem
    img = cv2.imread(imagem_teste)
    h, w = img.shape[:2]
    print(f"📐 Dimensões: {w}x{h}")
    
    # Testar com YOLO
    print("\n🔬 INICIANDO TESTE COM YOLO...")
    
    try:
        # Criar detector com modelo YOLO
        detector = PisoTatil(debug=True, yolo_model_path=modelo_path)
        
        # Status dos detectores
        status = detector.status_detectores()
        print(f"\n📊 YOLO Ativo: {'✅' if status['yolo_ativo'] else '❌'}")
        print(f"📁 Modelo: {status['modelo_yolo']}")
        
        # Detectar com YOLO específico
        print("\n🎯 DETECÇÃO COM YOLO...")
        resultado_yolo = detector._detectar_com_yolo(img)
        
        if resultado_yolo is not None:
            # Salvar resultado
            output_path = "yolo_deteccao_5_classes.jpg"
            cv2.imwrite(output_path, resultado_yolo)
            
            print("🎉 SUCESSO! YOLO DETECTOU PISO TÁTIL")
            print(f"💾 Resultado salvo: resultados/{output_path}")
            
            # Informações do resultado
            print(f"\n📏 Dimensões resultado: {resultado_yolo.shape[:2]}")
            
        else:
            print("❌ YOLO não detectou piso tátil na imagem")
        
        # Teste sistema híbrido
        print("\n⚡ TESTE SISTEMA HÍBRIDO...")
        resultado_hibrido = detector.detectar_piso_tatil(img)
        
        if resultado_hibrido is not None:
            output_hibrido = "hibrido_deteccao_5_classes.jpg"
            cv2.imwrite(output_hibrido, resultado_hibrido)
            print(f"✅ Sistema híbrido funcionando: resultados/{output_hibrido}")
        
        print(f"\n🎯 CLASSES TREINADAS (5 tipos):")
        print("0: piso_tatil - Geral/padrão")
        print("1: piso_tatil_direcional - Linhas direcionais") 
        print("2: piso_tatil_alerta - Pontos de alerta")
        print("3: piso_tatil_direcional_vertical - Vertical")
        print("4: piso_tatil_direcional_horizontal - Horizontal")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Garantir que pasta resultados existe
    os.makedirs("resultados", exist_ok=True)
    testar_yolo_treinado()
