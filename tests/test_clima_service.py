"""Testes para o serviço de clima"""

import sys
from pathlib import Path

# Adicionar diretório pai ao sys.path para permitir imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import Mock, patch

import pytest

from core.clima_service import ClimaService
from core.exceptions import ApiConnectionError, CidadeNaoEncontradaError
from core.models import CondicaoClima, Coordenadas


class TestClimaService:
    """Testes para ClimaService"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.service = ClimaService()
    
    def test_traduzir_clima(self):
        """Testa tradução de código WMO"""
        # Céu limpo
        condicao = CondicaoClima.from_code(0)
        assert condicao.icone == "☀️"
        assert condicao.descricao == "Céu limpo"
        
        # Chuva moderada
        condicao = CondicaoClima.from_code(63)
        assert condicao.icone == "🌧️"
        assert condicao.descricao == "Chuva moderada"
        
        # Código inválido
        condicao = CondicaoClima.from_code(999)
        assert condicao.icone == "❓"
        assert condicao.descricao == "Código 999"
    
    def test_cidade_invalida(self):
        """Testa rejeição de entrada malformada"""
        with pytest.raises(ValueError):
            self.service.buscar_previsao("!")

        with pytest.raises(ValueError):
            self.service.buscar_previsao("  ")

    @patch('core.api_client.ApiClient.geocodificar')
    def test_cidade_nao_encontrada(self, mock_geocode):
        """Testa erro quando cidade não é encontrada"""
        mock_geocode.return_value = None
        
        with pytest.raises(CidadeNaoEncontradaError):
            self.service.buscar_previsao("CidadeInexistente")

    @patch('core.api_client.ApiClient.geocodificar')
    def test_offline_fallback_usa_ultimo_dado(self, mock_geocode):
        """Testa retorno do último dado quando a rede falha e há dado em cache."""
        cidade = "Carambeí"
        previsao = self.service._parsear_previsao(
            Coordenadas(latitude=-24.0, longitude=-50.0, cidade=cidade, pais="Brasil"),
            {
                'current': {
                    'weather_code': 0,
                    'temperature_2m': 25.0,
                    'apparent_temperature': 26.0,
                    'relative_humidity_2m': 60,
                    'wind_speed_10m': 10.0,
                    'wind_direction_10m': 180,
                    'precipitation': 0.0,
                    'pressure_msl': 1012.0,
                    'cloud_cover': 10,
                },
                'daily': {
                    'time': ['2026-08-15'],
                    'weather_code': [0],
                    'temperature_2m_max': [28.0],
                    'temperature_2m_min': [18.0],
                    'precipitation_sum': [0.0],
                },
            }
        )
        self.service.cache[cidade.lower().strip()] = previsao
        self.service.ultimo_dado = previsao
        self.service.offline_mode = True

        mock_geocode.side_effect = ApiConnectionError("Sem conexão")

        resultado = self.service.buscar_previsao(cidade)

        assert resultado is previsao
        assert self.service.offline_mode is True