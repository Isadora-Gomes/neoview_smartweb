"""
Script utilitário para testar rapidamente a detecção de pisos táteis.
"""

import cv2
import numpy as np
import argparse
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para importar a biblioteca pisotatil
sys.path.append(str(Path(__file__).parent))

try:
    from pisotatil import PisoTatil, PerformanceMonitor, redimensionar_frame
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que as dependências estão instaladas: pip install -r requirements.txt")
    sys.exit(1)


def testar_imagem(caminho_imagem, debug=False):
    """Testa detecção em uma imagem específica."""
    print(f"Testando detecção na imagem: {caminho_imagem}")
    
    # Carregar imagem
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"Erro: Não foi possível carregar a imagem {caminho_imagem}")
        return False
    
    # Inicializar detector
    detector = PisoTatil(debug=debug)
    
    # Detectar
    resultado = detector.detectar_piso_tatil(img)
    
    if resultado is not None:
        print("✓ Piso tátil detectado!")
        
        # Redimensionar para exibição
        resultado = redimensionar_frame(resultado, width=800)
        
        # Mostrar resultado
        cv2.imshow('Detecção de Piso Tátil', resultado)
        print("Pressione qualquer tecla para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True
    else:
        print("✗ Nenhum piso tátil detectado")
        
        # Mostrar imagem original
        img_redim = redimensionar_frame(img, width=800)
        cv2.imshow('Imagem Original (sem detecções)', img_redim)
        print("Pressione qualquer tecla para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return False


def testar_webcam(debug=False):
    """Testa detecção em tempo real com webcam."""
    print("Testando detecção em tempo real...")
    print("Pressione 'q' para sair")
    
    # Inicializar detector e monitor
    detector = PisoTatil(debug=debug)
    monitor = PerformanceMonitor()
    
    # Abrir webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a webcam")
        return False
    
    deteccoes_count = 0
    frames_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frames_count += 1
            inicio = cv2.getTickCount()
            
            # Redimensionar para melhor performance
            frame_proc = redimensionar_frame(frame, width=640)
            
            # Detectar
            resultado = detector.detectar_piso_tatil(frame_proc)
            
            # Calcular performance
            fim = cv2.getTickCount()
            tempo = (fim - inicio) / cv2.getTickFrequency()
            monitor.atualizar(tempo)
            
            # Preparar frame para exibição
            if resultado is not None:
                frame_exibir = resultado
                deteccoes_count += 1
                status_text = "DETECTADO"
                status_color = (0, 255, 0)
            else:
                frame_exibir = frame_proc
                status_text = "Procurando..."
                status_color = (0, 255, 255)
            
            # Adicionar informações na tela
            stats = monitor.get_stats()
            cv2.putText(frame_exibir, f"FPS: {stats['fps']:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame_exibir, f"Status: {status_text}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(frame_exibir, f"Deteccoes: {deteccoes_count}/{frames_count}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Teste Webcam - Piso Tátil', frame_exibir)
            
            # Sair com 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Estatísticas finais
    stats = monitor.get_stats()
    print(f"\nEstatísticas:")
    print(f"Frames processados: {frames_count}")
    print(f"Detecções: {deteccoes_count}")
    print(f"Taxa de detecção: {(deteccoes_count/frames_count)*100:.1f}%")
    print(f"FPS médio: {stats['fps']:.2f}")
    
    return True


def criar_imagem_teste():
    """Cria uma imagem de teste com padrões similares a pisos táteis."""
    print("Criando imagem de teste...")
    
    # Criar imagem base
    img = np.ones((400, 600, 3), dtype=np.uint8) * 220
    
    # Adicionar pontos (lado esquerdo)
    for y in range(50, 350, 30):
        for x in range(50, 250, 30):
            # Variar posição e tamanho
            cx = x + np.random.randint(-5, 6)
            cy = y + np.random.randint(-5, 6)
            raio = np.random.randint(8, 12)
            
            cv2.circle(img, (cx, cy), raio, (80, 80, 80), -1)
            cv2.circle(img, (cx-2, cy-2), raio//3, (120, 120, 120), -1)
    
    # Adicionar linhas (lado direito)
    for x in range(320, 550, 12):
        cv2.line(img, (x, 50), (x, 350), (70, 70, 70), 2)
    
    # Salvar imagem
    caminho = "teste_piso_tatil.jpg"
    cv2.imwrite(caminho, img)
    print(f"Imagem de teste criada: {caminho}")
    
    return caminho


def main():
    parser = argparse.ArgumentParser(description="Teste rápido do detector de pisos táteis")
    parser.add_argument("--imagem", "-i", help="Caminho para imagem de teste")
    parser.add_argument("--webcam", "-w", action="store_true", help="Testar com webcam")
    parser.add_argument("--criar-teste", "-c", action="store_true", help="Criar imagem de teste")
    parser.add_argument("--debug", "-d", action="store_true", help="Modo debug (mostra processamento)")
    
    args = parser.parse_args()
    
    print("🔍 Teste Rápido - Detector de Pisos Táteis")
    print("==========================================")
    
    if args.criar_teste:
        caminho = criar_imagem_teste()
        print(f"\nImagem de teste criada: {caminho}")
        print("Execute novamente com: python teste_rapido.py -i teste_piso_tatil.jpg")
        
    elif args.imagem:
        sucesso = testar_imagem(args.imagem, debug=args.debug)
        if sucesso:
            print("\n✓ Teste concluído com sucesso!")
        else:
            print("\n⚠ Teste concluído - nenhuma detecção")
            
    elif args.webcam:
        sucesso = testar_webcam(debug=args.debug)
        if sucesso:
            print("\n✓ Teste de webcam concluído!")
        
    else:
        print("Uso:")
        print("  python teste_rapido.py -c              # Criar imagem de teste")
        print("  python teste_rapido.py -i imagem.jpg   # Testar imagem específica")
        print("  python teste_rapido.py -w              # Testar com webcam")
        print("  python teste_rapido.py -d -i img.jpg   # Modo debug")


if __name__ == "__main__":
    main()
