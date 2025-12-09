#!/usr/bin/env python3
"""
PisoTatil CLI - Interface de linha de comando para detecção de piso tátil.
"""

import argparse
import sys
import os
from pathlib import Path
import cv2
import numpy as np
from typing import Optional
from pisotatil import PisoTatil

# Adicionar o diretório atual ao path para importar a biblioteca
sys.path.insert(0, str(Path(__file__).parent))

def detectar_comando(args):
    """Comando para detectar elementos de piso tátil na imagem."""
    try:
        from pisotatil.detection.piso_tatil import PisoTatilDeteccao
        
        print("DETECÇÃO DE PISO TÁTIL")
        print("=" * 30)
        
        # Verificar se arquivo existe
        caminho_imagem = Path(args.imagem)
        if not caminho_imagem.exists():
            print(f"ERRO: Arquivo não encontrado: {args.imagem}")
            return
        
        # Carregar imagem
        imagem = cv2.imread(str(caminho_imagem))
        if imagem is None:
            print(f"ERRO: Não foi possível carregar a imagem: {args.imagem}")
            return
        
        altura, largura = imagem.shape[:2]
        print(f"Imagem: {caminho_imagem.name}")
        print(f"Dimensões: {largura}x{altura} pixels")
        
        # Inicializar detector
        detector = PisoTatilDeteccao(debug=True)
        
        print(f"\nStatus do detector:")
        print(f"   YOLO disponível: {detector.use_yolo}")
        
        if not detector.use_yolo or not detector.yolo_detector:
            print(f"   Modelo carregado: FALHA")
            print("Para usar YOLO, verifique se existe modelo em:")
            print("   - models/piso_tatil_detector5/weights/best.pt")
            return
        
        print(f"   Modelo carregado: OK")
        
        # Detectar elementos usando YOLO direto
        print(f"\nExecutando detecção...")
        resultado_frame = detector.detectar_piso_tatil(imagem)
        
        if resultado_frame is not None:
            print(f"Piso tátil detectado!")
            
            # Salvar resultado
            nome_base = caminho_imagem.stem
            arquivo_saida = f"resultado_{nome_base}.jpg"
            cv2.imwrite(arquivo_saida, resultado_frame)
            print(f"Imagem com detecções salva: {arquivo_saida}")
        else:
            print("Nenhum piso tátil detectado na imagem")
        
     
    except ImportError as e:
        print(f"Erro de importação: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

def mapear_comando(args):
    """Comando para mapear pisos táteis em uma sequência de imagens."""
    try:
        from pisotatil.detection.piso_tatil import PisoTatilDeteccao
        
        print("MAPEAMENTO DE PISO TÁTIL")
        print("=" * 30)
        
        # Verificar se arquivo existe
        caminho_imagem = Path(args.imagem)
        if not caminho_imagem.exists():
            print(f"ERRO: Arquivo não encontrado: {args.imagem}")
            return
        
        # Carregar imagem
        imagem = cv2.imread(str(caminho_imagem))
        if imagem is None:
            print(f"ERRO: Não foi possível carregar a imagem: {args.imagem}")
            return
        
        altura, largura = imagem.shape[:2]
        print(f"Imagem: {caminho_imagem.name}")
        print(f"Dimensões: {largura}x{altura} pixels")
        
        # Inicializar detector
        detector = PisoTatilDeteccao(debug=True)
        
        print(f"\nStatus do detector:")
        print(f"   YOLO disponível: {detector.use_yolo}")
        
        if not detector.use_yolo or not detector.yolo_detector:
            print(f"   Modelo carregado: FALHA")
            print("Para usar YOLO, verifique se existe modelo em:")
            print("   - models/piso_tatil_detector5/weights/best.pt")
            return
        
        print(f"   Modelo carregado: OK")
        
        # Mapear pisos táteis
        print(f"\nExecutando mapeamento...")
        resultado = detector.mapear(imagem)
        mapeamento = resultado.mapa

        def icone_para_piso(tipo_piso: PisoTatil):
            if tipo_piso == PisoTatil.horizontal:
                return "—"
            elif tipo_piso == PisoTatil.vertical:
                return "|"
            elif tipo_piso == PisoTatil.alerta:
                return "•"
            else:
                return "?"

        if mapeamento is not None:
            print(f"Mapeamento concluído!")

            show_matrix = np.full(mapeamento.shape, fill_value=" ", dtype=str)
            
            for i in range(mapeamento.shape[0]):
                for j in range(mapeamento.shape[1]):
                    cell = mapeamento[i,j]
                    
                    if cell is not None:
                        show_matrix[i,j] = icone_para_piso( cell.classe )
            
            print("\nMAPA:")
            for row in show_matrix:
                print(" ".join(row))
            
            # Salvar mapa em arquivo de texto
            nome_base = caminho_imagem.stem
            arquivo_mapa = f"mapa_{nome_base}.txt"
            
            with open(arquivo_mapa, 'w', encoding='utf-8') as f:
                f.write(f"# MAPA DE PISO TÁTIL\n")
                f.write(f"# Gerado a partir de: {caminho_imagem.name}\n")
                f.write(f"# Dimensões originais: {largura}x{altura} pixels\n")
                f.write(f"# Dimensões do mapa: {mapeamento.shape[1]}x{mapeamento.shape[0]} células\n")
                f.write(f"#\n")
                f.write(f"# Legenda:\n")
                f.write(f"#   — = Caminho horizontal\n")
                f.write(f"#   | = Caminho vertical\n")
                f.write(f"#   • = Ponto de alerta\n")
                f.write(f"#     = Vazio\n")
                f.write(f"#\n")
                
                for row in show_matrix:
                    f.write(" ".join(row) + "\n")
            
            print(f"Mapa salvo como: {arquivo_mapa}")
            
            # Gerar narração do caminho
            print(f"\nNARRAÇÃO DO CAMINHO:")
            print(resultado.leitura)
            
        else:
            print("Nenhum piso tátil detectado para mapeamento na imagem")
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

def treinar_comando(args):
    """Comando para treinar o modelo YOLO."""
    try:
        from pisotatil.training.yolo_trainer import YOLOTrainer, YOLOConfig
        
        print("TREINAMENTO DO MODELO YOLO")
        print("=" * 30)
        
        # Verificar se há dataset
        dataset_path = Path("dataset_piso_tatil")
        if not dataset_path.exists():
            print("ERRO: Dataset não encontrado!")
            print("Para treinar o modelo, você precisa de um dataset com:")
            print("  - dataset_piso_tatil/images/train/")
            print("  - dataset_piso_tatil/labels/train/")
            print("  - dataset_piso_tatil/images/val/")
            print("  - dataset_piso_tatil/labels/val/")
            return
        
        # Criar configuração de treinamento a partir do arquivo settings.conf
        try:
            from config import config_manager
            
            # Obter configurações YOLO do arquivo
            yolo_params = config_manager.get_yolo_params()
            
            config = YOLOConfig(
                model_name=yolo_params['model_name'],
                img_size=yolo_params['img_size'],
                batch_size=yolo_params['batch_size'],
                epochs=yolo_params['epochs'],
                learning_rate=yolo_params['learning_rate'],
                confidence_threshold=yolo_params['confidence_threshold'],
                iou_threshold=yolo_params['iou_threshold'],
                device=yolo_params['device'],
                patience=yolo_params['patience']
            )
            
            print(f"Configurações carregadas de: config/settings.conf")
            
        except ImportError:
            print("Aviso: config_manager não encontrado, usando valores padrão")
            config = YOLOConfig(
                epochs=100,  # Reduzir para teste inicial
                batch_size=8,  # Reduzir para hardware mais limitado
                device="cpu"  # Usar CPU por padrão
            )
        
        # Inicializar trainer
        project_root = str(Path.cwd())
        trainer = YOLOTrainer(config, project_root)
        
        print("Configuração do treinamento:")
        print(f"  - Modelo base: {trainer.config.model_name}")
        print(f"  - Épocas: {trainer.config.epochs}")
        print(f"  - Batch size: {trainer.config.batch_size}")
        print(f"  - Learning rate: {trainer.config.learning_rate}")
        print(f"  - Dispositivo: {trainer.config.device}")
        
        confirma = input("\nDeseja iniciar o treinamento? (s/N): ").strip().lower()
        if confirma != 's':
            print("Treinamento cancelado.")
            return
        
        print("\nIniciando treinamento...")
        print("NOTA: Este processo pode levar várias horas dependendo do hardware.")
        
        # Treinar modelo
        resultado = trainer.treinar_modelo()
        
        print("\nTreinamento concluído!")
        print(f"Modelo salvo em: models/piso_tatil_detector/weights/best.pt")
        
    except ImportError as e:
        print(f"Erro: {e}")
        print("Para usar treinamento, instale as dependências:")
        print("  pip install ultralytics")
    except Exception as e:
        print(f"Erro durante treinamento: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description='Sistema de Detecção e Mapeamento de Piso Tátil',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponíveis')
    
    # Comando detectar (básico)
    detectar_parser = subparsers.add_parser(
        'detectar',
        help='Detectar pisos táteis (básico)'
    )
    detectar_parser.add_argument(
        'imagem',
        type=str,
        help='Caminho para a imagem'
    )
    
    mapear_parser = subparsers.add_parser(
        'mapear',
        help='Mapear pisos táteis em uma sequência de imagens'
    )
    mapear_parser.add_argument(
        'imagem',
        type=str,
        help='Caminho para a imagem'
    )
    
    # Comando treinar
    treinar_parser = subparsers.add_parser(
        'treinar',
        help='Treinar o modelo YOLO para detecção de pisos táteis'
    )
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return

    if args.comando == 'detectar':
        detectar_comando(args)
    elif args.comando == 'mapear':
        mapear_comando(args)
    elif args.comando == 'treinar':
        treinar_comando(args)
    else:
        print(f"Comando desconhecido: {args.comando}")
        parser.print_help()

if __name__ == '__main__':
    main()
