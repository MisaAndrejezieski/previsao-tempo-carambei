from dataclasses import dataclass

from config.settings import config


@dataclass
class NeonTheme:
    """Tema neon do aplicativo"""
    bg: str = config.THEME_DARK['bg']
    bg_frame: str = config.THEME_DARK['bg_frame']
    bg_card: str = config.THEME_DARK['bg_card']
    neon_rosa: str = config.THEME_DARK['neon_rosa']
    neon_azul: str = config.THEME_DARK['neon_azul']
    neon_verde: str = config.THEME_DARK['neon_verde']
    neon_roxo: str = config.THEME_DARK['neon_roxo']
    neon_amarelo: str = config.THEME_DARK['neon_amarelo']
    neon_laranja: str = config.THEME_DARK['neon_laranja']
    texto_claro: str = config.THEME_DARK['texto_claro']
    neon_dourado: str = config.THEME_DARK['neon_dourado']
    neon_vermelho: str = config.THEME_DARK['neon_vermelho']
    
    def alternar_tema(self):
        """Alterna entre tema escuro e claro"""
        # Implementação para alternar tema
        pass