"""
Setup de logging comum para todas as mini apps.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    logger_name: str = "bwb"
) -> logging.Logger:
    """
    Configura logging para console e ficheiro.
    
    Args:
        log_file: Caminho para ficheiro de log (opcional)
        level: Nível de logging
        logger_name: Nome do logger
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Remover handlers existentes (para evitar duplicação em re-runs)
    logger.handlers = []
    
    # Formato
    fmt = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)
    
    # File handler (se especificado)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    
    return logger
