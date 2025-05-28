"""
Módulo de configuración centralizada de logging.

Este módulo proporciona funciones para configurar y obtener loggers
con una configuración consistente en toda la aplicación.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Configuración global para centralizar logs de todo inference
# Usar ruta relativa que funcione tanto en local como en CI/CD
log_file_path = os.path.join(os.getcwd(), 'logs', 'inference.log')
log_dir = os.path.dirname(log_file_path)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# Detectar el perfil de ejecución (dev o prod)
environment = os.getenv("ENVIRONMENT", "prod").lower()
log_level = logging.DEBUG if environment == "dev" else logging.INFO

# Formatos
console_format = logging.Formatter('      %(levelname)-7s %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handlers
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(console_format)
# Rotating file handler: 10MB por archivo, 5 backups
file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(file_format)


logging.basicConfig(level=log_level, handlers=[stream_handler, file_handler])

# También forzar handlers en root (por si basicConfig no los añade)
root_logger = logging.getLogger()
if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == file_handler.baseFilename for h in root_logger.handlers):
    root_logger.addHandler(file_handler)
if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
    root_logger.addHandler(stream_handler)

# Redirigir logs de uvicorn y FastAPI al root logger
for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    log = logging.getLogger(logger_name)
    if log.name == logger_name:
        log.handlers = []
        log.propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado con un formato y nivel consistente.
    Los logs van tanto a consola como a /logs/inference.log (rotativo)
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger
