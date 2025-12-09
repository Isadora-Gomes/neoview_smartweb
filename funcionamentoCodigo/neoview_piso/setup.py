"""
Setup script para a biblioteca pisotatil.

Este arquivo permite instalar a biblioteca pisotatil usando pip install.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler o README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Ler os requirements
requirements = []
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'opencv-python>=4.8.0',
        'numpy>=1.24.0',
        'pillow>=9.5.0',
        'pyyaml>=6.0',
        'pathlib2>=2.3.7',
        'configparser>=5.3.0'
    ]

setup(
    name="pisotatil",
    version="1.0.0",
    author="Sistema de Detecção de Pisos Táteis",
    author_email="",
    description="Biblioteca para detecção de pisos táteis usando visão computacional",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/neoview-piso",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "yolo": [
            "ultralytics>=8.0.0",
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "scikit-learn>=1.3.0"
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0"
        ]
    },
    include_package_data=True,
    package_data={
        "pisotatil": ["*.conf", "*.yaml", "*.yml"],
        "config": ["*.conf"]
    },
    entry_points={
        "console_scripts": [
            "pisotatil-test=teste_rapido:main",
            "pisotatil-exemplo=exemplo_uso:main",
        ],
    },
    keywords="computer-vision opencv tactile-paving accessibility yolo detection",
    project_urls={
        "Bug Reports": "https://github.com/seu-usuario/neoview-piso/issues",
        "Source": "https://github.com/seu-usuario/neoview-piso",
        "Documentation": "https://github.com/seu-usuario/neoview-piso/blob/main/README.md"
    }
)
