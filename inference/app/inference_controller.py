from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import os
try:
    from utils import get_logger
except ImportError:
    from .utils.logger import get_logger

logger = get_logger("inference_controller")

try:
    from models import SqueezeNet
except ImportError:
    from .models.squeezenet import SqueezeNet
try:
    from tasks import process_image_task
except ImportError:
    from .tasks import process_image_task

logger.info("Controlador de inferencia iniciado correctamente")


# Inyección de dependencia para la tarea de Celery
def get_process_image_task():
    return process_image_task


router = APIRouter()


@router.get(
    "/health",
    summary="Endpoint de comprobación de salud",
    description="""
    Devuelve el estado de salud de la API de inferencia.
    Útil para monitorización y sondas de readiness/liveness.
    """
)
def health_check():
    logger.debug("Health check solicitado")
    return {"status": "ok"}


@router.post(
    "/infer/image",
    summary="Inferencia de imagen asíncrona",
    description="""
    Recibe un archivo de imagen y lo procesa de forma asíncrona usando Celery.
    Devuelve un ID de tarea para consultar el resultado más tarde.
    """
)
def infer_image(
    file: UploadFile = File(...),
    process_image_task=Depends(get_process_image_task)
):
    logger.info(f"Recibida solicitud de inferencia asíncrona - archivo: {file.filename}")
    try:
        image_data = file.file.read()
        logger.debug(f"Imagen leída correctamente - tamaño: {len(image_data)} bytes")

        task = process_image_task.delay(image_data)
        logger.info(f"Tarea de Celery creada - ID: {task.id}")

        return JSONResponse(content={"task_id": task.id})
    except Exception as e:
        logger.error(f"Error procesando imagen asíncrona: {str(e)}", exc_info=True)
        raise


@router.post(
    "/infer/image/sync",
    summary="Inferencia de imagen síncrona",
    description="""
    Recibe un archivo de imagen y lo procesa de forma síncrona usando el modelo SqueezeNet.
    Devuelve las categorías predichas inmediatamente.
    """
)
def infer_image_sync(file: UploadFile = File(...)):
    logger.info(f"Recibida solicitud de inferencia síncrona - archivo: {file.filename}")
    try:
        model_path = os.getenv("MODEL_PATH", "model.onnx")
        logger.debug(f"Cargando modelo desde: {model_path}")

        model = SqueezeNet(model_path)
        image_data = file.file.read()
        logger.debug(f"Imagen leída correctamente - tamaño: {len(image_data)} bytes")

        categories = model(image_data)
        logger.debug(f"Inferencia completada - categorías: {categories}")

        result = {"category": categories}
        logger.info("Inferencia síncrona completada exitosamente")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error procesando imagen síncrona: {str(e)}", exc_info=True)
        raise
