#!/usr/bin/env python3
"""Ponto de entrada do aplicativo Previsão do Tempo Neon"""

import sys
import tkinter as tk
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from utils.logger import log


def main():
    """Função principal"""
    try:
        log.info("Iniciando Previsão do Tempo Neon v4.0")
        
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
        
        log.info("Aplicativo finalizado")
        
    except KeyboardInterrupt:
        log.info("Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        log.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()