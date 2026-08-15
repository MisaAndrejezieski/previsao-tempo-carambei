import logging
import re
from datetime import datetime
from typing import Optional

from cachetools import TTLCache

from config.settings import config
from core.api_client import ApiClient
from core.exceptions import (ApiConnectionError, ApiTimeoutError,
                             CidadeNaoEncontradaError)
from core.models import (ClimaAtual, CondicaoClima, PrevisaoCompleta,
                         PrevisaoDia)

logger = logging.getLogger(__name__)

class ClimaService:
    def __init__(self):
        self.api = ApiClient()
        self.cache = TTLCache(maxsize=100, ttl=config.API_CACHE_TTL)
        self.offline_mode = False
        self.ultimo_dado: Optional[PrevisaoCompleta] = None

    def validar_cidade(self, cidade: str) -> str:
        """Valida e normaliza o nome da cidade antes da busca."""
        if cidade is None:
            raise ValueError("Nome da cidade não pode ser vazio")

        cidade = cidade.strip()
        if len(cidade) < 2:
            raise ValueError("Nome da cidade deve ter pelo menos 2 caracteres")
        if len(cidade) > 100:
            raise ValueError("Nome da cidade excedeu o limite de 100 caracteres")

        if not re.fullmatch(r"[A-Za-zÀ-ÿ0-9\s\-\.]+", cidade):
            raise ValueError("Nome da cidade contém caracteres inválidos")

        return cidade

    def buscar_previsao(self, cidade: str) -> Optional[PrevisaoCompleta]:
        """Busca previsão e usa fallback offline quando a API falha."""
        cidade = self.validar_cidade(cidade)
        cache_key = cidade.lower().strip()

        if self.offline_mode and self.ultimo_dado is not None:
            logger.warning(f"Modo offline ativo para {cidade}; retornando último dado válido")
            return self.ultimo_dado

        if cache_key in self.cache:
            logger.info(f"Usando cache para {cidade}")
            previsao_cache = self.cache[cache_key]
            self.ultimo_dado = previsao_cache
            return previsao_cache

        try:
            coords = self.api.geocodificar(cidade)
            if not coords:
                logger.warning(f"Cidade não encontrada: {cidade}")
                raise CidadeNaoEncontradaError(f"Cidade '{cidade}' não encontrada")

            dados = self.api.buscar_clima(coords)
            if not dados:
                logger.error(f"Falha ao buscar dados para {cidade}")
                return None

            previsao = self._parsear_previsao(coords, dados)
            self.cache[cache_key] = previsao
            self.ultimo_dado = previsao
            self.offline_mode = False
            return previsao

        except (ApiConnectionError, ApiTimeoutError, ConnectionError, TimeoutError) as e:
            logger.error(f"Falha de rede ao buscar {cidade}: {e}")
            self.offline_mode = True
            if self.ultimo_dado is not None:
                return self.ultimo_dado
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar previsão: {e}")
            raise
    
    def _parsear_previsao(self, coords, dados) -> PrevisaoCompleta:
        """Converte dados da API para modelos"""
        current = dados.get('current', {})
        daily = dados.get('daily', {})
        
        # Clima atual
        condicao = CondicaoClima.from_code(current.get('weather_code', 0))
        clima_atual = ClimaAtual(
            coordenadas=coords,
            temperatura=current.get('temperature_2m', 0.0),
            sensacao_termica=current.get('apparent_temperature', 0.0),
            umidade=current.get('relative_humidity_2m', 0),
            vento_kmh=current.get('wind_speed_10m', 0.0),
            direcao_vento=current.get('wind_direction_10m', 0),
            precipitacao=current.get('precipitation', 0.0),
            pressao=current.get('pressure_msl', 0.0),
            nuvens=current.get('cloud_cover', 0),
            condicao=condicao
        )
        
        # Previsão 7 dias
        previsao_dias = []
        datas = daily.get('time', [])
        
        for i in range(min(7, len(datas))):
            data = datetime.strptime(datas[i], '%Y-%m-%d')
            condicao_dia = CondicaoClima.from_code(
                daily.get('weather_code', [])[i] if i < len(daily.get('weather_code', [])) else 0
            )
            
            previsao_dias.append(PrevisaoDia(
                data=data,
                condicao=condicao_dia,
                temp_max=daily.get('temperature_2m_max', [])[i] if i < len(daily.get('temperature_2m_max', [])) else 0.0,
                temp_min=daily.get('temperature_2m_min', [])[i] if i < len(daily.get('temperature_2m_min', [])) else 0.0,
                precipitacao=daily.get('precipitation_sum', [])[i] if i < len(daily.get('precipitation_sum', [])) else 0.0
            ))
        
        return PrevisaoCompleta(
            atual=clima_atual,
            previsao_7dias=previsao_dias
        )
    
    def limpar_cache(self):
        """Limpa o cache"""
        self.cache.clear()
        logger.info("Cache limpo")