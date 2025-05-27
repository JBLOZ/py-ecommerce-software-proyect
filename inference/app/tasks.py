import os
from celery import Celery
import requests
try:
    from utils import get_logger
except ImportError:
    from .utils.logger import get_logger

logger = get_logger("inference_tasks")

try:
    from models import SqueezeNet  
except ImportError:
    from .models.squeezenet import SqueezeNet

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND_WEBHOOK = os.getenv("BACKEND_WEBHOOK_URL", "http://backend:8000/webhook/task_completed")

logger.info(f"Configurando Celery con broker: {REDIS_URL}")
logger.info(f"Webhook backend configurado: {BACKEND_WEBHOOK}")

celery_app = Celery("inference", broker=REDIS_URL)
celery_app.conf.task_routes = {
    "tasks.process_image_task": {"queue": "image"},
    "app.tasks.process_image_task": {"queue": "image"}
}

logger.info("Celery configurado correctamente")


@celery_app.task(name='tasks.process_image_task')
def process_image_task(image_data: bytes):
    # Get the actual task ID from Celery
    task_id = process_image_task.request.id
    
    logger.info(f"Procesando tarea de imagen con ID: {task_id}")
    logger.debug(f"Tamaño de datos de imagen: {len(image_data)} bytes")

    try:
        model_path = os.getenv("SQUEEZENET_MODEL_PATH", "squeezenet.onnx")
        logger.debug(f"Cargando modelo desde: {model_path}")
        model = SqueezeNet(model_path)        
        logger.debug("Modelo SqueezeNet cargado correctamente")

        logger.info("Ejecutando inferencia en la imagen")
        result = model(image_data)
        logger.info(f"Inferencia completada. Resultados: {result}")

        # Transformar el resultado para que coincida con el formato esperado por el webhook
        # El modelo devuelve {"category": [{"label": X, "confidence": Y}]}
        # El webhook espera {"categories": [{"label": X, "score": Y}]}
        categories = [
            {"label": pred["label"], "score": pred["confidence"]}
            for pred in result["category"]
        ]

        response_data = {
            "task_id": task_id,
            "state": "completed",
            "categories": categories
        }
        
        logger.debug(f"Enviando respuesta al webhook: {BACKEND_WEBHOOK}")
        response = requests.post(BACKEND_WEBHOOK, json=response_data, timeout=10)
        logger.info(f"Respuesta enviada exitosamente. Status: {response.status_code}")

    except Exception as e:
        logger.error(f"Error procesando tarea {task_id}: {str(e)}", exc_info=True)
        
        error_response = {
            "task_id": task_id,
            "state": "failed",
            "error": str(e)
        }
        
        try:
            logger.debug(f"Enviando error al webhook: {BACKEND_WEBHOOK}")
            response = requests.post(BACKEND_WEBHOOK, json=error_response, timeout=10)
            logger.warning(f"Error enviado al webhook. Status: {response.status_code}")
        except Exception as webhook_error:
            logger.error(f"Error enviando webhook de fallo: {str(webhook_error)}", exc_info=True)

@celery_app.task(name='app.tasks.process_image_task')
def process_image_task_alias(image_data: bytes):
    logger.debug("Ejecutando alias de tarea de procesamiento de imagen")
    return process_image_task(image_data)
