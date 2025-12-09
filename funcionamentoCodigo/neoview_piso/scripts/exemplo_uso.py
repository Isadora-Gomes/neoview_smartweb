"""
Exemplo de uso da classe PisoTatil para detecção de pisos táteis.

Este exemplo demonstra como usar a classe PisoTatil para detectar
pisos táteis em imagens, vídeos ou câmera em tempo real.
"""

import cv2
import sys
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path para importar a biblioteca pisotatil
sys.path.append(str(Path(__file__).parent))

from pisotatil import PisoTatil, PerformanceMonitor, redimensionar_frame
from config import config_manager


def exemplo_imagem():
    """Exemplo de detecção em uma única imagem."""
    print("=== Exemplo: Detecção em Imagem ===")
    
    # Inicializar detector
    detector = PisoTatil(debug=True)
    
    # Simular uma imagem (você pode substituir por cv2.imread('sua_imagem.jpg'))
    # Criando uma imagem de exemplo com padrão circular
    img = criar_imagem_exemplo()
    
    if img is None:
        print("Erro: Não foi possível carregar a imagem")
        return
    
    # Detectar piso tátil
    resultado = detector.detectar_piso_tatil(img)
    
    if resultado is not None:
        print("✓ Piso tátil detectado!")
        
        # Redimensionar para visualização se necessário
        resultado_redim = redimensionar_frame(resultado, width=800)
        
        # Mostrar resultado
        cv2.imshow('Detecção de Piso Tátil', resultado_redim)
        print("Pressione qualquer tecla para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("✗ Nenhum piso tátil detectado")


def exemplo_video():
    """Exemplo de detecção em vídeo."""
    print("\n=== Exemplo: Detecção em Vídeo ===")
    
    # Inicializar detector e monitor de performance
    detector = PisoTatil(debug=False)
    monitor = PerformanceMonitor()
    
    # Usar webcam (0) ou arquivo de vídeo
    cap = cv2.VideoCapture(0)  # Webcam
    # cap = cv2.VideoCapture('seu_video.mp4')  # Arquivo de vídeo
    
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera/vídeo")
        return
    
    print("Iniciando detecção... Pressione 'q' para sair")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        inicio = cv2.getTickCount()
        
        # Redimensionar frame para melhor performance
        frame_processamento = redimensionar_frame(frame, width=640)
        
        # Detectar piso tátil
        resultado = detector.detectar_piso_tatil(frame_processamento)
        
        # Calcular tempo de processamento
        fim = cv2.getTickCount()
        tempo_processamento = (fim - inicio) / cv2.getTickFrequency()
        monitor.atualizar(tempo_processamento)
        
        # Mostrar frame (original ou com detecção)
        frame_exibir = resultado if resultado is not None else frame_processamento
        
        # Adicionar informações de performance
        stats = monitor.get_stats()
        cv2.putText(frame_exibir, f"FPS: {stats['fps']:.1f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame_exibir, f"Frame: {frame_count}", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Detecção de Piso Tátil - Vídeo', frame_exibir)
        
        # Sair com 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Limpeza
    cap.release()
    cv2.destroyAllWindows()
    
    # Mostrar estatísticas finais
    stats = monitor.get_stats()
    print(f"\nEstatísticas finais:")
    print(f"FPS médio: {stats['fps']:.2f}")
    print(f"Tempo médio: {stats['tempo_medio']:.3f}s")
    print(f"Frames processados: {frame_count}")


def criar_imagem_exemplo():
    """Cria uma imagem de exemplo com padrão que simula piso tátil."""
    import numpy as np
    
    # Criar imagem base
    img = np.ones((400, 600, 3), dtype=np.uint8) * 200  # Fundo cinza claro
    
    # Adicionar pontos circulares (simulando piso tátil de pontos)
    for i in range(5, 350, 40):
        for j in range(50, 300, 40):
            # Variar um pouco a posição para parecer mais real
            x = j + np.random.randint(-5, 6)
            y = i + np.random.randint(-5, 6)
            raio = np.random.randint(8, 15)
            
            # Círculos mais escuros
            cv2.circle(img, (x, y), raio, (100, 100, 100), -1)
            # Pequeno highlight
            cv2.circle(img, (x-3, y-3), raio//3, (150, 150, 150), -1)
    
    # Adicionar algumas linhas na segunda metade (simulando piso direcional)
    for i in range(320, 580, 15):
        cv2.line(img, (i, 50), (i, 350), (80, 80, 80), 3)
    
    # Adicionar ruído para tornar mais realista
    noise = np.random.randint(-20, 21, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return img


def exemplo_configuracao_personalizada():
    """Exemplo de como usar configurações personalizadas."""
    print("\n=== Exemplo: Configurações Personalizadas ===")
    
    # Carregar configurações personalizadas
    params = config_manager.get_detection_params()
    print("Parâmetros de detecção carregados:")
    print(f"- Raio mínimo de círculos: {params['hough_circles_params']['min_radius']}")
    print(f"- Raio máximo de círculos: {params['hough_circles_params']['max_radius']}")
    print(f"- Limiar de contraste: {params['contrast_threshold']}")
    
    # Criar detector com configurações
    detector = PisoTatil()
    
    # Configurar parâmetros dinamicamente
    detector.configurar_parametros(**params)
    
    print("✓ Detector configurado com parâmetros personalizados")


def exemplo_yolo_futuro():
    """Exemplo de como usar o detector YOLO (quando disponível)."""
    print("\n=== Exemplo: Detector YOLO (Futuro) ===")
    
    try:
        from pisotatil.training import YOLODetector
        
        # Verificar se existe modelo treinado
        modelo_path = "models/piso_tatil_detector/weights/best.pt"
        
        if Path(modelo_path).exists():
            detector_yolo = YOLODetector(modelo_path, confidence_threshold=0.5)
            print("✓ Detector YOLO carregado com sucesso")
            
            # Usar da mesma forma que o detector OpenCV
            img = criar_imagem_exemplo()
            resultado = detector_yolo.detectar_piso_tatil(img)
            
            if resultado is not None:
                print("✓ Detecção YOLO realizada com sucesso")
        else:
            print(f"ℹ Modelo YOLO não encontrado em: {modelo_path}")
            print("  Execute o treinamento primeiro para criar o modelo.")
            
    except ImportError as e:
        print(f"⚠ YOLO não disponível: {e}")
        print("  Instale as dependências: pip install ultralytics")


def main():
    """Função principal com menu de exemplos."""
    logging.basicConfig(level=logging.INFO)
    
    print("🔍 Exemplos de Detecção de Pisos Táteis")
    print("=====================================")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Detecção em imagem de exemplo")
        print("2. Detecção em vídeo/webcam")
        print("3. Configurações personalizadas")
        print("4. Exemplo YOLO (futuro)")
        print("5. Sair")
        
        escolha = input("\nOpção (1-5): ").strip()
        
        try:
            if escolha == '1':
                exemplo_imagem()
            elif escolha == '2':
                exemplo_video()
            elif escolha == '3':
                exemplo_configuracao_personalizada()
            elif escolha == '4':
                exemplo_yolo_futuro()
            elif escolha == '5':
                print("Saindo...")
                break
            else:
                print("Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário.")
            break
        except Exception as e:
            print(f"\nErro: {e}")
            logging.exception("Erro durante execução do exemplo")


if __name__ == "__main__":
    main()
