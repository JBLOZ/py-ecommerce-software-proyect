import os
# import logging
from api import core_router
from api import webhook_router
from api import tasks_router
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import DatabaseRegistry, load_sample_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar la base de datos y cargar datos de muestra
    print("Inicializando la conexión a la base de datos...")
    DatabaseRegistry.initialize(
        os.getenv("DB_URL", "mysql+pymysql://user:password@db/ecommerce")
    )
    # Cargar datos sintéticos
    load_sample_data()

    yield

    # Limpieza al cerrar la aplicación
    print("Cerrando conexiones a la base de datos...")
    DatabaseRegistry.close()


app = FastAPI(
    title="E-commerce Search API",
    lifespan=lifespan
)

# Configuración de la base de datos
# Usar la URL de conexión completa
DB_URL = os.getenv("DB_URL", "mysql+pymysql://user:password@db/ecommerce")

# Incluir routers de la API
app.include_router(core_router)
app.include_router(webhook_router)
app.include_router(tasks_router)
