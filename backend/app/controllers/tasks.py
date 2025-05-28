'''
API para la gestión de tareas.
Este módulo proporciona endpoints para consultar el estado y los resultados de tareas de inferencia.
'''

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from utils import get_logger

from services import ResultService
from db import Category, Product, DatabaseRegistry
from sqlmodel import select

logger = get_logger("backend_tasks_controller")

router = APIRouter()


class TaskStatus(BaseModel):
    """Estado de una tarea."""
    status: str


@router.get(
    "/tasks/{task_id}/result",
    status_code=status.HTTP_200_OK,
    responses={
        202: {"model": TaskStatus, "description": "Tarea pendiente"},
        404: {"model": TaskStatus, "description": "Tarea no encontrada"},
    },
)
async def get_task_result(task_id: str):
    """
    Consulta el resultado de una tarea de inferencia.
    Args:
        task_id: Identificador único de la tarea.
    Returns:
        Si la tarea está completada, devuelve las categorías predichas y los productos asociados.
        Si la tarea aún está en proceso, devuelve un estado "pending" con código HTTP 202.
        Si la tarea no existe, devuelve un error 404.
    """
    logger.info(f"Consultando resultado de tarea: {task_id}")
    result_service = ResultService()

    if not result_service.has_result(task_id):
        logger.debug(f"Tarea {task_id} aún en proceso")
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="La tarea aún está en proceso",
        )

    categories_predictions = result_service.get_result(task_id)
    logger.debug(f"Tarea {task_id} completada con {len(categories_predictions)} predicciones")

    # Filtrar predicciones por umbral de confianza (podría configurarse desde variables de entorno)
    confidence_threshold = 0.05  # Umbral configurable - lowered to show more results
    filtered_predictions = [p for p in categories_predictions if p.score >= confidence_threshold]
    logger.debug(f"Aplicado filtro de confianza {confidence_threshold}: {len(filtered_predictions)} predicciones válidas")

    if not filtered_predictions:
        logger.info(f"Tarea {task_id} - No hay predicciones que superen el umbral")
        return {"categories": [], "products": []}

    # Obtener categorías predichas
    category_ids = [p.label for p in filtered_predictions]
    logger.debug(f"IDs de categorías predichas: {category_ids}")

    # Buscar productos asociados a las categorías predichas
    session = DatabaseRegistry.session()
    categories = session.exec(
        select(Category).where(Category.id.in_(category_ids))
    ).all()

    # Obtener nombres de categorías
    category_names = [category.name for category in categories]
    logger.debug(f"Nombres de categorías encontradas: {category_names}")

    # Buscar productos de las categorías
    products = session.exec(
        select(Product).where(Product.category_id.in_(category_ids))
    ).all()

    logger.info(f"Tarea {task_id} completada exitosamente - {len(category_names)} categorías, {len(products)} productos")

    return {
        "categories": category_names,
        "products": [
            {"id": p.id, "name": p.name, "price": p.price}
            for p in products
        ],
    }
