#!/bin/bash
# Script de instalação para Linux/Mac
echo "📦 INSTALANDO PISOTATIL CLI"
echo "============================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado! Instale Python 3.8+ primeiro."
    exit 1
fi

# Instalar dependências
echo "🔄 Instalando dependências..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro na instalação das dependências!"
    exit 1
fi

# Tornar executável
chmod +x main.py
chmod +x piso_tatil.py

echo "✅ Instalação concluída!"
echo ""
echo "🚀 Como usar:"
echo "  python3 main.py detectar sua_imagem.jpg"
echo "  python3 main.py demo"
echo "  python3 main.py treinar"
echo ""
