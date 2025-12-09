# 🔍 NeoView Piso - Detecção de Pisos Táteis

Biblioteca Python para detecção automática de pisos táteis usando visão computacional e aprendizado de máquina.

## 🚀 Instalação Rápida

### Windows:
```bash
# Clone ou baixe o projeto
# Execute na pasta do projeto:
instalar.bat
```

### Linux/Mac:
```bash
# Clone ou baixe o projeto
# Execute na pasta do projeto:
chmod +x instalar.sh
./instalar.sh
```

### Manual:
```bash
pip install -r requirements.txt
```

## 📋 Uso via CLI

### 🔍 Detectar piso tátil em imagem:
```bash
# Detecção básica
python main.py detectar sua_imagem.jpg

# Com sensibilidade alta
python main.py detectar sua_imagem.jpg --sensibilidade alto

# Com debug ativo
python main.py detectar sua_imagem.jpg --debug
```

### 🎯 Executar demonstração:
```bash
python main.py demo
```

### 🤖 Configurar treinamento YOLO:
```bash
python main.py treinar
```

### ⚙️ Gerenciar configurações:
```bash
# Listar configurações
python main.py config --listar

# Definir configuração
python main.py config --definir chave valor
```

### 📦 Instalar dependências:
```bash
python main.py instalar
```

## 💻 Uso Programático

```python
from pisotatil import PisoTatil
import cv2

# Criar detector
detector = PisoTatil()

# Carregar imagem
img = cv2.imread('piso_tatil.jpg')

# Detectar
resultado = detector.detectar_piso_tatil(img)

if resultado is not None:
    cv2.imwrite('resultado.jpg', resultado)
    print("✅ Piso tátil detectado!")
else:
    print("❌ Nenhum piso tátil encontrado")
```

## 🎯 Funcionalidades

### 🔍 **Detecção OpenCV (Atual)**
- ✅ Detecta pontos circulares e linhas direcionais
- ✅ Múltiplos níveis de sensibilidade
- ✅ Validação avançada de padrões
- ⚠️ Limitado a blocos pequenos de piso

### 🤖 **Treinamento YOLO (Recomendado)**
- 🚀 Detecta caminhos completos de piso tátil
- 🎯 Reconhecimento de padrões complexos
- 🔧 Configuração automática de dataset
- 📊 Métricas de performance detalhadas

## 📁 Estrutura do Projeto

```
neoview_piso/
├── 🚀 main.py                 # Ponto de entrada CLI
├── 🔧 piso_tatil.py          # CLI principal
├── 📦 pisotatil/             # Biblioteca principal
├── 📁 scripts/               # Scripts auxiliares
├── 📁 config/                # Configurações
├── 🤖 dataset_piso_tatil/    # Dataset para treinamento
└── 📖 README.md              # Esta documentação
```

## 🎛️ Parâmetros de Sensibilidade

| Nível | Uso Recomendado | Descrição |
|-------|-----------------|-----------|
| `baixo` | Imagens claras, pisos bem definidos | Detecção conservadora |
| `medio` | **Uso geral** (padrão) | Equilibrio entre precisão e cobertura |
| `alto` | Imagens difíceis, baixo contraste | Detecção mais sensível |

## 🔄 Exemplos Práticos

### Detecção básica:
```bash
python main.py detectar teste_piso_tatil.jpg
# Saída: resultado_teste_piso_tatil.jpg
```

### Para caminhos completos:
```bash
# 1. Configurar treinamento
python main.py treinar

# 2. Adicionar suas imagens ao dataset
# 3. Anotar com LabelImg
# 4. Executar treinamento
```

## ❗ Limitações Atuais

- **OpenCV:** Detecta apenas blocos pequenos (3-5% da imagem)
- **Para caminhos completos:** Necessário treinamento YOLO
- **Precisão:** Dependente da qualidade da imagem

## 🎊 Resultados Esperados

### Com OpenCV:
- ✅ Pontos individuais marcados
- ✅ Linhas direcionais identificadas
- ⚠️ Cobertura limitada (blocos pequenos)

### Com YOLO Treinado:
- 🚀 Caminhos completos detectados
- 🎯 60-90% de cobertura da área
- 🔧 Robustez a variações de iluminação

---

**Versão:** 1.0.0 | **Autor:** NeoView Team
