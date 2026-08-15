import logging
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import config
from core.exceptions import ApiConnectionError, ApiTimeoutError
from core.models import Coordenadas

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = config.API_TIMEOUT
        
    @retry(
        stop=stop_after_attempt(config.API_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def geocodificar(self, cidade: str) -> Optional[Coordenadas]:
        """Busca coordenadas da cidade"""
        try:
            params = {
                'name': cidade,
                'count': 1,
                'language': 'pt',
                'format': 'json'
            }
            
            response = self.session.get(
                config.GEOCODING_URL,
                params=params,
                timeout=config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    return Coordenadas(
                        latitude=result['latitude'],
                        longitude=result['longitude'],
                        cidade=result['name'],
                        pais=result.get('country', 'Brasil'),
                        regiao=result.get('admin1')
                    )
            return None
            
        except requests.Timeout:
            logger.error(f"Timeout ao geocodificar {cidade}")
            raise ApiTimeoutError(f"Servidor demorou muito para responder")
        except requests.ConnectionError:
            logger.error(f"Sem conexão ao geocodificar {cidade}")
            raise ApiConnectionError("Verifique sua conexão com a internet")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None
    
    @retry(
        stop=stop_after_attempt(config.API_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def buscar_clima(self, coords: Coordenadas) -> Optional[dict]:
        """Busca dados climáticos"""
        try:
            params = {
                'latitude': coords.latitude,
                'longitude': coords.longitude,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'America/Sao_Paulo',
                'forecast_days': 7
            }
            
            response = self.session.get(
                config.WEATHER_URL,
                params=params,
                timeout=config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except requests.Timeout:
            logger.error(f"Timeout ao buscar clima para {coords.cidade}")
            raise ApiTimeoutError("Servidor demorou muito para responder")
        except requests.ConnectionError:
            logger.error(f"Sem conexão ao buscar clima para {coords.cidade}")
            raise ApiConnectionError("Verifique sua conexão com a internet")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None