import os
import logging

from fastapi import FastAPI
from api import core_router
from api import webhook_router
from api import tasks_router

app = FastAPI(title="E-commerce Search API")

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "ecomuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ecompass")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

# Incluir routers de la API
app.include_router(core_router)
app.include_router(webhook_router)
app.include_router(tasks_router)
