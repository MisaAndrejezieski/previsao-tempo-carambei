"""Testes para o serviço de clima"""

from unittest.mock import Mock, patch

import pytest

from core.clima_service import ClimaService
from core.exceptions import CidadeNaoEncontradaError
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
    
    @patch('core.api_client.ApiClient.geocodificar')
    def test_cidade_nao_encontrada(self, mock_geocode):
        """Testa erro quando cidade não é encontrada"""
        mock_geocode.return_value = None
        
        with pytest.raises(CidadeNaoEncontradaError):
            self.service.buscar_previsao("CidadeInexistente")