"""
Guia completo para treinar YOLO para detectar caminhos de piso tátil.

Para detectar CAMINHOS COMPLETOS de piso tátil (não apenas pontos isolados),
o treinamento de um modelo YOLO é altamente recomendado.

VANTAGENS DO TREINAMENTO:
- Detecta caminhos inteiros, não apenas blocos pequenos
- Reconhece diferentes tipos de piso tátil
- Funciona melhor com variações de iluminação e ângulo
- Detecta padrões complexos que algoritmos simples não conseguem
"""

from pisotatil.training.yolo_trainer import YOLOTrainer
import os

def iniciar_treinamento_piso_tatil():
    """
    Guia passo-a-passo para treinar YOLO para piso tátil.
    """
    print("🚀 GUIA DE TREINAMENTO YOLO PARA PISO TÁTIL")
    print("=" * 50)
    
    print("\n📋 PASSOS NECESSÁRIOS:")
    print("1. Coleta de dados - imagens de pisos táteis variados")
    print("2. Anotação das imagens - marcar regiões de piso tátil")
    print("3. Preparação do dataset - format YOLO")
    print("4. Treinamento do modelo")
    print("5. Validação e teste")
    
    print(f"\n📁 ESTRUTURA DE PASTAS RECOMENDADA:")
    print("dataset_piso_tatil/")
    print("├── images/")
    print("│   ├── train/")
    print("│   └── val/")
    print("└── labels/")
    print("    ├── train/")
    print("    └── val/")
    
    print(f"\n🎯 CLASSES ATUALIZADAS:")
    classes = [
        "piso_tatil_direcional",
        "piso_tatil_alerta",
        "piso_tatil_direcional_vertical",
        "piso_tatil_direcional_horizontal",
        "piso_tatil"
    ]
    
    for i, classe in enumerate(classes):
        print(f"   {i}: {classe}")
    
    print(f"\n📋 USO RECOMENDADO:")
    print(f"   🔍 piso_tatil - Para qualquer piso tátil genérico")
    print(f"   📏 piso_tatil_direcional - Pisos com linhas (qualquer direção)")
    print(f"   ⚠️ piso_tatil_alerta - Pisos com pontos/bolinhas de alerta")
    
    # Verificar se há dados para treinar
    dataset_dir = "dataset_piso_tatil"
    if not os.path.exists(dataset_dir):
        print(f"\n📦 CRIANDO ESTRUTURA INICIAL...")
        criar_estrutura_dataset(dataset_dir, classes)
        print(f"✅ Estrutura criada em: {dataset_dir}")
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"1. Adicione suas imagens em {dataset_dir}/images/train/")
        print(f"2. Use uma ferramenta como LabelImg para anotar")
        print(f"3. Execute novamente para iniciar o treinamento")
    else:
        # Verificar se há dados
        train_images = len(os.listdir(os.path.join(dataset_dir, "images", "train")))
        if train_images > 0:
            print(f"\n📊 DADOS ENCONTRADOS:")
            print(f"   Imagens de treino: {train_images}")
            iniciar_treinamento_yolo(dataset_dir, classes)
        else:
            print(f"\n⚠️ PASTA CRIADA MAS SEM IMAGENS")
            print(f"Adicione imagens em {dataset_dir}/images/train/")

def criar_estrutura_dataset(base_dir, classes):
    """Cria estrutura de pastas para dataset YOLO."""
    dirs_to_create = [
        "images/train",
        "images/val", 
        "labels/train",
        "labels/val"
    ]
    
    for dir_path in dirs_to_create:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
    
    # Criar arquivo de classes
    with open(os.path.join(base_dir, "classes.txt"), "w") as f:
        for classe in classes:
            f.write(f"{classe}\n")
    
    # Criar arquivo de configuração do dataset
    config_yaml = f"""# Dataset de Piso Tátil - Atualizado
path: {os.path.abspath(base_dir)}
train: images/train
val: images/val

# Classes atualizadas
nc: {len(classes)}
names: 
  - 'piso_tatil'                      # Classe 0 - Geral
  - 'piso_tatil_direcional'          # Classe 1 - Com linhas
  - 'piso_tatil_alerta'              # Classe 2 - Com bolinhas
  - 'piso_tatil_direcional_vertical' # Classe 3 - Linhas verticais
  - 'piso_tatil_direcional_horizontal' # Classe 4 - Linhas horizontais
"""
    
    with open(os.path.join(base_dir, "dataset.yaml"), "w") as f:
        f.write(config_yaml)

def iniciar_treinamento_yolo(dataset_dir, classes):
    """Inicia o treinamento YOLO."""
    print(f"\n🔧 CONFIGURANDO TREINAMENTO...")
    
    try:
        from pisotatil.training.yolo_trainer import YOLOConfig
        
        # Criar configuração
        config = YOLOConfig(
            model_name="yolov8n.pt",
            epochs=50,
            batch_size=8,
            img_size=640
        )
        
        # Usar o trainer da biblioteca
        trainer = YOLOTrainer(
            config=config,
            project_root="."
        )
        
        print(f"✅ Trainer configurado")
        print(f"\n🚀 PARA TREINAR:")
        print(f"1. Adicione imagens em dataset_piso_tatil/images/train/")
        print(f"2. Adicione anotações em dataset_piso_tatil/labels/train/") 
        print(f"3. Use: trainer.treinar_modelo()")
        
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        print(f"\n💡 ALTERNATIVAS:")
        print(f"1. Use um modelo pré-treinado e faça fine-tuning")
        print(f"2. Colete mais dados de treinamento")
        print(f"3. Use transfer learning com YOLOv8")

def usar_modelo_treinado(modelo_path="runs/detect/train/weights/best.pt"):
    """Como usar o modelo treinado para detectar caminhos completos."""
    print(f"\n🎯 USANDO MODELO TREINADO PARA CAMINHOS COMPLETOS")
    print("=" * 50)
    
    if not os.path.exists(modelo_path):
        print(f"❌ Modelo não encontrado: {modelo_path}")
        print(f"💡 Primeiro execute o treinamento!")
        return
    
    try:
        from pisotatil.training.yolo_trainer import YOLODetector
        
        # Carregar modelo treinado
        detector = YOLODetector(modelo_path)
        
        # Detectar em sua imagem
        resultado = detector.detect("teste_piso_tatil.jpg", 
                                   save_results=True,
                                   confidence_threshold=0.3)  # Mais sensível
        
        if resultado:
            print("🎉 CAMINHOS COMPLETOS DETECTADOS!")
            print(f"📊 Detecções encontradas: {len(resultado)}")
            for i, det in enumerate(resultado):
                print(f"   {i+1}. {det['class']} - confiança: {det['confidence']:.2f}")
        else:
            print("❌ Nenhum caminho detectado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🏗️ SISTEMA DE TREINAMENTO PARA CAMINHOS COMPLETOS")
    print()
    
    # Explicar diferença
    print("🔄 DIFERENÇA ENTRE ABORDAGENS:")
    print("📍 Detector atual (OpenCV): Detecta pontos/linhas individuais")
    print("🛤️ Detector treinado (YOLO): Detecta CAMINHOS COMPLETOS")
    print()
    
    escolha = input("Deseja configurar treinamento? (s/n): ").strip().lower()
    
    if escolha == 's':
        iniciar_treinamento_piso_tatil()
    else:
        print("💡 Para detectar caminhos completos, recomendo:")
        print("1. Executar este script com 's'")
        print("2. Coletar 100-500 imagens de pisos táteis variados") 
        print("3. Anotar as imagens")
        print("4. Treinar o modelo")
        print()
        print("🎯 Resultado: Detecção de caminhos inteiros, não apenas blocos!")
