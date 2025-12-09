"""
Demonstração rápida da biblioteca pisotatil.

Este script mostra como usar a biblioteca de diferentes formas:
1. Import direto
2. Detecção básica
3. Configuração personalizada
"""

import cv2
import numpy as np

def demo_uso_basico():
    """Demonstra uso básico da biblioteca."""
    print("🎯 Demo: Uso Básico da Biblioteca PisoTatil")
    print("-" * 50)
    
    # Import da biblioteca
    from pisotatil import PisoTatil
    
    # Criar detector
    detector = PisoTatil(debug=False)
    print("✓ Detector PisoTatil criado")
    
    # Criar imagem de exemplo
    img = criar_exemplo_piso_tatil()
    print("✓ Imagem de exemplo criada")
    
    # Detectar
    resultado = detector.detectar_piso_tatil(img)
    
    if resultado is not None:
        print("🎉 Piso tátil detectado!")
        
        # Salvar resultado
        cv2.imwrite("demo_resultado.jpg", resultado)
        print("✓ Resultado salvo em: demo_resultado.jpg")
        
        # Mostrar se possível
        try:
            cv2.imshow('Demo - Detecção de Piso Tátil', resultado)
            print("Pressione qualquer tecla para continuar...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except:
            print("(Interface gráfica não disponível)")
            
        return True
    else:
        print("❌ Nenhum piso tátil detectado")
        return False


def demo_configuracao():
    """Demonstra configuração personalizada."""
    print("\n⚙️ Demo: Configuração Personalizada")
    print("-" * 50)
    
    from pisotatil import PisoTatil
    from config import config_manager
    
    # Obter configurações
    params = config_manager.get_detection_params()
    print("✓ Parâmetros carregados do arquivo de configuração")
    
    # Criar detector com configurações
    detector = PisoTatil()
    detector.configurar_parametros(**params)
    print("✓ Detector configurado com parâmetros personalizados")
    
    print(f"- Raio mínimo: {params['hough_circles_params']['min_radius']}")
    print(f"- Raio máximo: {params['hough_circles_params']['max_radius']}")
    print(f"- Limiar de contraste: {params['contrast_threshold']}")


def demo_imports():
    """Demonstra diferentes formas de importar."""
    print("\n📦 Demo: Opções de Import")
    print("-" * 50)
    
    # Método 1: Import básico
    try:
        from pisotatil import PisoTatil
        print("✓ Método 1: from pisotatil import PisoTatil")
    except ImportError as e:
        print(f"❌ Método 1 falhou: {e}")
    
    # Método 2: Import completo
    try:
        import pisotatil
        detector = pisotatil.PisoTatil()
        print("✓ Método 2: import pisotatil")
    except ImportError as e:
        print(f"❌ Método 2 falhou: {e}")
    
    # Método 3: Import de módulos específicos
    try:
        from pisotatil.detection import PisoTatil
        print("✓ Método 3: from pisotatil.detection import PisoTatil")
    except ImportError as e:
        print(f"❌ Método 3 falhou: {e}")
    
    # Método 4: Import de treinamento (se disponível)
    try:
        from pisotatil.training import YOLOTrainer, YOLOConfig
        print("✓ Método 4: Módulos de treinamento YOLO disponíveis")
    except ImportError as e:
        print(f"⚠ Método 4: YOLO não disponível - {e}")


def criar_exemplo_piso_tatil():
    """Cria uma imagem sintética com padrão de piso tátil."""
    # Imagem base
    img = np.ones((300, 400, 3), dtype=np.uint8) * 200
    
    # Adicionar pontos táteis
    for y in range(50, 250, 25):
        for x in range(50, 200, 25):
            cv2.circle(img, (x, y), 8, (100, 100, 100), -1)
            cv2.circle(img, (x-2, y-2), 3, (150, 150, 150), -1)
    
    # Adicionar linhas direcionais
    for x in range(220, 350, 10):
        cv2.line(img, (x, 50), (x, 250), (80, 80, 80), 2)
    
    return img


def main():
    """Função principal da demonstração."""
    print("🚀 Demonstração da Biblioteca PisoTatil")
    print("=" * 50)
    print("Este script demonstra o uso da biblioteca pisotatil\n")
    
    # Demonstrações
    demos = [
        ("Imports", demo_imports),
        ("Configuração", demo_configuracao),
        ("Uso Básico", demo_uso_basico)
    ]
    
    for nome, func in demos:
        try:
            func()
        except Exception as e:
            print(f"❌ Erro na demo {nome}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Demonstração concluída!")
    print("\nPara mais exemplos, execute:")
    print("- python exemplo_uso.py")
    print("- python teste_rapido.py -c")
    print("- pisotatil-exemplo (se instalado)")


if __name__ == "__main__":
    main()
