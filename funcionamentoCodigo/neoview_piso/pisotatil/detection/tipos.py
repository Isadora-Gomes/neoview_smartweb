"""
Enumeração das classes de piso tátil.
"""

from enum import Enum

class PisoTatil(Enum):
    """Tipos de piso tátil para mapeamento."""
    horizontal = "piso_tatil_direcional_horizontal"
    vertical = "piso_tatil_direcional_vertical"  
    alerta = "piso_tatil_alerta"
