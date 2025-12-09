#!/usr/bin/env python3
"""
Ponto de entrada principal para o PisoTatil CLI.
Execute: python main.py <comando>
"""

import sys
import os
from pathlib import Path

# Garantir que o diretório atual está no path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    # Importar e executar a CLI principal
    from cli import main
    main()
