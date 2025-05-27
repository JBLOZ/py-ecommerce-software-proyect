from fastapi import FastAPI
try:
    from utils import get_logger
except ImportError:
    from .utils.logger import get_logger

logger = get_logger("inference_main")

try:
    from inference_controller import router as inference_router
except ImportError:
    from .inference_controller import router as inference_router

logger.info("Iniciando aplicación de inferencia")
app = FastAPI()

# Incluir el router sin prefijo para que las rutas estén en la raíz
app.include_router(inference_router)
logger.info("Router de inferencia configurado correctamente")
