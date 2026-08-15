import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')


@dataclass
class Config:
    APP_NAME: str = "Previsão do Tempo Neon"
    APP_VERSION: str = "4.0.0"

    # API
    API_TIMEOUT: int = 15
    API_RETRIES: int = 3
    API_CACHE_TTL: int = 300

    # Geocoding
    GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"

    # UI
    DEFAULT_WIDTH: int = 1200
    DEFAULT_HEIGHT: int = 800
    MIN_WIDTH: int = 1000
    MIN_HEIGHT: int = 700

    # Cores
    THEME_DARK: dict = None
    THEME_LIGHT: dict = None

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    CACHE_DIR: Path = BASE_DIR / ".cache"
    LOGS_DIR: Path = BASE_DIR / "logs"

    def __post_init__(self):
        self.API_TIMEOUT = int(os.getenv("API_TIMEOUT", self.API_TIMEOUT))
        self.API_RETRIES = int(os.getenv("API_RETRIES", self.API_RETRIES))
        self.API_CACHE_TTL = int(os.getenv("API_CACHE_TTL", self.API_CACHE_TTL))
        self.GEOCODING_URL = os.getenv("GEOCODING_URL", self.GEOCODING_URL)
        self.WEATHER_URL = os.getenv("WEATHER_URL", self.WEATHER_URL)

        self.CACHE_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)

        self.THEME_DARK = {
            'bg': '#0d1321',
            'bg_frame': '#121d2d',
            'bg_card': '#1a2940',
            'neon_rosa': '#ff9ec4',
            'neon_azul': '#8ecbff',
            'neon_verde': '#a9f0c9',
            'neon_roxo': '#d2c0ff',
            'neon_amarelo': '#fbe7a1',
            'neon_laranja': '#ffc9a2',
            'texto_claro': '#f5f1ff',
            'neon_dourado': '#f7d98a',
            'neon_vermelho': '#ff8ca8'
        }

        self.THEME_LIGHT = {
            'bg': '#f4f0ff',
            'bg_frame': '#e7e3ff',
            'bg_card': '#ffffff',
            'neon_rosa': '#ff9ec4',
            'neon_azul': '#7bb8ff',
            'neon_verde': '#8fe3b4',
            'neon_roxo': '#bca5ff',
            'neon_amarelo': '#f6d77d',
            'neon_laranja': '#f7be86',
            'texto_claro': '#24263a',
            'neon_dourado': '#f0c96a',
            'neon_vermelho': '#f28cab'
        }


config = Config()