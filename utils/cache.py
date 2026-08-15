"""Sistema de cache para dados climáticos"""

import hashlib
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


class FileCache:
    """Cache persistente em arquivo"""
    
    def __init__(self, cache_dir: Path, ttl_seconds: int = 300):
        """
        Inicializa o cache
        
        Args:
            cache_dir: Diretório para armazenar cache
            ttl_seconds: Tempo de vida do cache em segundos
        """
        self.cache_dir = cache_dir
        self.ttl = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Retorna o caminho do arquivo de cache"""
        # Criar hash da chave para nome de arquivo seguro
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache
        
        Args:
            key: Chave para buscar
            
        Returns:
            Valor armazenado ou None se não existir/expirou
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            # Verificar expiração
            timestamp = data.get('timestamp')
            if timestamp:
                criado_em = datetime.fromisoformat(timestamp)
                if datetime.now() - criado_em > timedelta(seconds=self.ttl):
                    # Cache expirado
                    cache_path.unlink(missing_ok=True)
                    return None
            
            return data.get('value')
            
        except Exception:
            return None
    
    def set(self, key: str, value: Any):
        """
        Armazena um valor no cache
        
        Args:
            key: Chave para armazenar
            value: Valor a ser armazenado
        """
        cache_path = self._get_cache_path(key)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass
    
    def clear(self):
        """Limpa todo o cache"""
        for file in self.cache_dir.glob('*.pkl'):
            file.unlink()
    
    def delete(self, key: str):
        """Remove um item específico do cache"""
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)