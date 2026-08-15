#!/usr/bin/env python
"""
Script para executar testes do projeto Previsão do Tempo.

Uso:
    python run_tests.py          # Executa com pytest
    python run_tests.py direct   # Executa direto sem pytest
"""

import subprocess
import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'direct':
        # Execução direta dos testes (sem pytest)
        print("Executando testes direto com pytest (unittest)...\n")
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v'],
            cwd='.'
        )
        return result.returncode
    else:
        # Execução padrão com pytest
        print("Executando testes com pytest...\n")
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            cwd='.'
        )
        return result.returncode

if __name__ == '__main__':
    sys.exit(main())
