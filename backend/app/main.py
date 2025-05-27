import os
from api import webhook_router
from controllers import core_router, tasks_router
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import DatabaseRegistry, load_sample_data
from utils import get_logger

logger = get_logger("backend_main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar la base de datos y cargar datos de muestra
    logger.info("Iniciando aplicación backend")
    logger.info("Inicializando la conexión a la base de datos...")
    DatabaseRegistry.initialize(
        os.getenv("DB_URL", "mysql+pymysql://user:password@db/ecommerce")
    )
    logger.info("Base de datos inicializada correctamente.")
    
    # Cargar datos sintéticos
    logger.info("Iniciando carga de datos de muestra...")
    load_sample_data()
    logger.info("Carga de datos de muestra completada.")

    yield

    # Limpieza al cerrar la aplicación
    logger.info("Cerrando conexiones a la base de datos...")
    DatabaseRegistry.close()
    logger.info("Aplicación backend cerrada correctamente")


app = FastAPI(
    title="E-commerce Search API",
    lifespan=lifespan
)

# Configuración de la base de datos
# Usar la URL de conexión completa
DB_URL = os.getenv("DB_URL", "mysql+pymysql://user:password@db/ecommerce")

# Incluir routers de la API
logger.info("Configurando routers de la aplicación")
app.include_router(core_router)
app.include_router(webhook_router)
app.include_router(tasks_router)
logger.info("Routers configurados correctamente")
