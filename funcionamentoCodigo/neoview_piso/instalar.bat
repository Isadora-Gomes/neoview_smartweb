@echo off
REM Script de instalação rápida para Windows
echo 📦 INSTALANDO PISOTATIL CLI
echo ============================

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Instalar dependências
echo 🔄 Instalando dependências...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro na instalação das dependências!
    pause
    exit /b 1
)

echo ✅ Instalação concluída!
echo.
echo 🚀 Como usar:
echo   python main.py detectar sua_imagem.jpg
echo   python main.py demo
echo   python main.py treinar
echo.
pause
