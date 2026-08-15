"""Pytest configuration for path resolution"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao sys.path para permitir imports
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
