from fastapi import APIRouter, Body, UploadFile, File, HTTPException
from sqlmodel import select
from db import DatabaseRegistry, Category, Product
from utils import get_logger
import requests
import os
import uuid

logger = get_logger("backend_core_controller")

router = APIRouter()

# Configuración del servicio de inferencia
INFERENCE_SERVICE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://inference-dev:80")


@router.get("/health")
def health_check():
    logger.debug("Health check solicitado")
    return {"status": "ok"}


@router.get("/categories")
def get_categories():
    logger.info("Solicitando lista de categorías")
    session = DatabaseRegistry.session()
    categories = session.exec(select(Category)).all()
    logger.debug(f"Encontradas {len(categories)} categorías")
    return {"categories": [{"id": c.id, "name": c.name} for c in categories]}


@router.get("/products")
def get_products():
    logger.info("Solicitando lista de productos")
    session = DatabaseRegistry.session()
    products = session.exec(select(Product)).all()
    logger.debug(f"Encontrados {len(products)} productos")
    return {"products": [{"id": p.id, "name": p.name, "price": p.price} for p in products]}


@router.post("/search/text")
def search_text(payload: dict = Body(...)):
    query = payload.get("query", "").lower()
    logger.info(f"Búsqueda de texto solicitada - query: '{query}'")
    
    session = DatabaseRegistry.session()
    # Buscar categorías por coincidencia de nombre
    all_cats = session.exec(select(Category)).all()
    matched = [c.name for c in all_cats if query and c.name.lower() in query]
    logger.debug(f"Categorías encontradas: {matched}")
    
    # Obtener productos de categorías coincidentes
    products = session.exec(select(Product)).all()
    filtered = [p for p in products if p.category_id in [c.id for c in all_cats if c.name in matched]]
    logger.info(f"Búsqueda completada - {len(matched)} categorías, {len(filtered)} productos")
    
    return {"categories": matched, "products": [{"id": p.id, "name": p.name, "price": p.price} for p in filtered]}


@router.post("/search/image")
async def search_image(file: UploadFile = File(...)):
    """
    Recibe una imagen enviada por el usuario, encola una tarea de inferencia y devuelve un task_id.
    """
    logger.info(f"Búsqueda por imagen solicitada - archivo: {file.filename}")
    try:
        # Verificar que el archivo sea una imagen
        if not file.content_type or not file.content_type.startswith("image/"):
            logger.warning(f"Archivo inválido recibido - tipo: {file.content_type}")
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Preparar el archivo para enviarlo al servicio de inferencia
        file_data = await file.read()
        logger.debug(f"Imagen leída - tamaño: {len(file_data)} bytes")
        
        # Enviar la imagen al servicio de inferencia
        files = {"file": (file.filename, file_data, file.content_type)}
        logger.debug(f"Enviando imagen al servicio de inferencia: {INFERENCE_SERVICE_URL}")
        response = requests.post(
            f"{INFERENCE_SERVICE_URL}/infer/image",
            files=files,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Error del servicio de inferencia - status: {response.status_code}")
            raise HTTPException(
                status_code=500, 
                detail="Error al procesar la imagen en el servicio de inferencia"
            )
        
        result = response.json()
        logger.info(f"Tarea de inferencia creada exitosamente - task_id: {result['task_id']}")
        return {"task_id": result["task_id"]}
        
    except requests.RequestException as e:
        logger.error(f"Error de conexión con servicio de inferencia: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión con el servicio de inferencia: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error interno en búsqueda por imagen: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
