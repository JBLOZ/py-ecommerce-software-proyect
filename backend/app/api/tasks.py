'''
API para la gestión de tareas.
Este módulo proporciona endpoints para consultar el estado y los resultados de tareas de inferencia.
'''

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from services import ResultService
from db import Category, Product, DatabaseRegistry
from sqlmodel import select

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
    result_service = ResultService()

    if not result_service.has_result(task_id):
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="La tarea aún está en proceso",
        )

    categories_predictions = result_service.get_result(task_id)

    # Filtrar predicciones por umbral de confianza (podría configurarse desde variables de entorno)
    confidence_threshold = 0.5  # Umbral configurable
    filtered_predictions = [p for p in categories_predictions if p.score >= confidence_threshold]

    if not filtered_predictions:
        return {"categories": [], "products": []}

    # Obtener categorías predichas
    category_ids = [p.label for p in filtered_predictions]

    # Buscar productos asociados a las categorías predichas
    session = DatabaseRegistry.session()
    categories = session.exec(
        select(Category).where(Category.id.in_(category_ids))
    ).all()

    # Obtener nombres de categorías
    category_names = [category.name for category in categories]

    # Buscar productos de las categorías
    products = session.exec(
        select(Product).where(Product.category_id.in_(category_ids))
    ).all()

    return {
        "categories": category_names,
        "products": [
            {"id": p.id, "name": p.name, "price": p.price}
            for p in products
        ],
    }
