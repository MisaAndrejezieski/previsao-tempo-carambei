import sys

from loguru import logger

from config.settings import config


def setup_logger():
    """Configura o sistema de logging"""
    logger.remove()  # Remove handlers padrão
    
    # Console
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Arquivo
    logger.add(
        config.LOGS_DIR / "app.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
        level="DEBUG"
    )
    
    return logger

# Exportar logger configurado
log = setup_logger()