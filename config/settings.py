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
            'bg': '#0a0a1a',
            'bg_frame': '#12122a',
            'bg_card': '#1a1a3e',
            'neon_rosa': '#ff6b9d',
            'neon_azul': '#4ecdc4',
            'neon_verde': '#7bed9f',
            'neon_roxo': '#a29bfe',
            'neon_amarelo': '#ffeaa7',
            'neon_laranja': '#fd79a8',
            'texto_claro': '#f0f0f0',
            'neon_dourado': '#ffd700',
            'neon_vermelho': '#ff4757'
        }

        self.THEME_LIGHT = {
            'bg': '#f0f0f0',
            'bg_frame': '#e0e0e0',
            'bg_card': '#ffffff',
            'neon_rosa': '#e84393',
            'neon_azul': '#00b894',
            'neon_verde': '#00b894',
            'neon_roxo': '#6c5ce7',
            'neon_amarelo': '#fdcb6e',
            'neon_laranja': '#e17055',
            'texto_claro': '#2d3436',
            'neon_dourado': '#fdcb6e',
            'neon_vermelho': '#d63031'
        }


config = Config()