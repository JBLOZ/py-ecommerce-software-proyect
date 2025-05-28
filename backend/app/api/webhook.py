"""
Weeebhook API for receiving task completion notifications from the inference server.
This API is used to receive the results of tasks that have been processed by the inference server.
The inference server sends a POST request to this API with the task ID and the result of the task.

You can learn more about the webhook API in the following link:
https://fastapi.tiangolo.com/advanced/openapi-webhooks/
"""

from typing import List
import os

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from services import ResultService
from db import CategoryTypes
from utils import get_logger

logger = get_logger("backend_webhook_api")

router = APIRouter()


class Prediction(BaseModel):
    """Inference result for a single task."""

    label: int = Field(..., ge=1, le=len(CategoryTypes), example=1)
    score: float = Field(..., ge=0, le=1, example=0.97)


class TaskResult(BaseModel):
    """Task result received from the inference server."""

    task_id: str
    state: str = Field(..., example="completed")
    categories: List[Prediction]


@router.post("/webhook/task_completed", status_code=status.HTTP_202_ACCEPTED)
async def receive_task_result(payload: TaskResult):
    """Receive task completion notification from the inference server."""
    logger.info(f"Recibida notificación de tarea completada: {payload.task_id}")
    logger.debug(f"Estado de la tarea: {payload.state}")
    logger.debug(f"Número de categorías recibidas: {len(payload.categories)}")

    # Leer umbral de confianza desde variable de entorno (por defecto 0.1)
    try:
        threshold = float(os.getenv("INFERENCE_CONFIDENCE_THRESHOLD", 0.1))
    except Exception:
        threshold = 0.1
    logger.info(f"Umbral de confianza para categorías: {threshold}")

    # Filtrar categorías por score
    filtered_categories = [cat for cat in payload.categories if cat.score > threshold]
    logger.info(f"Categorías filtradas (>{threshold}): {len(filtered_categories)}")

    try:
        result_service = ResultService()
        result_service.store_result(payload.task_id, filtered_categories)
        logger.info(f"Resultado almacenado exitosamente para tarea: {payload.task_id}")

        # Log category details in debug mode
        for i, pred in enumerate(filtered_categories):
            logger.debug(f"Categoría {i}: label={pred.label}, score={pred.score:.4f}")

        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error almacenando resultado para tarea {payload.task_id}: {str(e)}", exc_info=True)
        raise
