from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Coordenadas(BaseModel):
    latitude: float
    longitude: float
    cidade: str
    pais: str
    regiao: Optional[str] = None
    
    @validator('latitude')
    def validar_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude inválida')
        return v
    
    @validator('longitude')
    def validar_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude inválida')
        return v

class CondicaoClima(BaseModel):
    codigo: int
    descricao: str
    icone: str
    
    @classmethod
    def from_code(cls, code: int) -> 'CondicaoClima':
        codigos = {
            0: ("☀️", "Céu limpo"),
            1: ("🌤️", "Principalmente limpo"),
            2: ("⛅", "Parcialmente nublado"),
            3: ("☁️", "Encoberto"),
            45: ("🌫️", "Nevoeiro"),
            48: ("🌫️", "Nevoeiro gelado"),
            51: ("🌧️", "Chuvisco leve"),
            53: ("🌧️", "Chuvisco moderado"),
            55: ("🌧️", "Chuvisco forte"),
            61: ("🌧️", "Chuva leve"),
            63: ("🌧️", "Chuva moderada"),
            65: ("🌧️", "Chuva forte"),
            71: ("❄️", "Neve leve"),
            73: ("❄️", "Neve moderada"),
            75: ("❄️", "Neve forte"),
            80: ("🌧️", "Aguaceiros leves"),
            81: ("🌧️", "Aguaceiros moderados"),
            82: ("🌧️", "Aguaceiros fortes"),
            95: ("⛈️", "Trovoada"),
            96: ("⛈️", "Trovoada com granizo"),
            99: ("⛈️", "Trovoada forte com granizo")
        }
        icone, descricao = codigos.get(code, ("❓", f"Código {code}"))
        return cls(codigo=code, descricao=descricao, icone=icone)

class ClimaAtual(BaseModel):
    coordenadas: Coordenadas
    temperatura: float
    sensacao_termica: float
    umidade: int
    vento_kmh: float
    direcao_vento: int
    precipitacao: float
    pressao: float
    nuvens: int
    condicao: CondicaoClima
    atualizado_em: datetime = Field(default_factory=datetime.now)

class PrevisaoDia(BaseModel):
    data: datetime
    condicao: CondicaoClima
    temp_max: float
    temp_min: float
    precipitacao: float

class PrevisaoCompleta(BaseModel):
    atual: ClimaAtual
    previsao_7dias: List[PrevisaoDia]