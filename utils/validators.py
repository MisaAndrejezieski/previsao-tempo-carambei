"""Validadores para os dados de entrada"""

import re
from typing import Optional


def validar_cidade(cidade: str) -> bool:
    """
    Valida se o nome da cidade é válido
    
    Args:
        cidade: Nome da cidade
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not cidade or not cidade.strip():
        return False
    
    # Remover espaços extras
    cidade = cidade.strip()
    
    # Verificar comprimento
    if len(cidade) < 2 or len(cidade) > 100:
        return False
    
    # Verificar caracteres permitidos (letras, espaços, acentos, hífen, ponto)
    # Isso é básico, pode ser melhorado
    pattern = r'^[A-Za-zÀ-ÿ\s\-\.]+$'
    if not re.match(pattern, cidade):
        return False
    
    return True

def normalizar_cidade(cidade: str) -> str:
    """Normaliza o nome da cidade"""
    if not cidade:
        return ""
    return cidade.strip().title()

def extrair_pais(cidade_completa: str) -> Optional[str]:
    """Extrai o país do nome da cidade se presente"""
    # Exemplo: "São Paulo, Brasil" -> "Brasil"
    if ',' in cidade_completa:
        partes = cidade_completa.split(',')
        return partes[-1].strip()
    return None